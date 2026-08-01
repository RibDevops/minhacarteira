from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    TransacaoViewSet, CategoriaViewSet, CartaoViewSet, TipoViewSet,
    MetaCategoriaViewSet, RecorrenciaViewSet, DashboardAPIView
)

router = DefaultRouter()
router.register('transacoes', TransacaoViewSet, basename='api-transacoes')
router.register('categorias', CategoriaViewSet, basename='api-categorias')
router.register('cartoes', CartaoViewSet, basename='api-cartoes')
router.register('tipos', TipoViewSet, basename='api-tipos')
router.register('metas', MetaCategoriaViewSet, basename='api-metas')
router.register('recorrencias', RecorrenciaViewSet, basename='api-recorrencias')

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api-token-auth'),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    path('', include(router.urls)),
]
