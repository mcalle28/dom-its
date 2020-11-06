from django.shortcuts import render
from ..monitor.models import Group, VManager, User

def index(request):
    gps = Group.objects.all()
    vms = VManager.objects.all()
    users = User.objects.all()

    return render(request, 'manage.html', context={'gps':gps,'users':users,'vms':vms})