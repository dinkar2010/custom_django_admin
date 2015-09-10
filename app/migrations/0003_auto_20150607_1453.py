# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20150606_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='related_products',
            field=models.ManyToManyField(related_name='related_products_rel_+', null=True, to='app.Product', blank=True),
            # preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(to='app.Tag', null=True, blank=True),
            # preserve_default=True,
        ),
    ]
