from operator import itemgetter
from django.core.exceptions import ObjectDoesNotExist
from tastypie.models import ApiKey
from app.models import UserProfile, Order, Size, StoreProductMapping, StoreTimingInLocation, OfferLocationMapping, \
    OfferProductOrderMapping, Category, Suggestion, Location, Address, Invoice, Coupon, Cart, OrderedProduct, \
    OrderActivity, Service, LocationServiceMapping, Offer, OfferDeviceId
from app.utils import sms_send_otp
from app.models import verify_coupon
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import simplejson
import datetime as dt
import time
import threading
from app.utils import constant, api_helper
from app.utils.send_mail import notify_admin
from django.db.models import Q
from django.core.mail import send_mail

order_status_display={
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

@csrf_exempt
def send_otp(request):
    try:
        name = request.POST.get('name', '')
        username = ""
        if 'username' in request.POST.keys():
            username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        app_id = request.POST.get('app_id', '')
        device_id = request.POST.get('device_id', '')
        app_version = request.POST.get('app_version', '')
        if username:
            user = User.objects.filter(username=username)

            if not user:
                user = User.objects.create_user(str(username), str(email), str(username))
                user.first_name = name
                user.save()
                apikey = ApiKey.objects.get_or_create(user=user)
                UserProfile(user=user, contact=int(username), app_id=app_id, app_version=app_version,
                            device_id=device_id).save()
            else:
                user = user[0]
                apikey = ApiKey.objects.get_or_create(user=user)
                if not UserProfile.objects.filter(user=user):
                    UserProfile(user=user, contact=int(username), app_id=app_id, app_version=app_version,
                                device_id=device_id).save()

            sms_send_otp.send_otp(user)
        else:
            print "not a valid username "
        return HttpResponse("Done", content_type='application/json')
    except Exception as error_in_function:
        print "send_otp: {0}".format(str(error_in_function))


@csrf_exempt
def check_otp_sync_address(request):
    try:
        data = []
        username = request.GET.get('username', '')
        email = request.GET.get('email', '')
        app_id = request.GET.get('app_id', '')
        device_id = request.GET.get('device_id', '')
        app_version = request.GET.get('app_version', '')
        name = request.GET.get('name', '')
        otp = request.GET.get('otp', '')
        user = User.objects.get(username=username)
        print username
        customer = user.userprofile
        print otp
        if customer.otp == otp:

            customer.contact = int(username)
            customer.app_id = app_id
            customer.app_version = app_version
            customer.device_id = device_id
            user.first_name = name
            user.email = email
            customer_addresses = Address.objects.filter(user=user).exclude(location_show=None)
            for address in customer_addresses:
                data.append(
                    {'id': address.id, 'address': address.address, 'landmark': address.landmark, 'location_show': address.location_show,
                     'location_id': address.location.id})
            print data
            api_key = ApiKey.objects.get(user=user)
            print api_key
            customer.otp = None
            customer.save()
            user.save()
            print user
            data = simplejson.dumps({'fields': data, 'api_key': api_key.key})
        return HttpResponse(data, content_type='application/json')
    except Exception as e:
        print "check_otp_sync_address : " + str(e)


@csrf_exempt
def get_past_orders(request):
    data = []
    username = request.GET.get('username', '')

    user_api_key = request.GET.get('api_key', '')
    user = User.objects.get(username=username)
    api_key = ApiKey.objects.get(user=user)
    if api_key.key != user_api_key:
        return HttpResponse("", content_type='application/json')

    orders = Order.objects.filter(user=user).order_by('-created_at')
    if orders:
        for order in orders:
            try:
                address = order.address
                delivery_time = "Processing"
                if order.status == 1:
                    delivery_time = "Order Cancelled"
                elif order.status != 0 and order.status != 8:
                    current_time = dt.datetime.now()
                    current_time = int(time.mktime(current_time.timetuple()))
                    delivery_time_int = (order.created_at + dt.timedelta(hours=1))
                    delivery_time_int = int(time.mktime(delivery_time_int.timetuple()))
                    if int(current_time) < int(delivery_time_int):
                        delivery_time = (order.created_at + dt.timedelta(hours=1)).strftime('%I:%M %p')
                        delivery_time = "Will be delivered before\n" + delivery_time
                elif order.status == 0 or order.status == 8:
                    delivery_time = order.modified_at.strftime('%I:%M %p, %B %d, %Y')
                    delivery_time = "Delivered on\n" + delivery_time

                products = simplejson.loads(order.invoice.product_json)

                carts = []
                p_data = []
                for p in products:
                    product = {'name': p['name']}
                    size = Size.objects.get(pk=p['size_id'])
                    size = {'unit': size.unit, 'magnitude': size.magnitude}
                    prd_size_image = StoreProductMapping.objects.get(pk=p['spid']).product
                    image = prd_size_image.image
                    print image
                    product1 = {'image': str(image), 'product': product, 'size': size}
                    product2 = {'product': product1, 'id': 0, 'max_buy': 0, 'display_order': 0, 'price': p['price'],
                                'discount': p['discount']}
                    p_data.append({'product': product2, 'quantity': p['qn']})
                carts.append({'products': p_data})
                data1 = {'address': address.address, 'landmark': address.landmark,
                         'location_show': address.location_show, 'location_id': address.location.id,
                         'user': address.user.id}
                data2 = {'email': order.user.email, 'username': order.user.username}
                data.append(
                    {'address': data1, 'user': data2, 'carts': carts, 'change_requested': order.change_requested,
                     'final_amount': order.final_amount,
                     'id': order.id, 'status': 0, 'total_amount': order.total_amount, 'order_status': delivery_time})
            except ObjectDoesNotExist:
                pass
    data = simplejson.dumps({'objects': data})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_available_services(request):
    # api/v1/available_services/?format=json&location__mpoly__contains=&version=32&device_id=00000000-6305-d2aa-e2d5-38766587c3b3&contact=9820794989
    settings = {
        'version_no': constant.APP_VERSION,
        'time_slots': ';;'.join(constant.timeSlot)
    }
    data = []

    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    version = request.GET.get('version','0')
    device_id = request.GET.get('device_id')
    contact = request.GET.get('contact','')
    update_flg = False
    try:
        if contact:
            user = User.objects.filter(username=contact)
            if user:
                user=user[0]
                up = user.userprofile
                if OfferDeviceId.objects.filter(device_id=up.device_id):
                    if not OfferDeviceId.objects.filter(device_id=device_id):
                        OfferDeviceId(device_id=device_id).save()
                up.device_id=device_id
                up.verson = int(version)
                up.save()
                update_flg = True

        email=request.GET.get('email','')
        if email and not update_flg:
            user = User.objects.filter(email=email)
            if user:
                user=user[0]
                up = user.userprofile
                if OfferDeviceId.objects.filter(device_id=up.device_id):
                    if not OfferDeviceId.objects.filter(device_id=device_id):
                        OfferDeviceId(device_id=device_id).save()
                up.device_id=device_id
                up.verson = int(version)
                up.save()
                update_flg = True

        email=request.GET.get('preferred_email','')
        if email and not update_flg:
            user = User.objects.filter(email=email)
            if user:
                user=user[0]
                up = user.userprofile
                if OfferDeviceId.objects.filter(device_id=up.device_id):
                    if not OfferDeviceId.objects.filter(device_id=device_id):
                        OfferDeviceId(device_id=device_id).save()
                up.device_id=device_id
                up.verson = int(version)
                up.save()
    except:
        pass
    pkt = 'POINT(' + lat + ' ' + lng + ')'
    try:
        location_obj = Location.objects.get(mpoly__contains=pkt)
    except:
        location_obj = None
    if not location_obj:
        print 'location not found'
        data = simplejson.dumps({'objects': data, 'settings': settings})
        return HttpResponse(data, content_type='application/json')
    current_location_id = location_obj.id

    if int(version)>=constant.APP_VERSION:
        if api_helper.get_cat_structure_for_service_super_saver(location_obj):
            store_timing_in_location = StoreTimingInLocation.objects.filter(is_active=True)
            if store_timing_in_location:
                store_timing_in_location=store_timing_in_location[0]
            else:
                store_timing_in_location = StoreTimingInLocation.objects.all()[0]
            service = Service.objects.get(pk=16)
            data.append({
                'isComingSoon': False,
                'display_order': 0,
                'service': {
                    'delivery_charges': store_timing_in_location.delivery_charges,
                    'delivery_min_amount': store_timing_in_location.delivery_min_amount,
                    'delivery_time_min': store_timing_in_location.normal_hours_delivery_time_min,
                    'operating_time_end': str(store_timing_in_location.time_slot.all()[0].end_time),
                    'operating_time_start': str(store_timing_in_location.time_slot.all()[0].start_time),
                    'category': api_helper.get_cat_structure_for_service_super_saver(location_obj),
                    'name': service.name,
                    'id': service.id,
                    'image': str(service.image),
                }
            })
    location_service_mappings = LocationServiceMapping.objects.filter(service__is_active=True,location=location_obj,is_active=True,).exclude(service__id=16).distinct().order_by('-display_order')


    services = []
    for lsm in location_service_mappings:
        if lsm.service.id not in services:
            services.append(lsm.service.id)
            store_timing_in_location = StoreTimingInLocation.objects.filter(is_active=True, lsm=lsm)
            if store_timing_in_location:
                store_timing_in_location=store_timing_in_location[0]
            else:
                store_timing_in_location = StoreTimingInLocation.objects.all()[0]

            service = lsm.service
            data.append({
                'isComingSoon': lsm.is_coming_soon,
                'display_order': lsm.display_order,
                'service': {
                    'delivery_charges': store_timing_in_location.delivery_charges,
                    'delivery_min_amount': store_timing_in_location.delivery_min_amount,
                    'delivery_time_min': store_timing_in_location.normal_hours_delivery_time_min,
                    'operating_time_end': str(store_timing_in_location.time_slot.all()[0].end_time),
                    'operating_time_start': str(store_timing_in_location.time_slot.all()[0].start_time),
                    'category': api_helper.get_cat_structure_for_service_v2(service, location_obj),
                    'name': service.name,
                    'id': service.id,
                    'image': str(service.image),
                }
            })


    # data = sorted(data, key=itemgetter('display_order'))
    offer_data = {}
    offer = OfferLocationMapping.objects.filter(location=current_location_id, is_active=True, offer__is_active=True)
    if version and offer:
        offer_location_mapping = offer[0]
        offer = offer[0].offer
        offer_product_mapping = offer.offerproductmapping_set.all()[0]
        if not contact:
            contact = ""

        if (not OfferDeviceId.objects.filter(device_id=device_id)) and offer_product_mapping.product.stock:
            offer_data['id'] = offer_location_mapping.id
            offer_data['image'] = str(offer.image)
    if offer_data:
        data = simplejson.dumps(
            {'current_location_id': current_location_id, 'objects': data, 'offer': offer_data, 'settings': settings})
    else:
        data = simplejson.dumps({'current_location_id': current_location_id, 'objects': data, 'settings': settings})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_store_products(request):
    data = []
    location_id = request.GET.get('location')
    cat_id = request.GET.get('category')
    search_regex = request.GET.get('keyword')
    service_id = request.GET.get('service','')
    version = request.GET.get('version','')
    sps = []
    meta = {
        'limit': 12,
        'next': None,
        'offset': int(request.GET.get('offset', '0')),
        'previous': None,
        'total_count': 0
    }
    if location_id and cat_id:
        # print 'done'
        cat = Category.objects.get(pk=cat_id)
        service = cat.service
        sps=[]
        shops = map(lambda x: x.store,
                    StoreTimingInLocation.objects.filter(lsm__location=location_id,
                                                         lsm__service__is_active=True, is_active=True,
                                                        store__is_active=True).distinct())
        if version:
            if version >=constant.APP_VERSION:
                if str(service_id)=='16':
                    sps = StoreProductMapping.objects.filter(store__in=shops, stock=True,discount__gt=0,
                                                 product__product__category__is_active=True,
                                                 product__product__category__parent__is_active=True,
                                                 product__product__category=cat).distinct()
        if not sps:
            sps=StoreProductMapping.objects.filter(store__in=shops, stock=True,
                                                 product__product__category__is_active=True,
                                                 product__product__category__parent__is_active=True,
                                                 product__product__category=cat).distinct()
        meta['total_count'] = sps.count()
        sps = sps.order_by('product__product__sub_sub_category','display_order')[meta['offset']:meta['offset'] + meta['limit']]
        if meta['offset'] + meta['limit'] < meta['total_count']:
            if version:
                meta['next'] = "/api/v2/get_store_product/?limit=" + str(meta['limit']) + "&location=" + str(
                        location_id) + "&category=" + str(cat_id) + "&offset=" + str(meta['offset'] + meta['limit']) + "&format=json&version="+str(version)+"&service="+str(service_id)
            else:
                meta['next'] = "/api/v2/get_store_product/?limit=" + str(meta['limit']) + "&location=" + str(
                        location_id) + "&category=" + str(cat_id) + "&offset=" + str(meta['offset'] + meta['limit']) + "&format=json"


    elif search_regex and location_id:
        print search_regex
        keyword = search_regex.split(' ')
        regex = "^"
        for key in keyword:
            regex += "(?=.*" + key.strip() + ")"
        regex += ".*$"
        shops = map(lambda x: x.store,
                    StoreTimingInLocation.objects.filter(lsm__location=location_id, lsm__service__is_active=True,
                                                         is_active=True, store__is_active=True).distinct())
        sps = StoreProductMapping.objects.filter(store__in=shops, stock=True,
                                                 product__product__category__is_active=True,
                                                 product__product__category__parent__is_active=True,
                                                 product__product__tags__name__iregex=regex).distinct()
        meta['total_count'] = sps.count()
        # print offset

        sps = sps.order_by('product__product__sub_sub_category','display_order')[meta['offset']:meta['offset'] + meta['limit']]
        if meta['offset'] + meta['limit'] < meta['total_count']:
            meta['next'] = "/api/v2/get_store_product/?limit=" + str(meta['limit']) + "&location=" + str(
                location_id) + "&keyword=" + search_regex + "&offset=" + str(meta['offset'] + meta['limit']) + "&format=json"

    # print total

    for sp in sps:
        prd = sp.product.product
        service = sp.product.product.category.service
        data.append({
            'discount': int(sp.discount),
            'id': sp.id,
            'price': int(sp.price),
            'max_buy': sp.max_buy,
            'image': str(sp.product.image),
            'size': str(sp.product.size),
            'category': prd.category.id,
            'name': prd.name,
            'service_id': service.id,
        })


    data = simplejson.dumps({'meta': meta, 'objects': data})

    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_products_per_category(request):
    ids = request.GET.get('category_ids').split(',')
    version = request.GET.get('version','')
    service = request.GET.get('service','')
    location_id = request.GET.get('location')
    data = []

    cats = Category.objects.filter(pk__in=ids)
    shops = map(lambda x: x.store,
                StoreTimingInLocation.objects.filter(lsm__location__id=location_id,
                                                     is_active=True, store__is_active=True).distinct())

    for cat in cats:
        cat_data = {
            'id': cat.id,
            'products': [],
        }
        sps=[]
        if version:
            if version >= constant.APP_VERSION:
                if service=='16':
                    sps = StoreProductMapping.objects.filter(store__in=shops, stock=True,
                                                 product__product__category__is_active=True,discount__gt=0,
                                                 product__product__category__parent=cat).order_by('product__product__sub_sub_category','display_order').distinct()[:6]
        if not sps:
            sps = StoreProductMapping.objects.filter(store__in=shops, stock=True,
                                                 product__product__category__is_active=True,
                                                 product__product__category__parent=cat).order_by('product__product__sub_sub_category','display_order').distinct()[:6]

        for sp in sps:
            prd = sp.product.product
            cat_data['products'].append({
                'discount': int(sp.discount),
                'id': sp.id,
                'price': int(sp.price),
                'max_buy': sp.max_buy,
                'image': str(sp.product.image),
                'size': str(sp.product.size),
                'category': prd.category.id,
                'name': prd.name,
                'service_id': prd.category.service.id,
            })
        data.append(cat_data)
    data = simplejson.dumps({'objects': data})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def process_order(request):
    print 'placing order'

    try:
        phone_number = request.POST.get('phone_number')
        user_name = request.POST.get('userName')
        email = request.POST.get('email')
        app_version = request.POST.get('app_version')
        device_id = request.POST.get('device_id')
        app_id = request.POST.get('app_id')
        bring_change_of = int(request.POST.get('bring_change_of', '0'))
        address_str = request.POST.get('address')
        landmark = request.POST.get('landmark')
        location_show = request.POST.get('location_show')
        location_id = request.POST.get('location_id')
        api_key = request.POST.get('api_key')
        products = request.POST.get('products')
        tomorrow = request.POST.get('tomorrow')
        delivery_time = request.POST.get('delivery_time')
        # print request
        coupon_id = int(request.POST.get('coupon_id', '0'))

        coupon = None

        print 'coupon'
        print phone_number
        user = User.objects.get(username=phone_number)
        if user:
            user.email = email
            user.first_name = user_name.title()
            user.save()
            user_profile = user.userprofile
            user_profile.app_version = app_version
            user_profile.app_id = app_id
            user_profile.device_id = device_id
            user_profile.save()
            if user.api_key.key != api_key:
                print 'api key is not valid'
                data = simplejson.dumps({'status': 'Not Valid Request'})
                return HttpResponse(data, content_type='application/json', status=403)
        else:
            print 'User not found'
            data = simplejson.dumps({'status': 'Not Valid Request'})
            return HttpResponse(data, content_type='application/json', status=403)

        print 'user obj created'
        print coupon_id

        if coupon_id > 0:
            coupon = Coupon.objects.get(pk=coupon_id)
            coupon.used_count += 1
            coupon.save()
            print coupon
            prev_order = Order.objects.filter(coupon_applied=coupon, user=user)
            print user
            if prev_order:
                if prev_order[0].status != 1:
                    print 'coupon invalidation1'
                    coupon = None
            print coupon
        print 'check for coupon'
        location = Location.objects.get(pk=location_id)
        address = Address.objects.filter(user=user, address=address_str, landmark=landmark)
        if address:
            address = address[0]
            address.location = location
            address.save()
        else:
            address = Address(user=user, address=address_str, landmark=landmark, location_show=location_show,
                              location=location)
            address.save()
        print 'address done'

        # print products
        products = products.split(',')
        product_ids = map(lambda x: x.split('::')[0], products)
        product_qns = map(lambda x: x.split('::')[1], products)
        print product_ids
        print product_qns
        order = Order(user=user, total_amount=0, address=address, status=3)
        if tomorrow == '1':
            print delivery_time
            if dt.datetime.now().hour > 20:
                order.delivery_time = dt.datetime.strptime(
                    str((dt.datetime.now() + dt.timedelta(days=1)).date()) + " " + delivery_time, "%Y-%m-%d %I:%M %p")
            else:
                order.delivery_time = dt.datetime.strptime(str(dt.datetime.now().date()) + " " + delivery_time,
                                                           "%Y-%m-%d %I:%M %p")
        else:
            order.delivery_time = dt.datetime.now() + dt.timedelta(hours=1)
        if bring_change_of:
            order.change_requested = bring_change_of
        order.save()
        invoice = Invoice(order=order, product_json="")
        invoice.save()
        print 'order obj saved'
        total_amount = 0
        index = 0

        ordered_services = {}
        products_json = []
        for p_id in product_ids:
            prd = StoreProductMapping.objects.get(pk=p_id)
            products_json.append(
                {'spid': prd.id, 'pid': prd.product.product.id, 'name': prd.product.product.name, 'price': prd.price,
                 'discount': prd.discount, 'qn': product_qns[index], 'size_id': prd.product.size.id})
            service = prd.product.product.category.service
            if 'offer' in service.name.lower():
                OfferDeviceId(device_id=device_id).save()
                OfferProductOrderMapping(device_id=device_id, order=order,
                                         offer_product=prd.offerproductmapping_set.all()[0]).save()
            if str(service.id) not in ordered_services:
                ordered_services[str(service.id)] = 0
            total_amount += int(product_qns[index]) * (prd.price - prd.discount)
            ordered_services[str(service.id)] += int(product_qns[index]) * (prd.price - prd.discount)
            store = prd.store
            cart = Cart.objects.filter(order=order, store=store)
            if cart:
                cart = cart[0]
            else:
                cart = Cart(order=order, store=store)
                cart.save()

            OrderedProduct(product=prd, cart=cart, quantity=product_qns[index]).save()
            index += 1
        products_json = simplejson.dumps(products_json)
        invoice.product_json = products_json
        invoice.save()

        service_amount_ordered = []
        for key in ordered_services:
            service_amount_ordered.append(str(key) + ":" + str(ordered_services[key]))
        service_amount_ordered = ';;'.join(service_amount_ordered)
        print total_amount

        final_amount = total_amount

        if coupon:
            if total_amount >= coupon.min_total:
                order.coupon_applied = coupon
                print 'found coupon'
                print coupon.code
                print coupon
                print user
                print location_id
                print int(app_version)
                print final_amount
                print service_amount_ordered
                discount = verify_coupon(coupon, user, location_id, int(app_version), final_amount,
                                                       service_amount_ordered)['discount']
                print "discount" + str(discount)
                final_amount -= discount

        print "passed coupon part"

        delivery_charges = {}
        for key in ordered_services:
            service = Service.objects.get(pk=key)
            lsm = LocationServiceMapping.objects.filter(service=service, location=location)
            if lsm:
                lsm = lsm[0]
                stl = StoreTimingInLocation.objects.filter(store__is_active=True, is_active=True, lsm=lsm)
                print 'done'
                if stl:
                    stl = stl[0]
                    if key not in delivery_charges:
                        delivery_charges[key] = {'delivery_charges': 0, 'delivery_amount_min': stl.delivery_min_amount}
                    if ordered_services[key] < stl.delivery_min_amount:
                        final_amount += -stl.delivery_charges
                        total_amount += stl.delivery_charges
                        delivery_charges[key]['delivery_charges'] = stl.delivery_charges
                else:
                    delivery_charges[key] = {'delivery_charges': 0, 'delivery_amount_min': 0}
            else:
                delivery_charges[key] = {'delivery_charges': 0, 'delivery_amount_min': 0}

        print "passed delivery part"

        order.total_amount = total_amount
        order.final_amount = final_amount
        order.delivery_charges = simplejson.dumps(delivery_charges)
        order.save()
        OrderActivity(order=order, user=order.user, actions=0, comment=" ").save()

        data = simplejson.dumps({'status': 'done'})
        return HttpResponse(data, content_type='application/json', status=201)
    except Exception as process_order_function_error:
        print "process_order: " + str(process_order_function_error)
        data = simplejson.dumps({'status': 'Server Error'})
        send_mail('Order placing Error '+str(process_order_function_error), str(request)+"\n\n\n"+str(simplejson.dumps(request.POST)), 'query@movincart.com',['anurag@movincart.com'], fail_silently=False)
        return HttpResponse(data, content_type='application/json', status=500)


@csrf_exempt
def get_order_status(request):
    data = []
    user = User.objects.get(username=request.GET.get('username'))
    if user.api_key.key != request.GET.get('api_key'):
        data = simplejson.dumps("not valid Request")
        return HttpResponse(data, content_type='application/json', status=500)

    orders = Order.objects.filter(user=user, created_at__gte=dt.datetime.today().date()).order_by("-created_at")
    print orders
    for order in orders:
        order_data = {
            'total_amount': order.total_amount,
            'status': order_status_display[str(order.status)].title(),
            'show_popup': False,
            'id': order.id,
            'final_amount': order.final_amount,
            'address': {
                'address': order.address.address,
                'location_id': order.address.location_id,
                'landmark': order.address.landmark,
                'location_show': "",
            },
            'carts': []
        }
        if order.status not in [1, 3, 7, 8] and order.delivery_time < dt.datetime.now():
            order_data['show_popup'] = True

        invoice = Invoice.objects.filter(order=order)
        product_json = invoice[0].product_json
        products = simplejson.loads(product_json)
        # services = []
        for p in products:
            pdt = StoreProductMapping.objects.get(pk=p["spid"])
            service = pdt.product.product.category.service

            cart_data = {
                    'products': [],
                    'service_id': service.id,
                    'service_name': service.name,
                }

            size = Size.objects.get(pk=p["size_id"])
            cart_data['products'].append({
                'quantity': p["qn"],
                'discount': p["discount"],
                'id': p["spid"],
                'price': p["price"],
                'max_buy': p["spid"],
                'image': str(pdt.product.image),
                'size': str(size),
                'brand_name': pdt.product.product.brand_name,
                'category': pdt.product.product.category.id,
                'name': p["name"],
            })

            flag = True
            for single_order_data in order_data['carts']:
                if single_order_data['service_id'] == service.id:
                    flag = False
                    single_order_data['products'] += cart_data['products']
            if flag:
                order_data['carts'].append(cart_data)
        if len(order_data['carts']) > 0:
            data.append(order_data)
    data = simplejson.dumps({'objects': data})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_coupon_code_discount(request):
    data = {}
    coupon_code = request.GET.get('code')
    username = request.GET.get('username')
    api_key = request.GET.get('api_key')
    location_id = request.GET.get('location_id')
    version = request.GET.get('version')
    # device_id = request.GET.get('device_id')
    total = request.GET.get('total')
    service_vs_total = request.GET.get('service_vs_total')

    user = User.objects.get(username=username)
    if not user:
        data = simplejson.dumps("not valid Request")
        return HttpResponse(data, content_type='application/json', status=403)
    if user.api_key.key != api_key:
        data = simplejson.dumps("not valid Request")
        return HttpResponse(data, content_type='application/json', status=403)
    coupon = Coupon.objects.filter(code__iexact=coupon_code, is_active=True)
    if coupon:
        coupon = coupon[0]
        res = verify_coupon(coupon=coupon, user=user, location=int(location_id), version=int(version),
                                          total=total, service_amount_ordered=service_vs_total)
        data['id'] = coupon.id
        data['discount'] = res['discount']
        data = simplejson.dumps({'objects': data, 'status': res['status']})
    else:
        data = simplejson.dumps({'objects': {'discount': 0}, 'status': 'Promo code is not valid'})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_offer_products(request):
    data = []
    offer_location_id = request.GET.get('offer_id')
    device_id = request.GET.get('device_id')
    username = request.GET.get('username', '')
    # api_key = request.GET.get('api_key')
    # version = request.GET.get('version')
    status = "Thanks for the overwhelming response.\nWe are out of stock."

    if int(offer_location_id) in constant.out_of_stock_area:
        status = constant.offer_status
        data = simplejson.dumps({'object': [], 'status': status})
        return HttpResponse(data, content_type='application/json')

    offer=None
    try:
        offer_location = OfferLocationMapping.objects.get(pk=offer_location_id)
        offer = offer_location .offer
    except:
         offer = Offer.objects.get(pk=offer_location_id)
    offer_products = offer.offerproductmapping_set.filter(product__stock=True)

    if not offer_products:
        data = simplejson.dumps({'object': [], 'status': status})
        return HttpResponse(data, content_type='application/json')

    offer_device_id = OfferProductOrderMapping.objects.filter(device_id=device_id)
    flag = False
    if username != "":
        if OfferProductOrderMapping.objects.filter(order__user__username=username):
            flag = True
    if offer_device_id or flag:
        status = "Offer already used by this device"
        data = simplejson.dumps({'object': data, 'status': status})
        return HttpResponse(data, content_type='application/json')

    for offer_product in offer_products:
        sp = offer_product.product
        prd = sp.product.product
        p_object = {
            'discount': int(sp.discount),
            'id': sp.id,
            'price': int(sp.price),
            'max_buy': sp.max_buy,
            'image': str(sp.product.image),
            'size': str(sp.product.size),
            'category': prd.category.id,
            'name': prd.name,
        }
        data.append(p_object)

    data = simplejson.dumps({'object': data, 'status': status})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def save_suggestion(request):
    email = request.POST.get('email', '')
    suggestion = request.POST.get('suggestion', '')
    location = request.POST.get('location_id', '')
    comment = request.POST.get('comments', '')
    location = Location.objects.get(pk=location)
    Suggestion(email=email, suggestion=suggestion, location=location, comments=comment).save()
    return HttpResponse("done", content_type='application/json')


@csrf_exempt
def save_order_status(request):
    order_id = request.POST.get('order_id')
    status = request.POST.get('status')
    contact = request.POST.get('contact')
    services = request.POST.get('services')
    print 'ok'
    print order_id
    print status
    print contact

    print services
    print 'ok0'
    order = Order.objects.get(pk=order_id)

    if status and order.user.username == contact:
        if status == "no":
            service_names = ""
            if services:
                print 'ok1'
                services = simplejson.loads(services)  # .replace(' ','').split(',')
                print services

                def function(service):
                    return service.name

                service_names = ', '.join(map(function, Service.objects.filter(pk__in=services)))
                print service_names
            order.status = 7
            order.save()
            if service_names:
                OrderActivity(order=order, user=order.user, actions=8,
                              comment="Order Not Delivered :: services:" + service_names).save()
            else:
                OrderActivity(order=order, user=order.user, actions=8, comment="Order Not Delivered").save()
            thr = threading.Thread(target=notify_admin(order, service_names))
            thr.start()
        else:
            order.status = 8
            order.save()
            OrderActivity(order=order, user=order.user, actions=7, comment="Delivery Confirmation By User ").save()
            print "order received"
    return HttpResponse("", content_type='application/json')
