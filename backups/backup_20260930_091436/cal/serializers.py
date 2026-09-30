from rest_framework import serializers
from django.utils import timezone
from .models import Transacao, Categoria, Cartao, MetaCategoria, Recorrencia

class TransacaoSerializer(serializers.ModelSerializer):
    # O uuid e updated_at são gerenciados pelo servidor/banco
    uuid = serializers.UUIDField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transacao
        fields = '__all__' # Ou liste os campos específicos que você usa

    def update(self, instance, validated_data):
        # Sempre que houver um update, atualizamos o timestamp
        instance.updated_at = timezone.now()
        return super().update(instance, validated_data)

class CategoriaSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Categoria
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_at = timezone.now()
        return super().update(instance, validated_data)

# Repita o padrão para Cartao, MetaCategoria e Recorrencia se necessário
