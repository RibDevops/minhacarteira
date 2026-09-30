from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..forms import RecorrenciaForm
from ..models import Recorrencia
from ..utils import gerar_transacoes_pendentes


@login_required
def recorrencia_listar(request):
    # Garante que, ao abrir a tela, os lançamentos do mês corrente já existam
    # (o context_processor já faz isso globalmente, mas não custa garantir aqui
    # também caso essa view seja chamada isoladamente no futuro).
    gerar_transacoes_pendentes(request.user)

    recorrencias = Recorrencia.objects.filter(user=request.user).select_related('tipo', 'categoria', 'cartao')
    return render(request, 'cal/recorrencia_list.html', {
        'titulo_pagina': 'Assinaturas e Recorrências',
        'recorrencias': recorrencias,
    })


@login_required
def recorrencia_nova(request):
    form = RecorrenciaForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        recorrencia = form.save(commit=False)
        recorrencia.user = request.user
        recorrencia.save()
        gerar_transacoes_pendentes(request.user)
        messages.success(request, f'Recorrência "{recorrencia.titulo}" criada com sucesso.')
        return redirect('cal:recorrencia_listar')
    return render(request, 'cal/recorrencia_form.html', {'form': form, 'titulo_pagina': 'Nova Recorrência'})


@login_required
def recorrencia_editar(request, pk):
    recorrencia = get_object_or_404(Recorrencia, pk=pk, user=request.user)
    form = RecorrenciaForm(request.POST or None, instance=recorrencia, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Recorrência "{recorrencia.titulo}" atualizada.')
        return redirect('cal:recorrencia_listar')
    return render(request, 'cal/recorrencia_form.html', {'form': form, 'titulo_pagina': 'Editar Recorrência'})


@login_required
@require_POST
def recorrencia_alternar_status(request, pk):
    """Pausa ou reativa uma recorrência sem apagar o histórico de transações já geradas."""
    recorrencia = get_object_or_404(Recorrencia, pk=pk, user=request.user)
    recorrencia.ativa = not recorrencia.ativa
    recorrencia.save(update_fields=['ativa'])
    if recorrencia.ativa:
        gerar_transacoes_pendentes(request.user)
    messages.success(request, f'Recorrência "{recorrencia.titulo}" {"reativada" if recorrencia.ativa else "pausada"}.')
    return redirect('cal:recorrencia_listar')


@login_required
@require_POST
def recorrencia_excluir(request, pk):
    """
    Exclui a recorrência (deixa de gerar novos lançamentos). As transações já
    criadas no passado permanecem — apagá-las junto seria uma surpresa
    desagradável (reescrever o histórico financeiro do usuário sem avisar).
    """
    recorrencia = get_object_or_404(Recorrencia, pk=pk, user=request.user)
    titulo = recorrencia.titulo
    recorrencia.delete()
    messages.success(request, f'Recorrência "{titulo}" excluída. As transações já lançadas foram mantidas.')
    return redirect('cal:recorrencia_listar')
