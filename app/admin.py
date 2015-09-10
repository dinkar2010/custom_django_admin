from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.contrib.gis.admin.options import GeoModelAdmin
import simplejson
from app.models import LocationServiceMapping, Tag, ProductSizeImageMapping, Cart, Location, UserProfile, Address, \
    Service, Size, Store, Category, Product, StoreProductMapping, Coupon, CouponDeviceIdMapping, Order, Invoice, \
    OrderedProduct, Suggestion, Offer, OfferLocationMapping, OfferProductMapping, Visitor, CouponRuleBook, OrderActivity, \
    StoreTimingInLocation
import datetime as dt
from django.db.models import Q
from django import forms
from app.utils import analytics, constant
from app.models import verify_coupon


class LocationAdmin(GeoModelAdmin):
    list_display = ('city', 'zone', 'area','sub_area')
    list_filter = ('city', 'zone','area')
    search_fields = ['city','zone','area','sub_area']
    actions =None
    change_form_template ='new_custom_admin/edit_location.html'

    def get_osm_info(self,id):
        location = Location.objects.get(pk=id)
        polygon_text = location.mpoly.wkt
        polygon_coordi = simplejson.loads(location.mpoly.json)['coordinates'][0]
        locations = Location.objects.all().exclude(pk=id)
        polygons = []
        for l in locations:
            polygon_coordi1 = simplejson.loads(l.mpoly.json)['coordinates'][0]
            polygons.append(polygon_coordi1)
        context={
            'location':location,
            'polygon_text':polygon_text,
            'polygon_coordi':polygon_coordi,
            'polygons':polygons,
        }
        return context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # print object_id
        extra_context['custom_location'] = self.get_osm_info(id=object_id)
        return super(LocationAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('Name', 'contact', 'app_version','created_at')
    list_filter = ('app_version','created_at')
    readonly_fields = ('Name','contact','app_id','device_id','app_version')
    fields = ('Name','contact','app_version','app_id','device_id',)
    search_fields = ['user__email','user__first_name','user__username','device_id']

    def Name(self,obj):
        return str(obj.user.first_name)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_data', 'address_full','location', 'is_default',)
    readonly_fields = ('user_data','address_full')
    fields = ('user_data','address_full','address','landmark','location_show','location','is_default')
    search_fields = ['user__email','user__first_name','user__username']

    def address_full(self,obj):
        return obj

    def user_data(self, obj):
        return str(obj.user.first_name)+" / "+str(obj.user.username)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'is_active', )
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    list_display_links = ('name',)


class LocationServiceMappingAdmin(admin.ModelAdmin):
    list_display = ('service','sub_area','is_active','is_coming_soon','display_order')
    list_editable = ('is_active','is_coming_soon')
    list_filter = ('service','location','is_active','is_coming_soon')
    # readonly_fields = ('service','location')
    # fields = ('service','location','is_active','isComingSoon')

    def sub_area(self,obj):
        return obj.location.sub_area

    def area(self,obj):
        return obj.location.area


class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'contact','address','on_products','off_products','live_locations', )
    list_filter = ('rating', 'open_time', 'end_time', 'weekly_off',)
    search_fields = ['name','owner_name','address']

    def on_products(self, obj):
        return str(StoreProductMapping.objects.filter(store=obj,stock=True).count())

    def off_products(self, obj):
        return str(StoreProductMapping.objects.filter(store=obj,stock=False).count())

    def live_locations(self, obj):
        return str(obj.StoreTimingInLocations.objects.filter(is_active=True,store=obj).count())


class SizeAdmin(admin.ModelAdmin):
    list_display = ('magnitude', 'unit',)
    list_filter = ('unit',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'parent', 'service' ,'display_order','is_active')
    list_filter = ('parent', 'service')
    list_display_links = ('name',)
    list_editable =('is_active','display_order',)
    search_fields = ['name','service__name']


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand_name','category','description',)
    list_filter = ('category', 'rating',)
    search_fields = ('name','brand_name')
    list_per_page = 30


