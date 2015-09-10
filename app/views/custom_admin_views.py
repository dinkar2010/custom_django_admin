import mimetypes
from this import s
from app.utils import log_entry_test
from django.forms.models import model_to_dict
import simplejson, json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponseForbidden
import json
from app.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.shortcuts import render
import datetime as dt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from gcm import GCM
from django.contrib.auth import logout
from app.utils import constant, save_order_dump, save_product_dump, analytics
from django.contrib.admin.views.decorators import staff_member_required
from app.utils.image_utils import *
from django.db.models import Q
from django.contrib.auth import authenticate, login
import time
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.core.servers.basehttp import FileWrapper
from dateutil import parser
from app.models import CouponRuleBook,Coupon
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

from django.core import serializers
import xlrd
def blank(request):
    raise Http404

def admin_login(request):
    next_page = request.GET.get('next', '')
    # logger.debug('user_login request')
    context = {
        'next': next_page
    }
    if request.user:
        if request.user.is_active and request.user.is_staff:
            next_page = request.GET.get('next')
            if next_page:
                return HttpResponseRedirect(next_page)
            return HttpResponseRedirect('/admin/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print username + " " + password
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active and user.is_staff:
                login(request, user)
                # logger.debug('user_login ' + username)
                next_page = request.GET.get('next')
                if next_page:
                    return HttpResponseRedirect(next_page)
                return HttpResponseRedirect('/admin/')
            else:
                return HttpResponse("Your Movincart account is disabled.")
        else:
            # logger.debug("Invalid login details: {0}, {1}".format(username, password))
            # logger.debug('user_login ' + username + 'unable to login')
            messages.warning(request, 'Invalid Login Details', context)
            return render(request, 'new_custom_admin/login.html', context)
    else:
        return render(request, 'new_custom_admin/login.html', context)

@staff_member_required
def adminlogout(request):
    # logger.debug('admin : ' + request.user.username+' >> logout')
    logout(request)
    return HttpResponseRedirect('/admin/login/')

@staff_member_required
def dashboard(request):

    # logger.debug('admin : ' + request.user.username+' >> dashboard')
    # return HttpResponseRedirect('/admin/')
    date={}
    date['day']=dt.datetime.today().date().day
    date['month']=dt.datetime.today().date().strftime("%b")
    # print date['month']
    context={
        'date':date,
    }
    return render(request,'new_custom_admin/dashboard.html',context)

@staff_member_required
def cancel_single_order(request, id):
    user = request.user
    if id > 0:
        if user.has_perm('app.can_change_order_status'):
            order = Order.objects.get(pk=id)

            if order.status != 8 or request.user.groups.filter(name='Ops Head').exists():
                customer = order.user
                notify_user = request.GET.get('notify', '')
                notification_sent = ""
                if notify_user == '0':
                    app_ids = [customer.userprofile.app_id]
                    gcm = GCM(constant.API_KEY)
                    data = {'title': 'MovinCart',
                        'Notification': "Your order has been canceled. Sorry for the inconvenience.", 'popup': '0',
                        'page': "2", 'order_id': str(order.id)}
                    response = gcm.json_request(registration_ids=app_ids, data=data)
                    notification_sent = simplejson.dumps(data)
                    messages.error(request, 'Order Canceled and user notification sent!!')
                else:
                    messages.error(request, 'Order Canceled!!')
                order.status = 1
                message='this order canceled '+str(order.id)
                print message
                order.save()
                OrderActivity(order=order, user=user, actions=9, comment=notification_sent).save()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(order).pk,
                    object_id=order.pk,
                    object_repr=str(order),
                    action_flag=CHANGE,
                    change_message=message
                )
                logvalue=LogEntry.objects.filter(content_type_id=25)
                print logvalue.object_id
                print logvalue.change_message

    return HttpResponseRedirect('/admin/app/order/' + id + '/')

@staff_member_required
def order_delivered(request, id):
    user = request.user
    if id > 0:
        if user.has_perm('app.can_change_order_status'):
            order = Order.objects.get(pk=id)
            customer = order.user.userprofile
            notify_user = request.GET.get('notify', '')
            notification_sent = ""
            if notify_user == '0' and order.status == 7:
                app_id = [customer.app_id]
                gcm = GCM(constant.API_KEY)
                data = {'title': 'MovinCart', 'Notification': "Has your order been delivered", 'popup': "1",'page': "2", 'NeedRefresh': "1", 'order_id': str(order.id)}
                response = gcm.json_request(registration_ids=app_id, data=data)
                notification_sent = simplejson.dumps(data)
            else:
                notification_sent = "url accessed"
            order.status = 0
            message="your order is delivered with order id "+str(order.id)
            order.save()
            OrderActivity(order=order, user=user, actions=10, comment=notification_sent).save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(order).pk,
                object_id=order.pk,
                object_repr=str(order),
                action_flag=CHANGE,
                change_message=message
            )
            logValue=LogEntry.objects.filter(content_type_id=20)
            print logValue.object_id
            print logValue.change_message
            # logger.debug('admin : ' + request.user.username+' >> order_delivered > order : { id : '+str(order.id)+' userName : '+order.userName+'}, status : order delivered')
            messages.success(request, 'Order Delivered!!')
    return HttpResponseRedirect('/admin/app/order/' + id + '/')

@staff_member_required
def order_processed(request, id):
    user = request.user
    if id > 0:
        if user.has_perm('app.can_change_order_status'):
            order = Order.objects.get(pk=id)
            order.status = 2
            order.save()
            name = order.user.first_name.title()
            message = "Dear %s, your Order has been confirmed and will be dispatched soon." % (name)
            data = {'title': 'MovinCart', 'Notification': message, 'popup': '0', 'page': "2", 'order_id': str(order.id)}
            notification_sent = simplejson.dumps(data)
            order = Order.objects.get(pk=id)
            reg_id = order.user.userprofile.app_id
            API_KEY = "AIzaSyAMhTBccat-kQkU3TWw85GrjXvKZkbR9wc"
            gcm = GCM(API_KEY)
            response = gcm.json_request(registration_ids=[reg_id], data=data)
            OrderActivity(order=order, user=user, actions=6, comment=notification_sent).save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(order).pk,
                object_id=order.pk,
                object_repr=str(order),
                action_flag=CHANGE,
                change_message=message
            )
            logvalue=LogEntry.objects.filter(content_type_id=20)
            print logvalue.object_id
            print logvalue.change_message
            # logger.debug('admin : ' + request.user.username+' >> order_processed > order : { id : '+str(order.id)+' userName : '+order.userName+'}, status : order processed')
            messages.info(request, 'Order is in process!!')
    return HttpResponseRedirect('/admin/app/order/' + id + '/')

@staff_member_required
def add_new_location(request):

    if request.method == 'POST':
        nloc_city = request.POST.get('l_city', '').title()
        nloc_area = request.POST.get('l_area', '').title()
        nloc_zone = request.POST.get('l_zone', '').title()
        nloc_sub_area = request.POST.get('l_sub_area', '').title()
        nloc_coordinates = request.POST.get('l_coord', '')

        if nloc_city and nloc_coordinates and nloc_sub_area and nloc_area and nloc_zone:
            Location(city=nloc_city, area=nloc_area, sub_area=nloc_sub_area, mpoly=nloc_coordinates,
                     zone=nloc_zone).save()
            messages.success(request, 'Location Saved')
        else:
            messages.warning(request, 'Please Enter All Info')
        # logger.debug('admin : ' + request.user.username+' >> add_new_location > sub_area : '+nloc_sub_area+' area : '+ nloc_area+' polygon : '+nloc_coordinates+' status : new location added')
        message='you added '+' City '+str(nloc_city)+', Area '+str(nloc_area)+', Sub-Area '+str(nloc_sub_area)+', mpoly '+str(nloc_coordinates)+ ', zone '+str(nloc_zone)
        print message


    locations = Location.objects.all()

    polygons = []
    for l in locations:
        polygon_coordi = simplejson.loads(l.mpoly.json)['coordinates'][0]
        polygons.append(polygon_coordi)
    context={
        'polygons':zip(polygons,locations)
    }

    return render(request,'new_custom_admin/add_new_location.html',context)

@staff_member_required
def edit_location(request,id):
    location = Location.objects.get(pk=id)
    if request.method == 'POST':
        nloc_city = request.POST.get('l_city', '').title()
        nloc_area = request.POST.get('l_area', '').title()
        nloc_zone = request.POST.get('l_zone', '').title()
        nloc_sub_area = request.POST.get('l_sub_area', '').title()
        nloc_coordinates = request.POST.get('l_coord', '')
        if nloc_city and nloc_coordinates and nloc_sub_area and nloc_area and nloc_zone:
            location.city = nloc_city
            location.area = nloc_area
            location.sub_area = nloc_sub_area
            location.mpoly = nloc_coordinates
            location.zone = nloc_zone
            location.save()
            messages.warning(request, 'Location Updated')
        else:
            messages.warning(request, 'Please Enter All Info')
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
    return HttpResponseRedirect('/admin/app/location/' + str(id) + '/')

@staff_member_required
def change_image(request):
    product_id = request.GET.get('product_id')
    image_url = request.GET.get('product_image')
    print product_id + " " + image_url
    context = {
        'image': image_url
    }
    if product_id and image_url:
        sp = StoreProductMapping.objects.get(pk=product_id)
        psi = sp.product
        product_id = psi.id

        isServer = settings.IS_SERVER
        if isServer == 0:
            path1 = '/home/shubham/webapps/movincart/app/static/productImage/'
        else:
            path1 = 'app/static/productImage/'
        if 'http' in image_url:
            image = image_url
            if '.png' in image:
                newpath = path1 + str(product_id) + '/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 's')
                newpath = path1 + str(product_id) + '/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'xs')
                newpath = path1 + str(product_id) + '/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'xxs')
                newpath = path1 + str(product_id) + '/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'm')
                newpath = '/static/productImage/' + str(product_id) + '/m/'
                image = newpath + 'item.png'
            else:
                newpath = path1 + str(product_id) + '/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 's')
                newpath = path1 + str(product_id) + '/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'xs')
                newpath = path1 + str(product_id) + '/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'xxs')
                newpath = path1 + str(product_id) + '/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'm')
                newpath = '/static/productImage/' + str(product_id) + '/m/'
                image = newpath + 'item.jpg'
            if not image:
                image = '/static/no_image.jpg'
            psi.image = image + '?t=' + dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
        psi.save()
        context = {
            'image': psi.image
        }
    return render(request, 'new_custom_admin/refreshed_image_div.html', context)

