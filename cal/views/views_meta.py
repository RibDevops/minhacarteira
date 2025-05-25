from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta

from cal.forms import MetaCategoriaForm

from ..models import MetaCategoria, Transacao

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def get_mes_anterior_posterior(mes, ano):
    data_atual = date(ano, mes, 1)
    mes_anterior = (data_atual - timedelta(days=1)).replace(day=1)
    mes_posterior = (data_atual + timedelta(days=31)).replace(day=1)
    return mes_anterior, mes_posterior


@login_required
def metas_dashboard(request):
    user = request.user
    hoje = date.today()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    mes_nome = MESES_PT[mes]
    mes_anterior, mes_proximo = get_mes_anterior_posterior(mes, ano)

    categorias_labels = []
    categorias_valores = []
    dados = []

    metas = MetaCategoria.objects.filter(user=user, mes=mes, ano=ano)

    for meta in metas:
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
        'dados': dados,
        'mes': mes,
        'ano': ano,
        'mes_atual': f"{mes_nome} de {ano}",
        'meses': MESES_PT,
        'mes_anterior': mes_anterior,
        'mes_proximo': mes_proximo,
        'grafico_labels': categorias_labels,
        'grafico_valores': categorias_valores,
    }
    return render(request, 'cal/metas_dashboard.html', context)


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from ..forms import MetaCategoriaForm
from ..models import MetaCategoria

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse  # <-- IMPORT ESSENCIAL AQUI
from django.db.models import Sum
from datetime import date, timedelta

from ..models import MetaCategoria, Transacao
from ..forms import MetaCategoriaForm


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import MetaCategoriaForm
from ..models import MetaCategoria


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages



@login_required
def meta_adicionar(request):
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST, user=request.user)
        
        if form.is_valid():
            meta = form.save(commit=False)
            meta.user = request.user
            meta.mes = form.cleaned_data['mes']
            meta.ano = form.cleaned_data['ano']
            
            # Garanta que o limite está sendo passado
            if 'limite' in form.cleaned_data:
                meta.limite = form.cleaned_data['limite']
            else:
                # Se não estiver, adicione uma mensagem de erro
                form.add_error('limite', 'Este campo é obrigatório')
                return render(request, 'cal/meta_form.html', {'form': form})
            
            meta.save()
            messages.success(request, "Meta cadastrada com sucesso!")
            return redirect('cal:metas_categoria')
    else:
        form = MetaCategoriaForm(user=request.user)
    
    return render(request, 'cal/meta_form.html', {'form': form})

@login_required
def meta_editar(request, pk):  # Mude de 'meta_id' para 'pk'
    meta = get_object_or_404(MetaCategoria, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = MetaCategoriaForm(request.POST, instance=meta, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Meta atualizada com sucesso!")
            return redirect('cal:metas_categoria')
    else:
        # Pré-popula o campo mes_ano
        initial = {'mes_ano': f"{meta.mes:02d}-{meta.ano}"}
        form = MetaCategoriaForm(instance=meta, initial=initial, user=request.user)
    
    return render(request, 'cal/meta_form.html', {
        'form': form,
        'meta': meta
    })


# @login_required
# def meta_excluir(request, pk):
#     meta = get_object_or_404(MetaCategoria, pk=pk, user=request.user)
#     if request.method == 'POST':
#         meta.delete()
#         messages.success(request, "Meta excluída com sucesso.")
#         return redirect('metas_dashboard')
#     return render(request, 'cal/meta_confirm_delete.html', {'meta': meta})

# MES_NOMES = {
#     1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
#     5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
#     9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
# }
@login_required


def meta_excluir(request, meta_id):
    meta = get_object_or_404(MetaCategoria, id=meta_id)
    mes_nome = MESES_PT.get(meta.mes, '-')

    if request.method == 'POST':
        meta.delete()
        return redirect(f"{reverse('cal:metas_dashboard')}?mes={meta.mes}&ano={meta.ano}")

    return render(request, 'cal/confirmar_exclusao_meta.html', {'meta': meta, 'mes_nome': mes_nome})
