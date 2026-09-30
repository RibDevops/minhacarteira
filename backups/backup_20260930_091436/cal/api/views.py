from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from ..models import Transacao, Categoria, Cartao, Tipo, MetaCategoria, Recorrencia
from ..services import saldos_do_mes, detalhe_mensal_ano, resumo_categorias_e_tipos
from .serializers import (
    TransacaoSerializer, CategoriaSerializer, CartaoSerializer, TipoSerializer,
    MetaCategoriaSerializer, RecorrenciaSerializer
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


class RecorrenciaViewSet(viewsets.ModelViewSet):
    serializer_class = RecorrenciaSerializer

    def get_queryset(self):
        return Recorrencia.objects.filter(user=self.request.user).select_related(
            'tipo', 'categoria', 'cartao'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DashboardAPIView(APIView):
    """
    Endpoint agregado para o app mobile.
    Retorna saldos, dados de gráficos e metas do mês atual.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hoje = timezone.now()
        mes = int(request.query_params.get('mes', hoje.month))
        ano = int(request.query_params.get('ano', hoje.year))

        # 1. Saldos e Transações
        dados_saldos = saldos_do_mes(request.user, ano, mes)

        # 2. Resumo para Gráficos
        resumo = resumo_categorias_e_tipos(dados_saldos['transacoes'])

        # 3. Metas
        metas = MetaCategoria.objects.filter(user=request.user, mes=mes, ano=ano).select_related('categoria')
        dados_metas = []
        for m in metas:
            gasto_cat = Transacao.objects.filter(
                user=request.user,
                categoria=m.categoria,
                data__month=mes,
                data__year=ano,
                tipo__codigo='D'
            ).aggregate(total=Sum('valor'))['total'] or 0

            dados_metas.append({
                'categoria': m.categoria.nome,
                'limite': float(m.limite),
                'gasto': float(gasto_cat),
                'percentual': float((gasto_cat / m.limite) * 100) if m.limite > 0 else 0
            })

        return Response({
            'mes': mes,
            'ano': ano,
            'saldos': {
                'creditos': float(dados_saldos['creditos']),
                'debitos': float(dados_saldos['debitos']),
                'saldo': float(dados_saldos['saldo']),
            },
            'graficos': {
                'categorias': {
                    'labels': resumo['cat_labels'],
                    'valores': resumo['cat_valores'],
                },
                'tipos': {
                    'labels': resumo['tipo_labels'],
                    'valores': resumo['tipo_valores'],
                }
            },
            'metas': dados_metas
        })
