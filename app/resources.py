import json
import threading
from django.db.models import Q
from django.http.response import HttpResponse
import simplejson
import datetime as dt
import time
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource
from tastypie.contrib.gis.resources import ModelResource as GeoModelResource
from app.models import Category, Order, Coupon, Size, Cart, Service, Product, StoreProductMapping, ProductSizeImageMapping,LocationServiceMapping,Store,Address, Location, \
    OrderedProduct, UserProfile, CouponDeviceIdMapping, Invoice, Suggestion, Offer, OfferLocationMapping, \
    OfferProductMapping, OfferProductOrderMapping, Visitor, Tag, OrderActivity, StoreTimingInLocation, OfferDeviceId
from tastypie import fields
from django.contrib.auth.models import User
from app.models import verify_coupon
from app.utils import constant
from app.utils.send_mail import *
import urllib

class ServiceResource(ModelResource):
    def filter_cat_per_bundle(bundle):
        service = bundle.obj
        return Category.objects.filter(service =service,is_active=True)
    category = fields.ToManyField('app.resources.CategoryResource', filter_cat_per_bundle, full=True, blank=True, null=True, related_name='service')

    class Meta:
        queryset = Service.objects.filter(is_active = True)
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "service"
        include_resource_uri = True
        authentication = Authentication()
        authorization = Authorization()
        excludes = ['created_at', 'modified_at','is_active']
        fields=['name','image','id','is_active',]
        filtering = {
            'id' : ALL
        }

    def dehydrate(self, bundle):
        index=0
        size = len(bundle.data['category'])
        for i in range(size):
            if bundle.data['category'][index].data['parent']:
                del bundle.data['category'][index]
            else:
                index+=1

        return bundle

class CategoryResource(ModelResource):

    def filter_cat_per_bundle(bundle):
        parent = bundle.obj
        return Category.objects.filter(parent=parent,is_active=True)

    children = fields.ToManyField('self', filter_cat_per_bundle, full=True, blank=True, null=True)
    parent = fields.ToOneField('self', 'parent', null=True)
    service = fields.ToOneField(ServiceResource,'service',full=False)
    class Meta:
        queryset = Category.objects.filter(parent=None)
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "category"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['created_at','modified_at',]
        filtering = {
            'id': ALL,
            'service' : ALL_WITH_RELATIONS
        }

## Sync Address API
class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "user"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        fields=['email','username',]
        filtering = {
            'id' : ALL,
            'email' :ALL,
            'username' :ALL
        }

## Sync API Complete
class LocationResource(GeoModelResource):

    class Meta:
        queryset = Location.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "location"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        # fields=['id',]
        limit = 1
        excludes=['created_at','modified_at']
        filtering = {
            'id' : ALL,
            'mpoly' : ['contains',]
        }

class AddressResource(ModelResource):

    user = fields.ToOneField(UserResource, 'user', full=False, blank=True, null=True)
    location_id = fields.IntegerField('location_id')
    class Meta:
        queryset = Address.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "address"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        fields=['address','location_show','landmark','location']
        filtering = {
            'id' : ALL,
            'user' : ALL_WITH_RELATIONS
        }

class StoreResource(ModelResource):

    locations = fields.ToManyField(LocationResource, 'locations', full=False, blank=True, null=True)

    class Meta:
        queryset = Store.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "store"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        filtering = {
            'id' : ALL,
            'locations' :ALL_WITH_RELATIONS
        }

class TagResource(ModelResource):

    class Meta:
        queryset = Tag.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "tags"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        filtering = {
            'id' : ALL,
            'name':ALL,
        }

class ProductResource(ModelResource):

    category = fields.ToOneField(CategoryResource, 'category', full=False, blank=True, null=True)
    service_id = fields.IntegerField('category__service_id')
    tags = fields.ManyToManyField(TagResource,'tags',full=False, blank=True, null=True)
    class Meta:
        queryset = Product.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "product"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        fields=['name','brand_name',]
        filtering = {
            'id' : ALL,
            'category' : ALL_WITH_RELATIONS,
            'name':ALL,
            'brand_name':ALL,
            'tags':ALL_WITH_RELATIONS

        }

class SizeResource(ModelResource):

    class Meta:
        queryset = Size.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "size"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        fields=['unit','magnitude']

