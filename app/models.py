import threading
from django.contrib.auth.models import User
from django.db import models
from django.contrib.gis.db.models import PolygonField
from geoposition.fields import GeopositionField
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import datetime as dt
import simplejson
from tastypie.authentication import ApiKeyAuthentication
from tastypie.models import create_api_key, ApiKey
from app.utils import constant



class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract =True

class Location(BaseModel):
    city = models.CharField(max_length=100)
    zone = models.CharField(max_length=100,default="")
    area = models.CharField(max_length=100)
    sub_area = models.CharField(max_length=100)
    mpoly = PolygonField()

    class Meta:
        unique_together = ('city', 'zone','area','sub_area',)

    def __unicode__(self):
        return self.sub_area+", "+self.area

class TimeSlot(BaseModel):

    start_time = models.TimeField()
    end_time = models.TimeField()
    def __unicode__(self):
        return str(self.start_time)+" to "+str(self.end_time)

    class Meta:
        unique_together = ('start_time', 'end_time',)


class UserProfile(BaseModel):
    user = models.OneToOneField(User)
    contact = models.BigIntegerField()
    app_id=models.CharField(max_length=250, blank=True, null=True)
    app_version=models.CharField(max_length=10, blank=True, null=True)
    device_id=models.CharField(max_length=300, blank=True, null=True)
    otp=models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.user.email


class Address(BaseModel):
    user = models.ForeignKey(User)
    address = models.CharField(max_length=500)
    landmark = models.CharField(max_length=150)
    location_show = models.CharField(max_length=500)
    location = models.ForeignKey(Location)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.address+' '+self.landmark+' '+ self.location_show + self.location.sub_area + self.location.area


class Service(BaseModel):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="/media/")
    def __unicode__(self):
        return self.name


class Store(BaseModel):
    
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    contact = models.TextField()
    address = models.CharField(max_length=1000L)
    position = GeopositionField(blank=True, default='19.101985614850385, 72.88626194000244')
    rating = models.IntegerField(default=0)
    open_time = models.TimeField()
    end_time = models.TimeField()
    is_active=models.BooleanField(default=True)

    backup_shops = models.ManyToManyField('self', blank=True, null=True)

    rush_hours = models.ManyToManyField(TimeSlot,related_name='rush_hour')
    normal_hours = models.ManyToManyField(TimeSlot,related_name='normal_hour')


    services = models.ManyToManyField(Service)
    weekly_off = models.IntegerField(default = -1)

    def __unicode__(self):
        return self.name



class LocationServiceMapping(BaseModel):

    service= models.ForeignKey(Service)
    location=models.ForeignKey(Location)
    stores = models.ManyToManyField(Store,null=True, through='StoreTimingInLocation',related_name='stores')

    is_active=models.BooleanField(default=True)
    is_coming_soon = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)



    def __unicode__(self):
        return self.service.name

    class Meta:
        unique_together = ('service', 'location',)

    def save(self, *args, **kwargs):

        # if self.stores.all().count()>=1:
        #     raise ValueError(str('Can Not Add Multiple Store for single service location mapping'))

        super(LocationServiceMapping, self).save(*args, **kwargs)


class StoreTimingInLocation(BaseModel):

    store = models.ForeignKey(Store)
    time_slot = models.ManyToManyField(TimeSlot)
    lsm = models.ForeignKey(LocationServiceMapping)

    delivery_charges = models.IntegerField(default=0)
    delivery_min_amount = models.IntegerField(default=0)
    normal_hours_delivery_time_min = models.IntegerField(default=60, help_text="Time in Minutes")
    rush_hours_delivery_time_min = models.IntegerField(default=60, help_text="Time in Minutes")

    is_active=models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        def check_overlap(t1_all,t2_all):
            for t1 in t1_all:
                for t2 in t2_all:
                    latest_start=max(t1.start_time,t2.start_time)
                    earliest_end = min(t2.end_time,t1.end_time)
                    if latest_start<earliest_end:
                        return True
            return False
        other_stores = filter(lambda x: check_overlap(x.time_slot.all(),self.time_slot.all()),StoreTimingInLocation.objects.filter(lsm=self.lsm,is_active=True).exclude(store=self.store))
        if other_stores and self.is_active:
            raise ValueError(str('Something is wrong with your mind!! Can Not Add Multiple Store for '+str(self.lsm.service)+" in "+str(self.lsm.location)))
        super(StoreTimingInLocation, self).save(*args, **kwargs)
    class Meta:
        unique_together = ('store','lsm',)

