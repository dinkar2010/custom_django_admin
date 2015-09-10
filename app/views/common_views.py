import hmac
import sha
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
import simplejson
import time
import random
import datetime
from app.utils import constant
import hashlib
from django.views.decorators.csrf import csrf_exempt
from base64 import b64encode
from datetime import datetime
from django.utils.safestring import mark_safe
def appversioncode(request):
	return render(request,'appversioncode.html')

def android_app_redirection(request):
	return HttpResponseRedirect('https://play.google.com/store/apps/details?id=com.movincart')

def web_site_page(request):
	return render(request,'web_site.html')


@csrf_exempt
def bill(request):
    value=request.GET.get('amount')

    txn_id=str(int(time.mktime(datetime.now().timetuple())))+str(random.randint(100001,999999))
    data_string = "merchantAccessKey=" +constant.access_key + "&transactionId=" +txn_id + "&amount=" + value;
    sign=create_signature(data_string,constant.secret_key)
    amount = {'value':value, 'currency': 'INR'}
    data={
    'merchantTxnId': txn_id,
    'amount':amount,
    'requestSignature': sign,
    'merchantAccessKey': constant.access_key,
    'returnUrl': "http://anurag92.webfactional.com/api/v1/validate_txn/"
    }
    return HttpResponseRedirect('/citrus/bill.php?amount='+str(value))

@csrf_exempt
def validate_txn(request):
    k1 = request.POST.get("TxId",'')
    k2 = request.POST.get("TxStatus",'')
    k3 = request.POST.get("amount",'')
    k4 = request.POST.get("pgTxnNo",'')
    k5 = request.POST.get("issuerRefNo",'')
    k6 = request.POST.get("authIdCode",'')
    k7 = request.POST.get("firstName",'')
    k8 = request.POST.get("lastName",'')
    k9 = request.POST.get("pgRespCode",'')
    k10 = request.POST.get("addressZip",'')
    verification_data = k1 + k2 + k3 + k4 + k5 + k6 + k7 + k8 + k9 + k10;
    m = create_signature(verification_data,constant.secret_key)
    return HttpResponseRedirect('/citrus/validate.php')

def create_signature(s2, s1):
    """ Create the signed message from api_key and string_to_sign """
    # string_to_sign = s2.encode('utf-8')
    hm = hmac.new(s1,s2,sha)
    return hm.hexdigest()
