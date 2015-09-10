# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_suggestion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suggestion',
            name='user',
        ),
        migrations.AddField(
            model_name='suggestion',
            name='email',
            field=models.EmailField(default='admin@admin.com', max_length=75),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderedproduct',
            name='product',
            field=models.ForeignKey(editable=False, to='app.StoreProductMapping'),
            # preserve_default=True,
        ),
    ]
