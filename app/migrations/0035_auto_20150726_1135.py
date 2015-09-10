# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20150726_1128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storetiminginlocation',
            old_name='delivery_time_min',
            new_name='normal_hours_delivery_time_min',
        ),
        migrations.AddField(
            model_name='store',
            name='normal_hours',
            field=models.ManyToManyField(related_name='normal_hour', to='app.TimeSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='rush_hours',
            field=models.ManyToManyField(related_name='rush_hour', to='app.TimeSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storetiminginlocation',
            name='rush_hours_delivery_time_min',
            field=models.IntegerField(default=60, help_text=b'Time in Minutes'),
            preserve_default=True,
        ),
    ]
