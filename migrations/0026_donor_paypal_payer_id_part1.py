# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0025_event_minimumdonation'),
    ]

    operations = [
        migrations.AddField(
            model_name='donor',
            name='paypal_payer_id',
            field=models.CharField(null=True, max_length=13, blank=True, help_text=b'True unique ID per paypal user (as e-mail may not be unique)', unique=False, verbose_name=b'Paypal Payer ID'),
        ),
        migrations.AlterField(
            model_name='donor',
            name='email',
            field=models.EmailField(null=True, max_length=128, verbose_name=b'Contact Email', blank=True),
        ),
    ]
