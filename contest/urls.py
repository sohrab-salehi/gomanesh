from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('team/creation', views.team_creation, name='team_creation'),
    # path('team/invitation', views.invitation, name='invitation'),
    path('team/management', views.team_management, name='team_management'),
]
