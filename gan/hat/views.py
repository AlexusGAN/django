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
  return render(request, 'hat/new.html')  

#Начало новой игры
def create(request):

  allplayers = request.POST['players']
  wordsnum = request.POST['wordsnum']
  seconds = request.POST['seconds']
  roundsnum = request.POST['roundsnum']
  
  commands = allplayers.splitlines()
  if len(commands) == 0:
    return HttpResponseRedirect(reverse('hat:new'))
  players = commands[0].split('+')
  for cmd in commands:
    if cmd:
      players = cmd.split('+')
      if len(players) != 2:
        return HttpResponseRedirect(reverse('hat:new'))
  
  game = Game()
  game.wordsnum = wordsnum
  game.seconds = seconds
  game.roundsnum = roundsnum
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
  return HttpResponseRedirect(reverse('hat:link', args=(game.id,)))


#Авторизация, т.е. выбор игрока. Сюда приходим, если еще не выбрали себя
def login(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))
    
  return render(request, 'hat/login.html', {'game': game})  

def setlogin(request, game_id, player_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))

  #Проверим, не левый ли игрок
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('hat:login', args=(game.id,)))
  
  request.session['player_id'] = player_id
  return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
    

#Ввод слов игроком
def words(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))
    
  #Нельзя вводить слова, когда игра уже идет
  if game.state > 0:
    return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
    
  #Проверим, не левый ли игрок
  player_id = request.session.get('player_id', 0)
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('hat:login', args=(game.id,)))

  words = player.word_set.all()
  return render(request, 'hat/words.html', {'game': game, 'player':player, 'words':words})  

#Сохранение введенных слов
def savewords(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))

  #Проверим, не левый ли игрок
  player_id = request.session.get('player_id', 0)
  try:
    player = game.player_set.get(pk = player_id)
  except:
    return HttpResponseRedirect(reverse('hat:login', args=(game.id,)))

  #Менять слова во время игры нельзя
  if game.state > 0:
    return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
    
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
    game.turn_number = 0
    game.save()
    
  return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
  
def pull(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))

  #Игра окончена
  if game.IsOver():
    return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
    
  player_id = request.session.get('player_id', 0)
  #Проверим, принадлежит ли player_id данной игре
  try:
    player = game.player_set.get(pk = player_id)
  except:
    request.session['player_id'] = 0
    player_id = 0
  
  if player_id == 0:
    return HttpResponseRedirect(reverse('hat:login', args=(game.id,)))
    
  if not player.HasTurn():
    return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))

  #Начало хода
  if request.POST.get('action', '') == 'turn':
    game.turn_number = player.number
    game.timer = timezone.now() - datetime.timedelta(seconds=game.elapsed)  #с учетом уже потраченного времени в предыдущем раунде

  timeout = True
  elapsed_seconds = 0
  
  #Проверяем таймаут
  if game.timer:
    elapsed_time = timezone.now() - game.timer
    elapsed_seconds = elapsed_time.seconds
    if elapsed_seconds < game.seconds:
      timeout = False
   
  #Кнопка "Угадал"
  if request.POST.get('action', '') == 'match':
    if not timeout:
      player.grades += 1
      #Запоминаем выбор в истории
      game.history_set.create(**{'game':game, 'player':player, 'word':player.cur_word, 'state':game.state})
  #Кнопка "Сдаюсь"
  elif request.POST.get('action', '') == 'mismatch':
      timeout = True
  
  next_round = False
  #Истек таймаут
  if timeout:
    if player.cur_word:
      player.cur_word.checked = False
      player.cur_word.save()
      player.cur_word = None
      game.elapsed = 0
      #Ход следующего игрока
      game.turn_number = ((game.turn_number+1)%game.player_set.count())
    game.timer = None
  else:
    unchecked_words = game.word_set.filter(checked=False)
    #В шляпе еще есть слова
    if unchecked_words.count():
      num = randint(0, unchecked_words.count()-1)
      word = unchecked_words[num]
      word.checked = True
      player.cur_word = word
    #Раунд окончен. 
    else:
      next_round = True
      
  #Следующий раунд. Передачу хода не делаем, пусть доиграет свое время в новом раунде
  if next_round:
    player.cur_word = None
    game.timer = None
    game.elapsed = elapsed_seconds #Запомним истекшее время
    game.state += 1
    words = game.word_set.all()
    for word in words:
      word.checked = False
      word.save()

  game.save()
  player.save()
  if player.cur_word:
    player.cur_word.save()

  #Ведущему игроку перед начало раунда выдадим предварительную страницу раунда, чтобы
  #он обратил внимание на новые правила
  if next_round and not game.IsOver():
    return HttpResponseRedirect(reverse('hat:round', args=(game.id,)))
    
  return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))

def ajax(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponse(json.dumps({'error':1}), content_type="application/json")
  
  dic = {
    'error':0,
    'game_state':game.state,
    'turn_number':game.turn_number,
    'progress':game.progress(),
    'grades':game.cur_player().grades
  }
      
  return HttpResponse(json.dumps(dic), content_type="application/json")

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
  

def link(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))
    
  return render(request, 'hat/link.html', {'game': game})  

 
def round(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))
    
  return render(request, 'hat/round.html', {'game': game})  
  
def history(request, game_id):
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))

  #Нельзя смотреть историю, пока игра не закончилась
  if not game.IsOver():
    return HttpResponseRedirect(reverse('hat:game', args=(game.id,)))
    
  history = game.history_set.all()
  return render(request, 'hat/history.html', {'game': game, 'history':history})  
  
#Диспетчер игры
def game(request, game_id):
  #Проверим game_id
  try:
    game = Game.objects.get(pk=game_id)
  except:
    return HttpResponseRedirect(reverse('hat:new'))

  num_comnamds = game.player_set.count()//2
  commands_list = [None] * num_comnamds
  
  for pl in game.player_set.all():
    if commands_list[pl.command-1] == None:
      commands_list[pl.command-1] = [pl.name, None, pl.grades]
    else:
      commands_list[pl.command-1][1] = pl.name
      commands_list[pl.command-1][2] += pl.grades
    
  if game.IsOver():
    return render(request, 'hat/gameover.html', {'game': game, 'commands_list':commands_list})  
      
  player_id = request.session.get('player_id', 0)
  #Проверим, принадлежит ли player_id данной игре
  try:
    player = game.player_set.get(pk = player_id)
  except:
    request.session['player_id'] = 0
    player_id = 0
  
  if player_id == 0:
    return HttpResponseRedirect(reverse('hat:login', args=(game.id,)))
    
  #Проверим, заполнил ли игрок свои слова
  if not player.AllWordsCreated():
    return HttpResponseRedirect(reverse('hat:words', args=(game.id,)))

  #Ждем, пока все введут слова
  if game.state == 0:
    return render(request, 'hat/waitwords.html', {'game': game, 'player':player})  
    
  history_word = ''
  history_player = ''
  if game.history_set.count():
    history = game.history_set.all().last()
    history_word = history.word.word
    history_player = history.player.name
    
  return render(request, 'hat/game.html', 
    {
      'game': game, 
      'player':player, 
      'commands_list':commands_list, 
      'history_word':history_word,
      'history_player':history_player
    }
  )  
  
