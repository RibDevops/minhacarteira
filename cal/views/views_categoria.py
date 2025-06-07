from django.shortcuts import render, get_object_or_404, redirect
from cal.models import Categoria
from cal.forms import CategoriaForm  # você precisa criar esse form
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


# # LISTAR CATEGORIAS
# def categoria_list(request):
#     # categorias = Categoria.objects.filter(user=request.user)
#     categorias = Categoria.objects.all()
#     return render(request, 'cal/categoria_list.html', {'categorias': categorias})

# # CRIAR NOVA CATEGORIA
# def categoria_nova(request):
#     if request.method == 'POST':
#         form = CategoriaForm(request.POST)
#         if form.is_valid():
#             categoria = form.save(commit=False)
#             categoria.user = request.user  # associar ao usuário logado
#             categoria.save()
#             messages.success(request, 'Categoria criada com sucesso!')
#             return redirect('cal:categorias')
#     else:
#         form = CategoriaForm()
#     return render(request, 'cal/categoria_form.html', {'form': form})

# # ATUALIZAR CATEGORIA
# def categoria_update(request, pk):
#     categoria = get_object_or_404(Categoria, pk=pk)
#     if request.method == 'POST':
#         form = CategoriaForm(request.POST, instance=categoria)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Categoria atualizada com sucesso!')
#             return redirect('cal:categorias')
#     else:
#         form = CategoriaForm(instance=categoria)
#     return render(request, 'cal/categoria_form.html', {'form': form})

# # EXCLUIR CATEGORIA
# def categoria_delete(request, pk):
#     categoria = get_object_or_404(Categoria, pk=pk)
#     if request.method == 'POST':
#         categoria.delete()
#         messages.success(request, 'Categoria excluída com sucesso!')
#         return redirect('cal:categorias')
#     return render(request, 'cal/categoria_confirm_delete.html', {'categoria': categoria})



# @login_required
# def categoria_list(request):
#     categoria = Categoria.objects.all()  # Removido o filtro por usuário
#     return render(request, 'cal/categoria_list.html', {'categoria': categoria})



# @login_required
# def tipo_list(request):
#     tipos = Tipo.objects.all()  # Removido o filtro por usuário
#     return render(request, 'cal/tipo_list.html', {'tipos': tipos})

# @login_required
# def tipo_create(request):
#     if request.method == 'POST':
#         form = TipoForm(request.POST)
#         if form.is_valid():
#             tipo = form.save(commit=False)
#             # tipo.user = request.user  # Removido: tipos são globais
#             tipo.save()
#             return redirect('cal:tipo_list')
#     else:
#         form = TipoForm()
#     return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Novo Tipo'})

# @login_required
# def tipo_update(request, pk):
#     tipo = get_object_or_404(Tipo, pk=pk)  # Removido filtro por usuário
#     if request.method == 'POST':
#         form = TipoForm(request.POST, instance=tipo)
#         if form.is_valid():
#             form.save()
#             return redirect('cal:tipo_list')
#     else:
#         form = TipoForm(instance=tipo)
#     return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Editar Tipo'})

# @login_required
# def tipo_delete(request, pk):
#     tipo = get_object_or_404(Tipo, pk=pk)  # Removido filtro por usuário
#     if request.method == 'POST':
#         tipo.delete()
#         return redirect('cal:tipo_list')
#     return render(request, 'cal/tipo_confirm_delete.html', {'tipo': tipo})
