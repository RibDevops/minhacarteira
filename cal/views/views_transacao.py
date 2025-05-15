from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Transacao
from ..forms import TransacaoForm
from datetime import timedelta
from dateutil.relativedelta import relativedelta

@login_required
def listar_transacoes(request):
    transacoes = Transacao.objects.filter(user=request.user).order_by('-data')
    return render(request, 'cal/lista_transacoes.html', {'transacoes': transacoes})

@login_required
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    return redirect('cal:listar_transacoes')

@login_required
def transacao_editar(request, pk=None):
    instancia = get_object_or_404(Transacao, pk=pk, user=request.user) if pk else Transacao(user=request.user)
    form = TransacaoForm(request.POST or None, instance=instancia)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cal:calendar')

    return render(request, 'cal/event.html', {'form': form})

@login_required
def transacao_view(request):
    form = TransacaoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        parcelas = form.cleaned_data.get('parcelas')
        print(f'qtd: {parcelas}')
        if parcelas and parcelas > 1:
            for i in range(parcelas):
                nova = Transacao(
                    user=request.user,
                    tipo=transacao.tipo,
                    titulo=transacao.titulo + f' ({i+1}/{parcelas})',
                    valor=transacao.valor,
                    data=transacao.data + relativedelta(months=i),
                    parcelas=parcelas,
                    data_fim=transacao.data + relativedelta(months=parcelas-1)
                )
                nova.save()
        else:
            transacao.save()

        return redirect('cal:listar_transacoes')

    return render(request, 'cal/transacao_form.html', {'form': form})

from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from datetime import datetime


def transacoes_mes_view(request):
    # Pega o ano e mês da querystring ou usa o atual
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))


    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))


    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).order_by('-data')

    # Soma os valores (débitos negativos)
    total = sum([
        -t.valor if t.tipo.descricao.lower() == 'débito' else t.valor
        for t in transacoes
    ])

    mes_atual = date(ano, mes, 1)

    contexto = {
        'transacoes': transacoes,
        'mes_atual': mes_atual,
        'mes_anterior': mes_atual - relativedelta(months=1),
        'mes_proximo': mes_atual + relativedelta(months=1),
        'total': total,
    }
    return render(request, 'cal/transacoes_mes.html', contexto)