class ProductSizeImageResource(ModelResource):

    product = fields.ToOneField(ProductResource, 'product', full=True, blank=True, null=True)
    size = fields.ToOneField(SizeResource, 'size', full=True, blank=True, null=True)

    class Meta:
        queryset = ProductSizeImageMapping.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "product_size"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        fields=['product','image','size']
        filtering = {
            'id' : ALL,
            'product' : ALL_WITH_RELATIONS
        }
    def dehydrate(self, bundle):
        bundle.data['image']= urllib.unquote(bundle.data['image']).decode('utf8')
        # print bundle
        return bundle

class StoreProductResource(ModelResource):
    product = fields.ToOneField(ProductSizeImageResource, 'product', full=True, blank=True, null=True)
    # store = fields.ToOneField(StoreResource, 'store', full=True, blank=True, null=True)

    class Meta:
        queryset = StoreProductMapping.objects.filter(stock=True,product__product__category__service__is_active=True).order_by('-display_order')
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        resource_name = "store_product"
        include_resource_uri = False
        authentication=Authentication()
        authorization = Authorization()
        limit=100
        ordering=['-display_order',]
        fields =['id','product','price','discount','display_order','max_buy',]
        filtering = {
            'id' : ALL,
            'product' : ALL_WITH_RELATIONS,
        }


    def alter_list_data_to_serialize(self, request, data):

        location_id = request.GET.get('store__locations')
        location = Location.objects.get(pk=location_id)
        print location_id
        index=0
        size = len(data['objects'])
        print size
        for i in range(size):
            print data['objects'][index].obj.store
            storeproduct = data['objects'][index].obj
            data['objects'][index].data['display_order']=0
            print storeproduct.id
            service_location_mapping = LocationServiceMapping.objects.filter(location_id=location_id,service=storeproduct.product.product.category.service,is_active=True,is_coming_soon=False)
            if not service_location_mapping:
                del data['objects'][index]
            else:
                lsm = service_location_mapping[0]
                if not StoreTimingInLocation.objects.filter(is_active=True,lsm=lsm,store=storeproduct.store):
                    del data['objects'][index]
                else:
                    index+=1

        return data

class AvailableServiceResource(ModelResource):

    def __init__(self, *args, **kwargs):
        super(AvailableServiceResource, self).__init__(*args, **kwargs)
        for field_name, field_object in self.fields.items():
            if field_name == 'location':
                field_object.use_in = 'detail'
    def alter_list_data_to_serialize(self, request, data):
        if data['objects']:
            size = len(data['objects'])
            print size
            location_id = data['objects'][0].data['current_location_id']
            location =Location.objects.get(pk=location_id)
            shops = map(lambda x:x.store,StoreTimingInLocation.objects.filter(is_active=True,lsm__location=location))
            index=0
            for i in range(size):
                # print data['objects'][i]
                if location_id != data['objects'][index].data['current_location_id']:
                    del data['objects'][index]
                else:
                    lsm = data['objects'][index].obj
                    # store = lsm.stores.all()[0]
                    print lsm
                    print lsm.id
                    storetimingInlocation = StoreTimingInLocation.objects.filter(is_active=True,lsm=lsm)[0]

                    service_data = data['objects'][i].data['service'].data
                    categories = data['objects'][i].data['service'].data['category']
                    cat_size = len(categories)
                    cat_index=0

                    for j in range(cat_size):
                        cat_obj = categories[cat_index].obj
                        if StoreProductMapping.objects.filter(stock=True,store__in=shops,product__product__category__parent=cat_obj).count()==0:
                            del categories[cat_index]
                        else:
                            cat_index+=1
                    delivery_charges = storetimingInlocation.delivery_charges #data['objects'][i].data['delivery_charges']
                    delivery_min_amount =storetimingInlocation.delivery_min_amount # data['objects'][i].data['delivery_min_amount']
                    delivery_time_min = storetimingInlocation.normal_hours_delivery_time_min #data['objects'][i].data['delivery_time_min']
                    display_order = data['objects'][i].data['display_order']
                    operating_time_end = storetimingInlocation.time_slot.all()[0].end_time#data['objects'][i].data['operating_time_end']
                    operating_time_start = storetimingInlocation.time_slot.all()[0].start_time# data['objects'][i].data['operating_time_start']

                    service_data['delivery_charges']=delivery_charges
                    service_data['delivery_min_amount']=delivery_min_amount
                    service_data['delivery_time_min']=delivery_time_min
                    service_data['display_order']=display_order
                    service_data['operating_time_end']=operating_time_end
                    service_data['operating_time_start']=operating_time_start
                    data['objects'][i].data['isComingSoon']=data['objects'][i].data['is_coming_soon']
                    del data['objects'][i].data['is_coming_soon']
                    # del data['objects'][i].data['delivery_charges']
                    # del data['objects'][i].data['delivery_min_amount']
                    # del data['objects'][i].data['delivery_time_min']
                    del data['objects'][i].data['display_order']
                    # del data['objects'][i].data['operating_time_end']
                    # del data['objects'][i].data['operating_time_start']
                    index+=1


            offer=OfferLocationMapping.objects.filter(location=location_id,is_active=True,offer__is_active=True)
            device_id = request.GET.get('device_id')
            contact = request.GET.get('contact')
            version = request.GET.get("version","")
            if version:
                if offer:
                    offer=offer[0].offer
                    if offer.is_active:
                        offerproductMapping = offer.offerproductmapping_set.all()[0]
                        flag =True
                        if contact!="":
                            if OfferProductOrderMapping.objects.filter(order__user__username=contact):
                                flag = False
                        offer_device_id =  OfferProductOrderMapping.objects.filter(device_id=device_id)
                        if flag and (not offer_device_id) and offerproductMapping.product.stock == True:
                            data['offer']={}
                            data['offer']['id']=offer.id
                            data['offer']['image']=offer.image
                    # data['offer_id']=offer.valid_till

            del data['meta']
        data['settings'] = {
                'discard':'true',
                'multi_service':'true',
                'version_no':constant.APP_VERSION,
                'is_valid_time':True,
            }
        return data

    service = fields.ToOneField(ServiceResource, 'service', full=True, blank=True, null=True)
    location = fields.ToOneField(LocationResource, 'location', full=False, blank=True, null=True)
    current_location_id = fields.IntegerField('location_id')

    class Meta:
        queryset = LocationServiceMapping.objects.filter(service__is_active=True,is_active=True)
        list_allowed_methods=['get']
        detail_allowed_methods=['get']
        resource_name = "available_services"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['created_at','modified_at','is_active','id',]
        # fields = ['isComingSoon',]
        filtering = {
            'location' : ALL_WITH_RELATIONS
        }

