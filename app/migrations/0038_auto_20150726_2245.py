# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_auto_20150726_1327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locationservicemapping',
            name='delivery_charges',
        ),
        migrations.RemoveField(
            model_name='locationservicemapping',
            name='delivery_min_amount',
        ),
        migrations.RemoveField(
            model_name='locationservicemapping',
            name='delivery_time_min',
        ),
        migrations.RemoveField(
            model_name='locationservicemapping',
            name='operating_time_end',
        ),
        migrations.RemoveField(
            model_name='locationservicemapping',
            name='operating_time_start',
        ),
        migrations.RemoveField(
            model_name='store',
            name='locations',
        ),
        migrations.AddField(
            model_name='store',
            name='backup_shops',
            field=models.ManyToManyField(related_name='backup_shops_rel_+', null=True, to='app.Store', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('city', 'zone', 'area', 'sub_area')]),
        ),
    ]
