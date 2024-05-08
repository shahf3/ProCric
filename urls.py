from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('create-team/', views.create_team, name='create_team'),
    path('teamlist/', views.team_list, name='team_list'),
    path('tournamentlist', views.tournament_list, name='tournament_list'),
    path('login/', views.login_view, name='login'),
    path('create-match/', views.create_match, name='create_match'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('create-tournament/', views.create_tournament, name='create_tournament'),
    path('tournament/<int:tournament_id>/', views.tournament_details, name='tournament_details'),
    path('tournament/<int:tournament_id>/schedule', views.tournament_details, name='tournament_details'),
    #path('delete-team/<int:team_id>/', views.delete_team, name='delete_team'),
    path('deleteteams/', views.delete_selected_teams, name='delete_selected_teams'),
    path('logout/', views.logout_view, name='logout'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact_us', views.contact_us, name='contact_us'),
    # path('tournament/<int:tournament_id>/remove-match/<int:match_id>/', views.remove_match, name='remove_match'),
    path('change_password/', views.change_password, name='change_password'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('references/', views.references, name='references'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('check_player_existence/', views.check_player_existence, name='check_player_existence'),
    path('tournament/<int:tournament_id>/scoring/<int:match_id>/', views.scoring, name='scoring'),
    path('upload_profile_pic/', views.upload_profile_pic, name='upload_profile_pic'),
    path('finalize_tournament/<int:tournament_id>/', views.finalize_tournament, name='finalize_tournament'),
    path('tournament/<int:tournament_id>/results/', views.tournament_results, name='tournament_results'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)