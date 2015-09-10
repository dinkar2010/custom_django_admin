# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20150705_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderactivity',
            name='comment',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='orderactivity',
            name='order',
            field=models.ForeignKey(default=0, to='app.Order'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='couponrulebook',
            name='rule_type',
            field=models.IntegerField(choices=[(0, b'Minimum Total'), (1, b'Service Type'), (2, b'Service ID for Coupon'), (3, b'Universal'), (4, b'Username '), (5, b'Max Use Number'), (6, b'Location'), (7, b'Category'), (8, b'Ingore Category')]),
            preserve_default=True,
        ),
    ]
