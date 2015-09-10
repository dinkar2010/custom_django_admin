# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_visitor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, b'Delivered'), (1, b'Cancelled'), (2, b'Processed'), (3, b'Received'), (4, b'Dispatched'), (5, b'Handed Over'), (6, b'OLP in proc'), (7, b'Order Not Delivered')]),
            # preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=400),
            # preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='locationservicemapping',
            unique_together=set([('service', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='offerlocationmapping',
            unique_together=set([('offer', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='offerproductmapping',
            unique_together=set([('offer', 'product')]),
        ),
        migrations.AlterUniqueTogether(
            name='productsizeimagemapping',
            unique_together=set([('product', 'size')]),
        ),
        migrations.AlterUniqueTogether(
            name='storeproductmapping',
            unique_together=set([('product', 'store')]),
        ),
    ]
