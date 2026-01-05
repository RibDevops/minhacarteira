from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import UsuarioForm, UsuarioUpdateForm, UsuarioPasswordResetForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('cal:perfil')
    else:
        form = UsuarioUpdateForm(instance=request.user)
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Meu Perfil'})

@login_required
def editar_usuario(request, user_id):
    # Controle de permissão: superuser edita qualquer um, usuário comum apenas a si mesmo
    if not request.user.is_staff and request.user.id != user_id:
        messages.error(request, 'Você não tem permissão para editar este perfil.')
        return redirect('cal:home')
    
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            if request.user.is_staff:
                return redirect('cal:listar_usuarios')
            return redirect('cal:perfil')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'usuarios/form_usuario.html', {'form': form, 'titulo': 'Editar Usuário'})


@login_required
@staff_member_required
def desativar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()
    messages.success(request, "Usuário desativado com sucesso.")
    return redirect('usuarios_list')

@login_required
@staff_member_required
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


def home(request):
    return render(request, 'home.html', {})


def contato(request):
    return render(request, 'contato.html')
