# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20150703_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='used_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