class ProductsPerCategory(ModelResource):

    def filter_per_bundle(bundle):
        cat=bundle.obj
        service=cat.service
        location=bundle.request.GET.get('location')
        lsm=LocationServiceMapping.objects.filter(location=location,service=service,is_active=True)
        shops=[]
        if lsm:
            lsm=lsm[0]
            shops=map(lambda x:x.store,filter(lambda y:y.store.is_active==True,StoreTimingInLocation.objects.filter(lsm=lsm,is_active=True)))
        sub_cats = Category.objects.filter(parent=cat)
        return StoreProductMapping.objects.filter(store__in=shops,product__product__category__in=sub_cats,stock=True).order_by('-display_order')[:6]

    products = fields.ToManyField(StoreProductResource, filter_per_bundle, full=True, blank=True, null=True)

    class Meta:
        queryset = Category.objects.all()
        list_allowed_methods = ['get']
        detail_allowed_methods=['get']
        resource_name="products_per_cat"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        fields=['id',]
        filtering={
            'id':ALL,
        }

class OrderedProductResource(ModelResource):
    product = fields.ToOneField(StoreProductResource,'product',full=True)
    class Meta:
        queryset = OrderedProduct.objects.all()
        list_allowed_methods = ['get','post']
        resource_name="ordered_products"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        filtering={
            'id':ALL,
        }

class CartResource(ModelResource):
    def filter_per_bundle(bundle):
        cart = bundle.obj
        # print len(OrderedProduct.objects.filter(cart=cart))
        return OrderedProduct.objects.filter(cart=cart)
    # order = fields.ToOneField(OrderResource, 'order', full=True, blank=True, null=True)
    products = fields.ManyToManyField(OrderedProductResource, filter_per_bundle, full=True, blank=True, null=True)
    store = fields.ToOneField(StoreResource, 'store', full=False, blank=True, null=True)

    class Meta:
        queryset = Cart.objects.all()
        list_allowed_methods = ['get','post']
        detail_allowed_methods=['get']
        resource_name="cart"
        include_resource_uri = True
        authentication = Authentication()
        authorization = Authorization()
        fields=['store','order','products']
        filtering={
            'id':ALL,
            # 'order' : ALL_WITH_RELATIONS
        }

