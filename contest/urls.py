from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.login, {'template_name': 'login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('invitation/', views.invitation_page, name='invitation'),
    path('team/creation', views.team_creation, name='team_creation'),
    path('team/delete', views.team_delete, name='team_delete'),
    path('team/management', views.team_management, name='team_management'),
    path('team/change_admin', views.change_admin, name='change_admin'),
    path('team/delete_member', views.delete_member, name='delete_member'),
    path('team/resign_request', views.resign_request, name='resign_request'),
    path('team/accept_resign', views.accept_resign, name='accept_resign'),
    path('contest/', views.contests_page, name='contest'),
    path('contest/<int:contest_id>/', views.contest_info, name='contest_info'),
    path('admin/match/', views.matches_page, name='matches_page'),
    path('admin/match/management/<int:match_id>', views.match_management, name='match_management'),
    path('admin/match/create/', views.match_definition, name='match_definition'),
    path('admin/match/create/get_matches/', views.get_matches, name='get_matches'),
    path('admin/match/create/get_teams/', views.get_teams, name='get_teams'),
]
