# Generated by Django 3.0.4 on 2020-05-14 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hat', '0010_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='elapsed',
            field=models.SmallIntegerField(default=0),
        ),
    ]