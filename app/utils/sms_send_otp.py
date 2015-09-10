import urllib
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
import requests
import random
from app.models import *
import constant

def send_otp(user):
    try:
        print "sending sms"
        userprofile = user.userprofile
        password=urllib.quote('movincart@1234')
        contact=','.join([str(userprofile.contact),])
        if not userprofile.otp:
            temp = str(random.randint(100001,999999))
            userprofile.otp = temp
            userprofile.save()
        else:
            temp=userprofile.otp
        # url="http://49.50.69.90/api/smsapi.aspx?username=healthcare&password=%s&to=%s&from=HLTHCR&message=%s"%(password,contact,msg)
        url = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to=" + contact + "&msg=Your+One+Time+Password+for+MovinCart+is+: " + temp + "&msg_type=TEXT&userid=" + str(constant.gupshup_user_id) + "&auth_scheme=plain&password=" + constant.gupshup_password + "&v=1.1&format=text"
        # print url
        full_content = requests.get(url)
        LogEntry.objects.log_action(
        user_id         = userprofile.user.pk,
        content_type_id = ContentType.objects.get_for_model(userprofile).pk,
        object_id       = userprofile.pk,
        object_repr     = str(userprofile),
        action_flag     = CHANGE,
        change_message  = "OTP SENT :: response: "+str(full_content.text)+" otp: "+str(temp)
        )
        print full_content.text
    except Exception as e:
        print e
