from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from dateutil.relativedelta import relativedelta
from encrypted_model_fields.fields import (
    EncryptedCharField,
    EncryptedDecimalField,
    validate_fernet_key
)

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
    limite = EncryptedDecimalField(max_digits=15, decimal_places=2)
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
        unique=False
    )

    descricao = models.CharField(max_length=50)

    def __str__(self) -> str:
        return str(self.descricao)


# ======================================================
# FORMA DE PAGAMENTO
# ======================================================

class FormaPagamento(models.Model):
    DEBITO = 'DEBITO'
    CREDITO = 'CREDITO'
    DINHEIRO = 'DINHEIRO'
    PIX = 'PIX'

    CODIGO_CHOICES = (
        (DEBITO, 'Débito (à vista)'),
        (CREDITO, 'Crédito (a prazo)'),
        (DINHEIRO, 'Dinheiro'),
        (PIX, 'Pix'),
    )

    codigo = models.CharField(
        max_length=20,
        choices=CODIGO_CHOICES,
        unique=True
    )

    descricao = models.CharField(max_length=100)

    exige_cartao = models.BooleanField(
        default=False,
        help_text="Se marcado, esta forma de pagamento exige cartão."
    )

    def __str__(self) -> str:
        return str(self.descricao)


# ======================================================
# CARTÃO
# ======================================================

class Cartao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, verbose_name="Nome do cartão", default="Novo Cartão")
    limite = EncryptedDecimalField(max_digits=15, decimal_places=2, default=0)
    dia_fechamento = models.PositiveIntegerField(default=1)

    is_credito = models.BooleanField(
        default=True,
        help_text="Cartão de crédito (gera débito contábil)"
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

    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
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

    @property
    def valor_decimal(self):
        try:
            return Decimal(str(self.valor)) if self.valor is not None else Decimal('0')
        except:
            return Decimal('0')

    def get_html_url(self):
        url = reverse('cal:transacao_editar', args=[self.id])
        valor_formatado = f"R$ {self.valor_decimal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'

    def get_absolute_url(self):
        return reverse('cal:transacao_editar', args=[self.id])
