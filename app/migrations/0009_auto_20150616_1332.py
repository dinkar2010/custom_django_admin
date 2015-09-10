# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20150612_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='change_requested',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_charges',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
