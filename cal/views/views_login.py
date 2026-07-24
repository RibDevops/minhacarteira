from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render

from cal.forms import UserRegisterForm
from cal.models import Categoria

import logging

logger = logging.getLogger('django')


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            categorias_padrao = [
                'Alimentação', 'Transporte', 'Moradia', 'Lazer',
                'Saúde', 'Educação', 'Salário', 'Investimentos',
                'Outros'
            ]
            for nome_cat in categorias_padrao:
                Categoria.objects.create(user=user, nome=nome_cat)

            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            logger.info(f'Novo usuário registrado: {user.username}')
            return redirect('cal:home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
