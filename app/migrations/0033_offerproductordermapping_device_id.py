# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_locationservicemapping_stores'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerproductordermapping',
            name='device_id',
            field=models.CharField(default=None, max_length=500),
            preserve_default=True,
        ),
    ]
