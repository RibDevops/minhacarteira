from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from cal.views import views_categoria, views_dashboard, views_recorrencia
from cal.views import views_tipo, views_user, views_meta
from cal.views.views_cal import CalendarView
from cal.views.views_login import register_view
from cal.views.views_transacao import (
    listar_transacoes, transacao_view, transacao_rapida, transacao_editar,
    excluir_transacao, excluir_transacao_lista, transacoes_mes_view,
    TransacaoUpdateView,
)
from cal.views.views_cartao import (
    cartao_novo, cartao_editar, cartao_excluir, cartao_alternar_status,
    cartoes_resumo_view, resumo_categoria_view,
)
from cal.views.views_export import exportar_transacoes_csv

app_name = 'cal'

urlpatterns = [
    path('', views_user.home, name='home'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    path('calendar/', CalendarView.as_view(), name='calendar'),

    # Transações
    path('transacoes/', listar_transacoes, name='listar_transacoes'),
    path('transacao/nova/', transacao_view, name='transacao_nova'),
    path('transacao/rapida/', transacao_rapida, name='transacao_rapida'),
    path('transacao/editar/<int:pk>/', transacao_editar, name='transacao_editar'),
    path('transacao/excluir/<int:pk>/', excluir_transacao, name='transacao_excluir'),
    path('excluir_transacao_lista/<int:pk>/', excluir_transacao_lista, name='excluir_transacao_lista'),
    path('transacoes-mes/', transacoes_mes_view, name='transacoes_mes'),
    path('transacoes/exportar/', exportar_transacoes_csv, name='exportar_transacoes_csv'),
    path('resumo-categoria/', resumo_categoria_view, name='resumo_categoria'),
    path('transacao/<int:pk>/editar/', TransacaoUpdateView.as_view(), name='transacao_update'),

    # Cartões
    path('cartoes/resumo/', cartoes_resumo_view, name='cartoes_resumo'),
    path('cartao/novo/', cartao_novo, name='cartao_novo'),
    path('cartao/editar/<int:pk>/', cartao_editar, name='cartao_editar'),
    path('cartao/excluir/<int:pk>/', cartao_excluir, name='cartao_excluir'),
    path('cartao/alternar-status/<int:pk>/', cartao_alternar_status, name='cartao_alternar_status'),

    # Registro (login e logout vêm de django.contrib.auth.urls no core/urls.py)
    path('register/', register_view, name='register'),

    # Tipos
    path('tipos/', views_tipo.tipo_list, name='tipo_list'),
    path('tipos/novo/', views_tipo.tipo_create, name='tipo_create'),
    path('tipos/<int:pk>/editar/', views_tipo.tipo_update, name='tipo_update'),
    path('tipos/<int:pk>/excluir/', views_tipo.tipo_delete, name='tipo_delete'),

    # Categorias
    path('categorias/', views_categoria.categoria_list, name='categorias'),
    path('categorias/nova/', views_categoria.categoria_nova, name='categoria_nova'),
    path('categorias/<int:pk>/editar/', views_categoria.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/excluir/', views_categoria.categoria_delete, name='categoria_delete'),

    # Usuários
    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views_user.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views_user.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views_user.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar_senha/<int:user_id>/', views_user.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar_usuario/<int:user_id>/', views_user.desativar_usuario, name='desativar_usuario'),

    # Recorrências
    path('recorrencias/', views_recorrencia.recorrencia_listar, name='recorrencia_listar'),
    path('recorrencia/nova/', views_recorrencia.recorrencia_nova, name='recorrencia_nova'),
    path('recorrencia/<int:pk>/editar/', views_recorrencia.recorrencia_editar, name='recorrencia_editar'),
    path('recorrencia/<int:pk>/alternar-status/', views_recorrencia.recorrencia_alternar_status, name='recorrencia_alternar_status'),
    path('recorrencia/<int:pk>/excluir/', views_recorrencia.recorrencia_excluir, name='recorrencia_excluir'),

    # Páginas públicas
    path('manual/', views_user.manual_publico, name='manual_publico'),
    path('contato/', views_user.contato, name='contato'),
    path('perfil/', views_user.perfil_usuario, name='perfil'),

    # Metas
    path('metas/', views_meta.metas_dashboard, name='metas_categoria'),
    path('metas/nova/', views_meta.meta_adicionar, name='meta_criar'),
    path('metas/<int:pk>/editar/', views_meta.meta_editar, name='meta_editar'),
    path('metas/<int:meta_id>/excluir/', views_meta.meta_excluir, name='meta_excluir'),

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