@staff_member_required
def edit_product(request):
    p_id = request.POST.get('p_id', '')
    p_name = request.POST.get('p_name')
    p_brand = request.POST.get('p_brand', '')
    p_description = request.POST.get('p_desc', '')
    p_category = request.POST.get('p_category', '')
    p_price = request.POST.get('p_price', '')
    p_display_order = int(request.POST.get('p_display_order', '0'))
    p_discount = request.POST.get('p_discount', '')
    p_stock = request.POST.get('p_stock', '')
    print request.POST

    if p_id:
        stock = True
        if p_stock == '0':
            stock = False

        spm = StoreProductMapping.objects.get(pk=p_id)
        psi = spm.product
        prd = psi.product
        prd.name = p_name
        prd.brand_name = p_brand
        prd.description = p_description
        prd.category = Category.objects.get(pk=p_category)
        prd.save()
        spm.price = p_price
        spm.discount = p_discount
        spm.stock = stock
        spm.display_order = p_display_order
        spm.save()
        psi.save()
        messages.success(request, p_name + ' Info Saved ')
    return HttpResponseRedirect('/admin/app/storeproductmapping/' + str(p_id) + '/')

@staff_member_required
def add_product(request):
    main_stores = Store.objects.filter(id__in=constant.main_stores)
    stores = Store.objects.all().exclude(id__in=main_stores)
    sub_cat_list = Category.objects.filter(~Q(parent=None))
    for s in sub_cat_list:
        s.name += ' -- ' + s.service.name

    service_category = {}
    services = Service.objects.all()
    for s in services:
        cat_list = map(lambda x: x.id, s.category_set.all().exclude(parent=None))
        service_category[s.id] = cat_list

    # print service_category
    brands = list(set(Product.objects.all().values_list('brand_name', flat=True)))
    # print len(brands)
    context = {
        'categories': sub_cat_list,
        'stores': stores,
        'main_stores': main_stores,
        'service_category': service_category,
        'brands': brands
    }
    if request.method == 'POST':
        p_name = request.POST.get('p_name').title()
        p_brand = request.POST.get('p_brand', '').title()
        p_description = request.POST.get('p_description', '')
        p_category = request.POST.get('p_category', '')
        p_tags = request.POST.get('p_tags', '')
        p_rating = request.POST.get('p_rating', '')
        p_barcode = request.POST.get('p_barcode', '')
        p_related = request.POST.get('p_related', '')
        # p_displayOrder=request.POST.get('p_displayOrder','')
        p_price = request.POST.get('p_price', '')
        p_discount = request.POST.get('p_discount', '')
        p_stock = request.POST.get('p_stock', '')
        p_image = request.POST.get('p_image', '')
        p_size_mag = request.POST.get('p_magnitude', '')
        p_size_unit = request.POST.get('p_unit', '')
        p_local_store = request.POST.get('p_local_store', '')
        p_main_store = request.POST.get('p_main_store', '')
        # max_buy=request.POST.get('p_max_buy','')
        cat = Category.objects.get(pk=p_category)

        prd = Product.objects.filter(name=p_name, brand_name=p_brand, category=cat)

        if prd:
            prd = prd[0]
        else:
            prd = Product(name=p_name, brand_name=p_brand, description=p_description, category=cat)
            prd.save()
            new_tags = []
            tag_list = str(p_tags).split()
            for t in tag_list:
                prd.tags.create(name=t)

        size_obj = Size.objects.filter(magnitude=int(p_size_mag), unit=p_size_unit)
        if size_obj:
            size_obj = size_obj[0]
        else:
            size_obj = Size(magnitude=int(p_size_mag), unit=p_size_unit)
            size_obj.save()
        image = p_image
        isServer = settings.IS_SERVER
        if isServer == 0:
            path1 = '/home/shubham/webapps/movincart/app/static/productImage/'
        else:
            path1 = 'app/static/productImage/'
        if 'http' in image:
            psi = ProductSizeImageMapping.objects.filter(product=prd, size=size_obj)
            if psi:
                psi = psi[0]
            else:
                psi = ProductSizeImageMapping(product=prd, size=size_obj, image='image')
                psi.save()
            product_id = str(psi.id)
            if '.png' in image:
                newpath = path1 + str(product_id) + '/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 's')
                newpath = path1 + str(product_id) + '/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'xs')
                newpath = path1 + str(product_id) + '/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'xxs')
                newpath = path1 + str(product_id) + '/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.png')
                resize(newpath + 'item.png', 'm')
                newpath = '/static/productImage/' + str(product_id) + '/m/'
                image = newpath + 'item.png'
            else:
                newpath = path1 + str(product_id) + '/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 's')
                newpath = path1 + str(product_id) + '/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'xs')
                newpath = path1 + str(product_id) + '/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'xxs')
                newpath = path1 + str(product_id) + '/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath + 'item.jpg')
                resize(newpath + 'item.jpg', 'm')
                newpath = '/static/productImage/' + str(product_id) + '/m/'
                image = newpath + 'item.jpg'
            if not image:
                image = '/static/no_image.jpg'
            psi.image = image
            print image
            print psi.id
            psi.save()

        s_local = Store.objects.get(pk=int(p_local_store))
        s_main = Store.objects.get(pk=int(p_main_store))

        sp_local = StoreProductMapping.objects.filter(store=s_local, product=psi)

        if not sp_local:
            # if cat.service in sp_local.service.all():
            sp_local = StoreProductMapping(store=s_local, product=psi, price=p_price, discount=p_discount)

        sp_main = StoreProductMapping.objects.filter(store=s_main, product=psi)

        if not sp_main:
            # if cat.service in sp_main.service.all():
            sp_main = StoreProductMapping(store=s_main, product=psi, price=p_price, discount=p_discount)

        sp_local.save()
        sp_main.save()

        messages.success(request, 'Yo !!! ' + p_name + ' info saved')

        return render(request, 'new_custom_admin/add_product.html', context)
    return render(request, 'new_custom_admin/add_product.html', context)

@staff_member_required
def send_notification(request):
    context = {}
    if request.method == 'POST':
        message = request.POST.get('message', '')
        data = {'Notification': message}
        reg_ids = map(lambda x: x.app_id, Visitor.objects.all())
        n = 5
        for i in range(0, len(reg_ids), n):
            API_KEY = "AIzaSyAMhTBccat-kQkU3TWw85GrjXvKZkbR9wc"
            gcm = GCM(API_KEY)
            response = gcm.json_request(registration_ids=reg_ids[i:i + n], data=data)
            print i
            time.sleep(1)

        messages.warning(request, ' Notification Sent')
        return render(request, 'custom_admin/send_notification.html', context)
    return render(request, 'custom_admin/send_notification.html', context)

@staff_member_required
def covered_locations(request):
    locations = Location.objects.all()
    polygons = []
    for l in locations:
        polygon_coordi = simplejson.loads(l.mpoly.json)['coordinates'][0]
        polygons.append(polygon_coordi)
    context = {
        'polygons': zip(polygons,locations),
    }
    return render(request, 'new_custom_admin/covered_locations.html', context)

@staff_member_required
def remove_product_frm_order(request):
    user = request.user
    if user.has_perm('Can change order'):
        order_id = request.GET.get('order_id')
        sp_id = request.GET.get('sp_id')
        order = Order.objects.get(pk=order_id)
        if order.status == 3 or order.status == 2:
            # sp = StoreProductMapping.objects.get(pk=sp_id)
            invoice = order.invoice
            product_json = invoice.product_json
            ordered_product = simplejson.loads(product_json)
            price = 0
            new_ordered_products = []
            if len(ordered_product) > 1:
                for op in ordered_product:
                    if str(op['spid']) == sp_id:
                        print 'spid ' + sp_id
                        price = (int(float(op['price'])) - int(float(op['discount']))) * int(op['qn'])
                    else:
                        new_ordered_products.append(op)
                print price
                new_product_json = simplejson.dumps(new_ordered_products)
                invoice.product_json = new_product_json
                new_total_amount = order.total_amount - price
                if order.coupon_applied:
                    coupon = order.coupon_applied
                    prev_discount = 0
                    if coupon.discount_type == 0:
                        prev_discount = coupon.discount
                    else:
                        prev_discount = (order.total_amount * coupon.discount) / 100
                        if prev_discount > coupon.max_discount_limit:
                            prev_discount = coupon.max_discount_limit

                    order.final_amount += prev_discount

                    if order.total_amount < order.coupon_applied.min_total:
                        order.coupon_applied = None
                    else:
                        discount = 0
                        if coupon.discount_type == 0:
                            discount = coupon.discount
                        else:
                            discount = (new_total_amount * coupon.discount) / 100
                            if discount > coupon.max_discount_limit:
                                discount = coupon.max_discount_limit
                        order.final_amount += discount

                order.total_amount -= price
                carts = order.cart_set.all()
                for cart in carts:
                    ordered_products_in_cart = OrderedProduct.objects.filter(cart=cart, product_id=sp_id)
                    if ordered_products_in_cart:
                        ordered_products_in_cart.delete()
                        break
                print 'New order details saved'
                message="removed product "+sp_id+"from order "+order_id
                order.save()
                invoice.save()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(order).pk,
                    object_id=order.pk,
                    object_repr=str(order),
                    action_flag=CHANGE,
                    change_message=message
                )
                logValue=LogEntry.objects.filter(content_type_id=1112)
                print logValue.change_message
                messages.warning(request, 'Product Removed!!')
            else:
                messages.warning(request, "Can't remove product!!")
        else:
            messages.warning(request, "Invalid Request!!")
        return HttpResponseRedirect('/admin/app/order/' + str(order_id) + '/')

    else:
        raise HttpResponseForbidden()

@staff_member_required
def show_stores(request):
    selected_location = request.GET.getlist('search_location')
    selected_service = request.GET.getlist('search_service')
    locations = Location.objects.all()
    services = Service.objects.all()
    context = {
        'locations': locations,
        'services': services,
        'selected_location': map(lambda x: int(x), selected_location),
        'selected_service': map(lambda x: int(x), selected_service),
        'page': 5,
    }
    if selected_location and selected_service:
        stores_all = map(lambda x:x.store,StoreTimingInLocation.objects.filter(lsm__location__in=selected_location, lsm__service__in=selected_service))
        stores_all = list(set(list(stores_all)))
        for sa in stores_all:
            products = sa.storeproductmapping_set.all().count()
            on_products = sa.storeproductmapping_set.filter(stock=True).count()
            off_products = products - on_products
            setattr(sa, 'on_product', on_products)
            setattr(sa, 'off_products', off_products)
            context['stores'] = stores_all
    elif selected_location:
        stores_all = map(lambda x:x.store,StoreTimingInLocation.objects.filter(lsm__location__in=selected_location))
        stores_all = list(set(list(stores_all)))
        for sa in stores_all:
            products = sa.storeproductmapping_set.all().count()
            on_products = sa.storeproductmapping_set.filter(stock=True).count()
            off_products = products - on_products
            setattr(sa, 'on_product', on_products)
            setattr(sa, 'off_products', off_products)
            context['stores'] = stores_all
    elif selected_service:
        stores_all = map(lambda x:x.store,StoreTimingInLocation.objects.filter(lsm__service__in=selected_service))
        stores_all = list(set(list(stores_all)))
        for sa in stores_all:
            products = sa.storeproductmapping_set.all().count()
            on_products = sa.storeproductmapping_set.filter(stock=True).count()
            off_products = products - on_products
            setattr(sa, 'on_product', on_products)
            setattr(sa, 'off_products', off_products)
            context['stores'] = stores_all
    else:
        stores_all = Store.objects.all()
        for sa in stores_all:
            products = sa.storeproductmapping_set.all().count()
            on_products = sa.storeproductmapping_set.filter(stock=True).count()
            off_products = products - on_products
            setattr(sa, 'on_product', on_products)
            setattr(sa, 'off_products', off_products)
            context['stores'] = stores_all

    return render(request, 'new_custom_admin/stores.html', context)