class CouponResource(ModelResource):

    class Meta:
        queryset = Coupon.objects.filter(is_active=True)
        list_allowed_methods = ['get']
        detail_allowed_methods=['get']
        resource_name="apply_promo_code"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        fields=['id','code','discount','discount_type','max_discount_limit','min_total',]
        filtering={
            'id':ALL,
            'code':ALL,
            'min_total':ALL,
        }

    def alter_list_data_to_serialize(self, request, data):
        # Example iteration through data
        index=0
        status = 'Promo code is not Valid'
        for item in data['objects']:
            coupon = item.obj
            device_id = request.GET.get('device_id')
            contact = request.GET.get('contact')
            version = request.GET.get("version","")
            location = request.GET.get("location_id","")
            service_vs_total = request.GET.get("service_vs_total","")
            min_total = request.GET.get("total","")
            user = User.objects.filter(username=contact)
            print service_vs_total
            if version:
                version = int(version)
                if user and version>28:
                    user=user[0]
                    res = verify_coupon(coupon,
                                        user,
                                        int(location),
                                        int(version),
                                        min_total,
                                        service_vs_total
                                        )
                    status=res['status']
                    if res['discount'] ==0:
                        del data['objects'][index]
                    else:
                        data['objects'][index].data['discount']=res['discount']
                        data['objects'][index].data['discount_type']=0
            else:
                del data['objects'][index]
                status = "Coupon valid only on updated app"
            order = Order.objects.filter(Q(user__userprofile__contact= contact,coupon_applied=coupon)|Q(user__userprofile__device_id= device_id,coupon_applied=coupon))
            if order:
                if order[0].status!=1:
                    del data['objects'][index]
            index+=1
        del data['meta']
        data['status']=status
        return data