class Size(BaseModel):
    
    unit = models.CharField(max_length=100)
    magnitude =models.FloatField()
    description = models.CharField(max_length=500,default="")

    def __unicode__(self):
        return str(self.magnitude)+" "+self.unit

class Category(BaseModel):
    name = models.CharField(max_length=200)
    service = models.ForeignKey(Service)
    parent = models.ForeignKey('self', blank=True,null=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kw):
        serv = self.service
        par = self.parent
        if par:
            if par.service!= serv:
                raise ValueError(str('Entered Service and Parent Category Not Valid'))
        super(Category, self).save(*args, **kw)
        sub_cats = Category.objects.filter(parent=self)
        for s in sub_cats:
            print s.name
            s.service=self.service
            s.save()



class Tag(BaseModel):
    name = models.CharField(max_length=400)
    def __unicode__(self):
        return self.name

class SubSubCategory(BaseModel):

    name = models.CharField(max_length=255)
    sub_category = models.ForeignKey(Category)

    def save(self, *args, **kwargs):
        if not self.sub_category.parent:
            raise ValueError(str('invalid sub-category'))
        super(SubSubCategory, self).save(*args, **kwargs)




class Product(BaseModel):
    
    name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, limit_choices_to={'parent__gte': 1}, verbose_name="Sub Category")
    tags = models.ManyToManyField(Tag,blank=True,null=True)
    rating = models.IntegerField(default=0)
    barcode = models.TextField(blank=True, null=True)
    related_products = models.ManyToManyField('self',blank=True,null=True)

    sub_sub_category = models.ForeignKey(SubSubCategory,null=True)

    def __unicode__(self):
        return self.name


class ProductSizeImageMapping(BaseModel):
    product = models.ForeignKey(Product)
    size = models.ForeignKey(Size)
    image = models.ImageField(upload_to="/media/")
    is_basic_product = models.BooleanField(default=False)
    def __unicode__(self):
        return self.product.name

    def xs_image(self):
        return str(self.image).replace('/m/','/xs/')

    class Meta:
        unique_together = ('product', 'size',)


class StoreProductMapping(BaseModel):

    product = models.ForeignKey(ProductSizeImageMapping)
    store = models.ForeignKey(Store)

    price = models.FloatField(null=True, blank=True)
    price_to_movincart = models.FloatField(null=True, blank=True)
    discount = models.FloatField(default=0)

    stock = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    max_buy = models.IntegerField(default=20)
    freebies_list = models.CharField(max_length=100,blank=True,null=True)

    def __unicode__(self):
        return self.product.product.name+' '+str(self.product.size)+' '+str(self.price)

    def save(self, *args, **kwargs):
        if self.price==0 and self.stock:
            raise ValueError(str('Please add a price >0'))
        super(StoreProductMapping, self).save(*args, **kwargs)

    class Meta:

        unique_together = ('product', 'store',)
        permissions = (
            ("can_download_product_dump", "Can download products dump"),
        )

class StoreProductChanged(BaseModel):
    product = models.ForeignKey(StoreProductMapping)


class CouponRuleBook(BaseModel):

    MIN_TOTAL = 0 # minimum order total
    SERVICE_TYPE = 1 # Single Service or multi service or ALL services
    SERVICE_VALUE = 2 # Service ID for coupon Applied
    UNIVERSAL = 3 # universal if anyone can use this coupon anytime.. new_user if only new user can use coupon .. user_specific only one user can use this coupon
    USER_SPECIFIC =4 # username of user
    MAX_USE_NUMBER =5 # max use count
    LOCATION = 6 #
    CATEGORY = 7 #
    IGNORE_CATEGORY = 8 #
    VERSION_NUMBER = 9
    OFFER_USED_USER_CAN_USE =10
    CHOICES = ((MIN_TOTAL,'Minimum Total'),(SERVICE_TYPE,'Service Type'),(SERVICE_VALUE,'Service ID for Coupon'),(UNIVERSAL,'Universal'),(USER_SPECIFIC,'Username '),(MAX_USE_NUMBER,'Max Use Number'),
               (LOCATION,"Location"),(CATEGORY,'Category'),(IGNORE_CATEGORY,'Ingore Category'),(VERSION_NUMBER,'Version Number'),(OFFER_USED_USER_CAN_USE,'OFFER USED USER CAN USE'))

    rule_type = models.IntegerField(choices=CHOICES)
    rule_value = models.TextField()

    class Meta:
        unique_together = ('rule_type', 'rule_value',)

    def __unicode__(self):
        return self.get_rule_type_display()+' '+str(self.rule_value)

