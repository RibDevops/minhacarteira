# ✅ DEPOIS - Organizado
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

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        abstract = True

class Categoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class MetaCategoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    limite = models.DecimalField(max_digits=15, decimal_places=2)
    mes = models.PositiveIntegerField()  # 1-12
    ano = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['user', 'categoria', 'mes', 'ano']
        ordering = ['ano', 'mes', 'categoria']
    
    def __str__(self):
        return f"{self.categoria} - {self.mes}/{self.ano}: R$ {self.limite}"


class Tipo(models.Model):
    descricao = models.CharField(max_length=200, verbose_name="Descrição do tipo")
    categoria = models.CharField(max_length=200, verbose_name="Categoria")
    is_credito = models.BooleanField(default=False, verbose_name="É crédito?")
    dia_fechamento = models.PositiveIntegerField(default=0, help_text="Para cartões: dia que a fatura fecha. 0 se não for cartão.")
    adia_mes = models.BooleanField(default=False, help_text="Se marcado, transações após o fechamento vão para o mês subsequente.")

    def __str__(self):
        # return f"{'Crédito' if self.is_credito else 'Débito'} - {self.descricao}"
        return self.descricao

class EncryptedDecimalField(models.Field):
    def __init__(self, *args, max_digits=None, decimal_places=None, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.fernet = validate_fernet_key(settings.FERNET_SECRET_KEY)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        # Força o Django a criar uma coluna VARCHAR no banco
        return 'varchar(255)'
    
    def get_internal_type(self):
        return "CharField"
    
    
class Cartao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cartao = models.CharField(max_length=100, verbose_name="Nome do cartão")
    limite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Limite do cartão")
    dia_fechamento = models.PositiveIntegerField(default=1, verbose_name="Dia de fechamento")

    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"

    def __str__(self):
        return self.cartao


class Transacao(BaseModel):
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT, verbose_name="Tipo da transação")
    cartao = models.ForeignKey(Cartao, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cartão utilizado")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    # titulo = EncryptedCharField(models.CharField(max_length=200, verbose_name="Título"))
    titulo = EncryptedCharField(max_length=200, verbose_name="Título")

    valor = EncryptedDecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor total")
    
    # valor = EncryptedDecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(verbose_name="Data da transação")
    parcelas = models.IntegerField(null=True, blank=True, verbose_name="Quantidade de parcelas")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data da última parcela")
    observacoes = EncryptedCharField(max_length=500, null=True, blank=True, verbose_name="Observações (Criptografadas)")

    def get_html_url(self):
        url = reverse('cal:transacao_update', args=[self.id])  # isso cria o link para editar
        valor_formatado = f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        descricao = f"{self.titulo} - {valor_formatado}"
        return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'

    def get_absolute_url(self):
        return reverse('cal:transacao_update', args=[self.id])

