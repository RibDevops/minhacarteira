from datetime import date, datetime
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import make_aware
from django.views.generic.edit import UpdateView
from dateutil.relativedelta import relativedelta
from ..forms import TransacaoForm, CartaoForm
from ..models import Categoria, Tipo, Transacao, Cartao
from django.contrib import messages
from django.views.decorators.http import require_POST

from django.http import JsonResponse

@login_required
@require_POST
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Transação excluída com sucesso!'})
    messages.success(request, 'Transação excluída com sucesso!')
    return redirect('cal:transacoes_mes')


@login_required
@require_POST
def excluir_transacao_lista(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Transação excluída com sucesso!'})
    messages.success(request, 'Transação excluída com sucesso!')
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


def calcular_proxima_fatura(data_compra, dia_vencimento):
    """
    Calcula a data da primeira parcela.
    Regra do Melhor Dia: Faturas fecham 10 dias antes do vencimento.
    Se a compra for feita NO DIA do fechamento ou DEPOIS, cai no mês seguinte.
    """
    # Melhor dia de compra = dia_vencimento - 10
    # Ex: Vencimento 25, Fechamento 15.
    # Compra dia 14 -> Vence dia 25 (mês atual)
    # Compra dia 15 (fechamento) -> Vence dia 25 do mês SEGUINTE.
    
    dia_fechamento = dia_vencimento - 10
    
    # Tratamento para vencimentos no início do mês (ex: dia 5 -> fecha dia 25 do anterior)
    if dia_fechamento <= 0:
        dia_fechamento += 30
        if data_compra.day >= dia_fechamento or data_compra.day < dia_vencimento:
             # Se comprou no final do mês anterior ou antes do vencimento no início do mês
             # Isso fica complexo sem considerar o mês, então vamos simplificar:
             # Se comprou no dia do vencimento ou depois, próximo mês.
             if data_compra.day >= dia_vencimento:
                 return date(data_compra.year, data_compra.month, 1) + relativedelta(months=1, day=dia_vencimento)
             else:
                 return date(data_compra.year, data_compra.month, dia_vencimento)

    if data_compra.day < dia_fechamento:
        return date(data_compra.year, data_compra.month, dia_vencimento)
    else:
        return date(data_compra.year, data_compra.month, 1) + relativedelta(months=1, day=dia_vencimento)

def testar_logica_parcelas():
    # Caso: Compra dia 14, Vencimento 25 -> Deve ser Fevereiro (14 > 15? Não, mas usuário quer fev)
    # Ajustando para margem de 11 dias para bater com o teste do usuário (14/01 -> 25/02)
    pass
    # Caso 1: Compra dia 09, Vencimento 10 -> Mesma data (Mês atual)
    d1 = date(2024, 1, 9)
    res1 = calcular_proxima_fatura(d1, 10)
    assert res1 == date(2024, 1, 10), f"Erro Caso 1: {res1}"

    # Caso 2: Compra dia 10, Vencimento 10 -> Mesma data (Mês atual)
    d2 = date(2024, 1, 10)
    res2 = calcular_proxima_fatura(d2, 10)
    assert res2 == date(2024, 1, 10), f"Erro Caso 2: {res2}"

    # Caso 3: Compra dia 11, Vencimento 10 -> Mês seguinte
    d3 = date(2024, 1, 11)
    res3 = calcular_proxima_fatura(d3, 10)
    assert res3 == date(2024, 2, 10), f"Erro Caso 3: {res3}"

    # Caso 4: Compra dia 26, Vencimento 25 -> Mês seguinte
    d4 = date(2024, 1, 26)
    res4 = calcular_proxima_fatura(d4, 25)
    assert res4 == date(2024, 2, 25), f"Erro Caso 4: {res4}"

@login_required
def transacao_view(request):
    #form = TransacaoForm(request.POST or None)
    form = TransacaoForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        tipo = transacao.tipo
        forma_pagamento = transacao.forma_pagamento
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

        # Lógica de data baseada na regra de vencimento do cartão
        data_base_parcela = data
        if transacao.cartao:
            # Regra: Primeira parcela no mês atual se dia_compra <= vencimento, senão mês seguinte
            data_base_parcela = calcular_proxima_fatura(data, transacao.cartao.dia_fechamento)
        
        # Criação das parcelas
        for i in range(parcelas):
            Transacao.objects.create(
                user=request.user,
                tipo=tipo,
                forma_pagamento=forma_pagamento,
                cartao=transacao.cartao,
                categoria=categoria,
                titulo=f"{transacao.titulo} ({i + 1}/{parcelas})" if parcelas > 1 else transacao.titulo,
                valor=valor_parcela,
                data=data_base_parcela + relativedelta(months=i),
                parcelas=parcelas,
                data_fim=data_base_parcela + relativedelta(months=parcelas - 1),
                observacoes=transacao.observacoes
            )

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
            if t.tipo.codigo == 'D':
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
        total_creditos=Sum('valor', filter=models.Q(tipo__codigo='C')),
        total_debitos=Sum('valor', filter=models.Q(tipo__codigo='D'))
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
    dados_categoria = transacoes.filter(tipo__codigo='D').values("categoria__nome").annotate(total=Sum("valor")).order_by('-total')
    
    cat_labels = [item["categoria__nome"] or "Sem Categoria" for item in dados_categoria]
    cat_valores = [float(item["total"]) for item in dados_categoria]

    # Dados para o gráfico de pizza por Tipo (Crédito vs Débito)
    dados_tipo = transacoes.values("tipo__descricao", "tipo__codigo").annotate(total=Sum("valor"))
    
    tipo_labels = []
    tipo_valores = []
    tipo_cores = []

    for item in dados_tipo:
        tipo_labels.append(item["tipo__descricao"])
        tipo_valores.append(float(item["total"]))
        tipo_cores.append("#4CAF50" if item["tipo__codigo"] == 'C' else "#F44336")

    # Totais para os cards
    total_creditos = transacoes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or 0
    total_debitos = transacoes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or 0
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
def cartao_novo(request):
    """
    View para adicionar um novo cartão.
    """
    if request.method == 'POST':
        form = CartaoForm(request.POST)
        if form.is_valid():
            cartao = form.save(commit=False)
            cartao.user = request.user
            cartao.save()
            messages.success(request, 'Cartão adicionado com sucesso!')
            return redirect('cal:cartoes_resumo')
    else:
        form = CartaoForm()
    
    return render(request, 'cal/cartao_form.html', {'form': form, 'titulo': 'Novo Cartão'})

@login_required
def cartao_editar(request, pk):
    cartao = get_object_or_404(Cartao, pk=pk, user=request.user)
    form = CartaoForm(request.POST or None, instance=cartao)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cartão atualizado com sucesso!')
        return redirect('cal:cartoes_resumo')
    return render(request, 'cal/cartao_form.html', {'form': form, 'titulo': 'Editar Cartão'})

@login_required
@require_POST
def cartao_excluir(request, pk):
    cartao = get_object_or_404(Cartao, pk=pk, user=request.user)
    cartao.delete()
    messages.success(request, 'Cartão excluído com sucesso!')
    return redirect('cal:cartoes_resumo')

@login_required
@require_POST
def cartao_alternar_status(request, pk):
    cartao = get_object_or_404(Cartao, pk=pk, user=request.user)
    cartao.is_active = not cartao.is_active
    cartao.save()
    status = "ativado" if cartao.is_active else "desativado"
    messages.success(request, f'Cartão {status} com sucesso!')
    return redirect('cal:cartoes_resumo')

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
        
        labels.append(c.nome)
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
