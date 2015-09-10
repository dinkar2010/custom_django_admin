# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20150716_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationservicemapping',
            name='stores',
            field=models.ManyToManyField(to='app.Store', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='delivery_charges',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='delivery_min_amount',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='delivery_time_min',
            field=models.IntegerField(default=60, help_text=b'Time in Minutes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='store',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='store',
            name='contact',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
