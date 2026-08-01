from rest_framework import serializers
from ..models import Transacao, Categoria, Cartao, Tipo, MetaCategoria


class TipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo
        fields = ['id', 'codigo', 'descricao']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'is_global']
        read_only_fields = ['is_global']


class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartao
        fields = ['id', 'nome', 'limite', 'is_active']


class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = [
            'id', 'tipo', 'categoria', 'cartao', 'titulo', 'valor',
            'data', 'parcelas', 'data_fim', 'observacoes', 'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_categoria(self, categoria):
        # Mesma regra de segurança já usada nas views web: nunca aceitar
        # categoria de outro usuário.
        request = self.context['request']
        if categoria and categoria.user_id not in (None, request.user.id):
            raise serializers.ValidationError("Categoria inválida.")
        return categoria

    def validate_cartao(self, cartao):
        request = self.context['request']
        if cartao and cartao.user_id != request.user.id:
            raise serializers.ValidationError("Cartão inválido.")
        return cartao


class MetaCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaCategoria
        fields = ['id', 'categoria', 'limite', 'mes', 'ano']

    def validate_categoria(self, categoria):
        request = self.context['request']
        if categoria.user_id not in (None, request.user.id):
            raise serializers.ValidationError("Categoria inválida.")
        return categoria
