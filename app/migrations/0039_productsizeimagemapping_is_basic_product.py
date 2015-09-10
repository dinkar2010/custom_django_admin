# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_auto_20150726_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsizeimagemapping',
            name='is_basic_product',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
