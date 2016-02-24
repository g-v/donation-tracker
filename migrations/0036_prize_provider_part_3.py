# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0035_prize_provider_part_2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prize',
            name='provided',
        ),
        migrations.RemoveField(
            model_name='prize',
            name='provideremail',
        ),
    ]

