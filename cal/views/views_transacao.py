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
    #form = TransacaoForm(request.POST or None, instance=instancia)
    form = TransacaoForm(request.POST or None, instance=instancia, user=request.user)


    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cal:transacoes_mes')

    return render(request, 'cal/transacao_editar.html', {'form': form})


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

        if tipo.id == 3:  # Cartão de crédito
            # Parcelas começam no mês seguinte
            for i in range(parcelas):
                Transacao.objects.create(
                    user=request.user,
                    tipo=tipo,
                    categoria=categoria,
                    titulo=f"{transacao.titulo} - ({data_compra_str}) ({i + 1}/{parcelas})",
                    valor=valor_parcela,
                    data=data + relativedelta(months=i + 1),
                    parcelas=parcelas,
                    data_fim=data + relativedelta(months=parcelas),
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
                        data=data + relativedelta(months=i),
                        parcelas=parcelas,
                        data_fim=data + relativedelta(months=parcelas - 1),
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




@login_required
def listar_transacoes(request):
    transacoes = Transacao.objects.filter(user=request.user).order_by('-data')
    
    # print(connection.queries)
    # print(transacoes)
    # for t in transacoes:
        # print(f"{t.id} | {t.titulo} | {t.valor} | {t.data} | {t.categoria} | {t.tipo}")


    ano = request.GET.get('ano')
    # print(ano)
    mes = request.GET.get('mes')
    # print(mes)
    tipo = request.GET.get('tipo')
    categoria = request.GET.get('categoria')

    if ano:
        transacoes = transacoes.filter(data__year=int(ano))
        # print(f'ano_t {transacoes}')
    if mes:
        transacoes = transacoes.filter(data__month=int(mes))
    if tipo:
        transacoes = transacoes.filter(tipo_id=int(tipo))
    if categoria:
        transacoes = transacoes.filter(categoria_id=int(categoria))

    tipos = Tipo.objects.all()
    categorias = Categoria.objects.all()
    # print(f'transacoes: {transacoes}')

    return render(request, 'cal/lista_transacoes.html', {
        'transacoes': transacoes,
        'tipos': tipos,
        'categorias': categorias,
    })
