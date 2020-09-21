from django.shortcuts import render, redirect
from .models import User, VManager, Dashboard, Component, Widget
from django.http import HttpResponse
import json

# Create your views here.

def login(request):
    
    if request.method == 'POST':
        if User.objects.filter(userName=request.POST.get('user'), password=request.POST.get('password')).exists():
            request.session['user'] = User.objects.get( userName=request.POST.get('user'), password=request.POST.get('password')).id
            return redirect('/dashboard')
        else:            
            return render(request, 'login.html')
    return render(request, 'login.html')


def index(request):
    vms = VManager.objects.all()
    userDashboards = Dashboard.objects.filter(user = request.session['user'])
    return render(request, 'index.html', context={'dashboards':userDashboards, 'vms':vms})

def dashboard(request, id):

    if request.method == 'POST':
        vm = request.POST.get('vm')
        widget = request.POST.get('widget')
       
        c = Component(x=0,y=0,w=0,h=0,vManager_id=vm,widget_id=widget,dashboard_id=id)
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