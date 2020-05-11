from django.core.management.base import BaseCommand
from hat.models import Game, Player
import datetime 
from django.utils import timezone

class Command(BaseCommand):
  def handle(self, **options):
    g1 = Game()
    g1.save()
    g1.player_set.create(command=1, name='Федя')
    g1.player_set.create(command=2, name='Петя')
    g1.player_set.create(command=3, name='Лиса')
    g1.player_set.create(command=1, name='Зоя')
    g1.player_set.create(command=2, name='Андрей')
    g1.player_set.create(command=3, name='Маша')
    g1.player_set.all()
    p2 = g1.player_set.get(name='Петя')
    print(p2)
    print(Game.objects.all())
 