class StoreProductMappingAdmin(admin.ModelAdmin):
    list_display = ('product_image','product','product_brand_name','store','stock', 'price', 'discount','product_size','max_buy' ,'display_order')
    list_filter = ('store','product__product__category','stock')
    list_display_links = ['product']
    list_editable = ('price','discount','stock','max_buy','display_order',)
    search_fields = ('store__name','product__product__name','product__product__brand_name')

    def product_brand_name(self,obj):
        return obj.product.product.brand_name

    def product_size(self,obj):
        return obj.product.size

    def product_image(self,obj):
        return '<a target="_blank" href="%s"><img height="35" width="35" src="%s"></a>' % (obj.product.image,obj.product.image)

    product_image.allow_tags = True

    change_form_template ='new_custom_admin/single_product.html'

    def get_osm_info(self,id):
        product = StoreProductMapping.objects.get(pk=id)
        service= product.product.product.category.service
        categories = Category.objects.filter(parent=None)
        category_vise_sub_categories={}
        for c in categories:
            category_vise_sub_categories[str(c.name)]= map(lambda x:x,Category.objects.filter(parent_id=c.id))
        context = {
            'product':product,
            'category_vise_sub_categories':category_vise_sub_categories
        }
        return context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # print object_id
        extra_context['custom_product'] = self.get_osm_info(id=object_id)
        extra_context['page'] = 5
        return super(StoreProductMappingAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)


class CouponRuleBookAdmin(admin.ModelAdmin):
    list_display = ('rule_type','rule_value')
    search_fields = ('rule_value',)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'discount_type','max_discount_limit','min_total', 'expiry_date','is_active')
    list_filter = ('is_active', 'expiry_date')
    search_fields = ('code',)


class CouponDeviceIdMappingAdmin(admin.ModelAdmin):
    list_display = ('user','coupon')


class ProductSizeImageMappingAdmin(admin.ModelAdmin):
    list_display = ('product','size','image')
    search_fields = ('product__name','product__brand_name')


class OrderedProductInline(admin.TabularInline):
    # list_display = ('id','product','quantity',)
    model = OrderedProduct
    extra = 0
    fk_name = "cart"


class CartInline(admin.StackedInline):
    model = Cart
    filter_horizontal = ('products', )
    fk_name = "order"
    extra = 0

    inlines = [OrderedProductInline]


