"""
Camada de serviços: cálculos financeiros e regras de negócio que eram
duplicados entre views_dashboard, views_cal, context_processors,
views_cartao e views_transacao.

Centralizar aqui evita reescrever a mesma query/aggregate em N lugares
(cada um com pequenas variações que viravam bugs sutis) e facilita
futuros testes isolados da lógica financeira.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from .models import Cartao, Tipo, Transacao


def calcular_proxima_fatura(data_compra):
    """
    Compras em cartão (qualquer dia) vão sempre para o mês seguinte.

    Regra simplificada — o dia de fechamento foi removido da lógica de
    negócio. Mantida como função pública os módulos de view chamam
    diretamente (transacoes_mes_view, transacao_rapida, views_transacao).
    """
    return date(data_compra.year, data_compra.month, 1) + relativedelta(months=1)


def _aggregate_por_tipo(queryset):
    """ Retorna (creditos, debitos, saldo) via SQL aggregate. """
    por_codigo = queryset.values('tipo__codigo').annotate(total=Sum('valor'))
    creditos = Decimal('0')
    debitos = Decimal('0')
    for item in por_codigo:
        if item['tipo__codigo'] == 'C':
            creditos = item['total'] or Decimal('0')
        elif item['tipo__codigo'] == 'D':
            debitos = item['total'] or Decimal('0')
    return creditos, debitos, creditos - debitos


def saldos_do_mes(user, ano, mes):
    """
    Retorna dict com creditos, debitos e saldo de um mês/ano específico.

    Substitui o padrão repetido::

        ts = Transacao.objects.filter(user=user, data__year=ano, data__month=mes)
        c = ts.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or 0
        d = ts.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or 0
        s = c - d
    """
    qs = Transacao.objects.filter(
        user=user, data__year=ano, data__month=mes
    ).select_related('tipo')
    creditos, debitos, saldo = _aggregate_por_tipo(qs)
    return {
        'transacoes': qs,
        'creditos': creditos,
        'debitos': debitos,
        'saldo': saldo,
    }


def saldos_consecutivos(user, ano, mes):
    """
    Retorna saldos do mês atual e do mês seguinte — padrão usado pelo
    context_processor de navbar e pelo CalendarView.
    """
    atual = saldos_do_mes(user, ano, mes)

    data_prox = date(ano, mes, 1) + relativedelta(months=1)
    proximo = saldos_do_mes(user, data_prox.year, data_prox.month)

    return {
        'atual': atual,
        'proximo': proximo,
        'proximo_data': data_prox,
    }


def saldo_ano(user, ano):
    """
    Soma anual de creditos, debitos e saldo (substitui bloco equivalente
    em views_dashboard).
    """
    qs = Transacao.objects.filter(user=user, data__year=ano).select_related('tipo')
    return _aggregate_por_tipo(qs)


def detalhe_mensal_ano(user, ano):
    """
    Retorna OrderedDict {mes_num: {nome, credito, debito, saldo, grafico_labels, grafico_valores, tem_dados}}
    para alimentar o Dashboard Anual.
    """
    nomes_meses = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    from collections import OrderedDict
    detalhe = OrderedDict()
    for mes_num in range(1, 13):
        qs_mes = Transacao.objects.filter(
            user=user, data__year=ano, data__month=mes_num
        ).select_related('tipo', 'categoria')

        creditos, debitos, saldo = _aggregate_por_tipo(qs_mes)

        dados_categoria = qs_mes.values('categoria__nome').annotate(total=Sum('valor'))
        cat_labels = [item['categoria__nome'] or 'Sem Categoria' for item in dados_categoria]
        cat_valores = [float(item['total']) for item in dados_categoria]

        detalhe[mes_num] = {
            'nome': nomes_meses[mes_num],
            'credito': creditos,
            'debito': debitos,
            'saldo': saldo,
            'grafico_labels': cat_labels,
            'grafico_valores': cat_valores,
            'tem_dados': qs_mes.exists(),
        }
    return detalhe


def consumo_por_cartao(user, ano, mes):
    """
    Consumo total de cada cartão do usuário em um mês/ano específico.
    Substitui o loop em cartoes_resumo_view.
    """
    cartoes = Cartao.objects.filter(user=user)
    labels = []
    consumo_valores = []
    limite_valores = []
    for c in cartoes:
        transacoes_cartao = Transacao.objects.filter(
            user=user, cartao=c, data__month=mes, data__year=ano
        ).select_related('tipo')
        consumo = sum((t.valor_decimal for t in transacoes_cartao), Decimal('0'))
        labels.append(c.nome)
        consumo_valores.append(float(consumo))
        limite_valores.append(float(c.limite))
    return {
        'cartoes': cartoes,
        'labels': labels,
        'consumo': consumo_valores,
        'limites': limite_valores,
    }


def resumo_categorias_e_tipos(transacoes):
    """
    Dados para os gráficos de pizza em resumo_categoria_view.

    Recebe um queryset pré-filtrado (mês/ano) e retorna cat_labels,
    cat_valores, tipo_labels, tipo_valores, tipo_cores, total_creditos,
    total_debitos e saldo.
    """
    debitos_qs = [t for t in transacoes if t.tipo.codigo == 'D']
    cat_sums = defaultdict(Decimal)
    for t in debitos_qs:
        cat_name = t.categoria.nome if t.categoria else "Sem Categoria"
        cat_sums[cat_name] += t.valor_decimal

    cat_labels = list(cat_sums.keys())
    cat_valores = [float(v) for v in cat_sums.values()]

    tipo_sums = defaultdict(Decimal)
    for t in transacoes:
        tipo_sums[t.tipo.codigo] += t.valor_decimal

    tipo_labels = []
    tipo_valores = []
    tipo_cores = []
    for codigo, total in tipo_sums.items():
        desc = "Crédito (Entrada)" if codigo == 'C' else "Débito (Saída)"
        tipo_labels.append(desc)
        tipo_valores.append(float(total))
        tipo_cores.append("#4CAF50" if codigo == 'C' else "#F44336")

    total_creditos = sum((t.valor_decimal for t in transacoes if t.tipo.codigo == 'C'), Decimal('0'))
    total_debitos = sum((t.valor_decimal for t in transacoes if t.tipo.codigo == 'D'), Decimal('0'))

    return {
        'cat_labels': cat_labels,
        'cat_valores': cat_valores,
        'tipo_labels': tipo_labels,
        'tipo_valores': tipo_valores,
        'tipo_cores': tipo_cores,
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'saldo': total_creditos - total_debitos,
    }
