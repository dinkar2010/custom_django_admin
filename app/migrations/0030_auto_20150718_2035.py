# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_auto_20150718_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferRuleBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('rule_type', models.IntegerField(choices=[(1, b'Universal'), (2, b'Username '), (3, b'Max Use Number'), (4, b'Location'), (5, b'Category'), (6, b'Ingore Category'), (7, b'Version Number')])),
                ('rule_value', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubSubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('sub_category', models.ForeignKey(to='app.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='offerrulebook',
            unique_together=set([('rule_type', 'rule_value')]),
        ),
        migrations.AddField(
            model_name='offer',
            name='rule_book',
            field=models.ManyToManyField(to='app.OfferRuleBook'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='sub_sub_category',
            field=models.ForeignKey(to='app.SubSubCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='storeproductmapping',
            name='price_to_movincart',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='couponrulebook',
            name='rule_type',
            field=models.IntegerField(choices=[(0, b'Minimum Total'), (1, b'Service Type'), (2, b'Service ID for Coupon'), (3, b'Universal'), (4, b'Username '), (5, b'Max Use Number'), (6, b'Location'), (7, b'Category'), (8, b'Ingore Category'), (9, b'Version Number')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='couponrulebook',
            unique_together=set([('rule_type', 'rule_value')]),
        ),
    ]
