from datetime import date, datetime
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import make_aware
from django.views.generic.edit import UpdateView
from dateutil.relativedelta import relativedelta
from ..forms import TransacaoForm
from ..models import Categoria, Tipo, Transacao
from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
@require_POST
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    messages.success(request, 'Transação excluída com sucesso!')
    return redirect('cal:transacoes_mes')


@login_required
def excluir_transacao_lista(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    return redirect('cal:listar_transacoes')

@login_required
def transacao_editar(request, pk):
    instancia = get_object_or_404(Transacao, pk=pk, user=request.user)
    form = TransacaoForm(request.POST or None, instance=instancia, user=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Transação atualizada com sucesso!')
        return redirect('cal:calendar')

    return render(request, 'cal/transacao_editar.html', {'form': form, 'titulo': 'Editar Transação'})


@login_required
def transacao_view(request):
    #form = TransacaoForm(request.POST or None)
    form = TransacaoForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        tipo = transacao.tipo
        categoria = transacao.categoria
        data = transacao.data
        parcelas = int(form.cleaned_data.get('parcelas') or 1)

        # ⚠️ Tratamento de vírgula no valor
        valor_input = request.POST.get('valor', '0').replace(',', '.')
        try:
            valor_total = Decimal(valor_input)
        except (InvalidOperation, ValueError):
            valor_total = Decimal('0')

        valor_parcela = (valor_total / parcelas).quantize(Decimal("0.01"))

        data_compra_str = data.strftime('%d/%m')

        # Lógica Inteligente de Data para Cartões
        data_base_parcela = data
        if tipo.dia_fechamento > 0:
            # Se o dia da compra for >= ao dia de fechamento, a parcela cai no mês subsequente ao padrão
            if data.day >= tipo.dia_fechamento:
                data_base_parcela = data + relativedelta(months=1)
            
            # Se for cartão de crédito (ID 3 ou similar) ou tiver 'adia_mes', o padrão é já começar no mês seguinte
            if tipo.id == 3 or tipo.adia_mes:
                data_base_parcela = data_base_parcela + relativedelta(months=1)

        if tipo.id == 3:  # Cartão de crédito (Mantendo retrocompatibilidade de ID se necessário)
            for i in range(parcelas):
                Transacao.objects.create(
                    user=request.user,
                    tipo=tipo,
                    categoria=categoria,
                    titulo=f"{transacao.titulo} - ({data_compra_str}) ({i + 1}/{parcelas})",
                    valor=valor_parcela,
                    data=data_base_parcela + relativedelta(months=i),
                    parcelas=parcelas,
                    data_fim=data_base_parcela + relativedelta(months=parcelas - 1),
                )
        else:
            if parcelas > 1:
                for i in range(parcelas):
                    Transacao.objects.create(
                        user=request.user,
                        tipo=tipo,
                        categoria=categoria,
                        titulo=f"{transacao.titulo} ({i + 1}/{parcelas})",
                        valor=valor_parcela,
                        data=data_base_parcela + relativedelta(months=i),
                        parcelas=parcelas,
                        data_fim=data_base_parcela + relativedelta(months=parcelas - 1),
                    )
            else:
                transacao.data = data_base_parcela
                transacao.valor = valor_total
                transacao.save()

        return redirect('cal:transacoes_mes')

    return render(request, 'cal/transacao_form.html', {'form': form})


def get_absolute_url(self):
        return reverse('transacao_editar', args=[self.id])



class TransacaoUpdateView(UpdateView):
    model = Transacao
    fields = ['tipo', 'titulo', 'valor', 'data', 'parcelas', 'observacoes']
    template_name = 'cal/transacao_form.html'  # crie esse template se ainda não existir
    success_url = reverse_lazy('cal:calendar')  # ou outra URL para onde redirecionar depois da edição

@login_required
def transacoes_mes_view(request):
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    
    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria').order_by('-data')


    # Gráfico por tipo (Crédito/Débito)
    dados_por_tipo = defaultdict(Decimal)
    for t in transacoes:
        try:
            valor = Decimal(t.valor)
            if not t.tipo.is_credito:
                valor = -valor
            dados_por_tipo[t.tipo.descricao] += valor
        except Exception as e:
            #print(f"Erro ao processar transação {t.id}: {e}")
            import logging

            logger = logging.getLogger(__name__)

            # Substitua print por:
            logger.error(f"Erro ao processar transação {t.id}: {e}")
            logger.debug(f'Transações do ano: {transacoes}')

    labels = list(dados_por_tipo.keys())
    valores = [float(v) for v in dados_por_tipo.values()]

    # Gráfico por categoria (exclui transações sem categoria)
    dados_por_categoria = (
        transacoes.exclude(categoria__isnull=True)
                .values('categoria__nome')
                .annotate(total=Sum('valor'))
                .order_by('-total')
    )


    categorias = [item['categoria__nome'] for item in dados_por_categoria]
    totais_categoria = [float(item['total']) for item in dados_por_categoria]

    # Totais
    from django.db import models
    totais = transacoes.aggregate(
        total_creditos=Sum('valor', filter=models.Q(tipo__is_credito=True)),
        total_debitos=Sum('valor', filter=models.Q(tipo__is_credito=False))
    )
    total_creditos = totais['total_creditos'] or 0
    total_debitos = totais['total_debitos'] or 0
    saldo_total = total_creditos - total_debitos

    contexto = {
        'transacoes': transacoes,
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
        'grafico_labels': labels,
        'grafico_valores': valores,
        'grafico_categorias': categorias,  # para gráfico por categoria
        'grafico_totais_categoria': totais_categoria,  # para gráfico por categoria
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'saldo_total': saldo_total,
    }
    return render(request, 'cal/transacoes_mes.html', contexto)

@login_required
def resumo_categoria_view(request):
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    )

    # Dados para o gráfico de pizza por Categoria (apenas Débitos)
    dados_categoria = transacoes.filter(tipo__is_credito=False).values("categoria__nome").annotate(total=Sum("valor")).order_by('-total')
    
    cat_labels = [item["categoria__nome"] or "Sem Categoria" for item in dados_categoria]
    cat_valores = [float(item["total"]) for item in dados_categoria]

    # Dados para o gráfico de pizza por Tipo (Crédito vs Débito)
    dados_tipo = transacoes.values("tipo__descricao", "tipo__is_credito").annotate(total=Sum("valor"))
    
    tipo_labels = []
    tipo_valores = []
    tipo_cores = []

    for item in dados_tipo:
        tipo_labels.append(item["tipo__descricao"])
        tipo_valores.append(float(item["total"]))
        tipo_cores.append("#4CAF50" if item["tipo__is_credito"] else "#F44336")

    # Totais para os cards
    total_creditos = transacoes.filter(tipo__is_credito=True).aggregate(Sum('valor'))['valor__sum'] or 0
    total_debitos = transacoes.filter(tipo__is_credito=False).aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_creditos - total_debitos

    contexto = {
        "cat_labels": cat_labels,
        "cat_valores": cat_valores,
        "tipo_labels": tipo_labels,
        "tipo_valores": tipo_valores,
        "tipo_cores": tipo_cores,
        "total_creditos": total_creditos,
        "total_debitos": total_debitos,
        "saldo": saldo,
        "mes_atual": date(ano, mes, 1),
        "mes_anterior": date(ano, mes, 1) - relativedelta(months=1),
        "mes_proximo": date(ano, mes, 1) + relativedelta(months=1),
    }
    return render(request, "cal/resumo_categoria.html", contexto)




@login_required
def cartoes_resumo_view(request):
    """
    View simples para exibir o consumo total de cada cartão do usuário.
    """
    cartoes = Cartao.objects.filter(user=request.user)
    
    labels = []
    consumo_valores = []
    limite_valores = []
    
    for c in cartoes:
        # Soma transações do mês atual vinculadas a este cartão
        hoje = date.today()
        consumo = Transacao.objects.filter(
            user=request.user,
            cartao=c,
            data__month=hoje.month,
            data__year=hoje.year
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        labels.append(c.cartao)
        consumo_valores.append(float(consumo))
        limite_valores.append(float(c.limite))
        
    contexto = {
        'labels': labels,
        'consumo': consumo_valores,
        'limites': limite_valores,
        'cartoes': cartoes,
    }
    return render(request, 'cal/cartoes_resumo.html', contexto)

@login_required
def listar_transacoes(request):
    hoje = date.today()
    ano = int(request.GET.get('ano', hoje.year))
    mes = int(request.GET.get('mes', hoje.month))
    
    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))
    
    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria').order_by('-data')
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria').order_by('-data')

    tipo_filtro = request.GET.get('tipo')
    categoria_filtro = request.GET.get('categoria')

    if tipo_filtro:
        transacoes = transacoes.filter(tipo_id=int(tipo_filtro))
    if categoria_filtro:
        transacoes = transacoes.filter(categoria_id=int(categoria_filtro))

    tipos = Tipo.objects.all()
    categorias = Categoria.objects.all()

    contexto = {
        'transacoes': transacoes,
        'tipos': tipos,
        'categorias': categorias,
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
    }

    return render(request, 'cal/lista_transacoes.html', contexto)