@staff_member_required
def add_store(request):
    services = Service.objects.all()
    locations = Location.objects.all()
    context = {
        'services': services,
        'locations': locations,
        'page': 5,
    }

    if request.user.has_perm('app.add_store') and request.method == "POST":
        s_name = request.POST.get("s_name")
        s_owner = request.POST.get("s_owner")
        s_contact = request.POST.get("s_contact")
        s_address = request.POST.get("s_address")
        s_services = request.POST.getlist("s_services")
        # s_locations = request.POST.getlist("s_locations")
        s_open = request.POST.get("s_open")
        s_cord = request.POST.get("l_cord")
        s_end = request.POST.get("s_end")
        store = Store.objects.filter(name=s_name)


        message='Store Name '+ str(s_name)+' Store Owner '+str(s_owner)+' Contact '+str(s_contact)+' Address '+str(s_address)+' Open Time '+str(s_open)+' Service '+str(s_services)+' End Time '+str(s_end)

        if not store:
            s_open = dt.datetime.strptime(s_open, "%I:%M %p")
            s_end = dt.datetime.strptime(s_end, "%I:%M %p")
            store = Store(name=s_name, owner_name=s_owner, contact=s_contact, address=s_address, open_time=s_open,
                          end_time=s_end)
            store.position = s_cord


            store.save()

            for ss in s_services:
                service = Service.objects.get(pk=ss)
                store.services.add(service)
            # for ll in s_locations:
            # 	location = Location.objects.get(pk=ll)
            # 	store.locations.add(location)

            print  ContentType.objects.get_for_model(Store).pk
            store.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Store).pk,
                object_id=store.pk,
                object_repr=str(store),
                action_flag=ADDITION,
                change_message=message
            )
            logValue=LogEntry.objects.filter(content_type_id=12)
            for log in logValue:
                print log.change_message
            messages.success(request, str(store.name)+' Saved!!')
        else:
            messages.success(request, ' Not Authorized ')
        return render(request, 'new_custom_admin/add_store.html', context)


@staff_member_required
def edit_store(request, id):
    store = Store.objects.get(pk=id)
    if request.user.has_perm('app.change_store') and request.method == "POST":
        s_name = request.POST.get("s_name")
        s_owner = request.POST.get("s_owner")
        s_contact = request.POST.get("s_contact")
        s_address = request.POST.get("s_address")
        s_services = request.POST.getlist("s_services")
        # s_locations = request.POST.getlist("s_locations")
        l_cord = request.POST.get("l_cord").replace("(", "").replace(")", "")
        s_open = request.POST.get("s_open")
        s_end = request.POST.get("s_end")
        s_open = dt.datetime.strptime(s_open, "%I:%M %p")
        s_end = dt.datetime.strptime(s_end, "%I:%M %p")


        if store:
            store.name = s_name
            store.owner_name = s_owner
            store.contact = s_contact
            store.address = s_address
            store.open_time = s_open
            store.end_time = s_end
            store.position = l_cord

            message=log_entry_test.change_message(
            'Store Name ',store.name,s_name,
            'Owner  Name ',store.owner_name,s_owner,
            'Contact ',store.contact,s_contact,
            'Address ',store.address,s_address,
            'Open Time ',store.open_time,s_open,
            'End Time ',store.end_time,s_end,
            'Position',store.position,l_cord
            )
            store.save()
            store.services.clear()
            # store.locations.clear()


            for ss in s_services:
                service = Service.objects.get(pk=ss)
                store.services.add(service)
                store.save()
            # for ll in s_locations:
            # 	location = Location.objects.get(pk=ll)
            # 	store.locations.add(location)
            print ContentType.objects.get_for_model(Store).pk
            store.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Store).pk,
                object_id=store.pk,
                object_repr=str(store),
                action_flag=CHANGE,
                change_message=message
            )
        logValue=LogEntry.objects.filter(content_type_id=12)
        for log in logValue:
            print log.change_message
        messages.success(request, str(store.name)+' Saved!!')
    else:
        messages.success(request, ' Not Authorized ')
    store = Store.objects.get(pk=id)
    selected_services = store.services.all()
    is_fnv = Service.objects.get(pk=3) in store.services.all()
    selected_locations = map(lambda x: x.lsm.location,store.storetiminginlocation_set.filter(is_active=True))
    services = Service.objects.all()
    locations = Location.objects.all()
    categories =Category.objects.filter(service__in=store.services.all(),parent=None)
    cat_vise_brands=[]
    store_inventory=[]
    all_cats= Category.objects.all()
    store_products_cats = all_cats.filter(pk__in=store.storeproductmapping_set.all().values_list('product__product__category__parent',flat=True))
    for cat in store_products_cats:
        store_products_sub_cats = all_cats.filter(parent=cat)
        cat_dict={}
        cat_dict['name']=cat.name
        cat_dict['value']=[]
        for sub_cat in store_products_sub_cats:
            dict={}
            dict['name']=sub_cat.name
            dict['value']=list(set(store.storeproductmapping_set.filter(product__product__category=sub_cat).values_list('product__product__brand_name',flat=True)))
            if dict['value']:
                cat_dict['value'].append(dict)
        store_inventory.append(cat_dict)
    time_slots=TimeSlot.objects.all()
    products = Product.objects.all()
    for cat in categories:
        cat_dict = {}
        sub_categories = all_cats.filter(parent=cat)

        sub_cat_vise_brands=[]
        for sub_cat in sub_categories:
            dict={}
            dict["value"]=list(set(products.filter(category=sub_cat).values_list('brand_name',flat=True)))
            dict["name"]=sub_cat.name
            sub_cat_vise_brands.append(dict)
        cat_dict["value"]=sub_cat_vise_brands
        cat_dict["name"]=cat.name
        cat_vise_brands.append(cat_dict)
    context={
        'store' : store,
        'services' : services,
        'cat_vise_brands':cat_vise_brands,
        'locations' : locations,
        'store_inventory':store_inventory,
        'selected_services' : selected_services,
        'selected_locations' : selected_locations,
        'page':5,
        'time_slots':time_slots,
        'is_fnv':is_fnv,
    }
    return render(request, 'new_custom_admin/edit_store.html', context)


@staff_member_required
def save_orders_dump(request):
    if request.user.has_perm('app.can_download_order_dump'):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        start_date = dt.datetime.strptime(start_date,'%m/%d/%Y')
        end_date = dt.datetime.strptime(end_date,'%m/%d/%Y')
        print start_date
        check = request.POST.get('different_check')
        product_ids_check = request.POST.get('product_ids_format_check')
        product_ids_values = request.POST.get('product_ids_value')
        find_other_product_check = request.POST.get('find_other_product_check')

        if check:
            save_order_dump.save_dump_format2(start_date ,end_date)
        elif product_ids_check:
            product_ids_values = product_ids_values.split(',')
            product_ids_values = map(lambda x:int(x.strip()),product_ids_values)
            print product_ids_values
            if find_other_product_check:
                save_order_dump.save_order_dump_per_ids(start_date ,end_date,product_ids_values,find_other_product=True)
            else:
                save_order_dump.save_order_dump_per_ids(start_date ,end_date,product_ids_values,find_other_product=False)
        else:
            save_order_dump.save_dump(start_date ,end_date)

        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get(model="order").pk,
            object_id       = None,
            object_repr     = "Order Dump",
            action_flag     = ADDITION,
            change_message  = "downloaded dump for orders for dates : "+str(start_date)+" : "+str(end_date)
        )
        isServer =settings.IS_SERVER
        path1=''
        if isServer==0:
            path1='/home/shubham/webapps/movincart/'
        filename     = path1+"dump/orders_on_server.xls" # Select your file here.
        download_name ="orders.xls"
        wrapper      = FileWrapper(open(filename))
        content_type = mimetypes.guess_type(filename)[0]
        response     = HttpResponse(wrapper,content_type=content_type)
        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = "attachment; filename=%s"%download_name
        return response
    else:
        raise HttpResponseForbidden()

@staff_member_required
def show_list_storeproduct(request):
    all_store = Store.objects.all()
    main_stores = all_store.filter(id__in=constant.main_stores)
    local_stores = all_store.exclude(id__in=main_stores)
    categories = Category.objects.filter(parent=None)
    category_vise_sub_categories = {}

    for c in categories:
        category_vise_sub_categories[str(c.name)] = map(lambda x: x, Category.objects.filter(parent_id=c.id))

    context = {
        'main_stores': main_stores,
        'local_stores': local_stores,
        'page': 4,
        'category_vise_sub_categories': category_vise_sub_categories,
    }
    stores = request.GET.getlist('store')
    categories = request.GET.getlist('category')
    keyword = request.GET.get('p_name')
    p_id = request.GET.get('p_id')
    if p_id:
        context['store_products'] = [StoreProductMapping.objects.get(pk=p_id)]
        context['id'] = p_id
    elif stores:
        store_products = []
        for s in stores:
            if categories:
                if keyword:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                        Q(product__product__category__id__in=categories) & (
                        Q(product__product__name__icontains=keyword) | Q(
                            product__product__brand_name__icontains=keyword)))
                else:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                        product__product__category__id__in=categories)
            else:
                if keyword:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                        Q(product__product__name__icontains=keyword) | Q(
                            product__product__brand_name__icontains=keyword))
                else:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.all()
        context['store_products'] = store_products
        context['selected_stores'] = map(lambda x: int(x), stores)
        context['selected_categories'] = map(lambda x: int(x), categories)
        if keyword:
            context['keyword'] = keyword
    return render(request, 'new_custom_admin/storeproduct.html', context)

