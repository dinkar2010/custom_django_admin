from django.conf.urls import patterns, url, include
from django.contrib import admin
from app.views import api_v2_views as views
urlpatterns = patterns('',
	#app urls
	
	url(r'^get_otp/$', views.send_otp, name='send_otp'),
	url(r'^check_otp_sync_address/$', views.check_otp_sync_address, name='check_otp_sync_address'),
	url(r'^get_past_orders/$', views.get_past_orders, name='get_past_orders'),
	url(r'^get_store_product/$', views.get_store_products, name='get_store_products'),
    url(r'^available_services/$', views.get_available_services, name='get_available_services'),
	url(r'^place_order/$', views.process_order, name='process_order'),
	url(r'^order_status/$', views.get_order_status, name='get_order_status'),
	url(r'^products_per_cat/$', views.get_products_per_category, name='get_products_per_category'),
	url(r'^offer_product/$', views.get_offer_products, name='get_offer_products'),
	url(r'^apply_coupon_code/$', views.get_coupon_code_discount, name='get_coupon_code_discount'),
	url(r'^save_suggestion/$', views.save_suggestion, name='save_suggestion'),
	url(r'^send_order_status/$', views.save_order_status, name='save_order_status'),

	)
