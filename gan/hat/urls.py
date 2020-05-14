from . import views
from django.urls import path

app_name = 'hat'
urlpatterns = [
    path('', views.new, name='new'),
    path('create', views.create, name='create'),
    path('<int:game_id>/', views.game, name='game'),
    path('<int:game_id>/ajax', views.ajax, name='ajax'),
    path('<int:game_id>/wordsajax', views.wordsajax, name='wordsajax'),
    path('<int:game_id>/login', views.login, name='login'),
    path('<int:game_id>/login/<int:player_id>/', views.setlogin, name='setlogin'),
    path('<int:game_id>/words', views.words, name='words'),
    path('<int:game_id>/words/save', views.savewords, name='savewords'),
    path('<int:game_id>/pull', views.pull, name='pull'),
    path('<int:game_id>/link', views.link, name='link'),
    path('<int:game_id>/history', views.history, name='history'),
]