@staff_member_required
def edit_product_info_frm_table(request):
    if request.user.has_perm('app.add_storeproductmapping'):
        p_id = request.GET.get('p_id', '')
        p_price = request.GET.get('p_price', '')
        p_discount = request.GET.get('p_discount', '')
        p_visiblity = request.GET.get('p_visiblity')
        p_display_order = request.GET.get('p_display_order')
        p_max_buy = request.GET.get('p_max_buy')
        # logger.debug('admin : ' + request.user.username+' >> edit_product_frm_table > item { id : '+str(p_id)+", name : "+p_name+", brand : "+p_brand+", price : "+p_price+", discount : "+p_discount+", size : "+p_size+", visibility :  "+p_visiblity+", max buy : "+p_max_buy)
        # print p_price+" "+p_discount+" "+p_visiblity+" "+p_max_buy
        if p_id:
            spm = StoreProductMapping.objects.get(pk=p_id)
            spm.price = p_price
            spm.discount = p_discount
            visible = True
            if p_visiblity == '0':
                visible = False
            spm.stock = visible
            spm.max_buy = int(p_max_buy)
            spm.display_order = int(p_display_order)
            message=log_entry_test.change_message(
                'Price ',p_price,spm.price,
                'Discount',p_discount,spm.discount,
                'Visibility',p_visiblity,visible,
                'Display Order',p_display_order,spm.display_order,
                'Max Buy',p_max_buy,spm.max_buy
            )
            spm.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(spm).pk,
                object_id=spm.pk,
                object_repr=str(spm),
                action_flag=CHANGE,
                change_message=message
            )
            logValue=LogEntry.objects.filter(content_type_id=10)
            for log in logValue:
                print log.change_message
            messages.success(request, str(spm.product.product.name) + ' Saved!!')

    else:
        messages.success(request, ' Not Authorized ')
    return render(request, 'new_custom_admin/blank_page.html')


@staff_member_required
def productdump(request):

    if request.user.has_perm('app.can_download_product_dump'):
        stores = request.GET.get('stores').split(',')

        save_product_dump.save_dump(stores)
        LogEntry.objects.log_action(
        user_id         = request.user.pk,
        content_type_id = ContentType.objects.get(model="store").pk,
        object_id       = None,
        object_repr     = "Store Product Dump",
        action_flag     = ADDITION,
        change_message  = "downloaded dump for store products for stores : "+str(request.GET.get('stores'))
        )
        isServer =settings.IS_SERVER
        path1=''
        if isServer==0:
            path1='/home/shubham/webapps/movincart/'
        filename     = path1+"dump/products_on_server.xls" # Select your file here.
        download_name ="products.xls"
        wrapper      = FileWrapper(open(filename))
        content_type = mimetypes.guess_type(filename)[0]
        response     = HttpResponse(wrapper,content_type=content_type)
        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = "attachment; filename=%s"%download_name
        return response
    else:
        raise HttpResponseForbidden()

@staff_member_required
def save_tags_for_product(request, id):
    if request.user.has_perm('app.can_change_storeproductmapping'):
        prd = StoreProductMapping.objects.get(pk=id).product.product
        keywords = request.GET.get('p_tags')
        if keywords:
            keywords = keywords.split(',')
            for key in keywords:
                if key.strip():
                    tag = Tag.objects.filter(name__iexact=key.lower().strip())
                    if not tag:
                        tag = Tag(name=key.lower().strip())
                        tag.save()
                    else:
                        tag = tag[0]
                    prd.tags.add(tag)
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(prd).pk,
                object_id=prd.pk,
                object_repr=str(prd),
                action_flag=CHANGE,
                change_message=log_entry_test.change_message("changed product :: id:" + str(prd.id) + " keywords: " + ', '.join(keywords))
            )
            messages.success(request, str(prd.name) + ' tags Saved!!')
        return HttpResponseRedirect('/admin/app/storeproductmapping/' + str(id) + '/')

@staff_member_required
def show_list_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    next_page = 2
    prev_page = 1
    try:
        orders = paginator.page(page)
        next_page = int(page) + 1
        prev_page = int(page) - 1

    except PageNotAnInteger:
        orders = paginator.page(1)
        next_page = 2
        prev_page = 1
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
        next_page = paginator.num_pages
        prev_page = paginator.num_pages - 1
    if prev_page == 0:
        prev_page = 1
    orders_to_send = []
    # setattr(orders, 'has_next', orders.has_next())

    for order in orders:
        data = {}
        data['order'] = order
        up = order.user
        prev_order_by_cp = Order.objects.filter(user=up, created_at__lt=order.created_at, status__in=[0, 8])
        data['old'] = False  # 0 for new 1 for old
        if prev_order_by_cp:
            data['old'] = True  # 0 for new 1 for old
        service_ordered = []
        ordered_services = {}
        data['total_amount'] = 0
        invoice = order.invoice
        order_products = simplejson.loads(invoice.product_json)
        for p in order_products:
            try:
                prd = StoreProductMapping.objects.get(pk=p['spid'])
                service = prd.product.product.category.service.name
                if service not in ordered_services:
                    ordered_services[service] = 0
                price = p['price']
                if 'discount' in p:
                    price = p['price'] - p['discount']
                data['total_amount'] += int(p['qn']) * float(price)
                ordered_services[service] += int(p['qn']) * float(price)
                service_ordered.append(service)
            except:
                pass
        service_ordered = list(set(service_ordered))
        if order.delivery_time:
            delivery_time = order.delivery_time.strftime('%B %d, %Y, %I:%M %p')
        else:
            delivery_time = order.created_at + dt.timedelta(hours=1)
            delivery_time = delivery_time.strftime('%B %d, %Y, %I:%M %p')
        data['service_ordered'] = ', '.join(service_ordered)
        data['delivery_time'] = delivery_time
        data['isCouponApplied'] = 1  # 0 for true & 1 for false
        data['coupon_code_discount'] = ''
        discount_money = 0

        if order.coupon_applied:
            coupon = order.coupon_applied
            if coupon.discount_type == 0:
                discount_money = coupon.discount
            else:
                discount_money = (data['total_amount'] * coupon.discount) / 100
                if discount_money > coupon.limit:
                    discount_money = coupon.limit

            data['total_amount'] -= discount_money
            data['coupon_code'] = coupon.code + ' / ' + str(discount_money)
            data['isCouponApplied'] = 0
        delivery_charges_dictionary_new = simplejson.loads(order.delivery_charges)
        for key in delivery_charges_dictionary_new:
            data['total_amount'] += delivery_charges_dictionary_new[key]['delivery_charges']
        print data['total_amount']
        data['total_amount'] = str(int(data['total_amount']))
        data['id'] = order.id
        orders_to_send.append(data)
    context = {
        'orders': orders_to_send,
        'next_page': next_page,
        'prev_page': prev_page
    }

    return render(request, 'new_custom_admin/all_orders.html', context)

@staff_member_required
def copy_product_in_local_store(request):
    if request.method == "POST" and request.user.has_perm('app.add_storeproductmapping'):
        url = request.POST.get('page_url')
        p_id = request.POST.get('p_to_be_copied_id')
        store_id = request.POST.getlist('copy_store')
        print store_id[0]
        print store_id
        price = request.POST.get('price_to_be_copied')
        price_check = request.POST.get('price_checkbox')
        size_check = request.POST.get('new_size_chk')
        size_mag = request.POST.get('new_size_magnitude')
        size_unit = request.POST.get('new_size_unit')
        print price_check
        if store_id and p_id:
            sp = StoreProductMapping.objects.get(pk=p_id)

            for s_id in store_id:
                store = Store.objects.get(pk=s_id)
                if sp.product.product.category.service in store.services.all():
                    if price_check:
                        # print 'same price'
                        price = sp.price
                    else:
                        try:
                            price = int(price)
                        except:
                            price=None
                            pass
                    if price:
                        size=None
                        if size_check:
                            size = Size.objects.filter(magnitude=float(size_mag),unit=size_unit)
                            if size:
                                size=size[0]
                            else:
                                size = Size(magnitude=float(size_mag),unit=size_unit)
                                size.save()
                        if size:
                            psi= ProductSizeImageMapping.objects.filter(product = sp.product.product,size=size)
                            if psi:
                                psi=psi[0]
                            else:
                                psi = ProductSizeImageMapping(product = sp.product.product,size=size,image=sp.product.image)
                                psi.save()
                            new_sp = StoreProductMapping.objects.filter(product=psi,store=sp.store)
                            if not new_sp:
                                StoreProductMapping(product=psi,store=sp.store,price=price,stock=True).save()
                                LogEntry.objects.log_action(
                                    user_id         = request.user.pk,
                                    content_type_id = ContentType.objects.get_for_model(sp).pk,
                                    object_id       = sp.pk,
                                    object_repr     = str(sp),
                                    action_flag     = ADDITION,
                                    change_message  = "Added product from :: p_id:"+str(p_id)+" store_id: "+str(sp.store.id)
                                    )
                                messages.success(request, ' Product Copied In Main Store also')
                            new_sp = StoreProductMapping.objects.filter(product=psi,store=store)
                            if not new_sp:
                                StoreProductMapping(product=psi,store=store,price=price,stock=True).save()
                                LogEntry.objects.log_action(
                                    user_id         = request.user.pk,
                                    content_type_id = ContentType.objects.get_for_model(sp).pk,
                                    object_id       = sp.pk,
                                    object_repr     = str(sp),
                                    action_flag     = ADDITION,
                                    change_message  = "Added product from :: p_id:"+str(p_id)+" store_id: "+str(store.id)
                                    )
                                messages.success(request, ' Product Copied In Main Store also')
                            else:
                                messages.success(request, ' Product already exist with new size')

                        else:
                            if not StoreProductMapping.objects.filter(store=store,product=sp.product):
                                sp=StoreProductMapping(store = store,product=sp.product,price=price,stock=True)
                                sp.save()
                                LogEntry.objects.log_action(
                                    user_id         = request.user.pk,
                                    content_type_id = ContentType.objects.get_for_model(sp).pk,
                                    object_id       = sp.pk,
                                    object_repr     = str(sp),
                                    action_flag     = ADDITION,
                                    change_message  = "Added product from :: p_id:"+str(p_id)+" store_id: "+str(store_id)
                                    )
                                messages.success(request, ' Product Copied ')
                            else:
                                sp = StoreProductMapping.objects.filter(store = store,product=sp.product)[0]
                                sp.price= price
                                sp.stock=True
                                sp.save()
                                LogEntry.objects.log_action(
                                    user_id         = request.user.pk,
                                    content_type_id = ContentType.objects.get_for_model(sp).pk,
                                    object_id       = sp.pk,
                                    object_repr     = str(sp),
                                    action_flag     = CHANGE,
                                    change_message  = "changed product :: id:"+str(sp.id)+" price: "+str(sp.price)
                                    )
                                messages.warning(request, ' Be Careful!! Product is already exist in store. PS: Price updated and now its visible')
                    else:
                        messages.error(request, ' Invalid Price')

                else:
                    messages.error(request, ' product service not matched with store services')
        else:
            messages.error(request, 'Invalid Store or Product')
        return HttpResponseRedirect(url)



@staff_member_required
def show_all_coupon(request):
    coupons = Coupon.objects.all()
    context={
        'coupons':coupons
    }
    return render(request,'new_custom_admin/all_coupon.html',context)
