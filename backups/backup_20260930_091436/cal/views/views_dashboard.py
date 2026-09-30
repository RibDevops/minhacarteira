from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..services import saldo_ano, detalhe_mensal_ano
from ..utils import parse_mes_ano


@login_required
def dashboard(request):
    user = request.user
    hoje = date.today()
    ano_selecionado = int(request.GET.get('ano', hoje.year))

    credito_anual, debito_anual, saldo_anual = saldo_ano(user, ano_selecionado)
    meses_detalhe = detalhe_mensal_ano(user, ano_selecionado)
    anos_disponiveis = range(hoje.year - 5, hoje.year + 2)

    return render(request, 'cal/dashboard.html', {
        'titulo_pagina': 'Balanço Anual',
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'credito_anual': credito_anual,
        'debito_anual': debito_anual,
        'saldo_anual': saldo_anual,
        'meses_detalhe': meses_detalhe,
    })
