from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api
from app.views import custom_admin_views as views
from app.views import common_views as c_views
from app.views import api_v1_custom_views as v1_views
from app.models import OrderedProduct, OfferLocationMapping
from app import resources

v1_api = Api(api_name='v1')

v1_api.register(resources.ServiceResource())
v1_api.register(resources.CategoryResource())
v1_api.register(resources.AddressResource())
v1_api.register(resources.UserResource())
v1_api.register(resources.LocationResource())
v1_api.register(resources.StoreResource())
v1_api.register(resources.SizeResource())
v1_api.register(resources.ProductResource())
v1_api.register(resources.ProductSizeImageResource())
v1_api.register(resources.StoreProductResource())
v1_api.register(resources.AvailableServiceResource())
v1_api.register(resources.OrderResource())
v1_api.register(resources.CartResource())
v1_api.register(resources.CouponResource())
v1_api.register(resources.ProductsPerCategory())
v1_api.register(resources.OrderedProductResource())
v1_api.register(resources.SuggestionResource())
v1_api.register(resources.OrderStatusResource())
v1_api.register(resources.OfferResource())
v1_api.register(resources.OfferLocationResource())
v1_api.register(resources.OfferProductResource())
v1_api.register(resources.OfferProductOrderResource())
v1_api.register(resources.VisitorResource())
v1_api.register(resources.TagResource())

admin.site.login = views.admin_login

urlpatterns = patterns('',

    #common
    url(r'^$', c_views.web_site_page, name='web_site_page'),
    url(r'^bill/$', c_views.bill, name='bill'),
    url(r'^validate_txn/$', c_views.validate_txn, name='validate_txn'),
    url(r'^android/$', c_views.android_app_redirection,name='android_app_redirection'),
    url(r'^app_version_code/$', c_views.appversioncode,name='appversioncode'),

    #v2
    url('api/v2/', include('app.api_v2_urls')),

    #v1
    url(r'^api/v1/store_product/$',v1_views.get_store_products,name="get_store_products"),
    url(r'^api/v1/available_services/$',v1_views.get_available_services,name="get_available_services"),
    url(r'^api/v1/products_per_cat/set/(?P<ids>.*)/$',v1_views.get_products_per_category,name="get_products_per_category"),
    url(r'^api/v1/$', views.blank),
    url(r'^.*/schema/$', views.blank),
    (r'^api/', include(v1_api.urls)),

    #django admin
    url(r'^admin/app/store/$', views.show_stores, name='show_stores'),
    url(r'^admin/app/storeproductmapping/add/', views.add_product, name='add_product'),
    url(r'^admin/app/location/add/',views.add_new_location, name='add_new_location'),
    url(r'^admin/app/storeproductmapping/$',views.show_list_storeproduct, name='show_list_storeproduct'),
    url(r'^admin/app/offer/$', views.show_offers, name='show_offers'),
    url(r'^admin/', include(admin.site.urls)),

    #custom admin
    url('movinCartAdmin/', include('app.custom_admin_urls')),

    #custom api v1
    url('app/', include('app.custom_app_urls')),
)
