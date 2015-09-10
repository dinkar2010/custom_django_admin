# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_category_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggestion',
            name='location',
            field=models.ForeignKey(default=1, to='app.Location'),
            preserve_default=False,
        ),
    ]
