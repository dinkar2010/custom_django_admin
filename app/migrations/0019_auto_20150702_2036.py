# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0018_auto_20150630_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actions', models.IntegerField(choices=[(0, b'Order Received'), (1, b'Order Taken'), (2, b'Call to Shop'), (3, b'Call to Customer'), (4, b'FF Pass'), (5, b'Call to Delivery Boy'), (6, b'Order Placed'), (7, b'Delivery Confirmed by Customer'), (8, b'Delivery Declined By Customer'), (9, b'Order Cancelled'), (10, b'Delivery Confirmation By CS'), (11, b'Order Items Changed')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='delivery_charges',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='delivery_min_amount',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='delivery_time_min',
            field=models.IntegerField(default=60, help_text=b'Time in Minutes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='display_order',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='operating_time_end',
            field=models.TimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='operating_time_start',
            field=models.TimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='size',
            name='description',
            field=models.CharField(default=b'', max_length=500),
            preserve_default=True,
        ),
    ]
