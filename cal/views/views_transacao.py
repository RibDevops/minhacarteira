import uuid
from datetime import date
from decimal import Decimal, InvalidOperation

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.edit import UpdateView

from ..forms import TransacaoForm
from ..models import Categoria, Cartao, Tipo, Transacao
from ..services import calcular_proxima_fatura
from ..utils import parse_mes_ano, intervalo_do_mes


@login_required
@require_POST
def excluir_transacao(request, pk):
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

    aplicar_proximas = request.POST.get('aplicar_proximas') == 'true'

    if request.method == 'POST' and form.is_valid():
        transacao_editada = form.save(commit=False)

        if aplicar_proximas and instancia.grupo_id:
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

    data_base_parcela = calcular_proxima_fatura(hoje) if cartao else hoje

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


@login_required
def transacao_view(request):
    # Normaliza o valor (aceita vírgula decimal) antes do form validar,
    # porque o DecimalField rejeita '150,50' hard-coded. Mesmo cuidado já
    # aplicado em RecorrenciaForm.clean_valor e MetaCategoriaForm.clean_limite.
    if request.method == 'POST':
        post = request.POST.copy()
        if 'valor' in post:
            post['valor'] = post['valor'].replace('.', '').replace(',', '.')
        form = TransacaoForm(post, user=request.user)
    else:
        form = TransacaoForm(user=request.user)

    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        tipo = transacao.tipo
        categoria = transacao.categoria
        data = transacao.data
        parcelas = int(form.cleaned_data.get('parcelas') or 1)

        valor_total = transacao.valor or Decimal('0')
        valor_parcela = valor_total.quantize(Decimal("0.01"))
        grupo_id = str(uuid.uuid4()) if parcelas > 1 else None

        data_base_parcela = data
        if transacao.cartao:
            data_base_parcela = calcular_proxima_fatura(data)

        for i in range(parcelas):
            data_final_parcela = data_base_parcela + relativedelta(months=i)

            Transacao.objects.create(
                user=request.user,
                tipo=tipo,
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


@login_required
def transacoes_mes_view(request):
    """
    Removida: esta view/página duplicava os gráficos que já existem em
    /transacoes/ (TransacaoListView) para o mesmo mês, e nunca chegou a
    ter uma lista de transações — só totais e gráficos. Isso confundia
    quem clicava em "Despesas" e não via nenhuma transação listada.
    Mantida como redirect para não quebrar links/favoritos salvos.
    """
    destino = reverse('cal:listar_transacoes')
    if request.GET:
        destino += f'?{request.GET.urlencode()}'
    return redirect(destino)


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

    tipos = Tipo.objects.all()
    categorias = Categoria.get_for_user(request.user)

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
