from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from hat.models import Game, Player, Word
import re
from random import seed
from random import randint
import datetime
from django.utils import timezone
import json

#Заполнение игроков для новой игры
def new(request):
  return render(request, 'assoc/new.html')  

#Начало новой игры
def create(request):

  allplayers = request.POST['players']
  wordsnum = request.POST['wordsnum']
  
  commands = allplayers.splitlines()
  if len(commands) == 0:
    return HttpResponseRedirect(reverse('assoc:new'))

  for cmd in commands:
    if cmd:
      players = cmd.split('+')
      if len(players) != 2:
        return HttpResponseRedirect(reverse('assoc:new'))
  
  game = Game()
  game.wordsnum = wordsnum
  game.roundsnum = wordsnum
  game.save()
  
  #Создаем в базе первых игроков команды
  command = 1
  number = 0
  for cmd in commands:
    if cmd:
      players = cmd.split('+')
      if len(players) == 2:
        game.player_set.create(**{'command':command, 'name':players[0], 'number':number})
        command += 1
        number += 1

  #Создаем в базе вторых игроков команды
  command = 1
  for cmd in commands:
    if cmd:
      players = cmd.split('+')
      if len(players) == 2:
        game.player_set.create(**{'command':command, 'name':players[1], 'number':number})
        command += 1
        number += 1
    
  # Always return an HttpResponseRedirect after successfully dealing
  # with POST data. This prevents data from being posted twice if a
  # user hits the Back button.
  return HttpResponseRedirect(reverse('assoc:link', args=(game.id,)))

def link(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))
    
  return render(request, 'assoc/link.html', {'game': game})  

  
#Авторизация, т.е. выбор игрока. Сюда приходим, если еще не выбрали себя
def login(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))
    
  return render(request, 'assoc/login.html', {'game': game})  

def setlogin(request, game_id, player_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))

  #Проверим, не левый ли игрок
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('assoc:login', args=(game.id,)))
  
  request.session['player_id'] = player_id
  return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    

#Ввод слов игроком
def words(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))
    
  #Нельзя вводить слова, когда игра уже идет
  if game.state > 0:
    return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    
  #Проверим, не левый ли игрок
  player_id = request.session.get('player_id', 0)
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('assoc:login', args=(game.id,)))

  words = player.word_set.all()
  return render(request, 'assoc/words.html', {'game': game, 'player':player, 'words':words})  

#Рассчитывает номер следующего игрока относительно базового b и текущего t при числе игроков N
def incr_turn(b, t, N):
  return ( b + (t-b+1)%(N/2) )%N

#Является ли игрок t в этом раунде придумывающим ассоциацию относительно базового b
def is_assoc_player(b, t, N):
  return ( (t-b)%N < (N/2) )
  
#Сохранение введенных слов
def savewords(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))

  #Проверим, не левый ли игрок
  player_id = request.session.get('player_id', 0)
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('assoc:login', args=(game.id,)))

  #Менять слова во время игры нельзя
  if game.state > 0:
    return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    
  player.word_set.all().delete()
  allwords = request.POST['words']
  words = allwords.split()
  wordsnum = 0
  for word in words:
    if wordsnum >= game.wordsnum:
      break
    player.word_set.create(**{'game':game, 'player':player, 'word':word})
    wordsnum += 1

  #Если все ввели слова, переводим игру на следующий этап
  allWordsCreated = True
  for pl in game.player_set.all():
    if not pl.AllWordsCreated():
      allWordsCreated = False
      break
  
  if allWordsCreated:
    game.state = 1
    game.begin_number = 0
    game.turn_number = incr_turn(game.begin_number, game.begin_number, game.player_set.count())
    begin_player = game.begin_player()
    unchecked_words = begin_player.word_set.filter(checked=False)
    word = unchecked_words[0]
    word.checked = True
    begin_player.cur_word = word
    word.save()
    begin_player.save()
    game.save()
    
  return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))

 
