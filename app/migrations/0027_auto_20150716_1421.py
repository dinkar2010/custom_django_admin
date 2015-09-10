# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20150715_2003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='store',
            options={'permissions': (('can_add_store', 'Can Add Store'), ('can_edit_store', 'Can Edit Store'))},
        ),
    ]
