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
from decimal import Decimal, InvalidOperation

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
# def transacao_view(request):
#     form = TransacaoForm(request.POST or None)
#     print(f'post: {request.POST}')
#     if request.method == 'POST' and form.is_valid():
#         transacao = form.save(commit=False)
#         transacao.user = request.user

#         tipo = transacao.tipo
#         parcelas = form.cleaned_data.get('parcelas') or 1
#         valor_total = transacao.valor or 0


def transacao_view(request):
    form = TransacaoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.user = request.user

        tipo = transacao.tipo
        parcelas = form.cleaned_data.get('parcelas') or 1

        try:
            valor_total = Decimal(str(transacao.valor)) if transacao.valor else Decimal('0')
        except (TypeError, ValueError, InvalidOperation):
            valor_total = Decimal('0')

        if tipo.id == 3:
            # Lança uma transação "visual" na data atual
            Transacao.objects.create(
                user=request.user,
                tipo=tipo,
                titulo=transacao.titulo,
                valor=0,
                data=transacao.data,
                parcelas=None,
                data_fim=None,
            )
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
                transacao.valor = valor_total
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
# def transacoes_mes_view(request):
#     print('entrou na view transacoes_mes_view')
#     # Código anterior...
#     ano = int(request.GET.get('ano', date.today().year))
#     mes = int(request.GET.get('mes', date.today().month))

#     # data_inicio = make_aware(date(ano, mes, 1))
#     # data_fim = make_aware(date(ano, mes, 1) + relativedelta(months=1))
#     data_inicio = make_aware(datetime(ano, mes, 1))
#     data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

#     # transacoes = Transacao.objects.filter(
#     #     user=request.user,
#     #     data__gte=data_inicio,
#     #     data__lt=data_fim
#     # ).order_by('-data')
#     # print(f'transacoes na mes: {transacoes.valor}')
#     # # total = sum([
#     #     -t.valor if t.tipo.descricao.lower() == 'débito' else t.valor
#     #     for t in transacoes
#     # ])
#     transacoes = Transacao.objects.filter(
#         user=request.user,
#         data__gte=data_inicio,
#         data__lt=data_fim
#     ).order_by('-data')

#     total = Decimal('0')
#     for t in transacoes:
#         if t.valor is not None and str(t.valor).strip() != '':
#             print(f'Transação: {t.valor}')
#             total += Decimal(t.valor)

#     print(f'Total no mês: {total}')

#     # total = sum([
#     #     Decimal(t.valor)
#     #     for t in transacoes
#     #     print(f'transacao: {t.valor}')
#     #     if t.valor is not None and str(t.valor).strip() != ''
#     # ])
#     # print(f'Total no mês: {total}')

#     # total = sum([
#     #     # -Decimal(t.valor) if t.tipo.descricao.lower() == 'Pagando' else Decimal(t.valor)
#     #     -Decimal(t.valor) if t.tipo.is_credito == False else Decimal(t.valor)
#     #     for t in transacoes
#     #     if t.valor is not None and str(t.valor).strip() != ''
#     # ])
#     print(f'total: {total}')


#     # Prepara dados para o gráfico por tipo
#     dados_por_tipo = defaultdict(Decimal)  # Corrigido para Decimal
#     for t in transacoes:
#         debito = transacoes.filter(tipo__is_credito=False).aggregate(total=models.Sum('valor'))['total'] or 0

#         valor = -t.valor if t.tipo.descricao.lower() == 'Pagando' else t.valor
#         dados_por_tipo[t.tipo.descricao] += valor


#     labels = list(dados_por_tipo.keys())
#     valores = [float(v) for v in dados_por_tipo.values()]  # Para JSON e JS, converta para float

#     total_creditos = transacoes.filter(tipo__is_credito__iexact='1').aggregate(Sum('valor'))['valor__sum'] or 0
#     # print(total_creditos)
    
