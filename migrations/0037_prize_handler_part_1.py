# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0036_prize_provider_part_3'),
    ]

    operations = [
        migrations.RenameField('prize', 'provider', 'handler'),
        migrations.AddField(
            model_name='prize',
            name='provider',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='prize',
            name='handler',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, help_text=b'User account responsible for prize shipping', null=True),
        ),
        migrations.AlterField(
            model_name='prize',
            name='provider',
            field=models.CharField(help_text=b'Name of the person who provided the prize to the event', max_length=64, blank=True),
        ),
    ]
