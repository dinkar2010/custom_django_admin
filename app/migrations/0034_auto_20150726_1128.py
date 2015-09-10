# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_offerproductordermapping_device_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='delivery_charges',
        ),
        migrations.RemoveField(
            model_name='store',
            name='delivery_min_amount',
        ),
        migrations.RemoveField(
            model_name='store',
            name='delivery_time_min',
        ),
        migrations.RemoveField(
            model_name='store',
            name='is_active',
        ),
        migrations.AddField(
            model_name='storetiminginlocation',
            name='delivery_charges',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storetiminginlocation',
            name='delivery_min_amount',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storetiminginlocation',
            name='delivery_time_min',
            field=models.IntegerField(default=60, help_text=b'Time in Minutes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storetiminginlocation',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='offerproductordermapping',
            name='order',
            field=models.ForeignKey(to='app.Order', unique=True),
            preserve_default=True,
        ),
    ]
