from django.test import TestCase
from .models import Game, Player
import datetime 
from django.utils import timezone

# Create your tests here.
class QuestionModelTests(TestCase):

  def test_models(self):
    """
    Тест моделей
    """
    time = timezone.now() + datetime.timedelta(days=30)
    g1= Game()
    g1.save()
    g1.player_set.create(command=1, name='Федя')
    g1.player_set.create(command=2, name='Петя')
    g1.player_set.create(command=3, name='Лиса')
    g1.player_set.create(command=1, name='Зоя')
    g1.player_set.create(command=2, name='Андрей')
    g1.player_set.create(command=3, name='Маша')
    g1.player_set.all()
    
    p2 = g1.player_set.get(name='Петя')
    self.assertIs(p2.command, 2)