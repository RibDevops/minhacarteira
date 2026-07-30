from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import TransacaoViewSet, CategoriaViewSet, CartaoViewSet, TipoViewSet, MetaCategoriaViewSet

router = DefaultRouter()
router.register('transacoes', TransacaoViewSet, basename='api-transacoes')
router.register('categorias', CategoriaViewSet, basename='api-categorias')
router.register('cartoes', CartaoViewSet, basename='api-cartoes')
router.register('tipos', TipoViewSet, basename='api-tipos')
router.register('metas', MetaCategoriaViewSet, basename='api-metas')

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api-token-auth'),
    path('', include(router.urls)),
]
