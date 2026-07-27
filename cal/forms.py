from datetime import date
from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.widgets import DateInput

from .models import Categoria, MetaCategoria, Tipo, Transacao, Recorrencia, Cartao

class MetaCategoriaForm(forms.ModelForm):
    mes_ano = forms.ChoiceField(
        label="Mês/Ano",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    limite = forms.CharField(
        label="Valor Limite",
        required=True,
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
        self.fields['categoria'].queryset = Categoria.objects.filter(user=self.user)
        #self.fields['categoria'].queryset = Categoria.objects.all()  # Antes era .filter(user=self.user)
        self.fields['mes_ano'].choices = self.get_mes_ano_choices()

        # Se estiver editando, preencha o valor inicial
        if self.instance and self.instance.pk:
            self.fields['limite'].initial = self.instance.limite

    # ... restante do código ...

    def get_mes_ano_choices(self):
        """Gera opções de mês/ano para os próximos 5 anos em Português"""
        hoje = date.today()
        opcoes = []
        meses_pt = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        for ano in range(hoje.year, hoje.year + 6):
            for mes in range(1, 13):
                if ano == hoje.year and mes < hoje.month:
                    continue  # Pula meses passados do ano atual
                
                nome_mes = meses_pt[mes-1]
                valor = f"{mes:02d}-{ano}"
                label = f"{nome_mes}/{ano}"
                opcoes.append((valor, label))
        
        return opcoes

    def clean_limite(self):
        # Pega o valor diretamente do POST para evitar interferência da validação do campo
        valor = self.data.get('limite')
        
        if valor:
            # Remove qualquer caractere que não seja número, vírgula ou ponto
            import re
            valor_limpo = re.sub(r'[^\d,\.]', '', str(valor))
            
            # Normalização robusta para formato brasileiro (1.234,56)
            if ',' in valor_limpo:
                # Se tem vírgula, o que está antes (pontos) é milhar e deve sumir
                # O que está depois da vírgula é o decimal
                partes = valor_limpo.split(',')
                inteiro = partes[0].replace('.', '')
                decimal = partes[1][:2] if len(partes) > 1 else '00'
                if len(decimal) == 1: decimal += '0'
                valor_str = f"{inteiro}.{decimal}"
            else:
                # Sem vírgula, remove pontos de milhar
                valor_str = valor_limpo.replace('.', '')
                
            try:
                decimal_val = Decimal(valor_str)
                if decimal_val < 0:
                    raise forms.ValidationError("O valor não pode ser negativo.")
                return decimal_val
            except (InvalidOperation, ValueError):
                # Fallback final: apenas dígitos
                try:
                    apenas_digitos = re.sub(r'[^\d]', '', valor_limpo)
                    if len(apenas_digitos) > 2:
                        return Decimal(apenas_digitos[:-2] + '.' + apenas_digitos[-2:])
                    elif apenas_digitos:
                        return Decimal(apenas_digitos) / 100
                except:
                    pass
                raise forms.ValidationError("Informe um número válido (ex: 200,00).")
        return Decimal('0')
        
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

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'})
        }


class TransacaoForm(ModelForm):
    class Meta:
        model = Transacao
        fields = ['tipo', 'cartao', 'titulo', 'categoria', 'valor', 'data', 'parcelas', 'observacoes']
        widgets = {
            'data': DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'  # Formato obrigatório para input date
            ),
        }

    def clean_valor(self):
        """
        Aceita vírgula como separador decimal (formato brasileiro) num campo
        DecimalField que por padrão só aceita ponto. Antes essa conversão
        era feita só depois de form.is_valid() — o que fazia o form rejeitar
        '150,50' e nunca salvar via POST.html.
        """
        from decimal import Decimal, InvalidOperation
        raw = self.cleaned_data.get('valor')
        if raw in (None, ''):
            return raw
        try:
            return Decimal(str(raw).replace(',', '.'))
        except (InvalidOperation, ValueError):
            from django import forms
            raise forms.ValidationError("Informe um valor válido (ex: 150,50).")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
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

        if 'valor' in self.fields:
            self.fields['valor'].widget.attrs.update({
                'placeholder': 'Valor da parcela (ex: 100,00)',
                'class': 'form-control'
            })
            self.fields['valor'].help_text = "Informe o valor de cada parcela individualmente."
        
        for field in ['valor', 'tipo', 'parcelas', 'categoria', 'cartao', 'observacoes']:
            if field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'
        
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(user=user)
            self.fields['cartao'].queryset = Cartao.objects.filter(user=user)
            self.fields['tipo'].queryset = Tipo.objects.all()
            
            # Ajuste de exibição para simplificar Débito/Crédito
            self.fields['tipo'].label_from_instance = lambda obj: f"{'Crédito' if obj.codigo == 'C' else 'Débito'} - {obj.descricao}"


