"""
Testes do fluxo de transações: criar, parcelar, editar em cascata,
excluir, e a regra de cartão (transação vai para o mês seguinte).

Valida:
- TransacaoView cria 1 lançamento quando parcelas não informado
- Criar 3 parcelas gera 3 Transacao com mesmo grupo_id
- Cartão empurra a data para o mês seguinte
- transacao_rapida retorna JsonResponse success
- excluir_transacao com excluir_proximas=true remove o grupo inteiro
- Proteção IDOR: user A não edita/exclui transação do user B
"""
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from cal.models import Cartao, Categoria, Tipo, Transacao


class TransacaoCrudTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='p')
        self.tipo_debito = Tipo.objects.create(codigo='D', descricao='Débito')
        self.tipo_credito = Tipo.objects.create(codigo='C', descricao='Crédito')
        self.categoria = Categoria.objects.create(user=self.user, nome='Mercado')
        self.client.force_login(self.user)

    def test_criar_transacao_unica_sem_cartao(self):
        resp = self.client.post(reverse('cal:transacao_nova'), {
            'tipo': self.tipo_debito.id,
            'titulo': 'Mercado',
            'categoria': self.categoria.id,
            'valor': '150,50',
            'data': '2026-01-15',
        })
        self.assertEqual(resp.status_code, 302)

        ts = Transacao.objects.filter(user=self.user)
        self.assertEqual(ts.count(), 1)
        self.assertEqual(ts[0].titulo, 'Mercado')
        self.assertEqual(ts[0].valor, Decimal('150.50'))
        self.assertIsNone(ts[0].grupo_id)
        self.assertIsNone(ts[0].cartao)

    def test_criar_3_parcelas_gera_grupo(self):
        resp = self.client.post(reverse('cal:transacao_nova'), {
            'tipo': self.tipo_debito.id,
            'titulo': 'Notebook',
            'categoria': self.categoria.id,
            'valor': '1000',
            'data': '2026-01-15',
            'parcelas': '3',
        })
        self.assertEqual(resp.status_code, 302)

        ts = Transacao.objects.filter(user=self.user).order_by('data')
        self.assertEqual(ts.count(), 3)

        # Mesmo grupo_id
        grupo_ids = {t.grupo_id for t in ts}
        self.assertEqual(len(grupo_ids), 1)
        self.assertIsNotNone(grupo_ids.pop())

        # Títulos numerados
        self.assertEqual(ts[0].titulo, 'Notebook (1/3)')
        self.assertEqual(ts[2].titulo, 'Notebook (3/3)')

        # Datas em meses consecutivos
        self.assertEqual(ts[0].data, date(2026, 1, 15))
        self.assertEqual(ts[1].data, date(2026, 2, 15))
        self.assertEqual(ts[2].data, date(2026, 3, 15))


class TransacaoCartaoTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='p')
        self.tipo = Tipo.objects.create(codigo='D', descricao='Débito')
        self.categoria = Categoria.objects.create(user=self.user, nome='Online')
        self.cartao = Cartao.objects.create(
            user=self.user, nome='Nubank', limite=Decimal('5000'),
            dia_fechamento=1, is_credito=True, is_active=True
        )
        self.client.force_login(self.user)

    def test_transacao_cartao_vai_mes_seguinte(self):
        """
        Regra de negócio: compras em cartão sempre caem no mês seguinte,
        independente do dia da compra.
        """
        self.client.post(reverse('cal:transacao_nova'), {
            'tipo': self.tipo.id,
            'titulo': 'Compra Online',
            'cartao': self.cartao.id,
            'categoria': self.categoria.id,
            'valor': '300',
            'data': '2026-01-05',
        })

        t = Transacao.objects.get(user=self.user)
        # Janeiro -> Fevereiro (regra calcular_proxima_fatura)
        self.assertEqual(t.data, date(2026, 2, 1))


class TransacaoRapidaTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='carol', password='p')
        self.tipo = Tipo.objects.create(codigo='D', descricao='Débito')
        Categoria.objects.create(user=self.user, nome='Café')
        self.client.force_login(self.user)

    def test_rapida_sucesso_retorna_json(self):
        resp = self.client.post(reverse('cal:transacao_rapida'), {
            'titulo': 'Café da manhã',
            'tipo': self.tipo.id,
            'valor': '12,50',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(Transacao.objects.filter(user=self.user).count(), 1)

    def test_rapida_sem_titulo_falha(self):
        resp = self.client.post(reverse('cal:transacao_rapida'), {
            'titulo': '',
            'tipo': self.tipo.id,
            'valor': '10',
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data['status'], 'error')
        self.assertFalse(Transacao.objects.filter(user=self.user).exists())


class ExcluirCascataTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dave', password='p')
        self.tipo = Tipo.objects.create(codigo='D', descricao='Débito')
        self.client.force_login(self.user)

        # Cria 3 parcelas com mesmo grupo_id
        self.grupo = 'grupo-abc'
        for i in range(3):
            Transacao.objects.create(
                user=self.user, tipo=self.tipo, titulo=f'Item ({i+1}/3)',
                valor=Decimal('50'), data=date(2026, 1 + i, 1),
                grupo_id=self.grupo, parcelas=3,
            )

    def test_excluir_proximas_remove_do_grupo_da_data_em_diante(self):
        primeira = Transacao.objects.filter(user=self.user, grupo_id=self.grupo).order_by('data').first()
        # Exclui essa e todas as futuras
        resp = self.client.post(
            reverse('cal:transacao_excluir', args=[primeira.id]),
            {'excluir_proximas': 'true'},
        )
        self.assertEqual(resp.status_code, 302)
        # Ficou só a que tinha data anterior (não há-> 0 restantes)
        self.assertEqual(Transacao.objects.filter(user=self.user, grupo_id=self.grupo).count(), 0)

    def test_excluir_sozinha_mantem_outras(self):
        primeira = Transacao.objects.filter(user=self.user, grupo_id=self.grupo).order_by('data').first()
        self.client.post(reverse('cal:transacao_excluir', args=[primeira.id]))
        self.assertEqual(Transacao.objects.filter(user=self.user, grupo_id=self.grupo).count(), 2)


class IDORProtectionTest(TestCase):
    """
    Garantir que user B NÃO pode editar/excluir transação do user A
    apenas trocando o pk na URL (falha de IDOR clássica).
    """
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='p')
        self.bob = User.objects.create_user(username='bob', password='p')
        self.tipo = Tipo.objects.create(codigo='D', descricao='Débito')

        # Transação de alice
        self.trans_alice = Transacao.objects.create(
            user=self.alice, tipo=self.tipo, titulo='Segredo de Alice',
            valor=Decimal('999'), data=date(2026, 1, 1),
        )

    def test_bob_nao_edita_transacao_da_alice(self):
        self.client.force_login(self.bob)
        # GET: deve dar 404 (acesso negado via get_object_or_404 filtro por user)
        resp = self.client.get(reverse('cal:transacao_editar', args=[self.trans_alice.id]))
        self.assertEqual(resp.status_code, 404)

        # POST também
        resp = self.client.post(reverse('cal:transacao_editar', args=[self.trans_alice.id]), {
            'tipo': self.tipo.id,
            'titulo': 'HACKEADO',
            'valor': '1',
            'data': '2026-01-01',
        })
        self.assertEqual(resp.status_code, 404)
        # Dados não alterados
        self.trans_alice.refresh_from_db()
        self.assertEqual(self.trans_alice.titulo, 'Segredo de Alice')

    def test_bob_nao_exclui_transacao_da_alice(self):
        self.client.force_login(self.bob)
        resp = self.client.post(reverse('cal:transacao_excluir', args=[self.trans_alice.id]))
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Transacao.objects.filter(pk=self.trans_alice.id).exists())
