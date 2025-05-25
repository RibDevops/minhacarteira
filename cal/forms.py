from django import forms
from django.forms import ModelForm, DateInput, Select
from .models import Transacao
from django.forms import ModelForm
from django.forms.widgets import DateInput
from datetime import date
from .models import Transacao

from django import forms
from cal.models import Categoria

from .models import MetaCategoria


from datetime import date


from django import forms
from .models import MetaCategoria
from datetime import date

from django import forms
from .models import MetaCategoria

import calendar
from datetime import date
from django import forms
from .models import MetaCategoria


import calendar
from datetime import date
from django import forms
from .models import MetaCategoria


from django import forms
from .models import MetaCategoria
from datetime import date
import calendar
from django.forms import NumberInput

from django import forms
from .models import MetaCategoria, Categoria
from datetime import date
import calendar

from django import forms
from .models import MetaCategoria, Categoria
from datetime import date
import calendar

class MetaCategoriaForm(forms.ModelForm):
    mes_ano = forms.ChoiceField(
        label="Mês/Ano",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Adicione explicitamente o campo limite
    limite = forms.DecimalField(
        label="Valor Limite",
        max_digits=15,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0,00'
        })
    )

    class Meta:
        model = MetaCategoria
        fields = ['categoria', 'limite']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Não remova mais o campo limite
        # self.fields['categoria'].queryset = Categoria.objects.filter(user=self.user)
        self.fields['categoria'].queryset = Categoria.objects.all()  # Antes era .filter(user=self.user)
        self.fields['mes_ano'].choices = self.get_mes_ano_choices()

        # Se estiver editando, preencha o valor inicial
        if self.instance and self.instance.pk:
            self.fields['limite'].initial = self.instance.limite

    # ... restante do código ...

    def get_mes_ano_choices(self):
        """Gera opções de mês/ano para os próximos 5 anos"""
        hoje = date.today()
        opcoes = []
        
        for ano in range(hoje.year, hoje.year + 6):
            for mes in range(1, 13):
                if ano == hoje.year and mes < hoje.month:
                    continue  # Pula meses passados do ano atual
                
                nome_mes = calendar.month_name[mes]
                valor = f"{mes:02d}-{ano}"
                label = f"{nome_mes}/{ano}"
                opcoes.append((valor, label))
        
        return opcoes

    def clean(self):
        cleaned_data = super().clean()
        mes_ano = cleaned_data.get('mes_ano')
        
        if mes_ano:
            mes, ano = map(int, mes_ano.split('-'))
            cleaned_data['mes'] = mes
            cleaned_data['ano'] = ano
            
            # Verifica se meta já existe
            if self.instance.pk is None:  # Apenas para novas metas
                existe = MetaCategoria.objects.filter(
                    user=self.user,
                    categoria=cleaned_data.get('categoria'),
                    mes=mes,
                    ano=ano
                ).exists()
                
                if existe:
                    raise forms.ValidationError("Já existe uma meta para esta categoria no mês/ano selecionado.")
        
        return cleaned_data

        # Se sua model Categoria tem um campo `user`, descomente:
        # if user:
        #     self.fields['categoria'].queryset = self.fields['categoria'].queryset.filter(user=user)

        

        # Se quiser filtrar categorias por usuário, só se Categoria tiver campo `user`
        # self.fields['categoria'].queryset = self.fields['categoria'].queryset.filter(user=user)

        # Se precisar, filtra categorias só do usuário
        # if user:
        #     self.fields['categoria'].queryset = self.fields['categoria'].queryset.filter(user=user)




# from .models import MetaCategoria

# class MetaCategoriaForm(forms.ModelForm):
#     class Meta:
#         model = MetaCategoria
#         fields = ['categoria', 'limite', 'mes', 'ano']
#         widgets = {
#             'categoria': forms.Select(attrs={'class': 'form-control'}),
#             'limite': forms.NumberInput(attrs={'class': 'form-control'}),
#             'mes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
#             'ano': forms.NumberInput(attrs={'class': 'form-control'}),
#         }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'})
        }


