from django.contrib import admin

# Register your models here.
from hat.models import Game, Player, Word

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Word)