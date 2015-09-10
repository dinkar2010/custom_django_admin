# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_offerdeviceid'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnlineTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('gateway', models.IntegerField(choices=[(0, b'Citrus'), (1, b'PayU Money')])),
                ('txn_id', models.CharField(max_length=50)),
                ('amount', models.IntegerField()),
                ('status', models.IntegerField(choices=[(2, b'In process'), (0, b'Failed'), (1, b'success')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='online_payment',
            field=models.ForeignKey(blank=True, to='app.OnlineTransaction', null=True),
            preserve_default=True,
        ),
    ]
