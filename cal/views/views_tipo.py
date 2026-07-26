from django.shortcuts import render, redirect, get_object_or_404
from ..models import Tipo
from ..forms import TipoForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def tipo_list(request):
    tipos = Tipo.objects.all()
    return render(request, 'cal/tipo_list.html', {'tipos': tipos})

@staff_member_required
def tipo_create(request):
    if request.method == 'POST':
        form = TipoForm(request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.save()
            return redirect('cal:tipo_list')
    else:
        form = TipoForm()
    return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Novo Tipo'})

@staff_member_required
def tipo_update(request, pk):
    tipo = get_object_or_404(Tipo, pk=pk)
    if request.method == 'POST':
        form = TipoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            return redirect('cal:tipo_list')
    else:
        form = TipoForm(instance=tipo)
    return render(request, 'cal/tipo_form.html', {'form': form, 'title': 'Editar Tipo'})

@staff_member_required
def tipo_delete(request, pk):
    tipo = get_object_or_404(Tipo, pk=pk)
    if request.method == 'POST':
        tipo.delete()
        return redirect('cal:tipo_list')
    return render(request, 'cal/tipo_confirm_delete.html', {'tipo': tipo})
