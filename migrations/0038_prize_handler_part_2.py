# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def write_existing_providers(apps, schema_editor):
    Prize = apps.get_model('tracker', 'Prize')
    for prize in Prize.objects.all():
        if prize.handler:
            if prize.handler.username != prize.handler.email:
                prize.provider = prize.handler.username
            prize.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0037_prize_handler_part_1'),
    ]

    operations = [
        migrations.RunPython(write_existing_providers),
    ]
