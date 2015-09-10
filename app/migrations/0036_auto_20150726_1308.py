# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20150726_1135'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locationservicemapping',
            old_name='isActive',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='locationservicemapping',
            old_name='isComingSoon',
            new_name='is_coming_soon',
        ),
        migrations.RenameField(
            model_name='offer',
            old_name='isActive',
            new_name='is_active',
        ),
        migrations.RenameField(
            model_name='offerlocationmapping',
            old_name='isActive',
            new_name='is_active',
        ),
        migrations.AlterUniqueTogether(
            name='timeslot',
            unique_together=set([('start_time', 'end_time')]),
        ),
    ]
