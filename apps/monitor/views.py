from django.shortcuts import render, redirect
from .models import User, VManager, Dashboard, Component, Widget, Group
from django.http import HttpResponse
import json
from django.core import serializers

# Create your views here.

def empty(request):
    return redirect('login')


def login(request):
    
    if request.method == 'POST':
        if User.objects.filter(userName=request.POST.get('user'), password=request.POST.get('password')).exists():
            userObj = User.objects.get( userName=request.POST.get('user'), password=request.POST.get('password'))

            request.session['user'] = userObj.id

            userVms= list(VManager.objects.filter(vmGp__in=Group.objects.filter(users=userObj)))

           

            request.session['vms'] = json.loads(serializers.serialize("json", userVms))

            print(type(request.session['vms']),len(request.session['vms']))
           

            return redirect('/dashboard')
        else:            
            return render(request, 'login.html')
    return render(request, 'login.html')


def index(request):

    if request.method == 'POST':        
        dbName = request.POST.get('dbName','-1')
        Dashboard(user=User.objects.get(id = request.session['user']), name=dbName).save()

    
    userDashboards = Dashboard.objects.filter(user = request.session['user']).first()
    
    if userDashboards is None:
        obj = Dashboard(user=User.objects.get(id = request.session['user']), name='initial')
        obj.save()
        return redirect('/dashboard/'+str(obj.id))

    return redirect('/dashboard/'+str(userDashboards.id))

def dashboard(request, id):

    if request.method == 'POST':
        vm = request.POST.get('vm','-1')
        widget = request.POST.get('widget')
        title = request.POST.get('title',' ')
        dbName = request.POST.get('dbName','-1')
        
        if vm == '-1' and dbName != '-1':
            
            Dashboard(user=User.objects.get(id=request.session['user']), name=dbName).save()
        else:       
            c = Component(x=0,y=0,w=0,h=0,vManager_id=vm,title=title,widget_id=widget,dashboard_id=id)
            c.save()

    vms = VManager.objects.all()
    userDashboards = Dashboard.objects.filter(user = request.session['user'])
    dashboard = Dashboard.objects.get(id=id)

    return render(request, 'index.html', context={'vms':vms,'dashboards':userDashboards, 'dashboard':dashboard, 'name':request.get_full_path()})

def remove(request, id):
    wid = request.GET.get('wid','-1')
    if wid != '-1':
        Component.objects.get(id=wid).delete()
    return HttpResponse(status=200)

def move(request, id):    
    data = json.loads(request.POST.get('data'))

    for movement in data:
        c = Component.objects.get(id=movement['id'])
        c.x = movement['x']
        c.y = movement['y']
        c.w = movement['w']
        c.h = movement['h']
        c.save()

    return HttpResponse(status=200)