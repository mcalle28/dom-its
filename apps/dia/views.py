from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .diaScheduler import DiaScheduler
from ..monitor.models import VManager as dbVm
from ..monitor.models import Webhook
from ..api.sdwanUtils import sdwan as VManager
import json


def initSchedulers():
    schedulers = {}
    for v in dbVm.objects.all():
        schedulers[str(v.webhookId).replace('-','')] = DiaScheduler('biz-internet', 30, VManager(v.ip,v.user,v.password) )
    
    return schedulers

schedulers = initSchedulers()


def config(request):    
    return render(request, 'diaConfig.html')

@csrf_exempt
def webhook(request, webhookId):
    
    print('llegó un webhook', webhookId)

    data = json.loads(request.body.decode('utf-8'))

    schedulers[webhookId].processRequest(data)
    return HttpResponse('200')


def configId(request,id):

    vm = dbVm.objects.get(id=id)
    wh = Webhook.objects.filter(vManager=vm)
    return render(request, 'diaConfigDetail.html', context={'vm':vm,'wh':wh})

def DIAtoNoDIA(request):
    vm = request.POST.get('vm','-1').replace('-','')
    siteId = request.POST.get('siteId','-1') 

    data ={
    "values": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "...",
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
    return HttpResponse('200')


def NoDIAtoDIA(request):
    vm = request.POST.get('vm','-1').replace('-','')
    siteId = request.POST.get('siteId','-1')  

    data ={
    "values": [
        {
        "color": "biz-internet",
        "system-ip": "0.0.0.0",
        "host-name": "...",
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
    return HttpResponse('200')