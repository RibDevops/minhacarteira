# cal/views/views_tipo.py
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Tipo
from ..forms import TipoForm

def tipo_list(request):
    tipos = Tipo.objects.filter(user=request.user)
    return render(request, 'cal/tipo_list.html', {'tipos': tipos})

def tipo_create(request):
    if request.method == 'POST':
        form = TipoForm(request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.user = request.user
            tipo.save()
            return redirect('cal:tipo_list')
    else:
        form = TipoForm()
    return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Novo Tipo'})

def tipo_update(request, pk):
    tipo = get_object_or_404(Tipo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TipoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            return redirect('cal:tipo_list')
    else:
        form = TipoForm(instance=tipo)
    return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Editar Tipo'})

def tipo_delete(request, pk):
    tipo = get_object_or_404(Tipo, pk=pk, user=request.user)
    if request.method == 'POST':
        tipo.delete()
        return redirect('cal:tipo_list')
    return render(request, 'cal/tipo_confirm_delete.html', {'tipo': tipo})