class RecorrenciaForm(ModelForm):
    valor = forms.CharField(
        label="Valor mensal",
        widget=forms.TextInput(attrs={'placeholder': '0,00'})
    )

    class Meta:
        model = Recorrencia
        fields = ['tipo', 'titulo', 'valor', 'categoria', 'cartao', 'dia_cobranca', 'data_inicio', 'data_fim', 'observacoes']
        widgets = {
            'data_inicio': DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'data_fim': DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.initial['data_inicio'] = date.today().strftime('%Y-%m-%d')
        elif self.instance.data_inicio:
            self.initial['data_inicio'] = self.instance.data_inicio.strftime('%Y-%m-%d')
        if self.instance.pk and self.instance.data_fim:
            self.initial['data_fim'] = self.instance.data_fim.strftime('%Y-%m-%d')

        self.fields['titulo'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ex: Netflix, Aluguel, Academia'})
        self.fields['valor'].widget.attrs.update({'class': 'form-control', 'placeholder': '0,00'})
        self.fields['dia_cobranca'].widget.attrs.update({'class': 'form-control', 'min': 1, 'max': 28})
        self.fields['observacoes'].widget.attrs.update({'class': 'form-control'})
        for field in ['tipo', 'categoria', 'cartao']:
            self.fields[field].widget.attrs['class'] = 'form-select'
        self.fields['categoria'].required = False
        self.fields['cartao'].required = False
        self.fields['data_fim'].required = False

        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(user=user)
            self.fields['cartao'].queryset = Cartao.objects.filter(user=user, is_active=True)
            self.fields['tipo'].queryset = Tipo.objects.all()
            self.fields['tipo'].label_from_instance = lambda obj: f"{'Crédito' if obj.codigo == 'C' else 'Débito'} - {obj.descricao}"

    def clean_valor(self):
        # O campo é um DecimalField padrão do Django, que só aceita ponto como
        # separador decimal. O resto do app usa vírgula (formato brasileiro),
        # então aceitamos os dois aqui pra não surpreender o usuário.
        valor = self.data.get('valor', '')
        valor_normalizado = str(valor).replace('.', '').replace(',', '.') if ',' in str(valor) else str(valor)
        try:
            valor_decimal = Decimal(valor_normalizado)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Informe um valor válido (ex: 39,90).")
        if valor_decimal <= 0:
            raise forms.ValidationError("O valor deve ser maior que zero.")
        return valor_decimal


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}), label='Senha')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirme a Senha'}), label='Confirme a Senha')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Endereço de email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Último nome'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise ValidationError("As senhas não coincidem.")
        # Aplica os validadores de senha do Django (AUTH_PASSWORD_VALIDATORS)
        if password:
            validate_password(password)
        return password2


class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['codigo', 'descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Entrada, Saída'}),
            'codigo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'codigo': 'Código Contábil',
            'descricao': 'Descrição',
        }


class CartaoForm(forms.ModelForm):
    limite = forms.DecimalField(
        label="Limite Total",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'})
    )
    dia_fechamento = forms.IntegerField(
        label="Dia de Fechamento",
        min_value=1,
        max_value=31,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'})
    )

    class Meta:
        model = Cartao
        fields = ['nome', 'limite', 'dia_fechamento', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Nubank, Visa...'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }





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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UsuarioPasswordResetForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nova Senha")

    class Meta:
        model = User
        fields = []

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            validate_password(password)
        return password