#     total_debitos = transacoes.filter(tipo__is_credito__iexact='0').aggregate(Sum('valor'))['valor__sum'] or 0
#     # print(total_debitos)
#     # print(f'total_debitos:{total_debitos}')
#     saldo_total = total_creditos - total_debitos
#     # print(saldo_total)
#     contexto = {
#         'transacoes': transacoes,
#         'mes_atual': date(ano, mes, 1),
#         'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
#         'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
#         'total': total,
#         'grafico_labels': labels,
#         'grafico_valores': valores,
#         'total_creditos': total_creditos,
#         'total_debitos': total_debitos,
#         'saldo_total': saldo_total,
#     }
#     return render(request, 'cal/transacoes_mes.html', contexto)
# def transacoes_mes_view(request):
#     ano = int(request.GET.get('ano', date.today().year))
#     mes = int(request.GET.get('mes', date.today().month))

#     data_inicio = make_aware(datetime(ano, mes, 1))
#     data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

#     transacoes = Transacao.objects.filter(
#         user=request.user,
#         data__gte=data_inicio,
#         data__lt=data_fim
#     ).order_by('-data')

#     # Gráfico por tipo com valores ajustados
#     dados_por_tipo = defaultdict(Decimal)
#     for t in transacoes:
#         try:
#             valor = Decimal(t.valor)
#             if not t.tipo.is_credito:
#                 valor = -valor
#             dados_por_tipo[t.tipo.descricao] += valor

# #     dados_por_tipo = defaultdict(Decimal)
# # for t in transacoes:
# #     valor = Decimal(t.valor)
# #     if not t.tipo.is_credito:
# #         valor = -valor
# #     dados_por_tipo[t.tipo.descricao] += valor

#         except Exception as e:
#             print(f"Erro ao processar transação {t.id}: {e}")

#     labels = list(dados_por_tipo.keys())
#     valores = [float(v) for v in dados_por_tipo.values()]  # Para o gráfico

#     # Totais
#     total_creditos = transacoes.filter(tipo__is_credito=True).aggregate(Sum('valor'))['valor__sum'] or 0
#     total_debitos = transacoes.filter(tipo__is_credito=False).aggregate(Sum('valor'))['valor__sum'] or 0
#     saldo_total = total_creditos - total_debitos

#     contexto = {
#         'transacoes': transacoes,
#         'mes_atual': date(ano, mes, 1),
#         'mes_anterior': date(ano, mes, 1) - relativedelta(months=1),
#         'mes_proximo': date(ano, mes, 1) + relativedelta(months=1),
#         'grafico_labels': labels,
#         'grafico_valores': valores,
#         'total_creditos': total_creditos,
#         'total_debitos': total_debitos,
#         'saldo_total': saldo_total,
#     }
#     return render(request, 'cal/transacoes_mes.html', contexto)
def transacoes_mes_view(request):
    ano = int(request.GET.get('ano', date.today().year))
    mes = int(request.GET.get('mes', date.today().month))

    data_inicio = make_aware(datetime(ano, mes, 1))
    data_fim = make_aware(datetime(ano, mes, 1) + relativedelta(months=1))

    transacoes = Transacao.objects.filter(
        user=request.user,
        data__gte=data_inicio,
        data__lt=data_fim
    ).order_by('-data')

    # Gráfico por tipo (Crédito/Débito)
    dados_por_tipo = defaultdict(Decimal)
    for t in transacoes:
        try:
            valor = Decimal(t.valor)
            if not t.tipo.is_credito:
                valor = -valor
            dados_por_tipo[t.tipo.descricao] += valor
        except Exception as e:
            print(f"Erro ao processar transação {t.id}: {e}")

    labels = list(dados_por_tipo.keys())
    valores = [float(v) for v in dados_por_tipo.values()]

    # Gráfico por categoria
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
    total_creditos = transacoes.filter(tipo__is_credito=True).aggregate(Sum('valor'))['valor__sum'] or 0
    total_debitos = transacoes.filter(tipo__is_credito=False).aggregate(Sum('valor'))['valor__sum'] or 0
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