@staff_member_required
def add_lsm(request):
    services = Service.objects.all()
    locations = Location.objects.all()
    lsm = LocationServiceMapping.objects.all()
    store = Store.objects.all()
    context={
        'services' : services,
        'locations': locations,
        'store': store,
        'lsm': lsm,
        'page':9,
    }

    if request.user.has_perm('app.add_lsm') and request.method=="POST":
        s_sa = request.POST.get("s_sa")
        s_ss = request.POST.get("s_ss")
        s_sh = request.POST.get("s_sh")
        s_active = request.POST.get("s_ia")
        s_coming_soon = request.POST.get("s_cs")
        s_dc = request.POST.get("s_dc")
        s_mda = request.POST.get("s_mda")
        s_mdt = request.POST.get("s_mdt")
        s_do = request.POST.get("s_do")
        s_st = request.POST.get("s_st")
        s_et = request.POST.get("s_et")
        print s_sa

        sa = lsm.objects.filter(name=s_sa)
        ss = lsm.objects.filter(name=s_ss)
        sh = lsm.objects.filter(name=s_sh)

        if not sa and not ss and not sh:
            # s_open = dt.datetime.strptime(s_open,"%I:%M %p")
            # s_end = dt.datetime.strptime(s_end,"%I:%M %p")
            # store = Store(name=s_name,owner_name=s_owner,contact=s_contact,address=s_address,open_time=s_open,end_time=s_end)
            # store.position=s_cord
            store.save()

            # for ss in s_services:
            #     service = Service.objects.get(pk=ss)
            #     store.services.add(service)
            # for ll in s_locations:
            #     location = Location.objects.get(pk=ll)
            #     store.locations.add(location)
            # store.save()
            # LogEntry.objects.log_action(
            #         user_id         = request.user.pk,
            #         content_type_id = ContentType.objects.get_for_model(Store).pk,
            #         object_id       = store.pk,
            #         object_repr     = str(store),
            #         action_flag     = ADDITION,
            #         change_message = "added store with ID : " + str(store.pk)
            #     )
    return render(request,'new_custom_admin/add_lsm.html',context)

@staff_member_required
def edit_lsm_from_table(request, id):

    lsm = LocationServiceMapping.objects.get(pk=id)
    stores = Store.objects.all()
    slm = StoreTimingInLocation.objects.filter(lsm = lsm)
    # print lsm.storetiminginlocation_set.all()
    o_id = request.GET.get("s_id",'')

    context={
        'lsm': lsm,
        'stores':stores,
        'slm':slm,
        }
    if o_id:
        o_active = request.GET.get("s_ia",'')
        o_coming_soon = request.GET.get("s_cs",'')
        o_dc = request.GET.get("s_dc",'')
        # o_mda = request.GET.get("s_mda",'')
        # o_mdt = request.GET.get("s_mdt",'')
        o_do = request.GET.get("s_do",'')
        # o_et = request.GET.get("s_slot_et",'')
        # o_st = request.GET.get("s_slot_st",'')
        # o_st = datetime.strptime(o_st,"%I:%M %p")
        # o_et = datetime.strptime(o_et,"%I:%M %p")
        # tm = TimeSlot(start_time = o_st, end_time = o_et)
        # tm.save()
        # stil = StoreTimingInLocation(store = Store.objects.get(pk=int(request.GET.get("s_slot_shop",''))), lsm =lsm)
        # stil.save()
        #
        # stil.time_slot.add(tm)
        # stil.save()

        # lsm.delivery_charges = int(o_dc)
        # lsm.delivery_min_amount = int(o_mda)
        # lsm.delivery_time_min = int(o_mdt)
        lsm.display_order = int(o_do)
        activity = True
        if o_active=='0':
            activity=False
        cs = True
        if o_coming_soon=='0':
            cs = False
        lsm.isActive = activity
        lsm.isComingSoon = cs


        message="changed location store mappings :: id:"+str(lsm.id)+\
                " isActive: "+str(lsm.isActive)+\
                "coming soon: "+str(lsm.isComingSoon)+\
                " delivery charges: "+str(lsm.delivery_charges)+\
                " min delivery amount "+str(lsm.delivery_min_amount)+\
                " mi delivery time"+str(lsm.delivery_time_min) + \
                " display order:" + str(lsm.display_order)


        lsm.save()

        print lsm.delivery_charges
        LogEntry.objects.log_action(
        user_id         = request.user.pk,
        content_type_id = ContentType.objects.get_for_model(lsm).pk,
        object_id       = lsm.pk,
        object_repr     = str(lsm),
        action_flag     = CHANGE,
        change_message  = message
        )
        logValue=LogEntry.objects.filter(content_type_id=10)
        print logValue.change_message
        messages.success(request, str(lsm.id)+' Saved!!')
        return render(request,'new_custom_admin/blank_page.html')
    return render(request,'new_custom_admin/edit_lsm_from_table.html',context)


@staff_member_required
def show_all_coupon(request):
    coupons = Coupon.objects.all()
    context={
        'coupons':coupons
    }
    return render(request, 'new_custom_admin/all_coupon.html',context)

@staff_member_required
def show_services(request):
    services = Service.objects.all()
    context = {
        'services' : services,
    }
    return render(request, 'new_custom_admin/services.html',context)

@login_required(login_url='/admin/login/')
@staff_member_required
def show_services(request):
    services = Service.objects.all()
    context = {
        'services': services,
    }
    return render(request, 'new_custom_admin/services.html', context)

@staff_member_required
def edit_service(request, id):

    if request.user.has_perm('app.change_service') and request.method=="POST":
        s_name = request.POST.get("s_name")
        s_is_active = request.POST.get("s_is_active")

        service = Service.objects.get(pk=id)
        service.name = s_name
        if s_is_active:
            service.is_active = True
        else:
            service.is_active = False
            message=log_entry_test.change_message(
                'Service Name ',str(service.name),str(s_name),
                'Is Active',str(service.is_active),str(s_is_active)
            )
        service.save()
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(service).pk,
            object_id       = service.pk,
            object_repr     = str(service),
            action_flag     = CHANGE,
            change_message  = message
        )
        logValue=LogEntry.objects.filter(content_type_id=10)
        for log in logValue:
            print log.change_message

        messages.success(request, ' Service Saved')

    service = Service.objects.get(pk=id)
    cat_vs_sub_cat={}
    categories = Category.objects.filter(service=service,parent=None)
    for c in categories:
        sub_cats = Category.objects.filter(service=service,parent=c)
        cat_vs_sub_cat[c]=sub_cats
    context = {
        'service' : service,
        'categories' : categories,
        'cat_vs_sub_cat' : cat_vs_sub_cat,
    }

    return render(request, 'new_custom_admin/edit_service.html',context)

@staff_member_required
def change_service_image(request):
    service_id = request.GET.get('service_id')
    image_url = request.GET.get('service_image')
    context={
        'image':image_url
    }
    if service_id and image_url:
        service = Service.objects.get(pk=service_id)

        isServer =settings.IS_SERVER
        to_be_replace=""
        if isServer==0:
            path1='/home/shubham/webapps/movincart/app/static/serviceImage/'
            to_be_replace="/home/shubham/webapps/movincart/app/"
        else:
            path1='app/static/serviceImage/'
            to_be_replace='app/'
        if 'http' in image_url:
            image = image_url
            if '.png' in image:
                newpath=path1
                urllib.urlretrieve(image, newpath+service.name+'.png')
                resize(newpath+service.name+'.png','m')
                image = newpath.replace(to_be_replace,'/')+service.name+'.png'
                service.image = image+'?t='+dt.datetime.now().strftime("%Y%m%d%H%M%S%f")
                service.save()
            else:
                newpath=path1
                urllib.urlretrieve(image, newpath+service.name+'.jpg')
                resize(newpath+service.name+'.jpg','m')
                image = newpath.replace(to_be_replace,'/')+service.name+'.jpg'
                service.image = image+'?t='+dt.datetime.now().strftime("%Y%m%d%H%M%S%f")

                service.save()
            LogEntry.objects.log_action(
                                user_id         = request.user.pk,
                                content_type_id = ContentType.objects.get_for_model(service).pk,
                                object_id       = service.pk,
                                object_repr     = str(service),
                                action_flag     = CHANGE,
                                change_message  = "Changed Service Image"
                                )
            messages.success(request, ' Service image saved ')
        context={
            'image':str(service.image)
        }
    return render(request,'new_custom_admin/refreshed_image_div.html',context)

@staff_member_required
def show_offers(request):
    offers = Offer.objects.all()
    context = {
        'offers' : offers,
    }
    return render(request,'new_custom_admin/offers.html',context)

@staff_member_required
def edit_offer(request,id):

    if request.user.has_perm('app.change_offer') and request.method=="POST":
        o_name = request.POST.get("o_name")
        o_is_active = request.POST.get("o_is_active")
        valid_till = request.POST.get("valid_till")
        valid_till = parser.parse(valid_till)
        print valid_till
        offer = Offer.objects.get(pk=id)
        offer.name = o_name
        offer.valid_till=valid_till
        if o_is_active:
            offer.is_active = True
        else:
            offer.is_active = False

        message=log_entry_test.change_message(
            'Service Name',offer.name,o_name,
            'Is Active',offer.is_active,o_is_active,
            'Valid till',offer.valid_till,valid_till
        )
        offer.save()
        print offer.valid_till
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(offer).pk,
            object_id       = offer.pk,
            object_repr     = str(offer),
            action_flag     = CHANGE,
            change_message  = message
            )
        logValue=LogEntry.objects.filter(content_type_id=10)
        for log in logValue:
            print log.change_message
    messages.success(request, ' Offer Saved')
    offer = Offer.objects.get(pk=id)
    s = Service.objects.get(name="offer")
    p = OfferProductMapping.objects.filter(product__product__product__category__service=s,offer=offer)
    products = map(lambda x:x.product,p)
    locations = Location.objects.all()
    offer_locations = OfferLocationMapping.objects.filter(offer=offer,is_active=True)
    active_locations = map(lambda x:x.location,offer_locations)
    valid_till = offer.valid_till.strftime("%m/%d/%Y %I:%M %p")
    context = {
        'offer' : offer,
        'products': products,
        'locations' : locations,
        'active_locations' : active_locations,
        'valid_till':valid_till,
    }

    return render(request,'new_custom_admin/edit_offer.html',context)