class OfferRuleBook(BaseModel):

    UNIVERSAL = 1 # universal if anyone can use this coupon anytime.. new_user if only new user can use coupon .. user_specific only one user can use this coupon
    USER_SPECIFIC =2 # username of user
    MAX_USE_NUMBER =3 # max use count
    LOCATION = 4 #
    CATEGORY = 5 #
    IGNORE_CATEGORY = 6 #
    VERSION_NUMBER = 7

    CHOICES = ((UNIVERSAL,'Universal'),(USER_SPECIFIC,'Username '),(MAX_USE_NUMBER,'Max Use Number'),
               (LOCATION,"Location"),(CATEGORY,'Category'),(IGNORE_CATEGORY,'Ingore Category'),(VERSION_NUMBER,'Version Number'))

    rule_type = models.IntegerField(choices=CHOICES)
    rule_value = models.TextField()

    def __unicode__(self):
        return self.get_rule_type_display()+" -- "+self.rule_value

    class Meta:
        unique_together = ('rule_type', 'rule_value',)


class Coupon(BaseModel):
    discount_type_choices = (
        (0, 'direct_minus'),
        (1, 'percent_minus')
    )
    code = models.CharField(max_length=100)
    discount = models.IntegerField()
    discount_type = models.IntegerField(choices=discount_type_choices)
    max_discount_limit = models.IntegerField()
    min_total =models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)
    rule_book = models.ManyToManyField(CouponRuleBook)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.code

class Order(BaseModel):

    DELIVERED = 0
    CANCELLED = 1
    PROCESSED = 2
    RECEIVED = 3
    DISPATCHED = 4
    HANDED_OVER = 5
    OLP_PENDING = 6
    ORDER_NOT_DELIVERED = 7
    DELIVERY_CONFIRMATION_BY_USER = 8
    CHOICES = ((DELIVERED, 'Delivered'), (CANCELLED, 'Cancelled'), (PROCESSED, 'Processed'),
               (RECEIVED, 'Received'), (DISPATCHED, 'Dispatched'), (HANDED_OVER, 'Handed Over'),
               (OLP_PENDING,'OLP in proc'),(ORDER_NOT_DELIVERED ,'Order Not Delivered'),
               (DELIVERY_CONFIRMATION_BY_USER,"Delivery Confirmation By User"),)

    user = models.ForeignKey(User)
    total_amount = models.FloatField(help_text='')
    final_amount = models.FloatField(blank=True, null=True, editable=False)
    coupon_applied = models.ForeignKey(Coupon, blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True, help_text="To schedule delivery")
    address = models.ForeignKey(Address)
    status = models.IntegerField(choices=CHOICES)
    is_urgent = models.BooleanField(default=False)
    delivery_charges = models.TextField()
    change_requested = models.IntegerField(blank=True,null=True)

    COD = 0
    OLP_IN_PROC = 1
    PAID_OL = 2
    OLP_FAILED = 3
    REFUNDED = 4

    PAYMENT_CHOICES = ((COD,'COD'),(OLP_IN_PROC,'OLP in Proc'),
    (PAID_OL,'Paid Online'),
    (OLP_FAILED,'OLP Failed'), (REFUNDED,'Refunded'))
    paymentStatus = models.IntegerField(choices=PAYMENT_CHOICES, default=0)

    online_payment = models.ForeignKey('OnlineTransaction',null=True,blank=True)

    def __unicode__(self):
        return str(self.user.username)

    def save(self, *args, **kwargs):
        if self.address.user != self.user:
            raise ValueError(str('invalid address'))
        super(Order, self).save(*args, **kwargs)

    class Meta:
        permissions = (
            ("can_download_order_dump", "Can download orders dump"),
        )

