# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20150702_2036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='delivery_charges',
        ),
        migrations.RemoveField(
            model_name='service',
            name='delivery_min_amount',
        ),
        migrations.RemoveField(
            model_name='service',
            name='delivery_time_min',
        ),
        migrations.RemoveField(
            model_name='service',
            name='display_order',
        ),
        migrations.RemoveField(
            model_name='service',
            name='operating_time_end',
        ),
        migrations.RemoveField(
            model_name='service',
            name='operating_time_start',
        ),
    ]
