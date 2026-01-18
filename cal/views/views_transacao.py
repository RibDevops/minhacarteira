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
    excluir_proximas = request.POST.get('excluir_proximas') == 'true'
    
    if excluir_proximas and transacao.grupo_id:
        # Excluir esta e todas as parcelas futuras do mesmo grupo
        Transacao.objects.filter(
            user=request.user, 
            grupo_id=transacao.grupo_id, 
            data__gte=transacao.data
        ).delete()
    else:
        transacao.delete()
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Transação excluída com sucesso!'})
    messages.success(request, 'Transação excluída com sucesso!')
    return redirect('cal:transacoes_mes')


@login_required
@require_POST
def excluir_transacao_lista(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    excluir_proximas = request.POST.get('excluir_proximas') == 'true'

    if excluir_proximas and transacao.grupo_id:
        Transacao.objects.filter(
            user=request.user, 
            grupo_id=transacao.grupo_id, 
            data__gte=transacao.data
        ).delete()
    else:
        transacao.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Transação excluída com sucesso!'})
    messages.success(request, 'Transação excluída com sucesso!')
    return redirect('cal:listar_transacoes')

@login_required
def transacao_editar(request, pk):
    instancia = get_object_or_404(Transacao, pk=pk, user=request.user)
    form = TransacaoForm(request.POST or None, instance=instancia, user=request.user)
    
    # Campo para opção de cascata
    aplicar_proximas = request.POST.get('aplicar_proximas') == 'true'

    if request.method == 'POST' and form.is_valid():
        transacao_editada = form.save(commit=False)
        
        if aplicar_proximas and instancia.grupo_id:
            # Atualizar esta e todas as parcelas futuras do mesmo grupo
            Transacao.objects.filter(
                user=request.user,
                grupo_id=instancia.grupo_id,
                data__gte=instancia.data
            ).update(
                titulo=transacao_editada.titulo,
                valor=transacao_editada.valor,
                categoria=transacao_editada.categoria,
                observacoes=transacao_editada.observacoes
            )
            messages.success(request, 'Transações do grupo atualizadas com sucesso!')
        else:
            transacao_editada.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            
        return redirect('cal:transacoes_mes')

    return render(request, 'cal/transacao_editar.html', {
        'form': form, 
        'titulo': 'Editar Transação',
        'transacao': instancia
    })


def calcular_proxima_fatura(data_compra, dia_fechamento=None):
    """
    Regra de Negócio Simplificada:
    - Compras feitas em qualquer dia do mês X são lançadas para o mês X+1.
    - O conceito de 'dia de fechamento' foi removido para simplificação total.
    
    Exemplo:
    - Compra em Janeiro (qualquer dia) -> Lançamento em Fevereiro.
    - Compra em Fevereiro (qualquer dia) -> Lançamento em Março.
    """
    return date(data_compra.year, data_compra.month, 1) + relativedelta(months=1)

def testar_logica_parcelas():
    # Qualquer dia de Janeiro -> Fevereiro
    jan_01 = date(2024, 1, 1)
    res = calcular_proxima_fatura(jan_01)
    assert res.month == 2, f"Erro: 01/01 deveria ser Fev (2), veio {res.month}"
    
    jan_31 = date(2024, 1, 31)
    res_fim = calcular_proxima_fatura(jan_31)
    assert res_fim.month == 2, f"Erro: 31/01 deveria ser Fev (2), veio {res_fim.month}"
    
    print("Logica simplificada (Mês + 1) validada com sucesso!")

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
        import uuid
        grupo_id = str(uuid.uuid4()) if parcelas > 1 else None

        # Lógica de data baseada na regra de vencimento do cartão
        data_base_parcela = data
        if transacao.cartao:
            # Regra: Qualquer lançamento no cartão SEMPRE vai para o próximo mês (Mês+1)
            # Não importa se é Entrada ou Saída
            data_base_parcela = calcular_proxima_fatura(data)
        
        # Criação das parcelas
        for i in range(parcelas):
            # A data inicial da sequência de parcelas é definida acima (data ou data+1 mês)
            data_final_parcela = data_base_parcela + relativedelta(months=i)

            Transacao.objects.create(
                user=request.user,
                tipo=tipo,
                forma_pagamento=forma_pagamento,
                cartao=transacao.cartao,
                categoria=categoria,
                titulo=f"{transacao.titulo} ({i + 1}/{parcelas})" if parcelas > 1 else transacao.titulo,
                valor=valor_parcela,
                data=data_final_parcela,
                parcelas=parcelas,
                data_fim=data_base_parcela + relativedelta(months=parcelas - 1),
                observacoes=transacao.observacoes,
                grupo_id=grupo_id
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

import csv
from django.http import HttpResponse

@login_required
def exportar_transacoes_csv(request):
    try:
        ano = int(request.GET.get('ano', date.today().year))
        mes = int(request.GET.get('mes', date.today().month))
    except (ValueError, TypeError):
        ano, mes = date.today().year, date.today().month

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao').order_by('data')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="transacoes_{mes}_{ano}.csv"'
    response.write(u'\ufeff'.encode('utf8')) # BOM para Excel

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data', 'Título', 'Categoria', 'Tipo', 'Cartão', 'Valor'])

    for t in transacoes:
        writer.writerow([
            t.data.strftime('%d/%m/%Y'),
            t.titulo,
            t.categoria.nome if t.categoria else '-',
            t.tipo.descricao,
            t.cartao.nome if t.cartao else '-',
            str(t.valor).replace('.', ',')
        ])

    return response

@login_required
def transacoes_mes_view(request):
    try:
        ano = int(str(request.GET.get('ano', date.today().year)).replace('.', '').replace(',', ''))
        mes = int(str(request.GET.get('mes', date.today().month)).replace('.', '').replace(',', ''))
    except (ValueError, TypeError):
        ano, mes = date.today().year, date.today().month

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    
    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria').order_by('-data')


    # Totais
    total_creditos = transacoes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or 0
    total_debitos = transacoes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo_total = total_creditos - total_debitos

    # Gráfico por tipo (Crédito/Débito)
    dados_por_tipo = transacoes.values('tipo__descricao', 'tipo__codigo').annotate(total=Sum('valor'))
    
    labels = [item['tipo__descricao'] for item in dados_por_tipo]
    valores = []
    for item in dados_por_tipo:
        val = float(item['total'])
        if item['tipo__codigo'] == 'D':
            val = -val
        valores.append(val)

    # Gráfico por categoria (exclui transações sem categoria)
    dados_categoria = transacoes.filter(categoria__isnull=False).values('categoria__nome').annotate(total=Sum('valor'))
    
    categorias = [item['categoria__nome'] for item in dados_categoria]
    totais_categoria = [float(item['total']) for item in dados_categoria]

    contexto = {
        'transacoes': transacoes,
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
        'grafico_labels': labels,
        'grafico_valores': valores,
        'grafico_categorias': categorias,
        'grafico_totais_categoria': totais_categoria,
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'saldo_total': saldo_total,
    }
    return render(request, 'cal/transacoes_mes.html', contexto)

@login_required
def resumo_categoria_view(request):
    try:
        ano_raw = request.GET.get('ano', date.today().year)
        mes_raw = request.GET.get('mes', date.today().month)
        
        ano = int(float(str(ano_raw).replace('.', '').replace(',', '')))
        mes = int(float(str(mes_raw).replace('.', '').replace(',', '')))
    except (ValueError, TypeError):
        ano, mes = date.today().year, date.today().month

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    )

    # Dados para o gráfico de pizza por Categoria (apenas Débitos)
    debitos = [t for t in transacoes if t.tipo.codigo == 'D']
    cat_sums = defaultdict(Decimal)
    for t in debitos:
        cat_name = t.categoria.nome if t.categoria else "Sem Categoria"
        cat_sums[cat_name] += t.valor_decimal
    
    cat_labels = list(cat_sums.keys())
    cat_valores = [float(v) for v in cat_sums.values()]

    # Dados para o gráfico de pizza por Tipo (Crédito vs Débito)
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

    # Totais para os cards
    total_creditos = sum((t.valor_decimal for t in transacoes if t.tipo.codigo == 'C'), Decimal('0'))
    total_debitos = sum((t.valor_decimal for t in transacoes if t.tipo.codigo == 'D'), Decimal('0'))
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
        transacoes_cartao = Transacao.objects.filter(
            user=request.user,
            cartao=c,
            data__month=hoje.month,
            data__year=hoje.year
        ).select_related('tipo')
        
        consumo = sum((t.valor_decimal for t in transacoes_cartao), Decimal('0'))
        
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
    
    try:
        ano_raw = request.GET.get('ano', hoje.year)
        mes_raw = request.GET.get('mes', hoje.month)
        
        # Robust parsing for ano/mes (handle floats/strings)
        ano = int(float(str(ano_raw).replace('.', '').replace(',', '')))
        mes = int(float(str(mes_raw).replace('.', '').replace(',', '')))
    except (ValueError, TypeError):
        ano, mes = hoje.year, hoje.month
    
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
