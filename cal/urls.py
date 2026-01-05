from django import views
from django.urls import path
from cal.views import views_categoria, views_dashboard
from cal.views.views_cal import CalendarView
from cal.views.views_user import *
from cal.views.views_transacao import *
from cal.views.views_categoria import *
from cal.views.views_login import register_view, LogoutView
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import views_tipo
from .views import views_user
from .views import views_meta

from django.urls import path


app_name = 'cal'

urlpatterns = [
    path('', views_dashboard.dashboard, name='home'),
    path('dashboard/', views_dashboard.dashboard, name='dashboard'),
    
    # path('', CalendarView.as_view(), name='calendar'),
    path('calendar/', CalendarView.as_view(), name='calendar'),

    # Transações
    path('transacoes/', listar_transacoes, name='listar_transacoes'),
    path('transacao/nova/', transacao_view, name='transacao_nova'),
    path('transacao/editar/<int:pk>/', transacao_editar, name='transacao_editar'),
    path('transacao/excluir/<int:pk>/', excluir_transacao, name='transacao_excluir'),
    path('excluir_transacao_lista/<int:pk>/', excluir_transacao_lista, name='excluir_transacao_lista'),

    # Registro/Login/Logout
    path('register/', register_view, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),

    path('tipos/', views_tipo.tipo_list, name='tipo_list'),
    path('tipos/novo/', views_tipo.tipo_create, name='tipo_create'),
    path('tipos/<int:pk>/editar/', views_tipo.tipo_update, name='tipo_update'),
    path('tipos/<int:pk>/excluir/', views_tipo.tipo_delete, name='tipo_delete'),
    path('transacoes-mes/', transacoes_mes_view, name='transacoes_mes'),
    path("resumo-categoria/", resumo_categoria_view, name="resumo_categoria"),
    path('transacao/<int:pk>/editar/', TransacaoUpdateView.as_view(), name='transacao_update'),

    path('categorias/', views_categoria.categoria_list, name='categorias'),
    path('categorias/nova/', views_categoria.categoria_nova, name='categoria_nova'),
    path('categorias/<int:pk>/editar/', views_categoria.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/excluir/', views_categoria.categoria_delete, name='categoria_delete'),


    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views_user.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views_user.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views_user.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar_senha/<int:user_id>/', views_user.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar_usuario/<int:user_id>/', views_user.desativar_usuario, name='desativar_usuario'),

    path('contato/', views_user.contato, name='contato'),
    path('perfil/', views_user.perfil_usuario, name='perfil'),

    # Metas
    path('metas/', views_meta.metas_dashboard, name='metas_categoria'),
    path('metas/nova/', views_meta.meta_adicionar, name='meta_criar'),
    path('metas/<int:pk>/editar/', views_meta.meta_editar, name='meta_editar'),
    path('metas/<int:meta_id>/excluir/', views_meta.meta_excluir, name='meta_excluir'),

    # Reset de senha nativo
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset.html', email_template_name='usuarios/password_reset_email.html', success_url=reverse_lazy('cal:password_reset_done')), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html', success_url=reverse_lazy('cal:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
]






# from django.urls import path
# from . import views
# from cal.views.views_cal import *
# from cal.views.views_login import *
# from django.contrib.auth import views as auth_views
# from django.contrib.auth import login as login_django
# from cal.views.views_login import login_view



# app_name = 'cal'

# urlpatterns = [
#     path('calendar/', views.CalendarView.as_view(), name='calendar'),
#     path('', views.home, name='home'),
#     # path('', views.CalendarView.as_view(), name='calendar'),
#     path('transacao/nova/', views.transacao_view, name='transacao_nova'),
#     path('transacoes/', views.listar_transacoes, name='listar_transacoes'),
#     path('transacao/excluir/<int:pk>/', views.excluir_transacao, name='transacao_excluir'),
#     # path('transacao/editar/<int:transacao_id>/', views.transacao_editar, name='transacao_editar'),
#     path('transacao/editar/<int:pk>/', views.transacao_editar, name='transacao_editar'),

 


#     path('register/', register_view, name='register'),
#     # path('login/', auth_views.LoginView.as_view(), name='login'),
#     # path('login/', login_view, name='login'),
#     path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
#     # path('login/', views.login, name='login'),
#     # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
#     # path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
#     path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),

# ]



# from django.urls import path, re_path
# from . import views

# app_name = 'cal'

# urlpatterns = [
#     path('', views.home, name='home'),

#     path('index/', views.index, name='index'),
#     path('calendar/', views.CalendarView.as_view(), name='calendar'),
#     path('event/new/', views.event, name='event_new'),
#     path('eventos/', views.listar_eventos, name='listar_eventos'),
#     path('eventos/excluir/<int:event_id>/', views.excluir_evento, name='excluir_evento'),

#     re_path(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),
# ]


