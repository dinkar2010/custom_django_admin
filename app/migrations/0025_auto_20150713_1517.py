# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20150706_2317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': (('can_download_order_dump', 'Can download orders dump'),)},
        ),
        migrations.AddField(
            model_name='store',
            name='services',
            field=models.ManyToManyField(to='app.Service'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, b'Delivered'), (1, b'Cancelled'), (2, b'Processed'), (3, b'Received'), (4, b'Dispatched'), (5, b'Handed Over'), (6, b'OLP in proc'), (7, b'Order Not Delivered'), (8, b'Delivery Confirmation By User')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderactivity',
            name='actions',
            field=models.IntegerField(choices=[(0, b'Order Received'), (1, b'Order Taken'), (2, b'Call to Shop'), (3, b'Call to Customer'), (4, b'FF Pass'), (5, b'Call to Delivery Boy'), (6, b'Order Placed'), (7, b'Delivery Confirmed by Customer'), (8, b'Delivery Declined By Customer'), (9, b'Order Cancelled'), (10, b'Delivery Confirmation By CS'), (11, b'Order Items Changed'), (12, b'Delivery Confirmation notification sent')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderactivity',
            name='comment',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
