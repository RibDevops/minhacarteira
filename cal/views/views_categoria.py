from django.shortcuts import render, get_object_or_404, redirect
from cal.models import Categoria
from cal.forms import CategoriaForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def categoria_list(request):
    categorias = Categoria.objects.filter(user=request.user)
    return render(request, 'cal/categoria_list.html', {'categorias': categorias})


@login_required
def categoria_nova(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.user = request.user
            categoria.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('cal:categorias')
    else:
        form = CategoriaForm()
    return render(request, 'cal/categoria_form.html', {'form': form})


@login_required
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('cal:categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'cal/categoria_form.html', {'form': form})


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, user=request.user)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('cal:categorias')
    return render(request, 'cal/categoria_confirm_delete.html', {'categoria': categoria})