class Cart(BaseModel):

    store = models.ForeignKey(Store)
    order = models.ForeignKey(Order)
    products= models.ManyToManyField(StoreProductMapping,through='OrderedProduct',related_name='products1')

    def __unicode__(self):
        return self.store.name

class OrderedProduct(models.Model):

    product = models.ForeignKey(StoreProductMapping,editable=False)
    cart = models.ForeignKey(Cart)
    quantity = models.IntegerField(default=1)

class CouponDeviceIdMapping(BaseModel):

    user = models.ForeignKey(User)
    order=models.ForeignKey(Order)
    coupon = models.ForeignKey(Coupon)
    device_id = models.CharField(max_length=250)

    def __unicode__(self):
        return self.coupon.code

class Invoice(BaseModel):
    order = models.OneToOneField(Order)
    product_json = models.TextField()

    def __unicode__(self):
        return self.order.user.username

class Suggestion(BaseModel):
    suggestion = models.TextField()
    comments = models.TextField()
    email = models.EmailField()
    location = models.ForeignKey(Location)

class Visitor(BaseModel):

    email=models.CharField(max_length=50,blank=True,null=True)
    app_id=models.CharField(max_length=250)
    app_version=models.CharField(max_length=10)
    device_id=models.CharField(max_length=100,blank=True,null=True)
    platform=models.CharField(max_length=50)

class Offer(BaseModel):

    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="/media/")
    valid_till = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    rule_book = models.ManyToManyField(OfferRuleBook)

    def __unicode__(self):
        return self.name

class OfferLocationMapping(BaseModel):

    offer = models.ForeignKey(Offer)
    location = models.ForeignKey(Location)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('offer', 'location',)

class OfferProductMapping(BaseModel):

    offer = models.ForeignKey(Offer)
    product = models.ForeignKey(StoreProductMapping)

    class Meta:
        unique_together = ('offer', 'product',)


class OfferProductOrderMapping(BaseModel):

    order=models.ForeignKey(Order,unique=True)
    offer_product = models.ForeignKey(OfferProductMapping)
    device_id = models.CharField(max_length=500,default=None)

class OfferDeviceId(BaseModel):
    device_id = models.CharField(max_length=500,default=None)

class OrderActivity(BaseModel):

    RECEIVED = 0
    ORDER_TAKEN = 1
    CALL_SHOP = 2
    CALL_CUSTOMER = 3
    FF_PASS = 4
    CALL_DB = 5
    PLACED = 6
    POSITIVE_DELIVERY_CONFIRMATION_BY_CUSTOMER = 7
    NEGATIVE_DELIVERY_CONFIRMATION_BY_CUSTOMER = 8
    CANCELLED = 9
    DELIVERY_CONFIRMATION_BY_CS = 10
    ORDER_ITEM_CHANGED = 11
    DELIVERY_CONFIRMATION_NOTIFICATION_AUTO= 12
    ACTION_CHOICES = ((RECEIVED, 'Order Received'), (ORDER_TAKEN, 'Order Taken'), (CALL_SHOP, 'Call to Shop'),
               (CALL_CUSTOMER, 'Call to Customer'), (FF_PASS, 'FF Pass'), (CALL_DB, 'Call to Delivery Boy'),
               (PLACED,'Order Placed'),(POSITIVE_DELIVERY_CONFIRMATION_BY_CUSTOMER ,'Delivery Confirmed by Customer'),
               (NEGATIVE_DELIVERY_CONFIRMATION_BY_CUSTOMER, 'Delivery Declined By Customer'),(CANCELLED, 'Order Cancelled'),
               (DELIVERY_CONFIRMATION_BY_CS, 'Delivery Confirmation By CS'), (ORDER_ITEM_CHANGED, 'Order Items Changed'),
                      (DELIVERY_CONFIRMATION_NOTIFICATION_AUTO,'Delivery Confirmation notification sent'))

    actions = models.IntegerField(choices=ACTION_CHOICES)
    user = models.ForeignKey(User)
    order = models.ForeignKey(Order)
    comment = models.TextField()

    def __unicode__(self):
        return str(self.user.first_name)+" "+self.get_actions_display()

