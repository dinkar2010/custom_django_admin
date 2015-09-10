from django.conf.urls import patterns, url

from app.views import custom_admin_views as views
from app.views.test_api import v1
from app.views.test_api import v2

urlpatterns = patterns('',
#admin urls
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^logout/$', views.adminlogout,name='logout'),
    url(r'^add_new_location/$', views.add_new_location, name='add_new_location'),
    url(r'^edit_location/(?P<id>\d+)/$', views.edit_location, name='edit_location'),
    url(r'^edit_product_info/$', views.edit_product, name='edit_product'),
    url(r'^cancel_single_order/(?P<id>\d+)/$', views.cancel_single_order, name='cancel_single_order'),
    url(r'^order_delivered/(?P<id>\d+)/$', views.order_delivered, name='order_delivered'),
    url(r'^order_processed/(?P<id>\d+)/$', views.order_processed, name='order_processed'),
    url(r'^send_notification/', views.send_notification, name='send_notification'),
    url(r'^covered_locations/$', views.covered_locations, name='covered_locations'),
    url(r'^remove_product_frm_order/$', views.remove_product_frm_order, name='remove_product_frm_order'),
    url(r'^change_image/$', views.change_image, name='change_image'),
    url(r'^show_stores/$', views.show_stores, name='show_stores'),
    url(r'^dump/orders/$', views.save_orders_dump, name='save_order_dump'),
    url(r'^add_store/$', views.add_store, name='add_store'),
    url(r'^edit_store/(?P<id>\d+)/$', views.edit_store, name='edit_store'),
    url(r'^store/add/locations/$', views.add_location_in_store, name='add_location_in_store'),
    url(r'^store/edit_stl_info_frm_table/$', views.edit_stl_info_frm_table, name='edit_stl_info_frm_table'),
    url(r'^store/copy_product_from_main/$', views.copy_product_from_main, name='copy_product_from_main'),


    url(r'^storeproductmapping/$', views.show_list_storeproduct, name='show_list_storeproduct'),
    url(r'^get_store_product_json/$', views.get_store_product_json, name='get_store_product_json'),

    url(r'^orders/$', views.show_list_orders, name='show_list_orders'),
    url(r'^edit_product_info_frm_table/$', views.edit_product_info_frm_table, name='edit_product_info_frm_table'),
    url(r'suggestion/$',views.show_all_suggestion,name='show_all_suggestion'),
    url(r'userprofile/$',views.show_user_profile,name='show_user_profile'),
    url(r'visitors/$',views.show_all_visitors,name='show_all_visitors'),
    url(r'coupon/add/$',views.add_coupon_details,name='add_coupon_details'),
    url(r'coupon/(?P<id>\d+)/$',views.edit_coupon,name='edit_coupon'),
	url(r'^productdump/$', views.productdump, name='productdump'),
	url(r'^save_tags_for_product/(?P<id>\d+)/$', views.save_tags_for_product, name='save_tags_for_product'),
# <<<<<<< HEAD

    # url(r'^lsm/$',views.show_list_locations_services, name='show_list_locations_services'),
    # url(r'^edit_lsm/$', views.edit_lsm, name='edit_lsm'),
	url(r'^lsm/add/$', views.add_lsm, name='add_lsm'),
	url(r'^lsm/edit/(?P<id>\d+)/$', views.edit_lsm_from_table, name='edit_lsm_from_table'),
#
#
# =======
#     url(r'^copy_product_in_local_store/$', views.copy_product_in_local_store, name='copy_product_in_local_store'),
# >>>>>>> f48587c55b17b240ae61ba745be09ae77ece5f8f
	url(r'^coupon/$', views.show_all_coupon, name='show_all_coupon'),

	url(r'^show_services/$', views.show_services, name='show_services'),
    url(r'^edit_service/(?P<id>\d+)/$', views.edit_service, name='edit_service'),
    url(r'^change_service_image/$', views.change_service_image, name='change_service_image'),
	url(r'^show_offers/$', views.show_offers, name='show_offers'),
	url(r'^edit_offer/(?P<id>\d+)/$', views.edit_offer, name='edit_offer'),
	url(r'^change_offer_image/$', views.change_offer_image, name='change_offer_image'),
	url(r'^add_offer_product/(?P<id>\d+)/$', views.add_offer_product, name='add_offer_product'),
	url(r'^edit_offer_product_info_frm_table/$', views.edit_offer_product_info_frm_table, name='edit_offer_product_info_frm_table'),

	url(r'^edit_locations_offer/$', views.edit_locations_offer, name='edit_locations_offer'),
	url(r'^edit_category_from_service/$', views.edit_category_from_service, name='edit_category_from_service'),
    url(r'^get_location_service_mapping/$', views.get_location_service_mapping, name='get_location_service_mapping'),
    # url(r'^get_location_service_mapping_through_ajax/$', views.get_location_service_mapping_through_ajax, name='get_location_service_mapping_through_ajax'),
    url(r'^edit_location_service_mapping/$', views.edit_location_service_mapping, name='edit_location_service_mapping'),
    # url(r'^filter_orders/$', views.filter_orders, name='filter_orders'),
    # url(r'^filter_orders_delivered/$', views.filter_orders_delivered, name='filter_orders_delivered'),
    # url(r'^filter_orders_scheduled/$', views.filter_orders_scheduled, name='filter_orders_scheduled'),
    # url(r'^filter_orders_not_delivered/$', views.filter_orders_not_delivered, name='filter_orders_not_delivered'),

    #analytics
    url(r'^analytics/$', views.show_analytics_full, name='show_analytics_full'),
    url(r'^analytics/balance_analytics/$', views.get_balance_analytics, name='get_balance_analytics'),
    url(r'^analytics/new_repeated_users/$', views.get_new_repeated_users_analytics, name='get_new_repeated_users_analytics'),
    url(r'^analytics/orders_analytics/$', views.get_orders_analytics, name='get_orders_analytics'),
    url(r'^analytics/category_ordered/$', views.get_category_ordered_analytics, name='get_orders_analytics_analytics'),

    #Test API V1
    url(r'^test/v1/available_services/$',v1.available_services, name='available_services'),
    url(r'^test/v1/product_per_cat/$',v1.product_per_cat,name='product_per_cat'),
    url(r'^test/v1/sub_category/$',v1.sub_category,name='sub_category'),
    url(r'^test/v1/order_status/$',v1.order_status,name='order_status'),
    url(r'^test/v1/past_order/$',v1.past_order,name='past_order'),
    url(r'^test/v1/search_product/$',v1.search_product,name='search_product'),

    #Test API V2
    url(r'^test/v2/available_services/$',v2.available_services, name='available_services'),
    url(r'^test/v2/product_per_cat/$',v2.product_per_cat,name='product_per_cat'),
    url(r'^test/v2/sub_category/$',v2.sub_category,name='sub_category'),
    url(r'^test/v2/order_status/$',v2.order_status,name='order_status'),
    url(r'^test/v2/past_order/$',v2.past_order,name='past_order'),
    url(r'^test/v2/search_product/$',v2.search_product,name='search_product'),
    url(r'^test/v2/place_order/$',v2.place_order,name='place_order'),

    #upload url
    # url(r'^upload_excel_file_in_store/$', views.upload_excel_file_in_store, name='upload_excel_file_in_store'),
    # url(r'^upload_products_from_excel_in_store/$', views.upload_products_from_excel_in_store, name='upload_products_from_excel_in_store'),
)