class OrderResource(ModelResource):

    address = fields.ToOneField(AddressResource, 'address', full=True, blank=True, null=True)
    user = fields.ToOneField(UserResource, 'user', full=True , blank=True, null=True)
    coupon_applied = fields.ToOneField(CouponResource, 'coupon_applied', full=True, blank=True, null=True)
    carts = fields.ToManyField(CartResource,'cart_set',full=True,blank=True,null=True)

    class Meta:
        queryset = Order.objects.all()
        list_allowed_methods = ['post']
        detail_allowed_methods=['get']
        resource_name="order"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        # fields=['total_amount','final_amount','coupon_applied','address','status',]
        excludes=['modified_at','is_urgent','delivery_time']
        ordering=['created_at']
        filtering={
            'id':ALL,
            'user' : ALL_WITH_RELATIONS
        }

    def obj_create(self, bundle, request=None, **kwargs):
        # data={'status':'cant place order'}
        # return HttpResponse(data, content_type='application/json')
        print bundle.data
        phone_number =  bundle.data['phone_number']
        userName =  bundle.data['userName']
        email =  bundle.data['email']
        app_version =  bundle.data['app_version']
        device_id =  bundle.data['device_id']
        app_id =  bundle.data['app_id']
        bring_change_of =  int(bundle.data['bring_change_of'])

        address_str = bundle.data['address']
        landmark = bundle.data['landmark']
        location_show = bundle.data['location_show']
        location_id = bundle.data['location_id']
        coupon_id =""
        try:
            coupon_id = int(bundle.data['coupon_id'])
        except:
            pass

        coupon=None

        print 'coupon'
        print phone_number
        user = User.objects.filter(username=phone_number)
        print user
        print '----'
        if user:
            user=user[0]
            user.email = email
            user.first_name=userName.title()
            user.save()
            print 'user saved'
            userProfile =UserProfile.objects.filter(user=user)
            print 'userprofile'
            print userProfile
            print '----'
            if userProfile:
                userProfile = userProfile[0]
                userProfile.app_version=app_version
                userProfile.app_id=app_id
                userProfile.device_id=device_id
                userProfile.save()
            else:
                UserProfile(user=user,contact=int(phone_number),app_id=app_id,app_version=app_version,device_id=device_id).save()
        else:
            user=User.objects.create_user(phone_number,email,phone_number)
            user.first_name=userName.title()
            user.save()
            UserProfile(user=user,contact=int(phone_number),app_id=app_id,app_version=app_version,device_id=device_id).save()
        print 'user obj created'
        print coupon_id
        if coupon_id>0:
            coupon = Coupon.objects.get(pk=coupon_id)
            coupon.used_count+=1
            coupon.save()
            print coupon
            prev_order = Order.objects.filter(coupon_applied=coupon,user=user)
            print user
            if prev_order:
                if prev_order[0].status!=1:
                    print 'coupon invalidation1'
                    coupon=None
            print coupon
        print 'check for coupon'
        location = Location.objects.get(pk=location_id)
        address  = Address.objects.filter(user =user ,address=address_str,landmark=landmark)
        if address:
            address=address[0]
        else:
            address  = Address(user =user ,address=address_str,landmark=landmark,location_show=location_show,location=location )
            address.save()
        print 'address done'
        products = bundle.data['products']
        # print products
        products = products.split(',')
        product_ids = map(lambda x:x.split('::')[0],products)
        product_qns = map(lambda x:x.split('::')[1],products)
        print product_ids
        print product_qns
        order = Order(user = user,total_amount=0,address=address,status=3)
        order.delivery_time=dt.datetime.now()+dt.timedelta(hours=1)
        order.save()
        print 'order obj saved'
        total_amount = 0
        index=0

        ordered_services={}
        products_json=[]
        for p_id in product_ids:
            prd = StoreProductMapping.objects.get(pk=p_id)
            products_json.append({'spid':prd.id,'pid':prd.product.product.id,'name':prd.product.product.name,'price':prd.price,'discount':prd.discount,'qn':product_qns[index],'size_id':prd.product.size.id})
            service = prd.product.product.category.service
            if 'offer' in service.name.lower():
                OfferProductOrderMapping(device_id=device_id,order=order,offer_product=prd.offerproductmapping_set.all()[0]).save()
                OfferDeviceId(device_id=device_id).save()
            if str(service.id) not in ordered_services:
                ordered_services[str(service.id)]= 0
            total_amount+= int(product_qns[index])*(prd.price- prd.discount)
            ordered_services[str(service.id)]+= int(product_qns[index])*(prd.price- prd.discount)
            store = prd.store
            cart = Cart.objects.filter(order=order,store=store)
            if cart:
                cart=cart[0]
            else:
                cart = Cart(order=order,store=store)
                cart.save()

            OrderedProduct(product=prd,cart=cart,quantity=product_qns[index]).save()
            index+=1
        service_amount_ordered=[]
        for key in ordered_services:
            service_amount_ordered.append(str(key)+":"+str(ordered_services[key]))
        service_amount_ordered=';;'.join(service_amount_ordered)
        print total_amount

        final_amount=total_amount
        if coupon:
            if total_amount>=coupon.min_total:
                order.coupon_applied=coupon
                print 'found coupon'
                print coupon.code
                print coupon
                print user
                print location_id
                print int(app_version)
                print final_amount
                print service_amount_ordered
                discount = verify_coupon(coupon,user,location_id,int(app_version),final_amount,service_amount_ordered)['discount']
                print "discount" + str(discount)
                final_amount-=discount
        print "passed coupon part"
        delivery_charges = 0
        delivery_charges_to_save_in_order={}
        for key in ordered_services:
            service=Service.objects.get(pk=key)
            lsm = LocationServiceMapping.objects.filter(service=service,location=location)
            if lsm:
                lsm=lsm[0]
                stl = StoreTimingInLocation.objects.filter(store__is_active=True,is_active=True,lsm=lsm)
                print 'done'
                if stl:
                    stl=stl[0]
                    # print 'done1'
                    if key not in delivery_charges_to_save_in_order:
                        # print 'done10'
                        delivery_charges_to_save_in_order[key]={'delivery_charges':0,'delivery_amount_min':stl.delivery_min_amount}
                        # print 'done11'
                    if ordered_services[key]<stl.delivery_min_amount:
                        # print 'done20'
                        final_amount+=-stl.delivery_charges
                        total_amount+=stl.delivery_charges
                        # print 'done21'
                        delivery_charges_to_save_in_order[key]['delivery_charges']=stl.delivery_charges
                        # print 'done22'
                else:
                    delivery_charges_to_save_in_order[key]={'delivery_charges':0,'delivery_amount_min':0}
            else:
                delivery_charges_to_save_in_order[key]={'delivery_charges':0,'delivery_amount_min':0}
        print "passed delivery part"
        order.total_amount=total_amount
        order.final_amount=final_amount
        if bring_change_of:
            order.change_requested=bring_change_of
        order.delivery_charges = simplejson.dumps(delivery_charges_to_save_in_order)
        order.save()
        products_json=simplejson.dumps(products_json)
        Invoice(order=order,product_json=products_json).save()
        bundle.obj=order
        OrderActivity(order=order,user=order.user,actions=0,comment=" ").save()
        print bundle
        return bundle

