from tastypie.authentication import ApiKeyAuthentication
from tastypie.models import ApiKey
from app.es_movincart import es_utils
from app.models import *
from app.utils import sms_send_otp
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import simplejson
import datetime as dt
import time

@csrf_exempt
def send_otp(request):
	data="Done"
	username = request.POST.get('userName','')
	contact=""
	if 'contact' in request.POST.keys():
		contact = request.POST.get('contact','')
	email = request.POST.get('email','')
	app_id = request.POST.get('app_id','')
	device_id = request.POST.get('device_id','')
	app_version = request.POST.get('app_version',"")
	user = User.objects.filter(username=contact)
	if user:
		user=user[0]
		userProfile =user.userprofile
		if userProfile:
			userProfile.app_version=app_version
			userProfile.app_id=app_id
			userProfile.device_id=device_id
			userProfile.save()
		else:
			UserProfile(user=user,contact=int(contact),app_id=app_id,app_version=app_version,device_id=device_id).save()
	else:
		user=User.objects.create_user(contact,email,contact)
		user.first_name=username
		user.save()
		UserProfile(user=user,contact=int(contact),app_id=app_id,app_version=app_version,device_id=device_id).save()

	if contact:
		sms_send_otp.send_otp(contact)

	return HttpResponse(data, content_type='application/json')

@csrf_exempt
def check_otp_sync_address(request):
	data=[]
	contact = request.GET.get('contact','')
	otp = request.GET.get('otp','')
	customer = UserProfile.objects.filter(contact=int(contact))
	customer = customer[0]
	if customer.otp == otp:
		user = customer.user
		customerAddress = Address.objects.filter(user=user)
		for ca in customerAddress:
			if ca.location_show:
				data.append({'id':ca.id,'address':ca.address,'landmark':ca.landmark,'location_show':ca.location_show,'location_id':ca.location.id})

		try:
			api_key = ApiKey.objects.get(user=user)
		except ApiKey.DoesNotExist:
			api_key = ApiKey.objects.create(user=user)

		data = simplejson.dumps({'fields':data,'api_key':api_key.key})
	return HttpResponse(data, content_type='application/json')

@csrf_exempt
def get_past_orders(request):
	data=[]
	username = request.GET.get('username','')
	user = User.objects.filter(username=username)

	orders = Order.objects.filter(user=user).order_by('-created_at')
	if orders:
		for order in orders:
			try:
				address = order.address
				if order.status==1:
					delivery_time = "Order Cancelled"
				elif order.status!=0 and order.status !=8:
					current_time = dt.datetime.now()
					current_time = int(time.mktime(current_time.timetuple()))
					delivery_time = (order.created_at + dt.timedelta(hours=1))
					delivery_time = int(time.mktime(delivery_time.timetuple()))
					if int(current_time)<int(delivery_time):
						delivery_time = (order.created_at + dt.timedelta(hours=1)).strftime('%I:%M %p')
						delivery_time = "Will be delivered before\n"+delivery_time
					else:
						delivery_time = "Processing"
				elif order.status== 0 or order.status == 8 :
					delivery_time=order.modified_at.strftime('%I:%M %p, %B %d, %Y')
					delivery_time = "Delivered on\n"+delivery_time

				products = simplejson.loads(order.invoice.product_json)

				carts=[]
				p_data=[]
				for p in products:
					product = {'name':p['name']}
					size = Size.objects.get(pk=p['size_id'])
					size = {'unit':size.unit,'magnitude':size.magnitude}
					prdimage = StoreProductMapping.objects.get(pk=p['spid']).product
					image = prdimage.image
					print image
					product1 = {'image':str(image),'product':product,'size':size}
					product2 = {'product':product1,'id':0,'max_buy':0,'display_order':0,'price':p['price'],'discount':p['discount']}
					p_data.append({'product':product2,'quantity':p['qn']})
				carts.append({'products':p_data})
				data1 = {'address':address.address,'landmark':address.landmark,'location_show':address.location_show,'location_id':address.location.id,'user':address.user.id}
				data2 = {'email':order.user.email,'username':order.user.username}
				data.append({'address':data1,'user':data2,'carts':carts,'change_requested':order.change_requested,'final_amount':order.final_amount,
							 'id':order.id,'status':0,'total_amount':order.total_amount,'order_status':delivery_time})
			except:
				pass
	data = simplejson.dumps({'objects':data})
	return HttpResponse(data, content_type='application/json')

