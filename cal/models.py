from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from encrypted_model_fields.fields import EncryptedCharField, validate_fernet_key
from encrypted_model_fields.fields import EncryptedDecimalField
from encrypted_model_fields.fields import EncryptedCharField  # ou mantenha o EncryptedCharField do pacote, se quiser
from encrypted_model_fields.fields import EncryptedCharField

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        abstract = True

from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        # return f"{'Crédito' if self.is_credito else 'Débito'} - {self.descricao}"
        return self.descricao

from decimal import Decimal

from encrypted_model_fields.fields import EncryptedCharField, EncryptedDecimalField

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
    
    # ... (mantenha o resto da implementação igual)

    
class Cartao(models.Model):
    cartao = models.CharField(max_length=100, verbose_name="Nome do cartão")

    def __str__(self):
        return self.nome

class Transacao(BaseModel):
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT, verbose_name="Tipo da transação")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    # titulo = EncryptedCharField(models.CharField(max_length=200, verbose_name="Título"))
    titulo = EncryptedCharField(max_length=200, verbose_name="Título")

    valor = EncryptedDecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor total")
    
    # valor = EncryptedDecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(verbose_name="Data da transação")
    parcelas = models.IntegerField(null=True, blank=True, verbose_name="Quantidade de parcelas")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data da última parcela")

    def get_html_url(self):
        url = reverse('cal:transacao_update', args=[self.id])  # isso cria o link para editar
        valor_formatado = f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        descricao = f"{self.titulo} - {valor_formatado}"
        return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'

    def get_absolute_url(self):
        return reverse('cal:transacao_update', args=[self.id])

