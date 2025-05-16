from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.urls import reverse

class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        abstract = True


class Tipo(models.Model):
    descricao = models.CharField(max_length=200, verbose_name="Descrição do tipo")
    is_credito = models.BooleanField(default=False, verbose_name="É crédito?")

    def __str__(self):
        return f"{'Crédito' if self.is_credito else 'Débito'} - {self.descricao}"

class Transacao(BaseModel):
    tipo = models.ForeignKey(Tipo, on_delete=models.PROTECT, verbose_name="Tipo da transação")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data da transação (use a data de vencimento do proximo mês, se for no cartão de crédito")
    parcelas = models.IntegerField(null=True, blank=True, verbose_name="Quantidade de parcelas")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data da última parcela")

    def __str__(self):
        return f"{self.titulo} - R$ {self.valor} ({self.tipo})"
    
    # def get_html_url(self):
    #     url = reverse('transacao_update', args=[self.id])
    #     valor_formatado = f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #     descricao = f"{self.titulo} - {valor_formatado}"
    #     # return f'<a href="{url}">{descricao}</a>'
    #     return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'
    def get_html_url(self):
        url = reverse('cal:transacao_update', args=[self.id])  # isso cria o link para editar
        valor_formatado = f"R$ {self.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        descricao = f"{self.titulo} - {valor_formatado}"
        return f'<a href="{url}"><strong>{self.titulo}</strong><br><small>{valor_formatado}</small></a>'

    def get_absolute_url(self):
        return reverse('cal:transacao_update', args=[self.id])

