from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .diaScheduler import DiaScheduler
from ..monitor.models import Webhook as webhookDb
from ..monitor.models import WebhookLog, VManager, ExcludeSite
from ..api.sdwanUtils import sdwan as sdwan
import json
import time
import datetime
from django.conf import settings as djangoSettings
from ..api.views import sdwan as sdwansObjs


def initSchedulers():
    schedulers = {}
    for v in webhookDb.objects.all():        
        
        excluded = ExcludeSite.objects.filter(webhook=v.webhookId).values('siteId')

        excluded = [a['siteId'] for a in excluded]

        schedulers[str(v.webhookId).replace('-','')] = DiaScheduler('biz-internet', 30, sdwansObjs.sdwans[str(v.vManager.id)], str(v.vManager.id), excluded=excluded)
    
    return schedulers

schedulers = initSchedulers()


def config(request):

    if request.method == 'POST':
        vm = request.POST.get('vm')
        webhookDb(vManager = VManager.objects.get(id=vm)).save()

    wh = webhookDb.objects.all()    
    vms = VManager.objects.filter(webhook=None)
    
    return render(request, 'diaConfig.html', context={'webhooks':wh,'vms':vms})

@csrf_exempt
def webhook(request, webhookId):
    
    print('llegó un webhook', webhookId)

    data = json.loads(request.body.decode('utf-8'))

    schedulers[webhookId].processRequest(data)
    return HttpResponse('200')


def configId(request,id):

    wh = webhookDb.objects.get(webhookId=id)
    es = ExcludeSite.objects.filter(webhook=wh)
    
    return render(request, 'diaConfigDetail.html', context={'wh':wh,'excluded':es})

def DIAtoNoDIA(request):
    vm = request.POST.get('wh','-1').replace('-','')
    siteId = request.POST.get('siteId','-1') 

    data ={
    "values": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "DOM generated",
        "site-id": siteId
        }
    ],
    "values_short_display": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "..."
        }
    ],
    "message": "A tloc went down",
    
    }   

    schedulers[vm].processRequest(data)
    return  redirect('configDiaDetail', id=vm)


def NoDIAtoDIA(request):
    vm = request.POST.get('wh','-1').replace('-','')
    siteId = request.POST.get('siteId','-1')  

    data ={
    "values": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "DOM generated",
        "site-id": siteId
        }
    ],
    "values_short_display": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "..."
        }
    ],
    "message": "A tloc came up",
    }    

    schedulers[vm].processRequest(data)
    return  redirect('configDiaDetail', id=vm)

def stream(request,id):
    def event_stream():

        while True:
            res = 'data:'+ schedulers[id.replace('-','')].getLastMessage()+ '\n\n'
            time.sleep(3)
            yield (res)
            
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def downloadLog(request,id):

    filename = webhookDb.objects.get(webhookId=id).vManager.ip.split('.')[0]

    file_location = djangoSettings.STATICFILES_DIRS[0]+'/diaLogs/'+filename+'.log'
    with open(file_location, 'r') as f:
        file_data = f.read()
        # sending response 
        response = HttpResponse(file_data, content_type='text/log')
        response['Content-Disposition'] = 'attachment; filename="register.log"'

    return response


def excludeSites(request,id):
    if request.method == 'POST':
        oper = request.POST.get('oper','-1')
        siteId = request.POST.get('siteId','-1')

        wh = webhookDb.objects.get(webhookId=id)

        if oper == 'add':
           obj, created = ExcludeSite.objects.get_or_create(webhook=wh,siteId=siteId)
           obj.save()

        elif oper == 'delete':
            obj, created = ExcludeSite.objects.get_or_create(webhook=wh,siteId=siteId)
            obj.delete()
        else:
            print('NO NO NO NO '*50)

        return redirect('configDiaDetail', id=id)

