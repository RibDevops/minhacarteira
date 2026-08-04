from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from dateutil.relativedelta import relativedelta
from encrypted_model_fields.fields import EncryptedCharField, EncryptedDecimalField


# ======================================================
# CONSTANTES / CHOICES
# ======================================================

FORMA_PAGAMENTO_CHOICES = [
    ('DEBITO', 'Débito (à vista)'),
    ('CREDITO', 'Crédito (a prazo)'),
    ('DINHEIRO', 'Dinheiro'),
    ('PIX', 'Pix'),
]

FORMA_PAGAMENTO_EXIGE_CARTAO = {
    'CREDITO': True,
    'DEBITO': True,
    'DINHEIRO': False,
    'PIX': False,
}

# ======================================================
# BASE MODEL
# ======================================================

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        abstract = True


# ======================================================
# CATEGORIA
# ======================================================

class Categoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    is_global = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self) -> str:
        prefix = "[GLOBAL] " if self.is_global else ""
        return f"{prefix}{self.nome}"

    @classmethod
    def get_for_user(cls, user):
        """Retorna apenas as categorias ativas do usuário."""
        return cls.objects.filter(user=user, is_active=True)


# ======================================================
# META POR CATEGORIA
# ======================================================

class MetaCategoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    limite = models.DecimalField(max_digits=15, decimal_places=2)
    mes = models.PositiveIntegerField()  # 1–12
    ano = models.PositiveIntegerField()

    class Meta:
        unique_together = ['user', 'categoria', 'mes', 'ano']
        ordering = ['ano', 'mes', 'categoria']

    def __str__(self):
        return f"{self.categoria} - {self.mes}/{self.ano}: R$ {self.limite}"


# ======================================================
# TIPO CONTÁBIL (APENAS 2)
# ======================================================

class Tipo(models.Model):
    CREDITO = 'C'
    DEBITO = 'D'

    TIPO_CHOICES = (
        (CREDITO, 'Crédito (Entrada)'),
        (DEBITO, 'Débito (Saída)'),
    )

    codigo = models.CharField(
        max_length=1,
        choices=TIPO_CHOICES,
        default='D',
        unique=True
    )

    descricao = models.CharField(max_length=50)

    def __str__(self) -> str:
        return str(self.descricao)


# ======================================================
# CARTÃO
# ======================================================

class Cartao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, verbose_name="Nome do cartão", default="Novo Cartão")
    limite = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    dia_fechamento = models.PositiveIntegerField(default=1)

    tipo = models.ForeignKey(
        'Tipo',
        on_delete=models.PROTECT,
        verbose_name="Tipo contábil",
        help_text="Crédito (entrada no extrato do cartão = débito contábil) ou Débito",
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"

    def __str__(self) -> str:
        return str(self.nome)


# ======================================================
# TRANSAÇÃO
# ======================================================

class Transacao(BaseModel):
    tipo = models.ForeignKey(
        Tipo,
        on_delete=models.PROTECT,
        verbose_name="Tipo contábil"
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name="Forma de pagamento",
        null=True,
        blank=True
    )

    cartao = models.ForeignKey(
        Cartao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cartão"
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    titulo = EncryptedCharField(
        max_length=200,
        verbose_name="Título"
    )

    valor = EncryptedDecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor"
    )

    data = models.DateField(verbose_name="Data da transação")

    # Para unique_together com recorrencia (índice funcional não suportado no SQLite)
    ano = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    mes = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    parcelas = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Parcelas"
    )

    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data final"
    )

    observacoes = EncryptedCharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Observações"
    )

    grupo_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="ID do Grupo"
    )

    recorrencia = models.ForeignKey(
        'Recorrencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes_geradas',
        verbose_name="Recorrência de origem",
        help_text="Preenchido automaticamente quando esta transação foi gerada por uma assinatura/recorrência."
    )

    class Meta:
        unique_together = ['recorrencia', 'ano', 'mes']

    def save(self, *args, **kwargs):
        if self.data and (self.ano is None or self.mes is None):
            self.ano = self.data.year
            self.mes = self.data.month
        super().save(*args, **kwargs)

    @property
    def valor_decimal(self):
        return self.valor if self.valor is not None else Decimal('0')

    def get_html_url(self):
        url = reverse('cal:transacao_editar', args=[self.id])
        valor_formatado = f"R$ {self.valor_decimal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'

    def get_absolute_url(self):
        return reverse('cal:transacao_editar', args=[self.id])


# ======================================================
# RECORRÊNCIA (assinaturas, aluguel, mensalidades...)
# ======================================================

class Recorrencia(BaseModel):
    """
    Representa um lançamento que se repete todo mês (assinatura de
    streaming, aluguel, academia, etc). Diferente de Transacao.parcelas,
    que tem fim definido: uma Recorrencia não tem data de término a menos
    que o usuário a desative.

    As transações efetivas de cada mês são criadas sob demanda por
    `cal.utils.gerar_transacoes_pendentes()` (chamada via management command
    ou cron diário), não a cada request autenticado — evita N queries extra
    por page view e race conditions. Constraint única em
    Transacao(recorrencia, ano, mes) garante idempotência.
    """
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT, verbose_name="Tipo contábil")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    cartao = models.ForeignKey(Cartao, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cartão")

    titulo = EncryptedCharField(max_length=200, verbose_name="Título")
    valor = EncryptedDecimalField(max_digits=15, decimal_places=2, verbose_name="Valor mensal")

    dia_cobranca = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Dia da cobrança",
        help_text="Dia do mês em que o lançamento deve ser gerado (1-28, para evitar problemas com meses curtos)."
    )

    data_inicio = models.DateField(default=None, null=True, blank=True, verbose_name="Início")
    data_fim = models.DateField(
        null=True, blank=True, verbose_name="Repetir até",
        help_text="Deixe em branco para repetir indefinidamente até ser desativada."
    )
    ativa = models.BooleanField(default=True, verbose_name="Ativa")
    observacoes = EncryptedCharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = "Recorrência"
        verbose_name_plural = "Recorrências"
        ordering = ['-ativa', 'titulo']

    def __str__(self):
        return f"{self.titulo} (R$ {self.valor}/mês)"

    def get_absolute_url(self):
        return reverse('cal:recorrencia_editar', args=[self.id])