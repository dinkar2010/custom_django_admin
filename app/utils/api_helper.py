from functools32 import lru_cache
from app.models import *
@lru_cache(maxsize=64)
def get_cat_structure_for_service(s,l):
    shops = map(lambda x: x.store,StoreTimingInLocation.objects.filter(lsm__location=l,lsm__service=s,lsm__service__is_active=True,is_active=True,store__is_active=True))
    cat_list=[]
    cats = Category.objects.filter(service=s,is_active=True,parent=None)
    for cat in cats:
        cat_data={}
        cat_data['display_order']=cat.display_order
        cat_data['id']=cat.id
        cat_data['name']=cat.name
        cat_data['children']=[]
        children = Category.objects.filter(parent=cat,is_active=True)
        for sub_cat in children:
            if StoreProductMapping.objects.filter(stock=True,product__product__category__service=s,product__product__category=sub_cat,store__in=shops):
                sub_cat_data={}
                sub_cat_data['display_order']=sub_cat.display_order
                sub_cat_data['id']=sub_cat.id
                sub_cat_data['name']=sub_cat.name

                cat_data['children'].append(sub_cat_data)

        if len(cat_data['children'])>0:
            cat_list.append(cat_data)
    return cat_list

@lru_cache(maxsize=64)
def get_cat_structure_for_service_v2(s,l):
    shops = map(lambda x: x.store,StoreTimingInLocation.objects.filter(lsm__location=l,lsm__service=s,lsm__service__is_active=True,is_active=True,store__is_active=True))
    cat_list=[]
    cats = Category.objects.filter(service=s,is_active=True,parent=None).order_by('display_order')
    for cat in cats:
        cat_data={}
        cat_data['id']=cat.id
        cat_data['name']=cat.name
        cat_data['children']=[]
        children = Category.objects.filter(parent=cat,is_active=True).order_by('display_order')
        for sub_cat in children:
            if StoreProductMapping.objects.filter(stock=True,product__product__category__service=s,product__product__category=sub_cat,store__in=shops):
                sub_cat_data={}
                sub_cat_data['id']=sub_cat.id
                sub_cat_data['name']=sub_cat.name

                cat_data['children'].append(sub_cat_data)

        if cat_data['children']:
            cat_list.append(cat_data)
    return cat_list

@lru_cache(maxsize=64)
def get_cat_structure_for_service_super_saver(l):
    shops = map(lambda x: x.store,StoreTimingInLocation.objects.filter(lsm__location=l,lsm__service__is_active=True,is_active=True,store__is_active=True))
    cat_list=[]
    cats = Category.objects.filter(is_active=True,parent=None).order_by('display_order')
    for cat in cats:
        cat_data={}
        cat_data['id']=cat.id
        cat_data['name']=cat.name
        cat_data['children']=[]
        children = Category.objects.filter(parent=cat,is_active=True).order_by('display_order')
        for sub_cat in children:
            if StoreProductMapping.objects.filter(discount__gt=0,stock=True,product__product__category=sub_cat,store__in=shops):
                sub_cat_data={}
                sub_cat_data['id']=sub_cat.id
                sub_cat_data['name']=sub_cat.name

                cat_data['children'].append(sub_cat_data)

        if cat_data['children']:
            cat_list.append(cat_data)
    return cat_list
