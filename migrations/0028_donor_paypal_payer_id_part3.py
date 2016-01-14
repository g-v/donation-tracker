# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0027_donor_paypal_payer_id_part2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='paypal_payer_id',
            field=models.CharField(null=True, max_length=13, blank=True, help_text=b'True unique ID per paypal user (last known paypal email)', unique=True, verbose_name=b'Paypal Payer ID'),
        ),
        migrations.AlterField(
            model_name='donor',
            name='email',
            field=models.EmailField(null=True, unique=True, max_length=128, verbose_name=b'Contact Email', blank=True),
        ),
    ]
