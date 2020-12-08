from django.http import JsonResponse, HttpResponse
from .sdwanUtils import sdwan as sd
from django.views.decorators.csrf import csrf_exempt
from .migration import migration
from .base import baseTipo1, titulosTipo1, titulosTipo2, baseTipo2
from .Sdwan import Sdwan
from ..monitor.models import VManager, Webhook, WebhookLog

sdwan = Sdwan()



@csrf_exempt
def register(request):
    
    if request.method == 'POST':

        ip = request.POST.get('ip','')
        user = request.POST.get('user','')
        password = request.POST.get('password','')
        name = request.POST.get('name','')

        sdwans[name] = sd(ip,user,password)

@csrf_exempt
def csv(request):
    
    if request.method == 'POST':     

        data = {}
        auto = request.POST.getlist('auto')
        data['modeloSerial'] = request.POST.get('modeloSerial','nada')
        data['BWInternet'] = request.POST.get('BWInternet','nada')
        data['BWMpls'] = request.POST.get('BWMpls','nada')
        data['snmpName'] = request.POST.get('hostName','nada')
        data['autoIfInternet'] = 'TRUE' if 'internet' in auto else 'FALSE'
        data['autoIfMpls'] = 'TRUE' if 'mpls' in auto else 'FALSE'
        data['deviceIP'] = request.POST.get('deviceIP','nada')
        data['hostName'] = request.POST.get('hostName','nada')
        data['interfazInternet'] = request.POST.get('interfazInternet','nada')
        data['interfazMpls'] = request.POST.get('interfazMpls','nada')
        data['latitude'] = request.POST.get('latitude','nada').replace(',','.')
        data['longitude'] = request.POST.get('longitude','nada').replace(',','.')
        data['siteId'] = request.POST.get('siteId','nada')
        data['snmpLocation'] = request.POST.get('snmpLocation','nada')
        data['tipo'] = request.POST.get('tipo','1')

        
        
        print(data)
        

        file = request.FILES['txt'].read().decode('utf-8')
        txt = str(file).replace('\r','')
                        

        m = migration(txt, **data)
        v = m.toCSV()

       
        if data['tipo'] == '1':
            res = titulosTipo1+'\n'+baseTipo1.format(*v)
        else:
            print('LA 2',len(v))
            res = titulosTipo2+'\n'+baseTipo2.format(*v)
        

        response = HttpResponse(res, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ejemplo.csv"'

        return response   


def index(request):    
    return JsonResponse('', safe=False)

def wanEdgeHealth(request, id):
    return JsonResponse (sdwan.wanEdgeHealth(id),safe=False)

def wanEdgeHealthDetail(request, id):
    personality = request.GET.get('personality','')
    return JsonResponse (sdwan.wanEdgeHealthDetail(id, personality),safe=False)


def controlStatus(request, id):
    return JsonResponse (sdwan.controlStatus(id),safe=False)

def controlStatusDetail(request, id):
    detail = request.GET.get('state')
    return JsonResponse (sdwan.controlStatusDetail(id, detail),safe=False)


def generalState(request, id):
    return JsonResponse (sdwan.generalState(id),safe=False)        
        
def reachable(request, id):
    personality = request.GET.get('personality','')
    return JsonResponse (sdwan.reachable(id,personality), safe=False)

def unReachable(request, id):
    personality = request.GET.get('personality','')
    return JsonResponse (sdwan.unReachable(id,personality), safe=False)

def network(request,personality):
    vm = request.GET.get('vm','')
    return JsonResponse(sdwans[vm].network(personality), safe=False)

def tunnels(request, ip, id):
    return JsonResponse (sdwan.tunnels(id, ip),safe=False)

def health(request, personality):
    vm = request.GET.get('vm','')
    return JsonResponse(sdwans[vm].health(personality), safe=False)

def certificate(request, id):
    return JsonResponse(sdwan.certificate(id),safe=False)

def certs(request, id):
    return JsonResponse(sdwan.certs(id),safe=False)

def reboot(request, id):
    return JsonResponse(sdwan.reboot(id),safe=False)

def boot(request, id):
    return JsonResponse(sdwan.boot(id),safe=False)

def alerts(request, id):
    start = request.GET.get('start','na')
    end = request.GET.get('end','na')    
    return JsonResponse(sdwan.alerts(id, start, end), safe=False)

def alertsEx(request, id): 
    return JsonResponse(sdwan.alertsEx(id), safe=False)


def get(request):
    return JsonResponse(list(sdwans.keys()), safe=False)

def webhook(request, id):
    vm = VManager.objects.get(id=id)
    wh = [] 
    for w in WebhookLog.objects.filter(vManager=vm, inDia=False):
        wh.append('['+str(w.time.strftime("%Y-%m-%d %H:%M:%S"))+'] '+'SiteId: '+w.siteId)
    
    return JsonResponse(list(wh), safe=False)