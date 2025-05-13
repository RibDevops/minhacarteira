from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Ano
from ..forms import AnoForm
from .views_log import registrar_acao_usuario, registrar_acao_usuario_deletar
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views


@login_required
def ano_novo(request):
    user_id = request.user.id
    user = request.user
    if request.method == 'POST':
        form = AnoForm(request.POST)
        if form.is_valid():
            instance = form.save()
            registrar_acao_usuario(request, instance, f'cadastrou')  # Passa a instância do objeto Ano e a ação
            return redirect('ano_lista')  # Redirecione para a lista após criar
    else:
        form = AnoForm(initial={'fk_user': user_id})
    
    return render(request, 'ano/criar.html', {'form': form})


@login_required
def ano_editar(request, id):
    user_id = request.user.id
    user = request.user
    context = {}
    ano_ob = get_object_or_404(Ano, id=id)
    if request.method == 'POST':
        form = AnoForm(request.POST, instance=ano_ob)
        if form.is_valid():
            instance = form.save()
            registrar_acao_usuario(request, instance, f'Editou')  # Passa a instância do objeto Ano e a ação
            return redirect('ano_lista')
    else:
        form = AnoForm(instance=ano_ob, initial={'fk_user': user_id})

    context = {
        'form': form,
        'ano_ob': ano_ob
    }
    return render(request, 'ano/editar.html', context)


@login_required
def ano_delete(request, id):
    context = {}
    ano_ob = get_object_or_404(Ano, id=id)
    if request.method == 'POST':
        instance = ano_ob  # Salva a instância antes de excluir
        ano_id = instance.id  # Obtém o ID do objeto Ano antes de excluir

        ano_ob.delete()
#        registrar_acao_usuario(request, instance, f'Deletou')  # Passa a instância do objeto Ano
        registrar_acao_usuario_deletar(request, f'Ano', ano_id)  # Passa o ID do objeto Ano deletado

        return redirect('ano_lista')
    
    context = {
        'ano_ob': ano_ob
    }
    
    return render(request, 'ano/excluir.html', context)

@login_required
def ano_lista(request):
    dataset = Ano.objects.all()
    context = {"dataset": dataset}
    # print(dataset)
    return render(request, 'ano/lista.html', context)