class OnlineTransaction(BaseModel):
    CITRUS = 0
    PAYU = 1
    CHOICES = ((CITRUS,'Citrus'), (PAYU, 'PayU Money'))
    FAILED = 0
    SUCCESS = 1
    IN_PROCESS = 2
    STATUS_CHOICES = ((IN_PROCESS,'In process'),(FAILED,'Failed'),(SUCCESS,'success'))
    gateway = models.IntegerField(choices=CHOICES)
    txn_id = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.IntegerField(choices=STATUS_CHOICES)

#============================================================================================================================================================================================
#                                                            signals
#============================================================================================================================================================================================
# method for sending mail after order saved
# models.signals.post_save.connect(create_api_key, sender=User)

@receiver(post_save, sender=User)
def create_apikey(sender,instance,**kwargs):
    apikey = ApiKey.objects.get_or_create(user=instance)

@receiver(post_save, sender=Order)
def send_mail_to_cc(sender, instance,**kwargs):

    if instance.final_amount>0 and instance.status==3:
        thr = threading.Thread(target=send_simple_mail, args=[instance])
        thr.start()

def send_simple_mail(order):

    old_orders = Order.objects.filter(user=order.user)
    is_new_user = True
    if order.user.username in constant.old_users:
        is_new_user=False
    if old_orders:
        if old_orders.count()>1:
            is_new_user = False
    msg = ""
    if is_new_user:
        msg="New User\n"
    else:
        msg="Old User\n"
    print "sending mail"
    msg += "\nName: "+str(order.user.first_name).title()
    msg += "\nMobile: "+str(order.user.userprofile.contact)
    msg += "\nEmail: "+str(order.user.email)
    msg += "\nDelivery Address : "+str(order.address)
    msg += "\nAmount to be collected in cash: "+str(order.final_amount)

    if order.delivery_time:
        msg += "\nDelivery Time : " + order.delivery_time.strftime('%B %d, %Y, %I:%M %p')
    else:
        delivery_time = order.created_at + dt.timedelta(hours=1)
        msg += "\nDelivery Time : " + delivery_time.strftime('%B %d, %Y, %I:%M %p')

    if order.change_requested:
        msg += "\nBring change of : " + str(order.change_requested)
    else:
        if order.final_amount % 1000 < 100:
            bring_change_of = "100"
        elif order.final_amount % 1000 < 500:
            bring_change_of = "500"
        else:
            bring_change_of = "1000"
        msg += "\n(Auto) Bring change of : " + str(bring_change_of)
    msg += "\n\nItems are Following:\n\n"
    ordered_services = {}
    ordered_services_with_items = {}
    product_json = simplejson.loads(order.invoice.product_json)
    prev_offer_order=[]
    for p in product_json:
        prd = StoreProductMapping.objects.get(pk=p['spid'])
        service = prd.product.product.category.service
        if str(service) not in ordered_services:
            ordered_services[str(service)] = 0
            ordered_services_with_items[str(service)] = []

        price = float(p['price'])-float(p['discount'])
        total_price = int(price)*int(p['qn'])
        name = str(prd.product.product.name)+"  "+str(prd.product.size.magnitude)+"  "+str(prd.product.size.unit)

        ordered_services[str(service)] += total_price
        ordered_services_with_items[str(service)].append({
            'name': name,
            'price': str(price),
            'qn': p['qn'],
            'total_price': total_price
        })
    if order.coupon_applied:
        coupon=order.coupon_applied
        for key in ordered_services:
            disc = verify_coupon(coupon,order.user,order.address.location_id,int(order.user.userprofile.app_version),int(ordered_services[key]),str(Service.objects.filter(name=str(key))[0].id)+":"+str(ordered_services[key]),flag=0)['discount']
            ordered_services[key]-=disc
    for key in ordered_services:
        index_key = 1
        msg += key+":\t"+str(ordered_services[key])+"\n"
        for oswi in ordered_services_with_items[key]:
            msg += '\t'+str(index_key)+'. '+oswi['name']+"  Price: "+str(oswi['price'])\
                   + "  Qty: " + str(oswi['qn'])+" Total : "+str(oswi['total_price'])+"\n"
            index_key += 1
        msg += '\n'
    date = dt.datetime.now().date()
    send_mail('New Order Placed '+str(date), msg, 'query@movincart.com', settings.LIST_FOR_MAILS, fail_silently=False)
    print "mail sent"


