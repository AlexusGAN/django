# Generated by Django 3.0.4 on 2020-05-08 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hat', '0005_auto_20200507_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='cur_word',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cur_word', to='hat.Word'),
        ),
    ]
