from datetime import date
from decimal import Decimal
from django.db.models import Sum
from .models import Transacao, Categoria, Tipo, Cartao
from .utils import gerar_transacoes_pendentes

def saldos_mensais(request):
    # print(">>> Context Processor CHAMADO <<<")
    if not request.user.is_authenticated:
        return {}

    user = request.user
    hoje = date.today()

    # Gera lançamentos de assinaturas/recorrências pendentes antes de calcular
    # qualquer saldo, pra que o mês já apareça correto na primeira tela vista.
    gerar_transacoes_pendentes(user)

    # Saldo mês atual
    transacoes_mes = Transacao.objects.filter(
        user=user,
        data__year=hoje.year,
        data__month=hoje.month
    ).select_related('tipo')
    
    total_creditos = transacoes_mes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    total_debitos = transacoes_mes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    saldo_total = total_creditos - total_debitos

    # Próximo mês
    if hoje.month == 12:
        proximo_ano = hoje.year + 1
        proximo_mes = 1
    else:
        proximo_ano = hoje.year
        proximo_mes = hoje.month + 1

    transacoes_prox_mes = Transacao.objects.filter(
        user=user,
        data__year=proximo_ano,
        data__month=proximo_mes
    ).select_related('tipo')
    
    total_creditos_prox = transacoes_prox_mes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    total_debitos_prox = transacoes_prox_mes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    saldo_total_prox = total_creditos_prox - total_debitos_prox

    return {
        'saldo_total_nav': saldo_total,
        'saldo_total_prox_nav': saldo_total_prox,
        'month_name': hoje.strftime("%B"),
        'mes_proximo_nome': date(proximo_ano, proximo_mes, 1).strftime("%B"),
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'total_creditos_prox': total_creditos_prox,
        'total_debitos_prox': total_debitos_prox,
        # Usados pelo modal global de "Registro Rápido" (menos cliques no FAB)
        'categorias_quick_add': Categoria.get_for_user(user),
        'tipos_quick_add': Tipo.objects.all(),
        'cartoes_quick_add': Cartao.objects.filter(user=user, is_active=True),
    }
