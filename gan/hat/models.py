﻿from django.db import models
import datetime
from django.utils import timezone


#Модель Game
class Game(models.Model):
  date = models.DateTimeField(auto_now_add=True) #дата начала игры
  state = models.SmallIntegerField(default=0) #этап игры
  timer = models.DateTimeField(null=True)  #время начала хода игрока
  #текущий игрок
  '''
  cur_player = models.OneToOneField(
    'Player', 
    blank=True, 
    null=True, 
    related_name="game_turn", 
    on_delete=models.CASCADE
  ) 
  '''
  begin_number = models.SmallIntegerField(default=0) #номер игрока, с которого начался раунд
  turn_number = models.SmallIntegerField(default=0) #номер игрока, чей ход сейчас
  
  wordsnum = models.SmallIntegerField(default=5) #количество слов
  seconds = models.SmallIntegerField(default=60) #секунд на ход
  
  def cur_player(self):
    return self.player_set.all()[self.turn_number]
  
  def round_name(self):
    if self.state == 0:
      return "Подготовка к игре"
    elif self.state == 1:
      return "Раунд 1: Скажи иначе"
    elif self.state == 2:
      return "Раунд 2: Покажи жестами"
    elif self.state == 3:
      return "Раунд 3: Издай звуками"
    else:
      return "Игра окончена"
      
  def IsOver(self):
    return self.state == 4
      
  #Значение прогрессбара от 0 до 100
  def progress(self):
    if self.timer == None:
      return 0
    elapsed_time = timezone.now() - self.timer
    if elapsed_time.seconds >= self.seconds:
      return 100
      
    return (elapsed_time.seconds)*100//self.seconds

  #Текущее кол-во слов
  def TotalWordsCount(self):
    count = 0
    for pl in self.player_set.all():
      count += pl.word_set.count()
    return count;

 
#Модель Player
class Player(models.Model):
  command = models.SmallIntegerField() #номер команды
  name = models.CharField(max_length=30)
  game = models.ForeignKey(Game, on_delete=models.CASCADE)
  grades = models.SmallIntegerField(default=0) #набранные очки
  #текущее слово
  cur_word = models.OneToOneField(
    'Word', 
    blank=True, 
    null=True, 
    related_name="cur_word", 
    on_delete=models.CASCADE
  )  
  number = models.SmallIntegerField(default=0) #номер игрока
  
  def __str__(self):
    return f"#{self.id} game{self.game.id} {self.name}" 
    
  def AllWordsCreated(self):
    return self.word_set.count() == self.game.wordsnum
    
  def HasTurn(self):
    return self.number == self.game.turn_number and not self.game.IsOver()

#Модель Word
class Word(models.Model):
  word = models.CharField(max_length=30)
  game = models.ForeignKey(Game, on_delete=models.CASCADE)
  player = models.ForeignKey(Player, on_delete=models.CASCADE)
  checked = models.BooleanField(default=False)
    
  def __str__(self):
    return f"#{self.id} {self.word} {self.player.name}" 
