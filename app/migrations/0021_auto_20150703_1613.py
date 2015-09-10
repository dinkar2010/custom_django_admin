# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20150703_1411'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponRuleBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('rule_type', models.IntegerField(choices=[(0, b'Minimum Total'), (1, b'Service Type'), (2, b'Service ID for Coupon'), (3, b'Universal'), (4, b'Username '), (5, b'Max Use Number')])),
                ('rule_value', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='max_usage_limit',
        ),
        migrations.AddField(
            model_name='coupon',
            name='rule_book',
            field=models.ManyToManyField(to='app.CouponRuleBook'),
            preserve_default=True,
        ),
    ]
