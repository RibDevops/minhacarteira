from datetime import date
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from dateutil.relativedelta import relativedelta
from ..forms import TransacaoForm, CartaoForm
from ..models import Categoria, Tipo, Transacao, Cartao
from ..utils import parse_mes_ano, intervalo_do_mes
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


@login_required
@require_POST
def transacao_rapida(request):
    """
    Endpoint enxuto para o modal de registro rápido (menos cliques).

    Campos essenciais: título, valor, tipo, categoria (opcional).
    Campos avançados (opcionais, ficam escondidos atrás de um "+ opções" no
    modal): cartão e parcelas. Quando informados, reaproveita a mesma regra
    de fatura usada no formulário completo (calcular_proxima_fatura) para
    manter os dois fluxos consistentes.
    """
    titulo = (request.POST.get('titulo') or '').strip()
    tipo_id = request.POST.get('tipo')
    categoria_id = request.POST.get('categoria') or None
    cartao_id = request.POST.get('cartao') or None
    parcelas_raw = request.POST.get('parcelas') or '1'

    erros = []
    if not titulo:
        erros.append('Informe um título para o lançamento.')

    valor_input = (request.POST.get('valor') or '').replace(',', '.')
    try:
        valor_total = Decimal(valor_input).quantize(Decimal('0.01'))
        if valor_total <= 0:
            erros.append('Informe um valor maior que zero.')
    except (InvalidOperation, ValueError):
        valor_total = None
        erros.append('Informe um valor válido.')

    tipo = Tipo.objects.filter(pk=tipo_id).first() if tipo_id else None
    if not tipo:
        erros.append('Selecione o tipo (crédito ou débito).')

    categoria = None
    if categoria_id:
        # Sempre filtrado por user: nunca aceitar uma categoria de outro usuário
        # vinda do POST (o mesmo cuidado do bug de IDOR corrigido antes).
        categoria = Categoria.objects.filter(pk=categoria_id, user=request.user).first()

    cartao = None
    if cartao_id:
        cartao = Cartao.objects.filter(pk=cartao_id, user=request.user, is_active=True).first()
        if not cartao:
            erros.append('Cartão inválido.')

    try:
        parcelas = int(parcelas_raw)
        if parcelas < 1:
            raise ValueError
    except (ValueError, TypeError):
        parcelas = 1
        erros.append('Número de parcelas inválido.')

    if erros:
        return JsonResponse({'status': 'error', 'errors': erros}, status=400)

    hoje = date.today()
    valor_parcela = valor_total.quantize(Decimal('0.01'))

    # Mesma regra do formulário completo: lançamento em cartão sempre cai
    # na fatura do mês seguinte, independente do dia da compra.
    data_base_parcela = calcular_proxima_fatura(hoje) if cartao else hoje

    import uuid
    grupo_id = str(uuid.uuid4()) if parcelas > 1 else None

    transacoes_criadas = []
    for i in range(parcelas):
        data_final_parcela = data_base_parcela + relativedelta(months=i)
        transacoes_criadas.append(Transacao.objects.create(
            user=request.user,
            tipo=tipo,
            cartao=cartao,
            categoria=categoria,
            titulo=f"{titulo} ({i + 1}/{parcelas})" if parcelas > 1 else titulo,
            valor=valor_parcela,
            data=data_final_parcela,
            parcelas=parcelas,
            data_fim=data_base_parcela + relativedelta(months=parcelas - 1) if parcelas > 1 else None,
            grupo_id=grupo_id,
        ))

    primeira = transacoes_criadas[0]
    if parcelas > 1:
        mensagem = f'"{titulo}" registrado em {parcelas}x de R$ {valor_parcela}!'
    else:
        mensagem = f'"{titulo}" registrado com sucesso!'

    return JsonResponse({
        'status': 'success',
        'message': mensagem,
        'transacao': {
            'id': primeira.id,
            'titulo': titulo,
            'valor': str(valor_parcela),
            'tipo_codigo': tipo.codigo,
            'data': primeira.data.strftime('%d/%m/%Y'),
            'parcelas': parcelas,
        }
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

        valor_parcela = valor_total.quantize(Decimal("0.01"))
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


class TransacaoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View acessível em /transacao/<pk>/editar/ (rota 'cal:transacao_update').

    IMPORTANTE: get_queryset() é obrigatório aqui. Sem ele, o UpdateView usa
    Transacao.objects.all() por padrão, permitindo que qualquer usuário logado
    edite a transação de QUALQUER outro usuário apenas trocando o pk na URL
    (falha de IDOR - Insecure Direct Object Reference).
    """
    model = Transacao
    fields = ['tipo', 'titulo', 'valor', 'data', 'parcelas', 'observacoes']
    template_name = 'cal/transacao_form.html'
    success_url = reverse_lazy('cal:transacoes_mes')

    def get_queryset(self):
        return Transacao.objects.filter(user=self.request.user)


import csv
from django.http import HttpResponse

@login_required
def exportar_transacoes_csv(request):
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

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
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao').order_by('-data')


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
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao')

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
    View para exibir o consumo total de cada cartão do usuário com suporte a filtro de mês/ano.
    """
    ano, mes = parse_mes_ano(request)

    cartoes = Cartao.objects.filter(user=request.user)
    
    labels = []
    consumo_valores = []
    limite_valores = []
    
    for c in cartoes:
        # Soma transações do mês/ano filtrado vinculadas a este cartão
        transacoes_cartao = Transacao.objects.filter(
            user=request.user,
            cartao=c,
            data__month=mes,
            data__year=ano
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
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
    }
    return render(request, 'cal/cartoes_resumo.html', contexto)

@login_required
def listar_transacoes(request):
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao').order_by('-data')

    tipo_filtro = request.GET.get('tipo')
    categoria_filtro = request.GET.get('categoria')

    if tipo_filtro:
        transacoes = transacoes.filter(tipo_id=int(tipo_filtro))
    if categoria_filtro:
        transacoes = transacoes.filter(categoria_id=int(categoria_filtro))

    tipos = Tipo.objects.all()  # Tipo (Crédito/Débito) é global do sistema, não pertence a um usuário
    categorias = Categoria.get_for_user(request.user)

    # Totais para o card de saldo
    total_creditos = transacoes.filter(tipo__codigo='C').aggregate(Sum('valor'))['valor__sum'] or 0
    total_debitos = transacoes.filter(tipo__codigo='D').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo_total = total_creditos - total_debitos

    contexto = {
        'transacoes': transacoes,
        'tipos': tipos,
        'categorias': categorias,
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
        'saldo_total': saldo_total,
    }

    return render(request, 'cal/lista_transacoes.html', contexto)
