import urllib
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app.models import Location, StoreTimingInLocation, OfferLocationMapping, OfferProductOrderMapping, Category, \
    StoreProductMapping, OfferDeviceId
from app.utils import constant, api_helper
from django.db.models import Q
import simplejson


@csrf_exempt
def get_available_services(request):
    # api/v1/available_services/?format=json&location__mpoly__contains=&version=32&
    # device_id=00000000-6305-d2aa-e2d5-38766587c3b3&contact=9820794989
    data = []

    pkt = request.GET.get('location__mpoly__contains')
    version = request.GET.get('version')
    device_id = request.GET.get('device_id')
    contact = request.GET.get('contact')

    pkt = simplejson.loads(pkt.split("'coordinates':")[1].replace("}", ""))
    pkt = 'POINT(' + str(pkt[0]) + ' ' + str(pkt[1]) + ')'
    try:
        location_obj = Location.objects.get(mpoly__contains=pkt)
    except:
        location_obj = None

    if not location_obj:
        print 'location not found'
        data = simplejson.dumps({
            'objects': data,
            'settings': {
                'discard': "true",
                'is_valid_time': True,
                'multi_service': "true",
                'version_no': constant.APP_VERSION,
            }
        })
        return HttpResponse(data, content_type='application/json')

    def function(stl):
        """

        :type stl: StoreTimingInLocation
        """
        return stl.lsm

    location_service_mappings = map(
        function, StoreTimingInLocation.objects.filter(
            lsm__service__is_active=True,
            lsm__location=location_obj,
            is_active=True,
            lsm__is_active=True
        ).distinct()
    )
    services = []
    new_location_service_mappings = []
    for lsm in location_service_mappings:
        if lsm.service.id not in services:
            new_location_service_mappings.append(lsm)
            services.append(lsm.service.id)
    for lsm in new_location_service_mappings:
        store_timing_in_locations = StoreTimingInLocation.objects.filter(is_active=True, lsm=lsm)[0]
        service_data = dict(
            current_location_id=location_obj.id,
            isComingSoon=False,
            service=dict(
                delivery_charges=store_timing_in_locations.delivery_charges,
                delivery_min_amount=store_timing_in_locations.delivery_min_amount,
                delivery_time_min=store_timing_in_locations.normal_hours_delivery_time_min,
                display_order=lsm.display_order,
                operating_time_end=str(store_timing_in_locations.time_slot.all()[0].end_time),
                operating_time_start=str(store_timing_in_locations.time_slot.all()[0].start_time),
                id=lsm.service.id,
                category=api_helper.get_cat_structure_for_service(lsm.service, location_obj),
                name=lsm.service.name,
                image=str(lsm.service.image),
            )
        )
        data.append(service_data)
    offer = OfferLocationMapping.objects.filter(location=location_obj, is_active=True, offer__is_active=True)
    offer_data=None
    if version and offer:
        offer = offer[0].offer

        if not contact:
            contact = ""

        if (not OfferDeviceId.objects.filter(device_id=device_id)) and offer.offerproductmapping_set.all()[0].product.stock:
            offer_data = dict(id=offer.id, image=str(offer.image))
    if offer_data:
        data = simplejson.dumps({
            'objects': data,
            'settings': {
                'discard': "true",
                'is_valid_time': True,
                'multi_service': "true",
                'version_no': constant.APP_VERSION,
            },
            'offer': offer_data
        })
    else:
        data = simplejson.dumps({
            'objects': data,
            'settings': {
                'discard': "true",
                'is_valid_time': True,
                'multi_service': "true",
                'version_no': constant.APP_VERSION,
            }
        })
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_store_products(request):
    data = []
    location_id = request.GET.get('store__locations')
    cat_id = request.GET.get('product__product__category')
    search_regex = request.GET.get('product__product__tags__name__iregex')

    sps = []
    meta = {
        'limit': 12,
        'next': None,
        'offset': int(request.GET.get('offset', '0')),
        'previous': None,
        'total_count': 0
    }

    def function(stl):
        """

        :type stl: StoreTimingInLocation
        """
        return stl.store

    if location_id and cat_id:
        # print 'done'
        cat = Category.objects.get(pk=cat_id)
        service = cat.service

        shops = map(
            function, StoreTimingInLocation.objects.filter(
                lsm__location=location_id,
                lsm__service=service,
                lsm__service__is_active=True,
                is_active=True,
                store__is_active=True
            ).distinct()
        )
        sps = StoreProductMapping.objects.filter(
            store__in=shops,
            stock=True,
            product__product__category__is_active=True,
            product__product__category__parent__is_active=True,
            product__product__category=cat
        ).distinct()
        meta['total_count'] = sps.count()

        sps = sps.order_by('-display_order')[meta['offset']:meta['offset'] + meta['limit']]
        if meta['offset'] + meta['limit'] < meta['total_count']:
            meta['next'] = "/api/v1/store_product/?limit={0}&store__locations={1}&product__product__category={2}&offset={3}&format=json".format(
                str(meta['limit']), str(location_id), str(cat_id), str(int(meta['offset'] + meta['limit'])))

    elif search_regex and location_id:
        print search_regex
        shops = map(
            function, StoreTimingInLocation.objects.filter(
                lsm__location=location_id,
                lsm__service__is_active=True,
                is_active=True,
                store__is_active=True
            ).distinct()
        )
        sps = StoreProductMapping.objects.filter(
            store__in=shops,
            stock=True,
            product__product__category__is_active=True,
            product__product__category__parent__is_active=True,
            product__product__tags__name__iregex=search_regex
        ).distinct()
        meta['total_count'] = sps.count()

        sps = sps.order_by('-display_order')[meta['offset']:meta['offset'] + meta['limit']]
        if meta['offset'] + meta['limit'] < meta['total_count']:
            meta['next'] = "/api/v1/store_product/?limit=" + str(meta['limit']) + "&store__locations=" + str(location_id) + "&product__product__tags__name__iregex=" + urllib.quote(str(search_regex)) + "&offset=" + str(meta['offset'] + meta['limit']) + "&format=json"

    for sp in sps:
        prd = sp.product.product
        service = sp.product.product.category.service
        p_object = {
            'discount': sp.discount,
            'display_order': 0,
            'id': sp.id,
            'price': int(sp.price),
            'max_buy': sp.max_buy,
            'product': {
                'image': str(sp.product.image),
                'size': {
                    'magnitude': sp.product.size.magnitude,
                    'unit': sp.product.size.unit
                },
                'product': {
                    'brand_name': prd.brand_name,
                    'category': prd.category.id,
                    'name': prd.name,
                    'service_id': service.id,
                },
            },
        }
        data.append(p_object)

    data = simplejson.dumps({'meta': meta, 'objects': data})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_products_per_category(request, ids):
    # api/v1/products_per_cat/set/57;59/?format=json&location=1
    ids = ids.split(';')
    location_id = request.GET.get('location')
    cats = Category.objects.filter(pk__in=ids)

    def function(stl):
        """

        :type stl: StoreTimingInLocation
        """
        return stl.store

    shops = map(function,
                StoreTimingInLocation.objects.filter(lsm__location__id=location_id, lsm__service=cats[0].service,
                                                     is_active=True, store__is_active=True).distinct())
    data = []
    for cat in cats:
        cat_data = dict(id=cat.id)
        cat_data['products'] = []
        sps = StoreProductMapping.objects.filter(store__in=shops, stock=True,
                                                 product__product__category__is_active=True,
                                                 product__product__category__parent=cat).order_by('-display_order').distinct()[:6]
        for sp in sps:
            prd = sp.product.product
            service = sp.product.product.category.service
            p_object = {
                'discount': sp.discount,
                'display_order': 0,
                'id': sp.id,
                'price': int(sp.price),
                'max_buy': sp.max_buy,
                'product': {
                    'image': str(sp.product.image),
                    'size': {
                        'magnitude': sp.product.size.magnitude,
                        'unit': sp.product.size.unit
                    },
                    'product': {
                        'brand_name': prd.brand_name,
                        'category': prd.category.id,
                        'name': prd.name,
                        'service_id': service.id
                    }
                }
            }
            cat_data['products'].append(p_object)

        data.append(cat_data)
    data = simplejson.dumps({'objects': data})
    return HttpResponse(data, content_type='application/json')