@receiver(pre_delete, sender=StoreProductMapping)
@receiver(post_save, sender=StoreProductMapping)
def update_product_changed(sender, *args, **kwargs):
    sp = kwargs.get('instance')
    if StoreProductChanged.objects.filter(product=sp).count() == 0:
        StoreProductChanged(product=sp).save()


import json

def verify_coupon(coupon, user,location,version,total=0, service_amount_ordered=None,flag=1):
    # print 'verify'
    status=""
    if not can_user_use_coupon(coupon,user) and flag==1:
        status = "Promo Code is not valid"
        return {'discount':0,'status':status}
    rules = coupon.rule_book.all().values('rule_type','rule_value')
    rule_types = map(lambda x: x['rule_type'],rules)
    rule_values = map(lambda x: x['rule_value'],rules)

    if 10 in rule_types:
        if OfferDeviceId.objects.filter(device_id=user.userprofile.device_id):
            status="Sorry you have already availed 1 rupee offer"
            return {'discount':0,'status':status}
    if 6 in rule_types:
        index = rule_types.index(6)
        value = rule_values[index]
        value = json.loads(value)
        if int(location) not in value:
            status="Promo code is not valid in your location"
            return {'discount':0,'status':status}

    if 9 in rule_types:
        index = rule_types.index(9)
        value = int(rule_values[index])
        if version < value:
            status="Promo code is valid only on updated app"
            return {'discount':0,'status':status}

    if 5 in rule_types:
        index = rule_types.index(5)
        value = int(rule_values[index])
        if coupon.used_count > value:
            status = "Promo Code is not valid"
            return {'discount':0,'status':status}

    if 3 in rule_types:
        index = rule_types.index(3)
        value = rule_values[index]
        if 'new_user' == value:
            orders = Order.objects.filter(user = user)
            if orders.count() == 0:
                status="Code is valid only for new users"
                return {'discount':0,'status':status}
        elif 'user_specific' == value:
            index = rule_types.index(4)
            value = rule_values[index]
            if user.username not in value:
                status = "Promo Code Is Not Valid"
                return {'discount':0,'status':status}

    # print service_amount_ordered
    discount = 0
    index = rule_types.index(1)
    value = rule_values[index]
    services = json.loads(value)
    # print services
    service_ordered = map(lambda x: x.split(':')[0],service_amount_ordered.split(';;'))
    # print service_ordered
    total_ordered_for_service=0
    for s in service_ordered:
        if int(s) in services:
            total_ordered_for_service += int(float((filter(lambda x: x.split(':')[0]==s,service_amount_ordered.split(';;'))[0].split(":"))[1]))
    # print total_ordered_for_service
    index = rule_types.index(0)
    value = int(rule_values[index])
    if value<total_ordered_for_service or flag==0:
        discount = get_discount_for_coupon(coupon,total_ordered_for_service,discount)
        if flag==0 and discount >total_ordered_for_service:
            discount=total_ordered_for_service
    else:
        status_above_part=""
        if value>0:
            status_above_part=" above "+str(value)
        if len(services)>2:
            status="Promo code is valid on order"+status_above_part
        else:
            status="Promo code is valid on order"+status_above_part+" for "+', '.join(map(lambda x:x.name,Service.objects.filter(id__in=services)))

    if discount == 0:
        return {'discount':0,'status':status}
    return {'discount':discount,'status':status}



def get_discount_for_coupon(coupon,total,current_discount):

    if coupon.discount_type == 0:
        discount = coupon.discount
    else:
        discount = (total*coupon.discount) / 100
        if discount > coupon.max_discount_limit:
            discount = coupon.max_discount_limit
    if discount + current_discount > coupon.max_discount_limit:
        return coupon.max_discount_limit
    return discount + current_discount




def can_user_use_coupon(coupon,user):
    prev_orders = Order.objects.filter(user=user,coupon_applied=coupon).exclude(status=1)
    if prev_orders:
        return False
    prev_orders = Order.objects.filter(user__userprofile__device_id=user.userprofile.device_id,coupon_applied=coupon).exclude(status=1)
    if prev_orders:
        return False
    return True