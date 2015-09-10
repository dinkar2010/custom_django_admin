import datetime as dt
import simplejson
from app.models import Order, Category, StoreProductMapping


def get_short_order_summary():

    total_orders =0
    total_amount= 0

    total_per_day = 0
    count_per_day = 0

    for order in Order.objects.filter(created_at__gte=dt.datetime.now().date()).exclude(status=1):
        try:
            invoice= order.invoice
            count_per_day+=1
            order_products = simplejson.loads(invoice.product_json)
            for p in order_products:
                total_per_day+=int(p['qn'])*float(p['price'])
        except:
            pass

    total_amount+=total_per_day
    total_orders+=count_per_day
    context={
        'total_orders':int(total_orders),
        'total_amount':int(total_amount),
    }
    return context


def get_order_sales_analytics(start_date=dt.datetime.today()-dt.timedelta(days=30),end_date=dt.datetime.today()):
    context = {}
    delta = end_date-start_date
    context['ticks']=[]
    context['order_data']=[]
    context['sales_data']=[]
    context['canceled_orders']=[]
    context['cnf_by_user']=[]


    if delta.days<=31 and delta.days>0:
        diff = 1
        all_orders = Order.objects.filter(created_at__gte=start_date-dt.timedelta(days=diff),created_at__lte=end_date)
        index=1
        for d in xrange(1,delta.days+1,diff):
            filtered_orders = all_orders.filter(created_at__gt = start_date+dt.timedelta(days=d-diff),created_at__lte= start_date+dt.timedelta(days=d))
            sales=filtered_orders.exclude(status=1).count()
            orders=filtered_orders.count()
            canceled = filtered_orders.filter(status=1).count()
            cnf_by_user= filtered_orders.filter(status=8).count()

            date = start_date+dt.timedelta(days=d)
            context['ticks'].append([index,date.strftime("%b, %d")])
            context['sales_data'].append([index,sales])
            context['order_data'].append([index,orders])
            context['canceled_orders'].append([index,canceled])
            context['cnf_by_user'].append([index,cnf_by_user])
            index+=1
    # elif delta.days<=0:

    # print context['ticks']

    return context


def get_repeat_user_data(start_date=dt.datetime.today()-dt.timedelta(days=30),end_date=dt.datetime.today()):
    context={}
    delta = end_date-start_date
    context['new_user']=0
    context['repeated_user']=0
    all_orders = Order.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
    for order in all_orders:
        user = order.user
        if Order.objects.filter(user=user,created_at__lt=order.created_at):
            context['repeated_user']+=1
        else:
            context['new_user']+=1

    return context



def get_balance_data(start_date=dt.datetime.today()-dt.timedelta(days=30),end_date=dt.datetime.today()):
    context={}
    delta = end_date-start_date
    context['total_balance']=[]
    context['delivered_balance']=[]
    context['ticks']=[]
    if delta.days<=31 and delta.days>0:
        diff = 1
        all_orders = Order.objects.filter(created_at__gte=start_date-dt.timedelta(days=diff),created_at__lte=end_date)
        index=1
        for d in xrange(1,delta.days+1,diff):
            filtered_orders = all_orders.filter(created_at__gt = start_date+dt.timedelta(days=d-diff),created_at__lte= start_date+dt.timedelta(days=d))
            total_balance=0
            delivered_balance=0
            for order in filtered_orders:
                invoice= order.invoice
                order_products = simplejson.loads(invoice.product_json)
                for p in order_products:
                    price=p['price']
                    total_balance+=int(p['qn'])*float(price)
                    if order.status in [0,8]:
                        delivered_balance+=int(p['qn'])*float(price)
            date = start_date+dt.timedelta(days=d)
            context['ticks'].append([index,date.strftime("%b, %d")])
            context['total_balance'].append([index,total_balance])
            context['delivered_balance'].append([index,delivered_balance])
            index+=1
    return context


def get_ordered_category_analytics(start_date=dt.datetime.today()-dt.timedelta(days=30),end_date=dt.datetime.today()):
    context={}
    delta = end_date-start_date
    context['ticks']=[]
    context['categories_vs_orders_per_tick']={}
    all_cats=Category.objects.filter(parent=None)
    for cat in all_cats:
        context['categories_vs_orders_per_tick'][cat.name]=[]
    if delta.days<=61 and delta.days>0:
        diff = 1
        all_orders = Order.objects.filter(created_at__gte=start_date-dt.timedelta(days=diff),created_at__lte=end_date)
        index=1
        for d in xrange(1,delta.days+1,diff):
            cat_ordered_data={}
            for cat in all_cats:
                cat_ordered_data[cat.name]=0
            filtered_orders = all_orders.filter(created_at__gt = start_date+dt.timedelta(days=d-diff),created_at__lte= start_date+dt.timedelta(days=d))
            for order in filtered_orders:
                invoice= order.invoice
                order_products = simplejson.loads(invoice.product_json)
                for p in order_products:
                    try:
                        category=StoreProductMapping.objects.get(pk=p['spid']).product.product.category.parent.name
                        cat_ordered_data[category]+=1
                    except:
                        pass
            date = start_date+dt.timedelta(days=d)
            context['ticks'].append([index,date.strftime("%b, %d")])
            for cat in all_cats:
                context['categories_vs_orders_per_tick'][cat.name].append([index,cat_ordered_data[cat.name]])
            index+=1
    dict_to_send={}
    for key in context['categories_vs_orders_per_tick']:
        flag = True
        for v in context['categories_vs_orders_per_tick'][key]:
            if v[1]>0:
                dict_to_send[key]=context['categories_vs_orders_per_tick'][key]
    context['categories_vs_orders_per_tick']=dict_to_send

    return context