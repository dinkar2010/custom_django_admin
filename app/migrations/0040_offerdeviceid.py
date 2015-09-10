# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_productsizeimagemapping_is_basic_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferDeviceId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('device_id', models.CharField(default=None, max_length=500)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
