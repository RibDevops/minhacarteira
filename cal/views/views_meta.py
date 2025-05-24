from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from ..models import MetaCategoria, Transacao
from ..forms import MetaCategoriaForm
from django.db.models import Sum
from datetime import date
from dateutil.relativedelta import relativedelta

# Dicionário para exibir os nomes dos meses em português
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

@login_required
def metas_dashboard(request):
    user = request.user

    categorias_labels = []
    categorias_valores = []

    hoje = date.today()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))
    mes_nome = MESES_PT.get(mes, "Mês inválido")

    data_atual = date(ano, mes, 1)
    mes_anterior = data_atual - relativedelta(months=1)
    mes_proximo = data_atual + relativedelta(months=1)

    # Trata envio de formulário
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST)
        if form.is_valid():
            mes_form = int(form.cleaned_data['mes'])
            ano_form = int(form.cleaned_data['ano'])
            categoria = form.cleaned_data['categoria']

            # Evita duplicação de metas para mesma categoria/mes/ano
            if MetaCategoria.objects.filter(user=user, categoria=categoria, mes=mes_form, ano=ano_form).exists():
                messages.error(request, "Já existe uma meta cadastrada para essa categoria neste mês.")
            else:
                meta = form.save(commit=False)
                meta.user = user
                meta.save()
                messages.success(request, "Meta cadastrada com sucesso!")
    else:
        # Define sugestão de próximo mês/ano
        if hoje.month == 12:
            proximo_mes = 1
            proximo_ano = hoje.year + 1
        else:
            proximo_mes = hoje.month + 1
            proximo_ano = hoje.year

        form = MetaCategoriaForm(initial={
            'mes': proximo_mes,
            'ano': proximo_ano,
        })

    # Busca metas cadastradas para o período
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
        'mes_atual': mes_nome,
        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,
        'labels_json': categorias_labels,
        'valores_json': categorias_valores,
    })
