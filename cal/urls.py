from django import views
from django.urls import path
from cal.views.views_cal import CalendarView
from cal.views.views_user import *
from cal.views.views_transacao import *
from cal.views.views_login import register_view, LogoutView
from django.contrib.auth import views as auth_views

from django.urls import path
from .views import views_tipo
from .views import views_user

from django.urls import path


app_name = 'cal'

urlpatterns = [
    path('', views_user.home, name='home'),
    
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


    path('usuarios/', views_user.listar_usuarios, name='listar_usuarios'),
    path('usuarios/adicionar/', views_user.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<int:user_id>/', views_user.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views_user.excluir_usuario, name='excluir_usuario'),
    path('usuarios/resetar_senha/<int:user_id>/', views_user.resetar_senha, name='resetar_senha'),
    path('usuarios/desativar_usuario/<int:user_id>/', views_user.desativar_usuario, name='desativar_usuario'),

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


