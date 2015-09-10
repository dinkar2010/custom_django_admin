import xlwt
from app.models import *


def removeNonAscii(s):
    try:
        s = unidecode(s)
    except:
        pass

    try:
        return "".join(i for i in s if ord(i) < 128)
    except:
        return ""
def my_unicode(s):

	s=removeNonAscii(s)

	if s == None:
		return s

	try:
		s = unicode(unidecode(s))
	except:
		pass

	if isinstance(s, unicode):
		return unicode(s)
	else:
		try:
			return unicode(unidecode(s.decode('utf-8')))
		except:
			return unicode(s.decode('utf-8'))
# def is_number(s):
#     try:
#         float(s)
#         return True
#     except ValueError:
#         return False
#Old/New User	Name/No.	Services Ordered	Locality	Status	Coupon	Offer Applied	Total Amount	Final Amount
def save_dump(start_date,end_date):

    orders =Order.objects.filter(created_at__gte=start_date,created_at__lte=end_date).order_by('-created_at')
    book = xlwt.Workbook()
    sheet = book.add_sheet("Orders", cell_overwrite_ok=True)
    sheet.write(0,0,'ID')
    sheet.write(0,1,'Old/New')
    sheet.write(0,2,'Name')
    sheet.write(0,3,'Number')
    sheet.write(0,4,'Service Ordered')
    sheet.write(0,5,'Locality')
    sheet.write(0,6,'Status')
    sheet.write(0,7,'Coupon')
    sheet.write(0,8,'Offer Applied')
    sheet.write(0,9,'Total Amount')
    sheet.write(0,10,'Final Amount')
    sheet.write(0,11,'Date')
    sheet.write(0,12,'Address')
    sheet.write(0,13,'Landmark')
    sheet.write(0,14,'product_ids')
    index =1
    for order in orders:
        user = order.user
        created_at = order.created_at
        prev_orders = Order.objects.filter(created_at__lt=created_at,status__in=[0,8],user=user)

        old_new = "new"
        if user.username in constant.old_users:
            old_new="old"
        if prev_orders:
            old_new = "old"
        service_ordered = []
        invoice = order.invoice
        ordered_product = simplejson.loads(invoice.product_json)
        product_ids=[]
        for p in ordered_product:
            product_ids.append(str(p['spid']))
            try:
                prd = StoreProductMapping.objects.get(pk=p['spid'])
                service = prd.product.product.category.service.name
                service_ordered.append(service)
            except:
                pass
        service_ordered = ', '.join(list(set(service_ordered)))

        is_coupon = False
        if order.coupon_applied:
            is_coupon = True

        is_offer_applied= False
        if 'offer' in service_ordered.lower():
            is_offer_applied=True

        sheet.write(index,0,order.id)
        sheet.write(index,1,old_new)
        sheet.write(index,2,str(my_unicode(order.user.first_name)))
        sheet.write(index,3,str(my_unicode(order.user.username)))
        sheet.write(index,4,str(my_unicode(service_ordered)))
        sheet.write(index,5,str(my_unicode(order.address.location.sub_area)))
        sheet.write(index,6,order.get_status_display())
        sheet.write(index,7,is_coupon)
        sheet.write(index,8,is_offer_applied)
        sheet.write(index,9,order.total_amount)
        sheet.write(index,10,order.final_amount)
        sheet.write(index,11,str(order.created_at.date()))
        sheet.write(index,12,str(my_unicode(order.address.address)))
        sheet.write(index,13,str(my_unicode(order.address.landmark)))
        # try:
        product_ids = ','.join(product_ids)
        # except:
        #     product_ids=""
        #     pass
        sheet.write(index,14,product_ids)


        index+=1
    isServer =settings.IS_SERVER
    path1=''
    if isServer==0:
        path1='/home/shubham/webapps/movincart/'

    book.save(path1+'dump/orders_on_server.xls')


