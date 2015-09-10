import datetime
from gcm import GCM
from app.models import *
from django.core.management.base import BaseCommand
from app.utils import constant

def send_notifications():
    time_lt = datetime.datetime.now()-datetime.timedelta(hours=0.3)
    time_gt = datetime.datetime.now()
    orders = Order.objects.filter(delivery_time__gte=time_lt,delivery_time__lt=time_gt).exclude(status__in=[7,8,1])
    msg = "Delivery Notification sent to following order Ids\n"
    ids=""
    for order in orders:
        order_activity =  OrderActivity.objects.filter(order=order,actions__in=[12,10])
        if not order_activity:
            response = send_single_notification(order)
            ids+=str(order.id)+'\n'
    if ids != "":
        send_mail('Delivered Notification sent Auto', msg+ids, 'query@movincart.com', ['anurag@movincart.com'], fail_silently=False)
    dispacth_time_lt = datetime.datetime.now()-datetime.timedelta(hours=2.3)
    dispacth_time_gt = datetime.datetime.now()-datetime.timedelta(hours=2)
    orders = Order.objects.filter(delivery_time__gte=dispacth_time_gt,delivery_time__lt=dispacth_time_lt,status=2)
    for order in orders:
        order.status=0
        order.save()

def send_single_notification(order):
    customer = order.user.userprofile
    app_id=[customer.app_id]
    gcm=GCM(constant.API_KEY)
    data = {'title':'MovinCart','Notification': "Has your order been delivered",'popup':"1",'page':"2",'NeedRefresh':"1",'order_id':str(order.id)}
    response = gcm.json_request(registration_ids=app_id, data=data)
    notification_sent=simplejson.dumps(data)
    OrderActivity(order=order,user=order.user,actions=12,comment=notification_sent).save()
    return response
