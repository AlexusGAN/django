# Generated by Django 3.0.4 on 2020-06-03 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hat', '0012_remove_game_begin_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='begin_number',
            field=models.SmallIntegerField(default=0),
        ),
    ]