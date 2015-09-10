# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_auto_20150726_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='is_active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='storetiminginlocation',
            unique_together=set([('store', 'lsm')]),
        ),
    ]