@staff_member_required
def change_offer_image(request):
    offer_id = request.GET.get('offer_id')
    image_url = request.GET.get('offer_image')
    # print offer_id
    context={
        'image':image_url
    }
    if offer_id and image_url:
        offer = Offer.objects.get(pk=offer_id)

        isServer =settings.IS_SERVER
        to_replace=''
        if isServer==0:
            path1='/home/shubham/webapps/movincart/app/static/offerImage/'
            to_replace="/home/shubham/webapps/movincart/app/"
        else:
            path1='app/static/offerImage/'
            to_replace="app/"
        if 'http' in image_url:
            image = image_url
            if '.png' in image:
                newpath=path1
                urllib.urlretrieve(image, newpath+offer.name+'.png')
                image = newpath.replace(to_replace,'/')+offer.name+'.png'
                offer.image = str(image+'?t='+dt.datetime.now().strftime("%Y%m%d%H%M%S%f")).replace('/home/shubham/webapps/movincart/','').replace('app/','/')
                offer.save()
            else:
                newpath=path1
                urllib.urlretrieve(image, newpath+offer.name+'.jpg')
                image = newpath.replace(to_replace,'/')+offer.name+'.jpg'
                offer.image = str(image+'?t='+dt.datetime.now().strftime("%Y%m%d%H%M%S%f")).replace('/home/shubham/webapps/movincart/','').replace('app/','/')
                offer.save()
        else:
            offer.image=image_url
            offer.save()
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(offer).pk,
            object_id       = offer.pk,
            object_repr     = str(offer),
            action_flag     = CHANGE,
            change_message  = "Changed Service Image"
        )
        messages.success(request, ' Offer image saved ')
    context={
    'image':str(offer.image)
    }
    return render(request,'new_custom_admin/refreshed_image_div.html',context)

@staff_member_required
def add_offer_product(request,id):
    offer = Offer.objects.get(pk=id)
    store = Store.objects.filter(name__icontains="offer")[0]
    sub_cat =Category.objects.filter(~Q(parent=None),name__icontains="offer")[0]
    print sub_cat
    brands=list(set(Product.objects.all().values_list('brand_name',flat=True)))
    context = {
        'offer' : offer,
        'brands':brands
    }
    if request.user.has_perm('app.add_offerproductmapping') and request.method == 'POST':
        p_name=request.POST.get('p_name').title()
        p_brand=request.POST.get('p_brand','').title()
        p_description=request.POST.get('p_description','')
        p_tags=request.POST.get('p_tags','')
        p_max=request.POST.get('p_max','')
        p_rating=request.POST.get('p_rating','')
        p_barcode=request.POST.get('p_barcode','')
        p_related=request.POST.get('p_related','')
        p_price=request.POST.get('p_price','')
        p_discount=request.POST.get('p_discount','')
        p_stock=request.POST.get('p_stock','')
        p_image=request.POST.get('p_image','')
        p_size_mag=request.POST.get('p_magnitude','')
        p_size_unit=request.POST.get('p_unit','')

        prd = Product.objects.filter(name=p_name,brand_name=p_brand,category=sub_cat)

        if prd:
            prd=prd[0]
        else:
            prd = Product(name=p_name,brand_name=p_brand,description=p_description,category=sub_cat)
            prd.save()

            tag_list = str(p_tags).split()
            for t in tag_list:
                prd.tags.create(name=t)

        size_obj = Size.objects.filter(magnitude=int(p_size_mag),unit=p_size_unit)
        if size_obj:
            size_obj=size_obj[0]
        else:
            size_obj=Size(magnitude=int(p_size_mag),unit=p_size_unit)
            size_obj.save()
        image = p_image
        isServer=settings.IS_SERVER
        if isServer==0:
            path1='/home/shubham/webapps/movincart/app/static/productImage/'
        else:
            path1='app/static/productImage/'
        if 'http' in image:
            psi = ProductSizeImageMapping.objects.filter(product=prd,size=size_obj)
            if psi:
                psi = psi[0]
            else:
                psi = ProductSizeImageMapping(product=prd,size=size_obj,image='image')
                psi.save()
            product_id=str(psi.id)
            if '.png' in image:
                newpath=path1+str(product_id)+'/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.png')
                resize(newpath+'item.png','s')
                newpath=path1+str(product_id)+'/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.png')
                resize(newpath+'item.png','xs')
                newpath=path1+str(product_id)+'/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.png')
                resize(newpath+'item.png','xxs')
                newpath=path1+str(product_id)+'/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.png')
                resize(newpath+'item.png','m')
                newpath='/static/productImage/'+str(product_id)+'/m/'
                image = newpath+'item.png'
            else:
                newpath=path1+str(product_id)+'/s/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.jpg')
                resize(newpath+'item.jpg','s')
                newpath=path1+str(product_id)+'/xs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.jpg')
                resize(newpath+'item.jpg','xs')
                newpath=path1+str(product_id)+'/xxs/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.jpg')
                resize(newpath+'item.jpg','xxs')
                newpath=path1+str(product_id)+'/m/'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                urllib.urlretrieve(image, newpath+'item.jpg')
                resize(newpath+'item.jpg','m')
                newpath='/static/productImage/'+str(product_id)+'/m/'
                image = newpath+'item.jpg'
            if not image:
                image = '/static/no_image.jpg'
            psi.image = image
            psi.save()

        sp_mapping = StoreProductMapping.objects.filter(store=store,product=psi)

        if not sp_mapping:
            if p_stock == "true":
                stock = True
            else:
                stock = False
            sp_mapping =StoreProductMapping(store=store,product=psi,price=p_price,discount=p_discount,max_buy=p_max,stock=stock)
            sp_mapping.save()

        op_mapping = OfferProductMapping.objects.filter(offer=offer,product=sp_mapping)
        if op_mapping:
            op_mapping = op_mapping[0]
        else:
            op_mapping = OfferProductMapping(offer=offer,product=sp_mapping)
            op_mapping.save()

        messages.success(request, 'Yo !!! '+p_name+' info saved')

        return render(request, 'new_custom_admin/add_offer_product.html',context)
    return render(request, 'new_custom_admin/add_offer_product.html',context)

@staff_member_required
def show_all_coupon(request):
    coupons = Coupon.objects.all()
    context = {
        'coupons': coupons
    }
    return render(request, 'new_custom_admin/all_coupon.html', context)


@staff_member_required
def edit_offer_product_info_frm_table(request):
    if request.user.has_perm('app.add_storeproductmapping'):
        p_id = request.GET.get('p_id','')
        p_price=request.GET.get('p_price','')
        p_discount=request.GET.get('p_discount','')
        p_visiblity = request.GET.get('p_visiblity')
        p_display_order = request.GET.get('p_display_order')
        p_max_buy = request.GET.get('p_max_buy')

        if p_id:
            spm = StoreProductMapping.objects.get(pk=p_id)
            spm.price = p_price
            spm.discount = p_discount
            visible = True
            if p_visiblity=='0':
                visible=False
            spm.stock = visible
            spm.max_buy=int(p_max_buy)
            spm.display_order=int(p_display_order)
            message=log_entry_test.change_message(
                'Price',p_price,spm.price,
                'Discount',p_discount,spm.discount,
                'Visibility',p_visiblity,visible,
                'Display Order',p_display_order,spm.display_order,
                'Max Buy',p_max_buy,spm.max_buy
            )
            spm.save()
            LogEntry.objects.log_action(
                user_id         = request.user.pk,
                content_type_id = ContentType.objects.get_for_model(spm).pk,
                object_id       = spm.pk,
                object_repr     = str(spm),
                action_flag     = CHANGE,
                change_message  = message
            )
            logValue=LogEntry.objects.filter(content_type_id=10)
            for log in logValue:
                print log.change_message
            messages.success(request, str(spm.product.product.name)+' Saved!!')

    else:
        messages.success(request, ' Not Authorized ')
    return render(request,'new_custom_admin/blank_page.html')

@staff_member_required
def show_all_suggestion(request):
    suggestions = Suggestion.objects.all().order_by('-created_at')
    context = {
        'suggestion': suggestions
    }
    return render(request, 'new_custom_admin/all_suggestion.html', context)

@staff_member_required
def show_user_profile(request):
    userprofiles = UserProfile.objects.all()
    context = {
        'userprofiles': userprofiles
    }
    return render(request, 'new_custom_admin/all_user_profile.html', context)

@staff_member_required
def show_all_visitors(request):
    visitors = Visitor.objects.all()
    context = {
        'visitors': visitors
    }
    return render(request, 'new_custom_admin/all_visitors.html', context)

@staff_member_required
def add_coupon_details(request):
    rule_book=CouponRuleBook.objects.all()
    context = {
        'services': Service.objects.all(),
        'locations' : Location.objects.all(),
        'universal_options' : ['universal','user_specific','new_user'],
    }
    if request.user.has_perm('app.add_coupon') and request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        coupon_discount = request.POST.get("coupon_discount")
        coupon_discount_type=request.POST.get("coupon_discount_type")
        coupon_max_discount_limit= request.POST.get("coupon_max_discount_limit")
        coupon_min_total = request.POST.get("coupon_min_total")
        coupon_used_count= request.POST.get("coupon_used_count")
        coupon_is_active=request.POST.get("coupon_is_active")

        min_total_is_active = request.POST.get("min_total_is_active")
        min_total = request.POST.get("min_total")
        service_type_is_active = request.POST.get("service_type_is_active")
        service_type = request.POST.getlist("service_type")
        service_type = map(lambda x:int(x),service_type)
        universal_is_active = request.POST.get("universal_is_active")
        universal = request.POST.get("universal")
        user_specific_is_active = request.POST.get("user_specific_is_active")
        user_specific = request.POST.get("user_specific")
        if user_specific:
            user_specific = user_specific.split(',')
            user_specific = map(lambda x:int(x),user_specific)
            user_specific = simplejson.dumps(user_specific)
        max_use_number_is_active = request.POST.get("max_use_number_is_active")
        max_use_number = request.POST.get("max_use_number")
        location_is_active = request.POST.get("location_is_active")
        locations = request.POST.getlist("locations")
        locations = map(lambda x:int(x),locations)
        locations = simplejson.dumps(locations)
        min_version_is_active = request.POST.get("min_version_is_active")
        min_version = request.POST.get("min_version")


        if coupon_is_active:
            coupon_is_active = True
        else:
            coupon_is_active = False

        message='Coupon Code '+str(coupon_code)+' Discount '+str(coupon_discount)+' Discount Type '+str(coupon_discount_type)+\
            'Max Discount'+str(coupon_max_discount_limit)+' Min Total '+str(coupon_min_total)+' Used Count '+str(coupon_used_count)+\
            'Is Active '+str(coupon_is_active)+' Expiry Date '+str(dt.datetime.now()
        )
        print message
        coupon = Coupon.objects.filter(code=coupon_code)
        if not coupon:
            coupon=Coupon(
                code=coupon_code,
                discount=coupon_discount,
                discount_type=coupon_discount_type,
                max_discount_limit=coupon_max_discount_limit,
                min_total=coupon_min_total,
                used_count=coupon_used_count,
                is_active=coupon_is_active,
                expiry_date=dt.datetime.now(),
            )

        coupon.save()

        if min_total_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=0,rule_value=str(min_total))
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=0,rule_value=str(min_total))
                crb.save()
                coupon.rule_book.add(crb)

        if service_type_is_active:
            if len(service_type) != 0:
                service_type = simplejson.dumps(service_type)
            else:
                service_type = map(lambda x:x.id,Service.objects.all())
                service_type = simplejson.dumps(service_type)

            rule = CouponRuleBook.objects.filter(rule_type=1,rule_value=service_type)
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=1,rule_value=service_type)
                crb.save()
                coupon.rule_book.add(crb)

        if universal_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=3,rule_value=universal)
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=3,rule_value=universal)
                crb.save()
                coupon.rule_book.add(crb)

        if user_specific_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=4,rule_value=user_specific)
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=4,rule_value=user_specific)
                crb.save()
                coupon.rule_book.add(crb)

        if max_use_number_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=5,rule_value=str(max_use_number))
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=5,rule_value=str(max_use_number))
                crb.save()
                coupon.rule_book.add(crb)

        if location_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=6,rule_value=locations)
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=6,rule_value=locations)
                crb.save()
                coupon.rule_book.add(crb)

        if min_version_is_active:
            rule = CouponRuleBook.objects.filter(rule_type=9,rule_value=min_version)
            if rule:
                coupon.rule_book.add(rule[0])
            else:
                crb = CouponRuleBook(rule_type=9,rule_value=min_version)
                crb.save()
                coupon.rule_book.add(crb)

        coupon.save()


        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(coupon).pk,
            object_id=coupon.pk,
            object_repr=str(coupon),
            action_flag=ADDITION,
            change_message=message
        )
        logValue=LogEntry.objects.filter(content_type_id=10)
        print logValue.change_message
    return render(request, 'new_custom_admin/add_coupon.html',context)

