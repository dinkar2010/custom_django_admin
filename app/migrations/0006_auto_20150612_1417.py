# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20150612_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1)),
                ('cart', models.ForeignKey(to='app.Cart')),
                ('product', models.ForeignKey(to='app.StoreProductMapping')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='cart',
            name='products1',
            field=models.ManyToManyField(related_name='products1', through='app.OrderedProduct', to='app.StoreProductMapping'),
            preserve_default=True,
        ),
    ]
