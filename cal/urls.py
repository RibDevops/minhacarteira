from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from cal.views import views_categoria, views_dashboard, views_recorrencia
from cal.views import views_tipo, views_user, views_meta
from cal.views.views_cal import CalendarView
from cal.views.views_login import register_view
from cal.views.views_transacao import transacao_rapida, transacoes_mes_view, excluir_transacao_lista
from cal.views.views_cartao import cartao_alternar_status, resumo_categoria_view
from cal.views.views_export import exportar_transacoes_csv
from cal.views.views_cbv import (
    TransacaoListView, TransacaoCreateView, TransacaoUpdateView, TransacaoDeleteView,
    CartaoListView, CartaoCreateView, CartaoUpdateView, CartaoDeleteView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    MetaCategoriaListView, MetaCategoriaCreateView, MetaCategoriaUpdateView, MetaCategoriaDeleteView,
    RecorrenciaListView, RecorrenciaCreateView, RecorrenciaUpdateView, RecorrenciaDeleteView, RecorrenciaToggleStatusView,
    TipoListView, TipoCreateView, TipoUpdateView, TipoDeleteView,
)

app_name = 'cal'

urlpatterns = [
    path('', views_user.home, name='home'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('calendar/', CalendarView.as_view(), name='calendar'),

    # Transações
    path('transacoes/', TransacaoListView.as_view(), name='listar_transacoes'),
    path('transacao/nova/', TransacaoCreateView.as_view(), name='transacao_nova'),
    path('transacao/rapida/', transacao_rapida, name='transacao_rapida'),
    path('transacao/editar/<int:pk>/', TransacaoUpdateView.as_view(), name='transacao_editar'),
    path('transacao/excluir/<int:pk>/', TransacaoDeleteView.as_view(), name='transacao_excluir'),
    path('excluir_transacao_lista/<int:pk>/', excluir_transacao_lista, name='excluir_transacao_lista'),
    path('transacoes-mes/', transacoes_mes_view, name='transacoes_mes'),
    path('transacoes/exportar/', exportar_transacoes_csv, name='exportar_transacoes_csv'),
    path('resumo-categoria/', resumo_categoria_view, name='resumo_categoria'),
    path('transacao/<int:pk>/editar/', TransacaoUpdateView.as_view(), name='transacao_update'),

    # Cartões
    path('cartoes/resumo/', CartaoListView.as_view(), name='cartoes_resumo'),
    path('cartao/novo/', CartaoCreateView.as_view(), name='cartao_novo'),
    path('cartao/editar/<int:pk>/', CartaoUpdateView.as_view(), name='cartao_editar'),
    path('cartao/excluir/<int:pk>/', CartaoDeleteView.as_view(), name='cartao_excluir'),
    path('cartao/alternar-status/<int:pk>/', cartao_alternar_status, name='cartao_alternar_status'),

    # Registro (login e logout vêm de django.contrib.auth.urls no core/urls.py)
    path('register/', register_view, name='register'),

    # Tipos
    path('tipos/', TipoListView.as_view(), name='tipo_list'),
    path('tipos/novo/', TipoCreateView.as_view(), name='tipo_create'),
    path('tipos/<int:pk>/editar/', TipoUpdateView.as_view(), name='tipo_update'),
    path('tipos/<int:pk>/excluir/', TipoDeleteView.as_view(), name='tipo_delete'),

    # Categorias
    path('categorias/', CategoriaListView.as_view(), name='categorias'),
    path('categorias/nova/', CategoriaCreateView.as_view(), name='categoria_nova'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/excluir/', CategoriaDeleteView.as_view(), name='categoria_delete'),

    # Usuários (keep existing FBVs for now - staff only)
    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views_user.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views_user.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views_user.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar_senha/<int:user_id>/', views_user.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar_usuario/<int:user_id>/', views_user.desativar_usuario, name='desativar_usuario'),

    # Recorrências
    path('recorrencias/', RecorrenciaListView.as_view(), name='recorrencia_listar'),
    path('recorrencia/nova/', RecorrenciaCreateView.as_view(), name='recorrencia_nova'),
    path('recorrencia/<int:pk>/editar/', RecorrenciaUpdateView.as_view(), name='recorrencia_editar'),
    path('recorrencia/<int:pk>/alternar-status/', RecorrenciaToggleStatusView.as_view(), name='recorrencia_alternar_status'),
    path('recorrencia/<int:pk>/excluir/', RecorrenciaDeleteView.as_view(), name='recorrencia_excluir'),

    # Páginas públicas
    path('manual/', views_user.manual_publico, name='manual_publico'),
    path('contato/', views_user.contato, name='contato'),
    path('perfil/', views_user.perfil_usuario, name='perfil'),

    # Metas
    path('metas/', MetaCategoriaListView.as_view(), name='metas_categoria'),
    path('metas/nova/', MetaCategoriaCreateView.as_view(), name='meta_criar'),
    path('metas/<int:pk>/editar/', MetaCategoriaUpdateView.as_view(), name='meta_editar'),
    path('metas/<int:pk>/excluir/', MetaCategoriaDeleteView.as_view(), name='meta_excluir'),

    # Reset de senha nativo
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html',
        email_template_name='usuarios/password_reset_email.html',
        success_url=reverse_lazy('cal:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html',
        success_url=reverse_lazy('cal:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]
