# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150611_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='operating_time_end',
            field=models.TimeField(default='10:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='operating_time_start',
            field=models.TimeField(default='10:00'),
            preserve_default=False,
        ),
    ]
