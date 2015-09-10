# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import geoposition.fields
import django.contrib.gis.db.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('address', models.CharField(max_length=500)),
                ('landmark', models.CharField(max_length=150)),
                ('location_show', models.CharField(max_length=500)),
                ('is_default', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('display_order', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(default=0, to='app.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=100)),
                ('discount', models.IntegerField()),
                ('discount_type', models.IntegerField(choices=[(0, b'direct_minus'), (1, b'percent_minus')])),
                ('max_discount_limit', models.IntegerField()),
                ('min_total', models.IntegerField(default=0)),
                ('max_usage_limit', models.IntegerField(default=500)),
                ('expiry_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CouponDeviceIdMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('device_id', models.CharField(max_length=250)),
                ('coupon', models.ForeignKey(to='app.Coupon')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('product_json', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('city', models.CharField(max_length=100)),
                ('zone', models.CharField(default=b'', max_length=100)),
                ('area', models.CharField(max_length=100)),
                ('sub_area', models.CharField(max_length=100)),
                ('mpoly', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationServiceMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('isComingSoon', models.BooleanField(default=False)),
                ('location', models.ForeignKey(to='app.Location')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('total_amount', models.FloatField(help_text=b'')),
                ('final_amount', models.FloatField(null=True, editable=False, blank=True)),
                ('delivery_time', models.DateTimeField(help_text=b'To schedule delivery', null=True, blank=True)),
                ('status', models.IntegerField(choices=[(0, b'Delivered'), (1, b'Cancelled'), (2, b'Processed'), (3, b'Received'), (4, b'Dispatched'), (5, b'Handed Over'), (6, b'OLP in proc')])),
                ('is_urgent', models.BooleanField(default=False)),
                ('paymentStatus', models.IntegerField(default=0, choices=[(0, b'COD'), (1, b'OLP in Proc'), (2, b'Paid Online'), (3, b'OLP Failed'), (4, b'Refunded')])),
                ('address', models.ForeignKey(to='app.Address')),
                ('coupon_applied', models.ForeignKey(blank=True, to='app.Coupon', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('brand_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('rating', models.IntegerField(default=0)),
                ('barcode', models.TextField(null=True, blank=True)),
                ('category', models.ForeignKey(to='app.Category')),
                ('related_products', models.ManyToManyField(related_name='related_products_rel_+', to='app.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductSizeImageMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to=b'/media/')),
                ('product', models.ForeignKey(to='app.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('delivery_charges', models.IntegerField(default=0)),
                ('delivery_min_amount', models.IntegerField(default=0)),
                ('delivery_time_min', models.IntegerField(default=60, help_text=b'Time in Minutes')),
                ('display_order', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('unit', models.CharField(max_length=100)),
                ('magnitude', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('owner_name', models.CharField(max_length=100)),
                ('contact', models.BigIntegerField()),
                ('address', models.CharField(max_length=1000L)),
                ('position', geoposition.fields.GeopositionField(default=b'19.101985614850385, 72.88626194000244', max_length=42, blank=True)),
                ('rating', models.IntegerField(default=0)),
                ('open_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('weekly_off', models.IntegerField(default=-1)),
                ('locations', models.ManyToManyField(to='app.Location')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoreProductMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('price', models.FloatField(null=True, blank=True)),
                ('discount', models.FloatField(default=0)),
                ('stock', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(default=0)),
                ('max_buy', models.IntegerField(default=20)),
                ('freebies_list', models.CharField(max_length=100)),
                ('product', models.ForeignKey(to='app.ProductSizeImageMapping')),
                ('store', models.ForeignKey(to='app.Store')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('contact', models.BigIntegerField()),
                ('app_id', models.CharField(max_length=250, null=True, blank=True)),
                ('app_version', models.CharField(max_length=10, null=True, blank=True)),
                ('device_id', models.CharField(max_length=300, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='productsizeimagemapping',
            name='size',
            field=models.ForeignKey(to='app.Size'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(to='app.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationservicemapping',
            name='service',
            field=models.ForeignKey(to='app.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.OneToOneField(to='app.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coupondeviceidmapping',
            name='order',
            field=models.ForeignKey(to='app.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coupondeviceidmapping',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='service',
            field=models.ForeignKey(to='app.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cart',
            name='order',
            field=models.ForeignKey(to='app.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(to='app.StoreProductMapping'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cart',
            name='store',
            field=models.ForeignKey(to='app.Store'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='location',
            field=models.ForeignKey(to='app.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
