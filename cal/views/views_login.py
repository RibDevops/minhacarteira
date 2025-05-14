# cal/views/views_login.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from cal.forms import UserRegisterForm
import logging



logger = logging.getLogger('django')

def register_view(request):
    print('POST')
    if request.method == 'POST':
        print('POST')
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # login automático após cadastro
            messages.success(request, 'Cadastro realizado com sucesso!')
            logger.info(f'Novo usuário registrado: {user.username}')
            return redirect('home')  # ou outra página
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

from django.contrib.auth import authenticate, login as login_django
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def login_view(request):  # ✅ Evite sobrescrever 'login'
    if request.method == "GET":
        
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            login_django(request, user)
            return redirect('home')  # Ou qualquer nome de rota
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
            return redirect('login')

from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
