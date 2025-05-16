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



# from django.db import models
# from django.contrib.auth.models import User

# class BaseModel(models.Model):
#     id = models.AutoField(primary_key=True)
#     fk_user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário")
#     create_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         abstract = True

# class Transacao(BaseModel):
#     CATEGORIAS = [
#         ('CREDITO', 'Crédito'),
#         ('DEBITO', 'Débito'),
#         ('SALARIO', 'Salário'),
#         ('EMPRESTIMO', 'Empréstimo'),
#         ('CRIPTO', 'Criptomoeda'),
#     ]

#     titulo = models.CharField(max_length=200, verbose_name="Descrição")
#     valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
#     data = models.DateField(verbose_name="Data da transação")
#     categoria = models.CharField(max_length=20, choices=CATEGORIAS)
#     recorrente = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.get_categoria_display()} - {self.titulo} ({self.valor})'

#     @property
#     def get_html_url(self):
#         from django.urls import reverse
#         url = reverse('cal:transacao_editar', args=(self.id,))
#         return f'<a href="{url}" class="event">{self.titulo}</a>'

# from django.db import models
# from django.urls import reverse
# from django.contrib.auth.models import User

# class BaseModel(models.Model):
#     """
#     Modelo base com campos comuns a serem herdados por outros modelos.
#     """
#     id = models.AutoField(primary_key=True)
#     fk_user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Usuário", default=1)
#     create_at = models.DateTimeField(auto_now_add=True, null=True)

#     class Meta:
#         abstract = True


# class Emprestimo(BaseModel):#Event
#     banco = models.CharField(max_length=200, verbose_name="Nome da compra:",)
#     valor_emp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da compra:")
#     quantidade_parcelas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da compra:")

#     start_time = models.DateField(
#         verbose_name="Data de início:",
#         # auto_now_add=False,  # Define como data atual apenas na criação
#         null=True,           # Permite valores nulos
#         blank=True           # Permite campo em branco no formulário
#     )
#     end_time = models.DateField(
#         verbose_name="Data de término",
#         # auto_now_add=False,  # Define como data atual apenas na criação
#         null=True,           # Permite valores nulos
#         blank=True           # Permite campo em branco no formulário
#     )

#     # start_time = models.DateField()  # Armazena apenas data
#     # end_time = models.DateField()    # Armazena apenas data

#     def __str__(self):
#         return self.banco

#     class Meta:
#         verbose_name = 'Caixa'
#         verbose_name_plural = 'Caixas'


# class Credito(BaseModel):#Event
#     title = models.CharField(max_length=200, verbose_name="Nome da compra:",)
#     valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da compra:")
#     # description = models.TextField()
#     # start_time = models.DateTimeField()
#     # end_time = models.DateTimeField()
#     start_time = models.DateField(
#         verbose_name="Data da compra:",
#         # auto_now_add=False,  # Define como data atual apenas na criação
#         null=True,           # Permite valores nulos
#         blank=True           # Permite campo em branco no formulário
#     )
#     # end_time = models.DateField(
#     #     verbose_name="Data de início",
#     #     # auto_now_add=False,  # Define como data atual apenas na criação
#     #     null=True,           # Permite valores nulos
#     #     blank=True           # Permite campo em branco no formulário
#     # )

#     # start_time = models.DateField()  # Armazena apenas data
#     # end_time = models.DateField()    # Armazena apenas data

#     @property
#     def get_html_url(self):
#         url = reverse('cal:event_edit', args=(self.id,))
#         # return f'<a href="{url}"> {self.title} </a>'
#         return f'<a href="{url}" class="event">{self.title}</a>'

# class Debito(BaseModel):#Event
#     title = models.CharField(max_length=200, verbose_name="Nome da compra:",)
#     valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor da compra:")
#     # description = models.TextField()
#     # start_time = models.DateTimeField()
#     # end_time = models.DateTimeField()
#     start_time = models.DateField(
#         verbose_name="Data da compra:",
#         # auto_now_add=False,  # Define como data atual apenas na criação
#         null=True,           # Permite valores nulos
#         blank=True           # Permite campo em branco no formulário
#     )
#     # end_time = models.DateField(
#     #     verbose_name="Data de início",
#     #     # auto_now_add=False,  # Define como data atual apenas na criação
#     #     null=True,           # Permite valores nulos
#     #     blank=True           # Permite campo em branco no formulário
#     # )

#     # start_time = models.DateField()  # Armazena apenas data
#     # end_time = models.DateField()    # Armazena apenas data

#     @property
#     def get_html_url(self):
#         url = reverse('cal:event_edit', args=(self.id,))
#         # return f'<a href="{url}"> {self.title} </a>'
#         return f'<a href="{url}" class="event">{self.title}</a>'