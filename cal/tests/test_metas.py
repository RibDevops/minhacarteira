"""
Testes do fluxo de Metas por categoria.

Valida:
- Criar meta com form重建_data mes/ano
- Não permitir duplicar meta mesma categoria/mes/ano
- listar metas no dashboard calcula gasto e percentual corretamente
- Proteção: user B não edita meta do user A
"""
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from cal.models import Categoria, MetaCategoria, Tipo, Transacao


class MetaCrudTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='p')
        self.categoria = Categoria.objects.create(user=self.user, nome='Lazer')
        self.client.force_login(self.user)

    def test_criar_meta_salva_user_mes_ano(self):
        resp = self.client.post(reverse('cal:meta_criar'), {
            'categoria': self.categoria.id,
            'limite': '500,00',
            'mes_ano': '12-2026',  # mês futuro válido (julho corrente -_choices futuros)
        })
        self.assertEqual(resp.status_code, 302)

        meta = MetaCategoria.objects.get(user=self.user, categoria=self.categoria)
        self.assertEqual(meta.mes, 12)
        self.assertEqual(meta.ano, 2026)
        self.assertEqual(meta.limite, Decimal('500.00'))

    def test_meta_duplicada_falha(self):
        MetaCategoria.objects.create(
            user=self.user, categoria=self.categoria,
            mes=12, ano=2026, limite=Decimal('300'),
        )
        resp = self.client.post(reverse('cal:meta_criar'), {
            'categoria': self.categoria.id,
            'limite': '500',
            'mes_ano': '12-2026',
        })
        # Form inválido -> 200 (form re-renderizado com erros)
        self.assertEqual(resp.status_code, 200)
        # Aparece mensagem de erro no form
        self.assertContains(resp, 'Já existe uma meta', html=False)

    def test_editar_meta_atualiza_limite(self):
        meta = MetaCategoria.objects.create(
            user=self.user, categoria=self.categoria,
            mes=11, ano=2026, limite=Decimal('300'),
        )
        resp = self.client.post(reverse('cal:meta_editar', args=[meta.id]), {
            'categoria': self.categoria.id,
            'limite': '1000',
            'mes_ano': '11-2026',
        })
        self.assertEqual(resp.status_code, 302)
        meta.refresh_from_db()
        self.assertEqual(meta.limite, Decimal('1000.00'))


class MetaDashboardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='p')
        self.categoria = Categoria.objects.create(user=self.user, nome='Alimentação')
        self.tipo_debito = Tipo.objects.create(codigo='D', descricao='Débito')
        self.client.force_login(self.user)

    def test_dashboard_calcula_percentual_e_status(self):
        meta = MetaCategoria.objects.create(
            user=self.user, categoria=self.categoria,
            mes=1, ano=2026, limite=Decimal('500'),
        )
        # Gasta 400 -> 80% -> warning
        Transacao.objects.create(
            user=self.user, tipo=self.tipo_debito, categoria=self.categoria,
            titulo='Mercado', valor=Decimal('400'), data=date(2026, 1, 10),
        )

        resp = self.client.get(reverse('cal:metas_categoria'), {'mes': 1, 'ano': 2026})
        self.assertEqual(resp.status_code, 200)

        dados = resp.context['dados']
        self.assertEqual(len(dados), 1)
        d = dados[0]
        self.assertEqual(d['categoria'], 'Alimentação')
        self.assertEqual(d['limite'], Decimal('500'))
        self.assertEqual(d['gasto'], Decimal('400'))
        self.assertEqual(d['percentual'], 80.0)
        self.assertEqual(d['status'], 'warning')

    def test_dashboard_status_danger_quando_estoura(self):
        MetaCategoria.objects.create(
            user=self.user, categoria=self.categoria,
            mes=2, ano=2026, limite=Decimal('100'),
        )
        Transacao.objects.create(
            user=self.user, tipo=self.tipo_debito, categoria=self.categoria,
            titulo='Restaurante', valor=Decimal('150'), data=date(2026, 2, 10),
        )

        resp = self.client.get(reverse('cal:metas_categoria'), {'mes': 2, 'ano': 2026})
        d = resp.context['dados'][0]
        # 150% truncado para 100
        self.assertEqual(d['percentual'], 100)
        self.assertEqual(d['status'], 'danger')
        self.assertEqual(d['restante'], 0)


class MetaIDORTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='p')
        self.bob = User.objects.create_user(username='bob', password='p')
        self.cat_alice = Categoria.objects.create(user=self.alice, nome='Lazer A')
        self.meta_alice = MetaCategoria.objects.create(
            user=self.alice, categoria=self.cat_alice,
            mes=1, ano=2026, limite=Decimal('500'),
        )

    def test_bob_nao_edita_meta_da_alice(self):
        self.client.force_login(self.bob)
        resp = self.client.get(reverse('cal:meta_editar', args=[self.meta_alice.id]))
        self.assertEqual(resp.status_code, 404)
        # POST also
        cat_bob = Categoria.objects.create(user=self.bob, nome='Lazer B')
        resp = self.client.post(reverse('cal:meta_editar', args=[self.meta_alice.id]), {
            'categoria': cat_bob.id,
            'limite': '1',
            'mes_ano': '01-2026',
        })
        self.assertEqual(resp.status_code, 404)
        # Limite não alterado
        self.meta_alice.refresh_from_db()
        self.assertEqual(self.meta_alice.limite, Decimal('500'))
