# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_cart_products'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='products1',
            new_name='products',
        ),
    ]