@staff_member_required
def edit_coupon(request, id):
    coupon=Coupon.objects.get(pk=id)
    if request.user.has_perm('app.change_coupon'):
        if request.method == "POST":
            coupon_code = request.POST.get("coupon_code")
            coupon_discount = request.POST.get("coupon_discount")
            coupon_discount_type=request.POST.get("coupon_discount_type")
            coupon_max_discount_limit= request.POST.get("coupon_max_discount_limit")
            coupon_min_total = request.POST.get("coupon_min_total")
            coupon_used_count= request.POST.get("coupon_used_count")
            coupon_is_active=request.POST.get("coupon_is_active")
            min_total_is_active = request.POST.get("min_total_is_active")
            min_total = request.POST.get("min_total")

            service_type_is_active = request.POST.get("service_type_is_active")
            service_type = request.POST.getlist("service_type")
            service_type = map(lambda x:int(x),service_type)
            universal_is_active = request.POST.get("universal_is_active")
            universal = request.POST.get("universal")
            user_specific_is_active = request.POST.get("user_specific_is_active")
            user_specific = request.POST.get("user_specific")
            if user_specific:
                user_specific = user_specific.split(',')
                user_specific = map(lambda x:int(x),user_specific)
                user_specific = simplejson.dumps(user_specific)

            max_use_number_is_active = request.POST.get("max_use_number_is_active")
            max_use_number = request.POST.get("max_use_number")
            location_is_active = request.POST.get("location_is_active")
            locations = request.POST.getlist("locations")
            locations = map(lambda x:int(x),locations)
            locations = simplejson.dumps(locations)
            min_version_is_active = request.POST.get("min_version_is_active")
            min_version = request.POST.get("min_version")
            active_value=coupon_is_active
            if active_value:
                active_value = True
            else:
                active_value = False

            message=log_entry_test.change_message(
                'Coupon Code',coupon.code,coupon_code,
                'Discount',coupon.discount,coupon_discount,
                'Discount Type',coupon.discount_type,coupon_discount_type,
                'Maximum Discount Limit',coupon.max_discount_limit,coupon_max_discount_limit,
                'Used Count',coupon.used_count,coupon_used_count,
                'Min Total',coupon.min_total,coupon_min_total,
                'Is Active',coupon.is_active,active_value
            )

            if coupon:
                coupon.code = coupon_code
                coupon.discount =coupon_discount
                coupon.discount_type= coupon_discount_type
                coupon.max_discount_limit= coupon_max_discount_limit
                coupon.min_total=coupon_min_total
                coupon.used_count = coupon_used_count


                coupon.save()

                coupon.rule_book.clear()
                if min_total_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=0,rule_value=str(min_total))
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=0,rule_value=str(min_total))
                        crb.save()
                        coupon.rule_book.add(crb)

                if service_type_is_active:
                    if len(service_type) != 0:
                        service_type = simplejson.dumps(service_type)
                    else:
                        service_type = map(lambda x:x.id,Service.objects.all())
                        service_type = simplejson.dumps(service_type)

                    rule = CouponRuleBook.objects.filter(rule_type=1,rule_value=service_type)
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=1,rule_value=service_type)
                        crb.save()
                        coupon.rule_book.add(crb)

                if universal_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=3,rule_value=universal)
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=3,rule_value=universal)
                        crb.save()
                        coupon.rule_book.add(crb)

                if user_specific_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=4,rule_value=user_specific)
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=4,rule_value=user_specific)
                        crb.save()
                        coupon.rule_book.add(crb)

                if max_use_number_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=5,rule_value=str(max_use_number))
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=5,rule_value=str(max_use_number))
                        crb.save()
                        coupon.rule_book.add(crb)

                if location_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=6,rule_value=locations)
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=6,rule_value=locations)
                        crb.save()
                        coupon.rule_book.add(crb)

                if min_version_is_active:
                    rule = CouponRuleBook.objects.filter(rule_type=9,rule_value=min_version)
                    if rule:
                        coupon.rule_book.add(rule[0])
                    else:
                        crb = CouponRuleBook(rule_type=9,rule_value=min_version)
                        crb.save()
                        coupon.rule_book.add(crb)
                if coupon_is_active:
                    coupon_is_active=True
                else:
                    coupon_is_active=False


                coupon.save()

                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(coupon).pk,
                    object_id=coupon.pk,
                    object_repr=str(coupon),
                    action_flag=CHANGE,
                    change_message =message
                )
                logValue=LogEntry.objects.filter(content_type_id=25)
                for log in logValue:
                    print log.object_id
                    print log.change_message

                messages.success(request, str(coupon.code)+' Saved!!')
    else:
        messages.success(request, ' Not Authorized ')

    coupon=Coupon.objects.get(pk=id)

    rule_types_selected = map(lambda x: x.rule_type,coupon.rule_book.all())
    rule_selected={}
    for r in rule_types_selected:
        if r==1 or r==6:
            rule_selected[str(r)] = simplejson.loads(coupon.rule_book.filter(rule_type=r)[0].rule_value)
        elif r==4:
            value = ""
            user_value = coupon.rule_book.filter(rule_type=r)[0].rule_value
            if user_value:
                users = simplejson.loads(coupon.rule_book.filter(rule_type=r)[0].rule_value)
                for u in users:
                    if value == "":
                        value = value = str(u)
                    else:
                        value = value + "," + str(u)
            rule_selected[str(r)] = value
        else:
            rule_selected[str(r)] = coupon.rule_book.filter(rule_type=r)[0].rule_value

    context = {
        'coupon':coupon,
        'rule_type_selected':rule_types_selected,
        'rule_selected':rule_selected,
        'services': Service.objects.all(),
        'locations' : Location.objects.all(),
        'universal_options' : ['universal','user_specific','new_user'],
    }
    return render(request, 'new_custom_admin/edit_coupon.html', context)

@staff_member_required
def edit_locations_offer(request):

    if request.user.has_perm('app.add_offerlocationmapping'):
        locations = request.GET.get('locations')
        offer_id = request.GET.get('offer_id')
        offer = Offer.objects.get(pk=offer_id)
        locations = str(locations).split(',')
        previous_mappings = OfferLocationMapping.objects.filter(offer=offer)
        for pm in previous_mappings:
            pm.is_active = False
            pm.save()
        for l in locations:
            location = Location.objects.get(pk=l)
            offer_location = OfferLocationMapping.objects.filter(offer=offer,location=location)
            if offer_location:
                offer_location = offer_location[0]
            else:
                offer_location = OfferLocationMapping(offer=offer,location=location)
            offer_location.is_active = True
            offer_location.save()
        messages.success(request,'Locations Saved!!')

    return render(request,'new_custom_admin/blank_page.html')


@staff_member_required
def show_analytics_full(request):
    if request.user.groups.filter(name='analytics').exists() or request.user.is_superuser:
        context={}
        if request.method=="POST":
            date_range = request.POST.get("date_range_input")
            # print date_range
            context['date_selected']=date_range.strip()
        return render(request,'new_custom_admin/analytics_full.html',context)
    else:
        raise PermissionDenied

@staff_member_required
def get_balance_analytics(request):
    if request.user.groups.filter(name='analytics').exists() or request.user.is_superuser:
        context={}
        date_range = request.GET.get("date_range_input")
        if date_range:
            print date_range
            start_date = parser.parse(date_range.split('-')[0].strip())
            end_date = parser.parse(date_range.split('-')[1].strip())
            # print start_date
            context['balance_data']=analytics.get_balance_data(start_date=start_date,end_date=end_date)
        else:
            context['balance_data']=analytics.get_balance_data()
        return render(request,'new_custom_admin/analytics_ajax/balance_analytics.html',context)
    else:
        raise PermissionDenied

@staff_member_required
def get_new_repeated_users_analytics(request):
    if request.user.groups.filter(name='analytics').exists() or request.user.is_superuser:
        context={}
        date_range = request.GET.get("date_range_input")
        if date_range:
            start_date = parser.parse(date_range.split('-')[0].strip())
            end_date = parser.parse(date_range.split('-')[1].strip())
            context['repeat_user_data']=analytics.get_repeat_user_data(start_date=start_date,end_date=end_date)
        else:
            context['repeat_user_data']=analytics.get_repeat_user_data()
        return render(request,'new_custom_admin/analytics_ajax/users_analytics.html',context)
    else:
        raise PermissionDenied

@staff_member_required
def get_orders_analytics(request):
    if request.user.groups.filter(name='analytics').exists() or request.user.is_superuser:
        context={}
        date_range = request.GET.get("date_range_input")
        if date_range:
            start_date = parser.parse(date_range.split('-')[0].strip())
            end_date = parser.parse(date_range.split('-')[1].strip())
            context['order_sales_data']=analytics.get_order_sales_analytics(start_date=start_date,end_date=end_date)
        else:
            context['order_sales_data']=analytics.get_order_sales_analytics()
        return render(request,'new_custom_admin/analytics_ajax/orders_analytics.html',context)
    else:
        raise PermissionDenied

