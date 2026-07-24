"""
Testes de autenticação: login, logout e registro.

Valida os fluxos críticos que estavam quebrados/refatorados:
- redirect do @login_required
- registro cria categorias padrão e faz login automático
- logout redireciona para home
"""
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from cal.models import Categoria


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice', password='senha123', email='alice@test.com'
        )

    def test_login_get_mostra_form(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'password')

    def test_login_post_valido_autentica(self):
        resp = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'senha123',
        }, follow=True)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_login_post_invalido_nao_autentica(self):
        resp = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'errada',
        })
        self.assertEqual(resp.status_code, 200)  # volta pro form
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_login_redirect_para_next(self):
        # Sem auth, tentar acessar /transacoes-mes/ redireciona para login
        resp = self.client.get(reverse('cal:transacoes_mes'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='p4ss')

    def test_logout_desconecta(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse('logout'), follow=True)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)


class RegisterViewTest(TestCase):
    def test_registro_cria_user_e_categorias_padrao(self):
        resp = self.client.post(reverse('cal:register'), {
            'username': 'carol',
            'email': 'carol@test.com',
            'first_name': 'Carol',
            'last_name': 'Silva',
            'password': 'senha456',
            'password2': 'senha456',
        }, follow=True)

        # Usuário criado
        self.assertTrue(User.objects.filter(username='carol').exists())

        # Login automático
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

        # 9 categorias padrão criadas
        cats = Categoria.objects.filter(user__username='carol')
        self.assertEqual(cats.count(), 9)
        self.assertTrue(cats.filter(nome='Alimentação').exists())
        self.assertTrue(cats.filter(nome='Salário').exists())

    def test_registro_senhas_diferentes_falha(self):
        resp = self.client.post(reverse('cal:register'), {
            'username': 'dave',
            'email': 'dave@test.com',
            'first_name': 'Dave',
            'last_name': 'Souza',
            'password': 'aaa',
            'password2': 'bbb',
        })
        # Form inválido -> volta pro form com 200
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='dave').exists())
