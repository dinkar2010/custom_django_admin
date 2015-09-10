from django.conf.urls import patterns, url, include
from django.contrib import admin
from app.views import custom_app_views as views
urlpatterns = patterns('',
	#app urls
	
	url(r'^get_past_orders/$', views.get_past_orders, name='get_past_orders'),
	)
