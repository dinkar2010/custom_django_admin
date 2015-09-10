# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_coupon_used_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='comment',
            new_name='comments',
        ),
    ]
