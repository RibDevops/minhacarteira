from rest_framework import viewsets, permissions
from ..models import Transacao, Categoria, Cartao, Tipo, MetaCategoria
from .serializers import (
    TransacaoSerializer, CategoriaSerializer, CartaoSerializer, TipoSerializer,
    MetaCategoriaSerializer,
)


class TipoViewSet(viewsets.ReadOnlyModelViewSet):
    """Tipo (Crédito/Débito) é global do sistema, não pertence a um usuário."""
    queryset = Tipo.objects.all()
    serializer_class = TipoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        return Categoria.get_for_user(self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartaoViewSet(viewsets.ModelViewSet):
    serializer_class = CartaoSerializer

    def get_queryset(self):
        return Cartao.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MetaCategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = MetaCategoriaSerializer

    def get_queryset(self):
        qs = MetaCategoria.objects.filter(user=self.request.user).select_related('categoria')
        mes = self.request.query_params.get('mes')
        ano = self.request.query_params.get('ano')
        if mes and ano:
            qs = qs.filter(mes=mes, ano=ano)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransacaoViewSet(viewsets.ModelViewSet):
    serializer_class = TransacaoSerializer

    def get_queryset(self):
        qs = Transacao.objects.filter(user=self.request.user).select_related(
            'tipo', 'categoria', 'cartao'
        ).order_by('-data')
        mes = self.request.query_params.get('mes')
        ano = self.request.query_params.get('ano')
        if mes and ano:
            qs = qs.filter(data__month=mes, data__year=ano)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
