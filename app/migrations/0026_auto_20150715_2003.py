# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20150713_1517'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='storeproductmapping',
            options={'permissions': (('can_download_product_dump', 'Can download products dump'),)},
        ),
    ]
