from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from django.views.generic.edit import UpdateView
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from decimal import Decimal
from collections import defaultdict

from ..models import Transacao
from ..forms import TransacaoForm
from dateutil.relativedelta import relativedelta
from ..models import Tipo, Transacao
from ..forms import TransacaoForm
from django.shortcuts import render, redirect

from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from ..forms import TransacaoForm
from ..models import Transacao
from decimal import Decimal

@login_required
def listar_transacoes(request):
    transacoes = Transacao.objects.filter(user=request.user).order_by('-data')
    return render(request, 'cal/lista_transacoes.html', {'transacoes': transacoes})

@login_required
def excluir_transacao(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    return redirect('cal:transacoes_mes')

@login_required
def excluir_transacao_lista(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, user=request.user)
    transacao.delete()
    return redirect('cal:listar_transacoes')

@login_required
def transacao_editar(request, pk=None):
    instancia = get_object_or_404(Transacao, pk=pk, user=request.user) if pk else Transacao(user=request.user)
    form = TransacaoForm(request.POST or None, instance=instancia)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cal:transacoes_mes')

    return render(request, 'cal/event.html', {'form': form})


# def transacao_view(request):
#     form = TransacaoForm(request.POST or None)
#     print(request.POST)
#     if request.method == 'POST' and form.is_valid():
#         print(request.POST)
#         transacao = form.save(commit=False)
#         transacao.user = request.user

#         parcelas = form.cleaned_data.get('parcelas')
#         # print(f'qtd: {parcelas}')
#         if parcelas and parcelas > 1:
#             for i in range(parcelas):
#                 nova = Transacao(
#                     user=request.user,
#                     tipo=transacao.tipo,
#                     titulo=transacao.titulo + f' ({i+1}/{parcelas})',
#                     valor=(transacao.valor)/parcelas,
#                     data=transacao.data + relativedelta(months=i),
#                     parcelas=parcelas,
#                     data_fim=transacao.data + relativedelta(months=parcelas-1)
#                 )
#                 nova.save()
#         else:
#             transacao.save()

#         return redirect('cal:transacoes_mes')

#     return render(request, 'cal/transacao_form.html', {'form': form})


@login_required
def transacao_view(request):
    form = TransacaoForm(request.POST or None)
    print(f'post: {request.POST}')
    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        tipo = transacao.tipo
        parcelas = form.cleaned_data.get('parcelas') or 1
        valor_total = transacao.valor or 0

        # Caso seja compra no cartão (crédito)
        if tipo.id == 3:
            # Criar registro visual na data da compra (sem valor)
            Transacao.objects.create(
                user=request.user,
                tipo=tipo,
                titulo=transacao.titulo,
                valor=0,
                data=transacao.data,
                parcelas=None,
                data_fim=None,
            )

            # Criar as parcelas a partir do mês seguinte
            for i in range(parcelas):
                Transacao.objects.create(
                    user=request.user,
                    tipo=tipo,
                    titulo=f"{transacao.titulo} ({i+1}/{parcelas})",
                    valor=valor_total / parcelas,
                    data=transacao.data + relativedelta(months=i + 1),
                    parcelas=parcelas,
                    data_fim=transacao.data + relativedelta(months=parcelas),
                )
        else:
            # Transação normal (débito ou crédito sem parcelamento)
            if parcelas > 1:
                for i in range(parcelas):
                    Transacao.objects.create(
                        user=request.user,
                        tipo=tipo,
                        titulo=f"{transacao.titulo} ({i+1}/{parcelas})",
                        valor=valor_total / parcelas,
                        data=transacao.data + relativedelta(months=i),
                        parcelas=parcelas,
                        data_fim=transacao.data + relativedelta(months=parcelas - 1),
                    )
            else:
                print(f'Transação: título={transacao.titulo}, valor=R$ {transacao.valor:.2f}')
                transacao.save()
                

        return redirect('cal:transacoes_mes')

    return render(request, 'cal/transacao_form.html', {'form': form})





def get_absolute_url(self):
        return reverse('transacao_editar', args=[self.id])



class TransacaoUpdateView(UpdateView):
    model = Transacao
    fields = ['tipo', 'titulo', 'valor', 'data', 'parcelas']
    template_name = 'cal/transacao_form.html'  # crie esse template se ainda não existir
    success_url = reverse_lazy('cal:calendar')  # ou outra URL para onde redirecionar depois da edição

@login_required
def transacoes_mes_view(request):
    # Código anterior...
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))

    # data_inicio = make_aware(date(ano, mes, 1))
    # data_fim = make_aware(date(ano, mes, 1) + relativedelta(months=1))
    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).order_by('-data')

    # total = sum([
    #     -t.valor if t.tipo.descricao.lower() == 'débito' else t.valor
    #     for t in transacoes
    # ])
    

    total = sum([
        -Decimal(t.valor) if t.tipo.descricao.lower() == 'débito' else Decimal(t.valor)
        for t in transacoes
        if t.valor is not None and str(t.valor).strip() != ''
    ])


    # Prepara dados para o gráfico por tipo
    dados_por_tipo = defaultdict(Decimal)  # Corrigido para Decimal
    for t in transacoes:
        valor = -t.valor if t.tipo.descricao.lower() == 'débito' else t.valor
        dados_por_tipo[t.tipo.descricao] += valor  # Agora soma Decimal com Decimal

    labels = list(dados_por_tipo.keys())
    valores = [float(v) for v in dados_por_tipo.values()]  # Para JSON e JS, converta para float

    total_creditos = transacoes.filter(tipo__is_credito__iexact='1').aggregate(Sum('valor'))['valor__sum'] or 0
    # print(total_creditos)
    
    total_debitos = transacoes.filter(tipo__is_credito__iexact='0').aggregate(Sum('valor'))['valor__sum'] or 0
    # print(total_debitos)
    # print(f'total_debitos:{total_debitos}')
    saldo_total = total_creditos - total_debitos
    # print(saldo_total)
    contexto = {
        'transacoes': transacoes,
        'mes_atual': date(ano, mes, 1),
        'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
        'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
        'total': total,
        'grafico_labels': labels,
        'grafico_valores': valores,
        'total_creditos': total_creditos,
        'total_debitos': total_debitos,
        'saldo_total': saldo_total,
    }
    return render(request, 'cal/transacoes_mes.html', contexto)


@login_required
def resumo_categoria_view(request):
    transacoes = Transacao.objects.filter(user=request.user)

    dados_resumo = transacoes.values("tipo__descricao", "tipo__is_credito").annotate(total=Sum("valor"))

    labels = []
    valores = []
    cores = []

    for item in dados_resumo:
        tipo = item["tipo__descricao"]
        total = float(item["total"])
        labels.append(tipo)
        valores.append(total)
        cores.append("#4CAF50" if item["tipo__is_credito"] else "#F44336")

    contexto = {
        "labels": labels,
        "valores": valores,
        "cores": cores,
    }
    return render(request, "cal/resumo_categoria.html", contexto)