@staff_member_required
def get_category_ordered_analytics(request):
    if request.user.groups.filter(name='analytics').exists() or request.user.is_superuser:
        context={}

        date_range = request.GET.get("date_range_input")
        if date_range:
            start_date = parser.parse(date_range.split('-')[0].strip())
            end_date = parser.parse(date_range.split('-')[1].strip())
            context = analytics.get_ordered_category_analytics(start_date=start_date,end_date=end_date)
        else:
            context = analytics.get_ordered_category_analytics()
        return render(request,'new_custom_admin/analytics_ajax/category_ordered.html',context)
    else:
        raise PermissionDenied

@staff_member_required
def edit_category_from_service(request):

    if request.user.has_perm('app.change_category') and request.method=="GET":
        cat_id = request.GET.get("cat_id")
        cat_display_order = request.GET.get("cat_display_order")
        cat_is_active = request.GET.get("cat_is_active")
        category = Category.objects.get(pk=cat_id)
        if cat_is_active == "1":
            category.is_active = True
        else:
            category.is_active = False
        category.display_order = cat_display_order

        message=log_entry_test.change_message(
            'Category Display Order',category.display_order,cat_display_order,
            'Is Active ',category.is_active,cat_is_active,
            ''
        )
        category.save()
        print ContentType.objects.get_for_model(Service).pk
        LogEntry.objects.log_action(
            user_id         = request.user.pk,
            content_type_id = ContentType.objects.get_for_model(category).pk,
            object_id       = category.pk,
            object_repr     = str(category),
            action_flag     = CHANGE,
            change_message  =message
        )
        logValue=LogEntry.objectsfilter(content_type_id=10)
        print logValue.change_message
        messages.success(request, str(category.name)+' Saved!!')
    else:
        messages.success(request, ' Not Authorized ')
    return render(request,'new_custom_admin/blank_page.html')

@staff_member_required
def add_location_in_store(request):
    if request.user.has_perm('app.add_store'):
        if request.method == "POST":
            store_id = request.POST.get('store_id')
            store=Store.objects.get(pk=store_id)
            location_id = request.POST.get('new_location')
            location=Location.objects.get(pk=location_id)
            service_id = request.POST.get('new_service')
            service=Service.objects.get(pk=service_id)
            time_slot_id = request.POST.getlist('new_time_slot')
            time_slots = TimeSlot.objects.filter(pk__in=time_slot_id)
            dc = request.POST.get('new_dc')
            mda = request.POST.get('new_mda')
            rmdt = request.POST.get('new_rmdt')
            nmdt = request.POST.get('new_nmdt')
            lsm = LocationServiceMapping.objects.filter(location=location,service=service)
            if lsm:
                lsm=lsm[0]
            else:
                lsm=LocationServiceMapping(location_id=location_id,service_id=service_id,is_active=False)
                lsm.save()
            if not StoreTimingInLocation.objects.filter(lsm=lsm,store=store):
                stl = StoreTimingInLocation(lsm=lsm,store=store)
                stl.save()
            else:
                stl = StoreTimingInLocation.objects.filter(lsm=lsm,store=store)[0]
            stl.time_slot.clear()
            for time_slot in time_slots:
                stl.time_slot.add(time_slot)
            stl.delivery_charges=dc
            stl.delivery_min_amount=mda
            stl.rush_hours_delivery_time_min=rmdt
            stl.normal_hours_delivery_time_min=nmdt
            stl.save()
            messages.success(request,'Store Location added')
            return HttpResponseRedirect("/movinCartAdmin/edit_store/"+store_id+"/")
    return HttpResponseRedirect("/movinCartAdmin/show_stores/")

@staff_member_required
def edit_stl_info_frm_table(request):
    if request.user.has_perm('app.add_store'):
        stl_id = request.GET.get('stl_id')
        dc = request.GET.get('dc')
        mda = request.GET.get('mda')
        rmdt = request.GET.get('rmdt')
        nmdt = request.GET.get('nmdt')
        ts_id = request.GET.get('ts')
        is_active = request.GET.get('is_active')
        stl=StoreTimingInLocation.objects.get(pk=stl_id)
        stl.delivery_charges=dc
        if ts_id:
            ts=TimeSlot.objects.get(pk=ts_id)
            stl.time_slot.clear()
            stl.time_slot.add(ts)
        stl.delivery_min_amount=mda
        stl.rush_hours_delivery_time_min=rmdt
        stl.normal_hours_delivery_time_min=nmdt
        if is_active=='true':
            stl.is_active=True
        else:
            stl.is_active=False
        stl.save()
        messages.success(request, ' Saved Changes ')
    else:
        messages.success(request, ' Not Authorized ')
    return render(request,'new_custom_admin/blank_page.html')

@staff_member_required
def copy_product_from_main(request):
    if request.user.has_perm('app.add_store'):
        store_id = request.GET.get('store_id')
        if store_id:
            store=Store.objects.get(pk=store_id)
            fnv = Service.objects.get(pk=3)
            if fnv in store.services.all():
                main_fnv_store = Store.objects.get(pk=6)
                sps = StoreProductMapping.objects.filter(store=main_fnv_store)
                for sp in sps:
                    if not StoreProductMapping.objects.filter(store=store,product=sp.product):
                        StoreProductMapping(store=store,product=sp.product,price=sp.price,stock=False).save()
                messages.success(request, ' Copied successfully!! Please Refresh Page to See changes')
            else:
                messages.success(request, ' Can not copy')
        else:
            messages.error(request, ' ERROR')
    else:
        messages.success(request, ' Not Authorized ')
    return render(request,'new_custom_admin/blank_page.html')

@staff_member_required
def get_store_product_json(request):
    data=[]
    sp_id = request.GET.get('sp_id')
    stores = request.GET.get('store','').split(',')
    categories = request.GET.get('category','').split(',')
    if categories==[""]:
        categories=[]
    keyword = request.GET.get('p_name')
    print stores
    print categories
    print keyword
    store_products=[]
    if sp_id:
        store_products=[StoreProductMapping.objects.get(pk=sp_id)]
    else:
        for s in stores:
            if categories!=[] and categories !="":
                if keyword:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                        Q(product__product__category__id__in=categories) & (
                        Q(product__product__name__icontains=keyword) | Q(
                        product__product__brand_name__icontains=keyword)))
                else:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                        product__product__category__id__in=categories)
            else:
                if keyword:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.filter(
                    Q(product__product__name__icontains=keyword) | Q(
                    product__product__brand_name__icontains=keyword))
                else:
                    store_products += Store.objects.get(pk=s).storeproductmapping_set.all()
    for sp_object in store_products:
        sp={}
        sp['id']=sp_object.id
        sp['image']='<a target="_blank" href="'+str(sp_object.product.image)+'" id="p_image'+str(sp_object.id)+'"><img height="42" width="42" src="'+str(sp_object.product.image)+'"></a>'
        sp['name']='<a href="/admin/app/storeproductmapping/%s/" target="_blank">%s</a>'%(str(sp_object.id),str(sp_object.product.product.name))
        sp['brand']=sp_object.product.product.brand_name
        sp['store']=str(sp_object.store)
        sp['category']=str(sp_object.product.product.category)
        sp['size']=str(sp_object.product.size)
        sp['price']='<p style="display:none">%s</p><input id="p_price%s" class="form-control" style="width:80px;" type="text" value="%s">'%(str(sp_object.price),str(sp_object.id),str(sp_object.price))
        sp['discount']='<p style="display:none">%d</p><input id="p_discount%d"class="form-control" style="width:80px;" type="text" value="%d">'%(sp_object.discount,sp_object.id,sp_object.discount)
        sp['order']='<p style="display:none">%d</p><input id="p_display_order%d" class="form-control" style="width:80px;" type="text" value="%d">'%(sp_object.display_order,sp_object.id,sp_object.display_order)
        sp['max_buy']='<p style="display:none">%d</p><input class="form-control" id="p_max_buy%d" style="width:80px;" type="text" value="%d">'%(sp_object.max_buy,sp_object.id,sp_object.max_buy)

        if sp_object.stock:
            sp['status']='<p style="display:none">%s</p><select class="form-control" id="p_visiblity%d" name="p_visiblity"><option value="1" selected >ON</option><option value="0">OFF</option></select>'%(str(sp_object.stock),sp_object.id)
        else:
            sp['status']='<p style="display:none">%s</p><select class="form-control" id="p_visiblity%d" name="p_visiblity"><option value="1">ON</option><option selected value="0">OFF</option></select>'%(str(sp_object.stock),sp_object.id)

        sp['action']='<button id="save_button%d" onclick="save_product(%d)" class="btn btn-success btn-rounded-20 mb-10"><i class="fa fa-save"></i></button>'%(sp_object.id,sp_object.id)
        if sp_object.store.id in constant.main_stores:
            sp['action'] += '<a data-toggle="modal" onclick="copy_product(%d)" data-target="#copy_Model"><button class="btn btn-blue btn-rounded-20 mb-10"><i class="fa fa-copy"></i></button></a>'%(sp_object.id)

        data.append(sp)
    data = simplejson.dumps({'data':data})
    return HttpResponse(data, content_type='application/json')

@staff_member_required
def get_location_service_mapping(request):
    lsm = LocationServiceMapping.objects.all()
    context = {
        'lsm': lsm,
    }

    return render(request, 'new_custom_admin/location_service_mapping.html', context)

@staff_member_required
def edit_location_service_mapping(request):
    if request.user.has_perm('app.change_locationservicemapping'):
        lsm_id = request.GET.get('lsm_id','')
        lsm_is_active = request.GET.get("lsm_is_active",'')
        lsm_is_coming_soon = request.GET.get("lsm_is_coming_soon",'')
        lsm_display_order = request.GET.get("lsm_display_order",'')

        if lsm_id:
            lsm = LocationServiceMapping.objects.get(pk=lsm_id)

            lsm.display_order = lsm_display_order

            if lsm_is_active == 'true':
                lsm.is_active = True
            else:
                lsm.is_active = False
            if lsm_is_coming_soon == 'true':
                lsm.is_coming_soon = True
            else:
                lsm.is_coming_soon = False

                message=log_entry_test.change_message(
                    'isActive',lsm.is_active,lsm_is_active,
                    'Coming Soon',lsm.is_coming_soon,lsm_is_coming_soon,
                    'Display Order',lsm.display_order,lsm_display_order
                )

            lsm.save()
            print lsm.is_coming_soon
            print lsm.is_active
            print lsm.display_order
            print ContentType.objects.get_for_model(lsm).pk

            LogEntry.objects.log_action(
                user_id         = request.user.pk,
                content_type_id = ContentType.objects.get_for_model(lsm).pk,
                object_id       = lsm.pk,
                object_repr     = str(lsm),
                action_flag     = CHANGE,
                change_message  = message
            )
            logValue=LogEntry.objects.filter(content_type_id=10)
            print logValue.change_message
            messages.success(request, str(lsm.service.name + lsm.location.sub_area)+' Saved!!')
    else:
        messages.warning(request, 'Something is not right!!')
    return render(request,'new_custom_admin/blank_page.html')
