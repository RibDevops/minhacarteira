from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import MetaCategoria, Transacao
from ..forms import MetaCategoriaForm
from django.db.models import Sum
from datetime import date
from calendar import monthrange
from datetime import datetime
from dateutil.relativedelta import relativedelta


MESES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

@login_required
def metas_dashboard(request):
    user = request.user
    categorias_labels = []
    categorias_valores = []

    hoje = date.today()
    mes_atual_num = hoje.month
    mes_atual_nome = MESES_PT.get(mes_atual_num, "Mês inválido")
    # ano = hoje.year
    

    # data_atual = date(ano, mes, 1)
    # mes_anterior = data_atual - relativedelta(months=1)
    # mes_proximo = data_atual + relativedelta(months=1)

    # Verifica se veio via GET na URL
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    hoje = date.today()

    # Se não veio nada, usa o mês e ano atual
    if mes is None:
        mes = hoje.month
    else:
        mes = int(mes)

    if ano is None:
        ano = hoje.year
    else:
        ano = int(ano)

    data_atual = date(ano, mes, 1)
    mes_anterior = data_atual - relativedelta(months=1)
    mes_proximo = data_atual + relativedelta(months=1)


    # Formulário
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.user = user
            meta.save()
    else:
        # Descobrir mês/ano seguinte
        if hoje.month == 12:
            proximo_mes = 1
            proximo_ano = hoje.year + 1
        else:
            proximo_mes = hoje.month + 1
            proximo_ano = hoje.year

        # Cria formulário com valores iniciais
        form = MetaCategoriaForm(initial={
            'mes': proximo_mes,
            'ano': proximo_ano,
        })

    # Metas do mês
    metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

    dados = []

    for meta in metas:
        transacoes = Transacao.objects.filter(
            user=user,
            categoria=meta.categoria,
            tipo__is_credito=False,
            data__year=ano,
            data__month=mes
        )

        gasto = transacoes.aggregate(total=Sum('valor'))['total'] or 0
        restante = float(meta.limite) - float(gasto)
        percentual = (gasto / float(meta.limite)) * 100 if meta.limite else 0

        # adiciona para gráfico geral (se você for usar)
        categorias_labels.append(f"{meta.categoria.nome} (R$ {gasto:.2f})")
        categorias_valores.append(float(gasto))

        dados.append({
            'categoria': meta.categoria.nome,
            'limite': float(meta.limite),
            'gasto': float(gasto),
            'restante': float(restante),
            'percentual': round(percentual, 1),
            'status': (
                'success' if percentual <= 70 else
                'warning' if percentual <= 100 else
                'danger'
            ),
            'transacoes': transacoes,
            'id': meta.categoria.id
        })


    meses = list(range(1, 13))

    return render(request, 'cal/metas_dashboard.html', {
        'form': form,
        'dados': dados,
        'mes': mes,
        'ano': ano,
        'meses': meses,
        'mes_atual': mes_atual_nome,


        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,

        'labels_json': categorias_labels,
        'valores_json': categorias_valores,
    })