class SuggestionResource(ModelResource):

    class Meta:
        queryset = Suggestion.objects.all()
        list_allowed_methods = ['get','post']
        detail_allowed_methods=['get']
        resource_name="suggestion"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at',]
        filtering={
            'id':ALL,
        }

    def obj_create(self, bundle, request=None, **kwargs):
        suggestion =  bundle.data['suggestion']
        comment =  bundle.data['comments']
        email =  bundle.data['email']
        suggestion = Suggestion(suggestion=suggestion,comment=comment,email=email)
        suggestion.save()
        bundle.obj=suggestion
        return bundle

class OrderStatusResource(ModelResource):

    address = fields.ToOneField(AddressResource, 'address', full=True, blank=True, null=True)
    user = fields.ToOneField(UserResource, 'user', full=False , blank=True, null=True)
    carts = fields.ToManyField(CartResource,'cart_set',full=True,blank=True,null=True)

    class Meta:
        queryset = Order.objects.filter(created_at__gte = dt.datetime.today().date()).order_by("-created_at")
        list_allowed_methods = ['get','post','patch']
        detail_allowed_methods=['get']
        resource_name="order_status"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at','delivery_time','change_requested','delivery_charges','paymentStatus','is_urgent',]
        ordering=['created_at']

        filtering={
            'id':ALL,
            'user' : ALL_WITH_RELATIONS,
        }
    def dehydrate(self, bundle):
        order_status={
            '0':'Delivered',
            '1' : 'CANCELLED',
            '2' : 'Confirmed',
            '3': 'Processing',
            '4' : 'Dispatched',
            '5' : 'Dispatched',
            '6' : 'Processing',
            '7' : 'We are on it.\nYour Order Will be Delivered Soon',
            '8' : 'Delivered'
        }
        bundle.data['status']=order_status[str(bundle.data['status'])].title()
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        contact = request.GET.get('user__username','')
        if not contact:
            return None
        for item in data['objects']:
            order = item.obj
            item.data['show_popup']='false'

            if order.delivery_time:
                if order.delivery_time < dt.datetime.now():
                    if order.status in [2,0]:
                        print 'yes'
                        item.data['show_popup']='true'
            else:
                if order.created_at + dt.timedelta(hours=1)< dt.datetime.now():
                    if order.status in [2,0]:
                        print 'yes1'
                        item.data['show_popup']='true'

            carts = item.data['carts']
            for cart in carts:
                service_id = cart.data['products'][0].data['product'].data['product'].data['product'].data['service_id']
                cart.data['service_id']=service_id
                cart.data['service_name']=Service.objects.get(pk=service_id).name
        del data['meta']
        return data

    def obj_create(self, bundle, request=None, **kwargs):

        order_id =  bundle.data['order_id']
        status =  bundle.data['status']
        contact =  bundle.data['contact']
        services=""
        try:
            services =  bundle.data['services']
        except:
            pass
        # print services[0]
        print 'ok'
        print order_id
        print status
        print contact

        print services
        print 'ok0'
        order = Order.objects.get(pk=order_id)

        if status and order.user.username==contact:
            if status=="no":
                service_names=""
                if services:
                    print 'ok1'
                    services=simplejson.loads(services)#.replace(' ','').split(',')
                    print services
                    service_names = ', '.join(map(lambda x:x.name,Service.objects.filter(pk__in=services)))
                    print service_names
                order.status=7
                order.save()
                if service_names:
                    OrderActivity(order=order,user=order.user,actions=8,comment="Order Not Delivered :: services:"+service_names).save()
                else:
                    OrderActivity(order=order,user=order.user,actions=8,comment="Order Not Delivered").save()
                thr = threading.Thread(target=notify_admin(order,service_names))
                thr.start()
            else:
                order.status=8
                order.save()
                OrderActivity(order=order,user=order.user,actions=7,comment="Delivery Confirmation By User ").save()
                print "order received"
        bundle.obj=order
        return bundle