@csrf_exempt
def get_past_orders_v2(request):
	data=[]
	username = request.GET.get('username','')
	user_api_key = request.GET.get('api_key','')
	user = User.objects.filter(username=username)

	try:
		api_key = ApiKey.objects.get(user=user)
		if api_key.key != user_api_key:
			return HttpResponse("", content_type='application/json')
	except:
		return HttpResponse("", content_type='application/json')

	orders = Order.objects.filter(user=user).order_by('-created_at')
	if orders:
		for order in orders:
			try:
				address = order.address
				if order.status==1:
					delivery_time = "Order Cancelled"
				elif order.status!=0 and order.status !=8:
					current_time = dt.datetime.now()
					current_time = int(time.mktime(current_time.timetuple()))
					delivery_time = (order.created_at + dt.timedelta(hours=1))
					delivery_time = int(time.mktime(delivery_time.timetuple()))
					if int(current_time)<int(delivery_time):
						delivery_time = (order.created_at + dt.timedelta(hours=1)).strftime('%I:%M %p')
						delivery_time = "Will be delivered before\n"+delivery_time
					else:
						delivery_time = "Processing"
				elif order.status== 0 or order.status == 8 :
					delivery_time=order.modified_at.strftime('%I:%M %p, %B %d, %Y')
					delivery_time = "Delivered on\n"+delivery_time

				products = simplejson.loads(order.invoice.product_json)

				carts=[]
				p_data=[]
				for p in products:
					product = {'name':p['name']}
					size = Size.objects.get(pk=p['size_id'])
					size = {'unit':size.unit,'magnitude':size.magnitude}
					prdimage = StoreProductMapping.objects.get(pk=p['spid']).product
					image = prdimage.image
					print image
					product1 = {'image':str(image),'product':product,'size':size}
					product2 = {'product':product1,'id':0,'max_buy':0,'display_order':0,'price':p['price'],'discount':p['discount']}
					p_data.append({'product':product2,'quantity':p['qn']})
				carts.append({'products':p_data})
				data1 = {'address':address.address,'landmark':address.landmark,'location_show':address.location_show,'location_id':address.location.id,'user':address.user.id}
				data2 = {'email':order.user.email,'username':order.user.username}
				data.append({'address':data1,'user':data2,'carts':carts,'change_requested':order.change_requested,'final_amount':order.final_amount,
							 'id':order.id,'status':0,'total_amount':order.total_amount,'order_status':delivery_time})
			except:
				pass
	data = simplejson.dumps({'objects':data})
	return HttpResponse(data, content_type='application/json')


# @csrf_exempt
# def process_order(request):


@csrf_exempt
def get_store_product(request):
	data={}
	data['products']=[]
	location_id = request.GET.get('location_id')
	category_id = request.GET.get('category_id')
	shops = map(lambda x:x.id ,Store.objects.filter(locations=location_id))
	for s in shops:
		try:
			data['products'] += es_utils.full_productsearch(shopid=s,catkey=category_id)['products'][:15]
		except:
			pass

	data = simplejson.dumps(data)
	return HttpResponse(data, content_type='application/json')

@csrf_exempt
def get_search_product(request):
	data={}
	data['products']=[]
	location_id = request.GET.get('location_id')
	keyword = request.GET.get('keyword')
	shops = map(lambda x:x.id ,Store.objects.filter(locations=location_id))
	for s in shops:
		try:
			data['products'] += es_utils.full_productsearch(keywordstr=keyword,shopid=s)['products'][:15]
		except:
			pass

	data = simplejson.dumps(data)
	return HttpResponse(data, content_type='application/json')
