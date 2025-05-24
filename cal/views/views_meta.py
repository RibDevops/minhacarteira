from django.contrib.auth.decorators import login_required
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
    user = request.user  # Usuário logado

    # Listas para armazenar dados do gráfico
    categorias_labels = []
    categorias_valores = []

    # Obtém mês e ano da URL (GET) ou usa os atuais
    hoje = date.today()
    mes = int(request.GET.get('mes', hoje.month))  # ex: ?mes=5
    ano = int(request.GET.get('ano', hoje.year))   # ex: ?ano=2025

    # Corrige o nome do mês baseado na seleção do usuário (não na data atual)
    mes_nome = MESES_PT.get(mes, "Mês inválido")

    # Calcula o primeiro dia do mês atual selecionado
    data_atual = date(ano, mes, 1)
    mes_anterior = data_atual - relativedelta(months=1)
    mes_proximo = data_atual + relativedelta(months=1)

    # Se o formulário for enviado (POST), salva a meta
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.user = user
            meta.save()
    else:
        # Inicializa formulário com o próximo mês como sugestão
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

    # Busca metas cadastradas para esse usuário, mês e ano
    metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

    dados = []

    for meta in metas:
        # Filtra transações de despesas dessa categoria no mês/ano
        transacoes = Transacao.objects.filter(
            user=user,
            categoria=meta.categoria,
            tipo__is_credito=False,
            data__year=ano,
            data__month=mes
        )

        # Soma os gastos
        gasto = transacoes.aggregate(total=Sum('valor'))['total'] or 0
        restante = float(meta.limite) - float(gasto)
        percentual = (gasto / float(meta.limite)) * 100 if meta.limite else 0

        # Adiciona dados para o gráfico de pizza (ou barra)
        categorias_labels.append(f"{meta.categoria.nome} (R$ {gasto:.2f})")
        categorias_valores.append(float(gasto))

        # Dados detalhados para exibir na tabela
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

    # Lista de todos os meses para o dropdown
    meses = list(range(1, 13))

    # Renderiza o template com todos os dados
    return render(request, 'cal/metas_dashboard.html', {
        'form': form,
        'dados': dados,
        'mes': mes,
        'ano': ano,
        'meses': meses,
        'mes_atual': mes_nome,  # Corrigido aqui para nome do mês selecionado
        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,
        'labels_json': categorias_labels,
        'valores_json': categorias_valores,
    })