class SuggestionResource(ModelResource):

    class Meta:
        queryset = Suggestion.objects.all()
        list_allowed_methods = ['get','post']
        detail_allowed_methods=['get']
        resource_name="suggestion"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at',]
        filtering={
            'id':ALL,
        }
    def obj_create(self, bundle, request=None, **kwargs):
        suggestion = bundle.data['suggestion']
        comments =bundle.data['comments']
        email = bundle.data['email']
        location_id = bundle.data['location_id']
        suggestion = Suggestion(location_id=location_id,suggestion=suggestion,comments=comments,email=email)
        suggestion.save()
        bundle.obj = suggestion
        return bundle

class VisitorResource(ModelResource):

    class Meta:
        queryset = Visitor.objects.all()
        list_allowed_methods = ['post']
        resource_name="register_app_id"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()

    def obj_create(self, bundle, request=None, **kwargs):
        email =  bundle.data['email']
        device_id =  bundle.data['device_id']
        app_id =  bundle.data['app_id']
        app_version =  bundle.data['app_version']
        platform =  bundle.data['platform']
        visitor=None
        if device_id:
            visitors = Visitor.objects.filter(device_id=device_id)
            if visitors:
                visitor=visitors[0]
                visitor.app_id=app_id
                visitor.app_version=app_version
        elif email:
            visitors = Visitor.objects.filter(email= email)
            if visitors:
                visitor=visitors[0]
                visitor.app_id=app_id
                visitor.app_version=app_version
        if not visitor:
            visitor=Visitor(email=email,device_id=device_id,app_version=app_version,app_id=app_id,platform=platform)
            visitor.save()

        bundle.obj=visitor
        return bundle

class OfferResource(ModelResource):

    class Meta:
        queryset = Offer.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods=['get']
        resource_name="offer"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['image','valid_till','modified_at','created_at',]
        filtering={
            'id':ALL,
        }

class OfferLocationResource(ModelResource):

    location = fields.ToOneField(LocationResource, 'location', full=False, blank=True, null=True)

    class Meta:
        queryset = OfferLocationMapping.objects.filter(is_active=True)
        list_allowed_methods = ['get',]
        detail_allowed_methods=['get']
        resource_name="offer_location"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at',]
        filtering={
            'id':ALL,
            'location' : ALL
        }

class OfferProductResource(ModelResource):

    product = fields.ToOneField(StoreProductResource, 'product', full=True, blank=True, null=True)
    offer = fields.ToOneField(OfferResource, 'offer', full=True, blank=True, null=True)

    class Meta:
        queryset = OfferProductMapping.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods=['get']
        resource_name="offer_product"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at',]
        filtering={
            'id':ALL,
            'offer' : ALL_WITH_RELATIONS
        }
    def alter_list_data_to_serialize(self, request, data):
        # Example iteration through data
        index=0
        status="We are out of stock "
        if len(data['objects'])==0:
            status = "out of stock"
        contact = request.GET.get('contact')
        device_id= request.GET.get('device_id')
        flag = False
        for item in data['objects']:
            offerproductMapping = item.obj
            # print item.obj.product
            # order = Order.objects.filter(user__username = contact,coupon_applied=coupon)
            # cart = Cart.objects.filter(products=offerproductMapping.product,order__user__userprofile__device_id=device_id).exclude(order__status=1)
            offer_device_id =  OfferProductOrderMapping.objects.filter(device_id=device_id)
            my_flag =False
            if contact!="":
                if OfferProductOrderMapping.objects.filter(order__user__username=contact):
                    my_flag  = True
            if offer_device_id or my_flag:
                flag =True
                del data['objects'][index]
            elif offerproductMapping.product.stock == False:
                del data['objects'][index]
	    else:
                index+=1
        del data['meta']
        if flag == True and len(data['objects'])==0:
            status="Offer already used by this device"
	else:
	    status = "Thanks for the overwhelming response.\nWe are out of stock.\nLet us get reloaded and will be ready to serve after 5pm today.\nCheers!!"
        data['status']=status
        return data

class OfferProductOrderResource(ModelResource):

    offer_product = fields.ToOneField(OfferProductResource, 'product', full=True, blank=True, null=True)
    order = fields.ToOneField(OrderResource, 'order', full=True, blank=True, null=True)

    class Meta:
        queryset = OfferProductOrderMapping.objects.all()
        list_allowed_methods = ['get',]
        detail_allowed_methods=['get']
        resource_name="offer_product_order"
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        excludes=['modified_at','created_at',]
        filtering={
            'id':ALL,
            'order' : ALL,
            'offer_product' : ALL
        }
