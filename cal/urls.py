from django.urls import path
from . import views
from cal.views.views_cal import *
from cal.views.views_login import *
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as login_django
from cal.views.views_login import login_view



app_name = 'cal'

urlpatterns = [
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('', views.home, name='home'),
    # path('', views.CalendarView.as_view(), name='calendar'),
    path('transacao/nova/', views.transacao_view, name='transacao_nova'),
    path('transacoes/', views.listar_transacoes, name='listar_transacoes'),
    path('transacao/excluir/<int:pk>/', views.excluir_transacao, name='transacao_excluir'),
    # path('transacao/editar/<int:transacao_id>/', views.transacao_editar, name='transacao_editar'),
    path('transacao/editar/<int:pk>/', views.transacao_editar, name='transacao_editar'),

 


    path('register/', register_view, name='register'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('login/', login_view, name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    # path('login/', views.login, name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),

]



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


