# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20150721_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationservicemapping',
            name='stores',
            field=models.ManyToManyField(related_name='stores', null=True, through='app.StoreTimingInLocation', to='app.Store'),
            preserve_default=True,
        ),
    ]
