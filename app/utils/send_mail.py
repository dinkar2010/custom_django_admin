from django.core.mail import send_mail
from app.utils.constant import *
from django.conf import settings
import datetime as dt


def notify_admin(order, service_names):
	msg = ""
	msg+="\nName: "+str(order.user.first_name).title()
	msg+="\nMobile: "+str(order.user.userprofile.contact)
	msg+="\nEmail: "+str(order.user.email)
	msg+="\nOrder ID: "+str(order.id)
	if order.delivery_time:
		msg += "\nDelivery Time : " + order.delivery_time.strftime('%B %d, %Y, %I:%M %p')
	else:
		delivery_time = order.created_at + dt.timedelta(hours=1)
		msg += "\nDelivery Time : " + delivery_time.strftime('%B %d, %Y, %I:%M %p')

	msg+="\nDelivery Address: "+ str(order.address.address)+", "+ str(order.address.landmark)+", "+ str(order.address.location_show)+", Location: "+ str(order.address.location.sub_area)
	if service_names:
		msg+="\nservices not delivered : "+service_names
	print msg
	# send_mail('Order Not Delivered', msg, 'query@movincart.com', ['shubhamdrolia87@gmail.com'], fail_silently=False)
	date = dt.datetime.now().date()
	send_mail('Order Not Delivered '+str(date), msg, 'query@movincart.com', settings.LIST_FOR_MAILS, fail_silently=False)
	# send_mail('New Order Placed',msg, 'query@movincart.com', ['anuragmeena92@gmail.com'], fail_silently=False,html_message=msg)
	print "mail sent"


