from . import assoc
from django.urls import path

app_name = 'assoc'
urlpatterns = [
    path('', assoc.new, name='new'),
    path('create', assoc.create, name='create'),
    path('<int:game_id>/', assoc.game, name='game'),
    path('<int:game_id>/ajax', assoc.ajax, name='ajax'),
    path('<int:game_id>/wordsajax', assoc.wordsajax, name='wordsajax'),
    path('<int:game_id>/login', assoc.login, name='login'),
    path('<int:game_id>/login/<int:player_id>/', assoc.setlogin, name='setlogin'),
    path('<int:game_id>/push', assoc.push, name='push'),
    path('<int:game_id>/link', assoc.link, name='link'),
    path('<int:game_id>/words', assoc.words, name='words'),
    path('<int:game_id>/words/save', assoc.savewords, name='savewords'),
    path('<int:game_id>/history', assoc.history, name='history'),
]