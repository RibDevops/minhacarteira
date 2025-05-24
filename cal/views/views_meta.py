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

from django.utils.safestring import mark_safe
import json

# @login_required
# def metas_dashboard(request):
#     user = request.user

#     categorias_labels = []
#     categorias_valores = []
    

#     hoje = date.today()
#     mes = int(request.GET.get('mes', hoje.month))
#     ano = int(request.GET.get('ano', hoje.year))
#     mes_nome = MESES_PT.get(mes, "Mês inválido")

#     data_atual = date(ano, mes, 1)
#     mes_anterior = data_atual - relativedelta(months=1)
#     mes_proximo = data_atual + relativedelta(months=1)

#     # Trata envio de formulário
#     if request.method == 'POST':
#         form = MetaCategoriaForm(request.POST)
#         if form.is_valid():
#             mes_form = int(form.cleaned_data['mes'])
#             ano_form = int(form.cleaned_data['ano'])
#             categoria = form.cleaned_data['categoria']

#             # Evita duplicação de metas para mesma categoria/mes/ano
#             if MetaCategoria.objects.filter(user=user, categoria=categoria, mes=mes_form, ano=ano_form).exists():
#                 messages.error(request, "Já existe uma meta cadastrada para essa categoria neste mês.")
#             else:
#                 meta = form.save(commit=False)
#                 meta.user = user
#                 meta.save()
#                 messages.success(request, "Meta cadastrada com sucesso!")
#     else:
#         # Define sugestão de próximo mês/ano
#         if hoje.month == 12:
#             proximo_mes = 1
#             proximo_ano = hoje.year + 1
#         else:
#             proximo_mes = hoje.month + 1
#             proximo_ano = hoje.year

#         form = MetaCategoriaForm(initial={
#             'mes': proximo_mes,
#             'ano': proximo_ano,
#         })

#     # Busca metas cadastradas para o período
#     metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

#     dados = []

#     for meta in metas:
#         transacoes = Transacao.objects.filter(
#             user=user,
#             categoria=meta.categoria,
#             tipo__is_credito=False,
#             data__year=ano,
#             data__month=mes
#         )

#         gasto = transacoes.aggregate(total=Sum('valor'))['total'] or 0
#         # restante = float(meta.limite) - float(gasto)
#         restante = max(float(meta.limite) - float(gasto), 0)

#         percentual = (gasto / float(meta.limite)) * 100 if meta.limite else 0

#         categorias_labels.append(f"{meta.categoria.nome} (R$ {gasto:.2f})")
#         categorias_valores.append(float(gasto))

#         dados.append({
#             'categoria': meta.categoria.nome,
#             'limite': float(meta.limite),
#             'gasto': float(gasto),
#             'restante': restante,  # J
#             # 'gasto': float(gasto),
#             # 'restante': max(float(restante), 0),  # Garante que não seja negativo
            
#             'percentual': round(percentual, 1),
#             'status': (
#                 'success' if percentual <= 70 else
#                 'warning' if percentual <= 100 else
#                 'danger'
#             ),
#             'transacoes': transacoes,
#             'id': meta.categoria.id
#         })

#     meses = list(range(1, 13))
#     # para exportar dados em JSON no template
#     grafico_labels = categorias_labels
#     grafico_valores = categorias_valores

#     return render(request, 'cal/metas_dashboard.html', {
#         'form': form,
#         'dados': dados,
#         'mes': mes,
#         'ano': ano,
#         'meses': meses,
#         'mes_atual': mes_nome,
#         'mes_anterior': mes_anterior,
#         'mes_proximo': mes_proximo,
#         'labels_json': categorias_labels,
#         'valores_json': categorias_valores,
#         'grafico_labels': grafico_labels,
#         'grafico_valores': grafico_valores,
# })

# @login_required
# def metas_dashboard(request):
#     ...
#     categorias_labels = []
#     categorias_valores = []

#     ...
#     metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

#     for meta in metas:
#         ...
#         gasto = transacoes.aggregate(total=Sum('valor'))['total'] or 0
#         restante = max(float(meta.limite) - float(gasto), 0)
#         ...

#         categorias_labels.append(f"{meta.categoria.nome}")
#         categorias_valores.append(float(gasto))

#         dados.append({
#             ...
#         })

#     ...

#     return render(request, 'cal/metas_dashboard.html', {
#         'form': form,
#         'dados': dados,
#         'mes': mes,
#         'ano': ano,
#         'meses': meses,
#         'mes_atual': mes_nome,
#         'mes_anterior': mes_anterior,
#         'mes_proximo': mes_proximo,
#         'grafico_labels': categorias_labels,
#         'grafico_valores': categorias_valores,
#     })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
import calendar

from ..models import MetaCategoria, Transacao  # Ajuste conforme seus modelos
from ..forms import MetaCategoriaForm            # Ajuste conforme seu formulário

@login_required
def metas_dashboard(request):
    user = request.user

    # Pega mês e ano da query string ?mes=xx&ano=xxxx, se não pega o atual
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')

    hoje = date.today()
    mes = int(mes) if mes and mes.isdigit() and 1 <= int(mes) <= 12 else hoje.month
    ano = int(ano) if ano and ano.isdigit() else hoje.year

    # Para nome do mês em português (se preferir)
    meses = [ "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro" ]
    mes_nome = meses[mes - 1]

    # Mes anterior e próximo para navegação (tratando bordas)
    if mes == 1:
        mes_anterior = date(ano - 1, 12, 1)
    else:
        mes_anterior = date(ano, mes - 1, 1)
    if mes == 12:
        mes_proximo = date(ano + 1, 1, 1)
    else:
        mes_proximo = date(ano, mes + 1, 1)

    # Processa o formulário de nova meta (se for POST)
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST)
        if form.is_valid():
            nova_meta = form.save(commit=False)
            nova_meta.user = user
            nova_meta.mes = mes
            nova_meta.ano = ano
            nova_meta.save()
            return redirect(f'/metas/?mes={mes}&ano={ano}')  # ou use reverse()
    else:
        form = MetaCategoriaForm()

    categorias_labels = []
    categorias_valores = []
    dados = []

    # Busca metas do usuário no mês e ano
    metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

    for meta in metas:
        # Transações nessa categoria, mês e ano do usuário
        transacoes = Transacao.objects.filter(
            user=user,
            categoria=meta.categoria,
            data__year=ano,
            data__month=mes
        )

        gasto = transacoes.aggregate(total=Sum('valor'))['total'] or 0
        restante = max(float(meta.limite) - float(gasto), 0)

        percentual = round((float(gasto) / float(meta.limite)) * 100, 2) if meta.limite else 0
        percentual = min(percentual, 100)

        # Status da barra de progresso (exemplo: verde, amarelo, vermelho)
        if percentual < 70:
            status = 'success'
        elif percentual < 100:
            status = 'warning'
        else:
            status = 'danger'

        categorias_labels.append(meta.categoria.nome)
        categorias_valores.append(float(gasto))

        dados.append({
            'id': meta.id,
            'categoria': meta.categoria.nome,
            'limite': meta.limite,
            'gasto': gasto,
            'restante': restante,
            'percentual': percentual,
            'status': status,
            'transacoes': transacoes.order_by('-data'),
        })

    context = {
        'form': form,
        'dados': dados,
        'mes': mes,
        'ano': ano,
        'meses': meses,
        'mes_atual': mes_nome,
        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,
        'grafico_labels': categorias_labels,
        'grafico_valores': categorias_valores,
    }
    return render(request, 'cal/metas_dashboard.html', context)