def save_dump_format2(start_date,end_date):

    orders =Order.objects.filter(created_at__gte=start_date,created_at__lte=end_date).order_by('-created_at')
    book = xlwt.Workbook()
    sheet = book.add_sheet("Orders", cell_overwrite_ok=True)
    sheet.write(0,0,'ID')
    sheet.write(0,1,'Old/New')
    sheet.write(0,2,'Name')
    sheet.write(0,3,'Number')
    sheet.write(0,4,'Service Ordered')
    sheet.write(0,5,'Locality')
    sheet.write(0,6,'Status')
    sheet.write(0,7,'Coupon')
    sheet.write(0,8,'Total Amount without discount')
    sheet.write(0,9,'Discounted Total')
    sheet.write(0,10,'Date')
    sheet.write(0,11,'Address')
    sheet.write(0,12,'Landmark')
    index =1
    for order in orders:
        user = order.user
        created_at = order.created_at
        prev_orders = Order.objects.filter(created_at__lt=created_at,status__in=[0,8],user=user)

        old_new = "new"
        if prev_orders:
            old_new = "old"
        service_ordered = {}
        service_ordered_discounted={}
        invoice = order.invoice
        ordered_product = simplejson.loads(invoice.product_json)
        product_ids=[]
        for p in ordered_product:
            product_ids.append(p['spid'])
            try:
                prd = StoreProductMapping.objects.get(pk=p['spid'])
                service = prd.product.product.category.service.name
                if service not in service_ordered:
                    service_ordered[service]=0
                    service_ordered_discounted[service]=0
                price =p['price']
                if 'discount' in p:
                    price=p['price']-p['discount']
                service_ordered_discounted[service]+=int(p['qn'])*float(p['price']-p['discount'])
                service_ordered[service]+=int(p['qn'])*float(p['price']-p['discount'])
            except:
                pass
        # service_ordered = ', '.join(list(set(service_ordered)))

        is_coupon = False
        if order.coupon_applied:
            is_coupon = True

        for key in service_ordered:
            sheet.write(index,0,order.id)
            sheet.write(index,1,old_new)
            sheet.write(index,2,str(my_unicode(order.user.first_name)))
            sheet.write(index,3,str(my_unicode(order.user.username)))
            sheet.write(index,4,str(my_unicode(key)))
            sheet.write(index,5,str(my_unicode(order.address.location.sub_area)))
            sheet.write(index,6,order.get_status_display())
            sheet.write(index,7,is_coupon)
            sheet.write(index,8,service_ordered[key])
            sheet.write(index,9,service_ordered_discounted[key])
            sheet.write(index,10,str(order.created_at.date()))
            sheet.write(index,11,str(my_unicode(order.address.address)))
            sheet.write(index,12,str(my_unicode(order.address.landmark)))


            index+=1
    isServer =settings.IS_SERVER
    path1=''
    if isServer==0:
        path1='/home/shubham/webapps/movincart/'

    book.save(path1+'dump/orders_on_server.xls')

def save_order_dump_per_ids(start_date,end_date, product_ids,find_other_product=True):
    print "------#-------"
    if find_other_product:
        size = len(product_ids)
        for p in range(size):
            prd = StoreProductMapping.objects.get(pk=product_ids[p]).product
            sps = StoreProductMapping.objects.filter(product=prd)
            for sp in sps:
                product_ids.append(sp.id)
        product_ids = list(set(product_ids))
    print '-----------'
    print product_ids
    orders = Order.objects.filter(created_at__gte=start_date,created_at__lte=end_date).order_by('-created_at')
    book = xlwt.Workbook()
    sheet = book.add_sheet("Orders", cell_overwrite_ok=True)
    sheet.write(0,0,'ID')
    sheet.write(0,1,'Date')
    sheet.write(0,2,'Name')
    sheet.write(0,3,'Number')
    sheet.write(0,4,'Locality')
    sheet.write(0,5,'Status')
    sheet.write(0,6,'Coupon')
    sheet.write(0,7,'Final Amount')
    sheet.write(0,8,'Address')
    sheet.write(0,9,'Landmark')
    sheet.write(0,10,'Product')
    sheet.write(0,11,'Store Name')
    sheet.write(0,12,'Price')
    sheet.write(0,13,'Discounted Price')
    sheet.write(0,14,'Quantity')
    sheet.write(0,15,'Total Discounted Price')
    index =1
    for order in orders:
        invoice = order.invoice
        ordered_product = simplejson.loads(invoice.product_json)
        is_coupon = False
        if order.coupon_applied:
            is_coupon = True
        for p in ordered_product:
            try:
                prd = StoreProductMapping.objects.get(pk=p['spid'])
                size = Size.objects.get(pk=p['size_id'])
                service = prd.product.product.category.service.name
                price =p['price']
                if 'discount' in p:
                    price=p['price']-p['discount']
                flag = False

                if prd.id in product_ids:
                    flag = True
                if flag:
                    sheet.write(index,0,order.id)
                    sheet.write(index,1,str(order.created_at.date()))
                    sheet.write(index,2,str(my_unicode(order.user.first_name)))
                    sheet.write(index,3,str(my_unicode(order.user.username)))
                    sheet.write(index,4,str(my_unicode(order.address.location.sub_area)))
                    sheet.write(index,5,order.get_status_display())
                    sheet.write(index,6,is_coupon)
                    sheet.write(index,7,order.final_amount)
                    sheet.write(index,8,str(my_unicode(order.address.address)))
                    sheet.write(index,9,str(my_unicode(order.address.landmark)))
                    sheet.write(index,10,str(my_unicode(p['name'])+" "+str(size.magnitude)+" "+str(size.unit)))
                    sheet.write(index,11,str(my_unicode(prd.store.name)))
                    sheet.write(index,12,str(p['price']))
                    sheet.write(index,13,str(p['price']-p['discount']))
                    sheet.write(index,14,str(p['qn']))
                    sheet.write(index,15,str(int(p['qn'])*(float(p['price']-p['discount']))))
                    index+=1
            except:
                pass

    isServer =settings.IS_SERVER
    path1=''
    if isServer==0:
        path1='/home/shubham/webapps/movincart/'

    book.save(path1+'dump/orders_on_server.xls')