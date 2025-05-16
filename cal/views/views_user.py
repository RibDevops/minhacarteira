from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import UsuarioForm, UsuarioUpdateForm, UsuarioPasswordResetForm
from django.contrib import messages

def listar_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})

def adicionar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário adicionado com sucesso!')
            return redirect('cal:listar_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Adicionar Usuário'})

def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('cal:listar_usuarios')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Editar Usuário'})

def excluir_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('cal:listar_usuarios')

def desativar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    messages.success(request, "Usuário desativado com sucesso.")
    return redirect('usuarios_list')

def resetar_senha(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UsuarioPasswordResetForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data['new_password'])
            usuario.save()
            messages.success(request, 'Senha redefinida com sucesso!')
            return redirect('cal:listar_usuarios')
    else:
        form = UsuarioPasswordResetForm()
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Resetar Senha'})