def wordsajax(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponse(json.dumps({'error':1}), content_type="application/json")

  allwords = game.TotalWordsCount()
  dic = {
    'error':0,
    'allwords':allwords
  }
      
  return HttpResponse(json.dumps(dic), content_type="application/json")
  
def push(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))

  #Игра окончена
  if game.IsOver():
    return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    
  player_id = request.session.get('player_id', 0)
  #Проверим, принадлежит ли player_id данной игре
  try:
    player = game.player_set.get(pk = player_id)
  except:
    request.session['player_id'] = 0
    player_id = 0
  
  if player_id == 0:
    return HttpResponseRedirect(reverse('assoc:login', args=(game.id,)))
    
  if not player.HasTurn():
    return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))

  N = game.player_set.count()
    
  #Кнопка "Угадал". Начинаем новый круг со следующей базы
  if request.POST.get('action', '') == 'match':
    player.grades += 1
    player.save()
    #Запоминаем выбор в истории
    if game.begin_player().cur_word:
      game.history_set.create(**{'game':game, 'player':player, 'word':game.begin_player().cur_word, 'state':game.state})

    game.begin_number = (game.begin_number+1)%N
    if  game.begin_number == 0:
      game.state += 1
      
    #Конец игры
    if game.IsOver():
      game.save()
      return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    
    begin_player = game.begin_player()
    unchecked_words = begin_player.word_set.filter(checked=False)
    word = unchecked_words[0]
    word.checked = True
    begin_player.cur_word = word
    print(word.word)
    game.turn_number = incr_turn(game.begin_number, game.begin_number, N)
    word.save()
    begin_player.save()
  #Кнопка "Не угадал". Передача хода
  elif request.POST.get('action', '') == 'mismatch':
    game.turn_number = incr_turn(game.begin_number, game.turn_number, N)
    
  game.save()

  return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))

def ajax(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponse(json.dumps({'error':1}), content_type="application/json")
  
  dic = {
    'error':0,
    'game_state':game.state,
    'turn_number':game.turn_number
  }
      
  return HttpResponse(json.dumps(dic), content_type="application/json")

def history(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))

  #Нельзя смотреть историю, пока игра не закончилась
  if not game.IsOver():
    return HttpResponseRedirect(reverse('assoc:game', args=(game.id,)))
    
  history = game.history_set.all()
  return render(request, 'assoc/history.html', {'game': game, 'history':history})  


#Диспетчер игры
def game(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('assoc:new'))

  N = game.player_set.count()
  num_comnamds = N//2
  commands_list = [None] * num_comnamds
  
  for pl in game.player_set.all():
    if commands_list[pl.command-1] == None:
      commands_list[pl.command-1] = [pl.name, None, pl.grades]
    else:
      commands_list[pl.command-1][1] = pl.name
      commands_list[pl.command-1][2] += pl.grades
    
  if game.IsOver():
    return render(request, 'assoc/gameover.html', {'game': game, 'commands_list':commands_list})  
      
  player_id = request.session.get('player_id', 0)
  #Проверим, принадлежит ли player_id данной игре
  try:
    player = game.player_set.get(pk = player_id)
  except:
    request.session['player_id'] = 0
    player_id = 0
  
  if player_id == 0:
    return HttpResponseRedirect(reverse('assoc:login', args=(game.id,)))
    
  #Проверим, заполнил ли игрок свои слова
  if not player.AllWordsCreated():
    return HttpResponseRedirect(reverse('assoc:words', args=(game.id,)))

  #Ждем, пока все введут слова
  if game.state == 0:
    return render(request, 'assoc/waitwords.html', {'game': game, 'player':player})  
 
  word = ""
  if is_assoc_player(game.begin_number, player.number, N):
    if game.begin_player().cur_word:
      word = game.begin_player().cur_word.word
 
  return render(request, 'assoc/game.html', 
    {
      'game': game, 
      'player':player, 
      'word':word, 
      'commands_list':commands_list
    }
  )  
 