from django import forms
from django.forms import ModelForm, DateInput
from .models import Transacao
from datetime import date

class TransacaoForm(ModelForm):
    class Meta:
        model = Transacao
        fields = ['tipo', 'titulo', 'categoria', 'valor', 'data', 'parcelas']
        widgets = {
            'data': DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'  # Formato obrigatório para input date
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configura o valor inicial da data corretamente
        if self.instance.pk and self.instance.data:
            self.initial['data'] = self.instance.data.strftime('%Y-%m-%d')
        elif not self.instance.pk:
            self.initial['data'] = date.today().strftime('%Y-%m-%d')
        
        # Configurações dos outros campos
        self.fields['titulo'].widget.attrs.update({
            'placeholder': 'ex: Mercado, Salário, Bitcoin',
            'class': 'form-control'
        })
        
        for field in ['valor', 'tipo', 'parcelas', 'categoria']:
            self.fields[field].widget.attrs['class'] = 'form-control'





from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirme a Senha')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError("As senhas não coincidem.")
        return password2

# cal/forms.py
from django import forms
from .models import Tipo

class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['descricao', 'is_credito']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Salário, Compra'}),
            'is_credito': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'descricao': 'Descrição',
            'is_credito': 'É crédito?',
        }



# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Endereço de email")
    first_name = forms.CharField(label="Primeiro nome", required=True)
    last_name = forms.CharField(label="Último nome", required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Nome', required=False)
    last_name = forms.CharField(label='Sobrenome', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class UsuarioUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UsuarioPasswordResetForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nova Senha")

    class Meta:
        model = User
        fields = []











# from django.forms import ModelForm, DateInput, Select
# from .models import Transacao
# from django import forms
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError

# class TransacaoForm(ModelForm):
#     class Meta:
#         model = Transacao
#         fields = ['titulo', 'valor', 'data', 'categoria', 'recorrente']
#         widgets = {
#             'data': DateInput(attrs={'type': 'date'}),
#             'categoria': Select(),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['titulo'].widget.attrs['placeholder'] = 'ex: Mercado, Salário, Bitcoin'
#         self.fields['titulo'].widget.attrs['class'] = 'form-control'
#         self.fields['valor'].widget.attrs['class'] = 'form-control'
#         self.fields['data'].widget.attrs['class'] = 'form-control'
#         self.fields['categoria'].widget.attrs['class'] = 'form-control'
        

# # cal/forms.py

# from django import forms
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError

# class UserRegisterForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput, label='Senha')
#     password2 = forms.CharField(widget=forms.PasswordInput, label='Confirme a Senha')

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name']

#     def clean_password2(self):
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password and password2 and password != password2:
#             raise ValidationError("As senhas não coincidem.")
#         return password2




# # from django.forms import ModelForm, DateInput
# # from cal.models import Event

# # # class EventForm(ModelForm):
# # #   class Meta:
# # #     model = Event
# # #     # datetime-local is a HTML5 input type, format to make date time show on fields
# # #     widgets = {
# # #       'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
# # #       'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
# # #     }
# # #     fields = '__all__'

# # #   def __init__(self, *args, **kwargs):
# # #     super(EventForm, self).__init__(*args, **kwargs)
# # #     # input_formats parses HTML5 datetime-local input to datetime field
# # #     self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
# # #     self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)


# # class EventForm(ModelForm):
# #     class Meta:
# #         model = Event
# #         widgets = {
# #             'start_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),  # Somente data
# #             # 'end_time': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),    # Somente data
# #         }
# #         fields = '__all__'

# #     def __init__(self, *args, **kwargs):
# #         super(EventForm, self).__init__(*args, **kwargs)
# #         self.fields['title'].widget.attrs['placeholder'] = 'ex: Mercado BigBox'
# #         # Remove os input_formats com hora, pois agora só queremos a data
# #         self.fields['start_time'].input_formats = ('%Y-%m-%d',)  # Formato ISO para data
# #         # self.fields['end_time'].input_formats = ('%Y-%m-%d',)   # Formato ISO para data

# #         self.fields['valor'].widget.attrs['class'] = 'form-control'



# # forms.py


