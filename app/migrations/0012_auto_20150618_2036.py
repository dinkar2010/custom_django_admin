# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20150616_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeproductmapping',
            name='freebies_list',
            field=models.CharField(max_length=100, null=True, blank=True),
            # preserve_default=True,
        ),
    ]