class OrderAdmin(admin.ModelAdmin):

    readonly_fields = ('user_data', 'service_ordered', 'final_amount', 'user', 'total_amount', 'address')
    fields = ('user_data', 'service_ordered', 'final_amount', 'total_amount', 'address', 'status', )

    list_display = ('id','old','user_data', 'service_ordered', 'full_address', 'locality_data', 'delivery_time_data', 'status_', 'coupon_data', 'final_amount_', 'see_order')
    list_display_links = ['see_order']
    # list_editable = ('status',)

    list_per_page = 20
    ordering = ('-delivery_time',)
    save_on_top = True
    search_fields = ['user__email','user__first_name','user__username','address__address','address__landmark']
    show_full_result_count = True
    list_filter = ('created_at', 'modified_at', 'delivery_time','status')
    change_form_template ='new_custom_admin/single_order_detail.html'
    # change_list_template = 'new_custom_admin/all_orders.html'
    def get_osm_info(self,id):
        # print id
        order = Order.objects.get(pk=id)
        invoice= order.invoice
        products=[]
        total_amount=0
        order_products = simplejson.loads(invoice.product_json)
        # reduce db query
        # products = map(lambda x: x['spid'],order_products)
        # products =
        all_in_one=[]
        for p in order_products:
            dict_index = -1
            service_dict={}
            product={}
            product['sp']=StoreProductMapping.objects.get(pk=p['spid'])
            prd = product['sp']

            service = str(prd.product.product.category.service.id)
            if service not in map(lambda x: x['id'],all_in_one):
                service_dict['total']=0
                service_dict['sub_total']=0
                service_dict['id']=service
                service_dict['name']=str(prd.product.product.category.service.name)
                service_dict['items']=[]
                service_dict['coupon_code']="----"
                service_dict['coupon_discount']=0
                service_dict['delivery_charges']=0
                service_dict['store']=prd.store
            else:
                dict_index+=1
                for elem in all_in_one:
                    if service==elem['id']:
                        service_dict=elem
                        break


            if 'discount' in p:
                if p['discount']>0:
                    product['normal_price']=p['price']
                    product['normal_total_price']=int(p['qn'])*p['price']
                product['price']=p['price']-p['discount']
            else:
                product['price']=p['price']
            product['qn']=p['qn']
            product['total_price']=int(p['qn'])*float(product['price'])

            product['size']={}
            mag = int(Size.objects.get(pk=p['size_id']).magnitude)
            if float(mag)!=Size.objects.get(pk=p['size_id']).magnitude:
                mag = Size.objects.get(pk=p['size_id']).magnitude
            product['size']['mag']= mag
            product['size']['unit']=Size.objects.get(pk=p['size_id']).unit
            product['image_link']=str(StoreProductMapping.objects.get(pk=p['spid']).product.image).replace('movinCartApp/','/')
            total_amount+=int(p['qn'])*float(product['price'])
            service_dict['total']+=int(p['qn'])*float(product['price'])
            service_dict['sub_total']+=int(p['qn'])*float(p['price'])
            service_dict['items'].append(product)
            products.append(product)
            if dict_index<0:
                all_in_one.append(service_dict)

        if order.delivery_time:
            delivery_time = order.delivery_time.strftime('%B %d, %Y, %I:%M %p')
        else:
            delivery_time = order.created_at + dt.timedelta(hours=1)
            delivery_time = delivery_time.strftime('%B %d, %Y, %I:%M %p')

        coupon = order.coupon_applied
        isDiscounted=False
        discount_money=0
        coupon_code='No Coupon'
        total_without_discount=total_amount
        total_without_discount_without_delivery_charges=total_amount
        if coupon:
            service_amount_ordered=[]
            for a in all_in_one:
                service_amount_ordered.append(str(a['id'])+":"+str(a['total']))
            service_amount_ordered=';;'.join(service_amount_ordered)
            coupon_code = coupon.code
            discount_money= verify_coupon(coupon,order.user,order.address.location_id,int(order.user.userprofile.app_version),order.final_amount,service_amount_ordered,flag=0)['discount']
            total_amount-=discount_money
            discount_temp = discount_money
            for a in all_in_one:
                if discount_temp>0:
                    # service_amount_ordered.append(str(a['id'])+":"+str(a['total']))
                    disc = verify_coupon(coupon,order.user,order.address.location_id,int(order.user.userprofile.app_version),int(float(a['total'])),str(a['id'])+":"+str(a['total']),flag=0)['discount']
                    print a['name']
                    print a['total']
                    print a['sub_total']
                    print disc
                    print discount_temp
                    print '---------------------------------------------------'
                    if disc>discount_temp:
                        disc=discount_temp
                    a['total'] -= disc
                    discount_temp-=disc
                    if disc > 0:
                        a['coupon_code']=coupon.code
                    a['coupon_discount']=disc

            isDiscounted=True
        delivery_charges_dictionary_new=simplejson.loads(order.delivery_charges)
        delivery_charges=0
        for key in delivery_charges_dictionary_new:
            if filter(lambda x:x['id']==key,all_in_one):
                filter(lambda x:x['id']==key,all_in_one)[0]['delivery_charges']+=delivery_charges_dictionary_new[key]['delivery_charges']
                total_amount+=delivery_charges_dictionary_new[key]['delivery_charges']
                total_without_discount+=delivery_charges_dictionary_new[key]['delivery_charges']
                delivery_charges+=delivery_charges_dictionary_new[key]['delivery_charges']
        change_req = ""
        if order.change_requested:
            change_req = "Bring change of : " + str(order.change_requested)
        else:
            if order.final_amount % 1000 < 100:
                bring_change_of = "100"
            elif order.final_amount % 1000 < 500:
                bring_change_of = "500"
            else:
                bring_change_of = "1000"
            change_req = "(Auto) Bring change of : " + str(bring_change_of)
        order_activities = OrderActivity.objects.filter(order=order).order_by('-created_at')
        context = {
            'customer':order.user,
            'order':order,
            'products':products,
            'total_amount':total_amount,
            'total_without_discount':total_without_discount,
            'delivery_time':delivery_time,
            'isDiscounted':isDiscounted,
            'discount_money':discount_money,
            'coupon_code':coupon_code,
            'all_in_one':all_in_one,
            'total_without_discount_without_delivery_charges':total_without_discount_without_delivery_charges,
            'delivery_charges':delivery_charges,
            'change_req':change_req,
            'order_activities':order_activities,
        }
        return context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # print object_id
        extra_context['custom_order'] = self.get_osm_info(id=object_id)
        extra_context['shot_order_summary'] = analytics.get_short_order_summary()
        extra_context['page'] = 2
        return super(OrderAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    # inlines = [CartInline]
    def see_order(self,obj):
        return "See Order Details"

    def status_(self,obj):
        order_status={
            '0':'DELIVERED',
            '1' : 'CANCELLED',
            '2' : 'PROCESSED',
            '3': 'RECEIVED',
            '4' : 'DISPATCHED',
            '5' : 'HANDED_OVER',
            '6' : 'OLP_PENDING',
            '7' : 'NOT DELIVERED',
            '8' : 'DELIVERY CNF BY USER',
        }
        colors={
            '0':'40b868',
            '1' : 'bce6e6',
            '2' : '3b5998',
            '3': '000000',
            '4' : '259073',
            '5' : '88a35c',
            '6' : '990000',
            '7' : 'FF0000',
            '8' : '40b868'
        }
        status='<center><span style="color: #%s;"><b>%s</b></span></center>' % (colors[str(obj.status)],order_status[str(obj.status)].title())
        if obj.delivery_time:
            if obj.delivery_time < dt.datetime.now() and obj.status==2:
                status= '<center><span style="color: #000000;"><b>%s</b></span></center>' % ("Time Over")
        else:
            if obj.created_at + dt.timedelta(hours=1)< dt.datetime.now() and obj.status ==2:
                status= '<center><span style="color: #000000;"><b>%s</b></span></center>' % ("Time Over")
        return status
    status_.allow_tags = True
    def final_amount_(self,obj):
        f=obj.final_amount
        return '<center>'+str(int(f))+'</center>'
    final_amount_.allow_tags = True

    def delivery_time_data(self,obj):
        if obj.delivery_time:
            delivery_time = obj.delivery_time
        else:
            delivery_time = obj.created_at + dt.timedelta(hours=1)
        time_delta = (dt.datetime.today().day == delivery_time.day and dt.datetime.today().month == delivery_time.month and dt.datetime.today().year == delivery_time.year)

        if time_delta:
            format_time = '%I:%M %p'
        else:
            format_time = '%B %d, %Y, %I:%M %p'

        return delivery_time.strftime(format_time)

    def service_ordered(self,obj):
        service_ordered = []
        invoice = obj.invoice
        ordered_product = simplejson.loads(invoice.product_json)
        for p in ordered_product:
            prd = StoreProductMapping.objects.get(pk=p['spid'])
            service = prd.product.product.category.service.name
            service_ordered.append(service)
        service_ordered = list(set(service_ordered))
        return ', '.join(service_ordered)

    def coupon_data(self, obj):
        if obj.coupon_applied:
            return '<center>'+str(obj.coupon_applied)+'</center>'
        return '<center>----</center>'
    coupon_data.allow_tags=True
    def user_data(self, obj):
        return str(obj.user.first_name).title()+" / "+str(obj.user.username)

    def locality_data(self,obj):
        return obj.address.location.sub_area+", "+obj.address.location.area

    def old(self,obj):
        user = obj.user
        prev_orders = Order.objects.filter(status__in=[0,8],user=user,created_at__lt=obj.created_at)
        return (prev_orders.count() >= 1 or user.userprofile.created_at < dt.datetime.now() - dt.timedelta(days=5) or user.username in constant.old_users)
    old.boolean = True

    class Media:
        js=("refresh.js",)

    def full_address(self,obj):
        return obj.address.address.title()+" "+obj.address.landmark.title()


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('user_data', 'service_ordered', 'locality_data', 'delivery_time_data', 'status', 'coupon_data', 'final_amount','see_invoice' ,'see_order')
    list_display_links=('see_invoice',)
    
    def see_order(self,obj):
        return '<a target="_blank" href="/admin/app/order/%s/">See Order Details</a>' % (obj.order.id)
    
    see_order.allow_tags = True
    
    def see_invoice(self,obj):
        return "see invoice"
    
    def delivery_time_data(self,obj):
        if obj.order.delivery_time:
            return obj.order.delivery_time.strftime('%B %d, %Y, %I:%M %p')
        delivery_time = obj.order.created_at + dt.timedelta(hours=1)
        time_delta = dt.datetime.today() - obj.order.created_at
        if time_delta.days==0:
            format_time = '%I:%M %p'
        else:
            format_time = '%B %d, %Y, %I:%M %p'

        return delivery_time.strftime(format_time)

    change_form_template ='new_custom_admin/single_invoice.html'

    def get_osm_info(self,id):
        invoice = Invoice.objects.get(pk=id)
        products=[]
        total_amount=0
        ordered_services={}
        ordered_services_items={}
        order_products = simplejson.loads(invoice.product_json)
        for p in order_products:
            product={}
            product['sp']=StoreProductMapping.objects.get(pk=p['spid'])
            prd = product['sp']
            service= prd.product.product.category.service.name
            if service not in ordered_services:
                ordered_services[service]=0
                ordered_services_items[service]=[]
            product['price']=p['price']
            product['discount']=p['discount']
            product['qn']=p['qn']
            product['size']= str(int(float(Size.objects.get(pk=p['size_id']).magnitude)))+" "+str(Size.objects.get(pk=p['size_id']).unit)
            product['image_link']=str(StoreProductMapping.objects.get(pk=p['spid']).product.image).replace('movinCartApp/','/')
            total_amount+=int(p['qn'])*(float(product['price'])-float(p['discount']))
            product['product_final_total']=int(p['qn'])*(float(product['price'])-float(p['discount']))
            ordered_services[service]+=int(p['qn'])*(float(product['price'])-float(p['discount']))
            products.append(product)
            ordered_services_items[service].append(product)
        # print products
        coupon= invoice.order.coupon_applied
        isDiscounted=False
        discount_money=0
        coupon_code='----'
        total_without_discount=total_amount
        if coupon:
            coupon_code = coupon.code
            if coupon.discount_type==0:
                    discount_money= coupon.discount
            else:
                discount_money = (total_amount*coupon.discount)/100
                if discount_money > coupon.max_discount_limit:
                    discount_money = coupon.max_discount_limit
            total_amount-=discount_money
            isDiscounted=True
        delivery_charges=0
        delivery_charges_dictionary={}
        delivery_charges_dictionary_new={}
        # if invoice.order.delivery_charges!="" and not is_number(order.delivery_charges):
        delivery_charges_dictionary_new=simplejson.loads(invoice.order.delivery_charges)
        for key in delivery_charges_dictionary_new:
            total_amount+=delivery_charges_dictionary_new[key]['delivery_charges']
            # total_without_discount+=delivery_charges_dictionary_new[key]['delivery_charges']
            delivery_charges+=delivery_charges_dictionary_new[key]['delivery_charges']
        context={
            # 'customer':customer,
            'order':invoice.order,
            'invoice':invoice,
            'products':products,
            'total_amount':total_amount,
            'total_without_discount':total_without_discount,
            'isDiscounted':isDiscounted,
            'discount_money':discount_money,
            'coupon_code':coupon_code,
            'services' : ordered_services_items,
            'total' : ordered_services,
            'delivery_charges':delivery_charges
        }

        return context

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # print object_id
        print extra_context
        extra_context['custom_invoice'] = self.get_osm_info(id=object_id)
        extra_context['shot_order_summary'] = analytics.get_short_order_summary()

        extra_context['page'] = 2
        return super(InvoiceAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def status(self,obj):
        order_status={
            '0':'DELIVERED',
            '1' : 'CANCELLED',
            '2' : 'PROCESSED',
            '3': 'RECEIVED',
            '4' : 'DISPATCHED',
            '5' : 'HANDED_OVER',
            '6' : 'OLP_PENDING',
            '7' : 'NOT_DELIVERED_BY_USER',
            '8' : 'DELIVERY_CONFIRMATION_USER',
        }
        return order_status[str(obj.order.status)]

    def final_amount(self,obj):
        return obj.order.final_amount

    def service_ordered(self,obj):
        service_ordered = []
        invoice = obj
        ordered_product = simplejson.loads(invoice.product_json)
        for p in ordered_product:
            prd = StoreProductMapping.objects.get(pk=p['spid'])
            service = prd.product.product.category.service.name
            service_ordered.append(service)
        service_ordered = list(set(service_ordered))
        return ', '.join(service_ordered)

    def coupon_data(self, obj):
        if obj.order.coupon_applied:
            return str(obj.order.coupon_applied)
        return '----'
    def user_data(self, obj):
        return str(obj.order.user.first_name)+" / "+str(obj.order.user.username)

    def locality_data(self,obj):
        return obj.order.address.location.sub_area+", "+obj.order.address.location.area


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('suggestion','comments','email','sub_area','area','created_at')

    def sub_area(self,obj):
        return obj.location.sub_area

    def area(self,obj):
        return obj.location.area


class VisitorAdmin(admin.ModelAdmin):
    list_display = ('email','app_id','app_version','device_id','platform')
    actions =None


class OfferAdmin(admin.ModelAdmin):
    list_display = ('name','valid_till','is_active')


class OfferLocationAdmin(admin.ModelAdmin):
    list_display = ('offer','location','is_active')


class OfferProductAdmin(admin.ModelAdmin):
    list_display = ('offer','product',)

class OrderActivityAdmin(admin.ModelAdmin):
    list_display = ('order','user','actions')

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user','content_type','object_repr','action_flag','change_message')
    list_filter = ('user', 'content_type','action_flag')

class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name','content_type','codename',)

class StoreTimingInLocationAdmin(admin.ModelAdmin):
    list_display = ('store','lsm','delivery_charges',)



admin.site.register(Location, LocationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(StoreProductMapping, StoreProductMappingAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(CouponDeviceIdMapping, CouponDeviceIdMappingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(LocationServiceMapping,LocationServiceMappingAdmin)
admin.site.register(Tag)
admin.site.register(OrderActivity,OrderActivityAdmin)
admin.site.register(Suggestion, SuggestionAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferLocationMapping, OfferLocationAdmin)
admin.site.register(OfferProductMapping, OfferProductAdmin)
admin.site.register(Visitor, VisitorAdmin)
admin.site.register(LogEntry,LogEntryAdmin)
admin.site.register(Permission,PermissionAdmin)
admin.site.register(CouponRuleBook, CouponRuleBookAdmin)
admin.site.register(StoreTimingInLocation, StoreTimingInLocationAdmin)