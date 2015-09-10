__author__ = 'dinkar'
from app.models import *
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

def available_services(request):
    test_locations = []
    for line in open('/home/dinkar/movincart_new/app/views/test_api/services_location.txt','r').readlines():
        try:
            line=line.split(",")
            location_id=line[0]
            name=line[1]
            lat=line[2]
            lng=line[3]
            print(location_id+' '+name+" "+lat+' '+lng)
            location = {
                "location_id":location_id,
                "name":name,
                "lat":lat,
                "lng":lng,
                }
            test_locations.append(location)
        except:
	    	pass
    context={
		'location':test_locations,
	}
    return render(request, "new_custom_admin/v2/available_services.html", context)


def product_per_cat(request):                      # Category API testing
    product_category = Category.objects.filter(parent = None)
    locations = Location.objects.all()
    context = {
        "category":product_category,
        "locations":locations,
    }
    return render(request, "new_custom_admin/v2/product_per_cat.html",context)


def sub_category(request):                     #subcategory API testing
    sub_category = Category.objects.all()
    subcategory = sub_category.exclude(parent = None).distinct()
    locations = Location.objects.all()
    context = {
        "subcategory":subcategory,
        "locations":locations,
    }
    return render(request, "new_custom_admin/v2/sub_category.html",context)

def order_status(request):
    userprofile = UserProfile.objects.all()
    context = {
        "userprofile":userprofile,
    }
    return render(request, "new_custom_admin/v2/order_status.html",context)

def past_order(request):
    userprofile = UserProfile.objects.all()
    context = {
        "userprofile":userprofile,}
    return render(request, "new_custom_admin/v2/past_order.html",context)

def search_product(request):
    locations = Location.objects.all()
    product_name = Product.objects.all()
    context = {
        "locations":locations,
        "p_name":product_name,
    }
    return render(request, "new_custom_admin/v2/search_product.html",context)

def place_order(request):
    return render(request, "new_custom_admin/v2/place_order.html")
