from app.models import *
from django.shortcuts import render
from app.views import *
def available_services(request):
	locations = []
	for line in open('/home/dinkar/movincart_new/app/views/test_api/services_location.txt','r').readlines():
		try:
			line=line.split(",")
			location_id=line[0]
			name=line[1]
			lat=line[2]
			lng=line[3].strip()
			location = {
				"location_id":location_id,
				"name":name,
				"lat":lat,
				"lng":lng,
				}
			locations.append(location)

		except:
			pass


	context={
		'location':locations
	}
	return render(request, "new_custom_admin/v1/available_services.html", context)

def product_per_cat(request):               # Category API testing
	product_category = Category.objects.filter(parent=None)
	location = Location.objects.all()
	context = {
		"category":product_category,
		"location":location,
	}
	return render(request, "new_custom_admin/v1/product_per_cat.html",context)

def sub_category(request):             #subcategory API testing
	sub_category = Category.objects.all()
	subcategory = sub_category.exclude(parent = None).distinct()
	locations = Location.objects.all()
	context = {
		"subcategory":subcategory,
		"location":locations,
	}
	return render(request, "new_custom_admin/v1/sub_category.html",context)

def order_status(request):
	userprofile = UserProfile.objects.all()
	context = {
		"userprofile":userprofile,
	}
	return render(request, "new_custom_admin/v1/order_status.html",context)

def past_order(request):
	userprofile = UserProfile.objects.all()
	context = {
		"userprofile":userprofile,
	}
	return render(request, "new_custom_admin/v1/past_order.html",context)

def search_product(request):
	locations = Location.objects.all()
	product_name = Product.objects.all()
	context = {
		"location":locations,
		"p_name":product_name,
	}
	return render(request, "new_custom_admin/v1/search_product.html",context)