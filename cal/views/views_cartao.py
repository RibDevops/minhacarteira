from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import CartaoForm
from ..models import Cartao, Transacao
from ..services import consumo_por_cartao, resumo_categorias_e_tipos
from ..utils import parse_mes_ano, intervalo_do_mes


@login_required
def cartao_novo(request):
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
    Exibe o consumo total de cada cartão do usuário com suporte a
    filtro de mês/ano.
    """
    ano, mes = parse_mes_ano(request)
    dados = consumo_por_cartao(request.user, ano, mes)

    contexto = {
        'labels': dados['labels'],
        'consumo': dados['consumo'],
        'limites': dados['limites'],
        'cartoes': dados['cartoes'],
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
    }
    return render(request, 'cal/cartoes_resumo.html', contexto)


@login_required
def resumo_categoria_view(request):
    ano, mes = parse_mes_ano(request)
    data_inicio, data_fim = intervalo_do_mes(ano, mes)

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).select_related('tipo', 'categoria', 'cartao')

    dados = resumo_categorias_e_tipos(transacoes)

    contexto = {
        "cat_labels": dados['cat_labels'],
        "cat_valores": dados['cat_valores'],
        "tipo_labels": dados['tipo_labels'],
        "tipo_valores": dados['tipo_valores'],
        "tipo_cores": dados['tipo_cores'],
        "total_creditos": dados['total_creditos'],
        "total_debitos": dados['total_debitos'],
        "saldo": dados['saldo'],
        "mes_atual": date(ano, mes, 1),
        "mes_anterior": date(ano, mes, 1) - relativedelta(months=1),
        "mes_proximo": date(ano, mes, 1) + relativedelta(months=1),
    }
    return render(request, "cal/resumo_categoria.html", contexto)
