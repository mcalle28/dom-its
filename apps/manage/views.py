from django.shortcuts import render, redirect
from ..monitor.models import Group, VManager, User, VmColor

def index(request):
    gps = Group.objects.all()
    vms = VManager.objects.all()
    users = User.objects.all()
    colors = VmColor.objects.all()
    return render(request, 'manage.html', context={'gps':gps,'users':users,'vms':vms, 'colors':colors})


#_____CRUD GP_______
def cGroup(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        Group(name=name).save()
    return redirect(index)


def rGroup(request,id):

    gp = Group.objects.get(id=id)

    if request.method == 'POST':
        users = request.POST.getlist('gpUsers')
        vms = request.POST.getlist('gpVms')
        name = request.POST.get('gpName')

        gp.users.through.objects.filter(group_id=id).delete()
        for user in users:
            userObj = User.objects.get(id=user)
            gp.users.add(userObj)

        gp.vManagers.through.objects.filter(group_id=id).delete()
        for vm in vms:
            vmObj = VManager.objects.get(id=vm)
            gp.vManagers.add(vmObj)                     

        gp.name = name
        gp.save()
           


    aUsers = User.objects.all()
    aVms = VManager.objects.all()

    
    context = {'gp':gp, 'vms':aVms, 'users':aUsers}
    return render(request,'group.html', context=context)

def dGroup(request):

    if request.method == 'POST':
        gid = int(request.POST.get('id'))
        Group.objects.get(id=gid).delete()

    return redirect(index)


#_____CRUD VM_______
def cVmanager(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        ip = request.POST.get('ip')
        color = request.POST.get('color')
        user = request.POST.get('user')
        password = request.POST.get('password')
        dia = request.POST.get('dia')
        noDia = request.POST.get('noDia')

        VManager(
            name = name,
            ip = ip,
            color = VmColor.objects.get(id=color),
            user = user,
            password= password,
            diaUri = dia,
            noDiaUri = noDia
        ).save()
        
    return redirect(index)


def rVmanager(request, id):

    vm = VManager.objects.get(id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        ip = request.POST.get('ip')
        color = request.POST.get('color')
        user = request.POST.get('user')
        password = request.POST.get('password')
        dia = request.POST.get('dia')
        noDia = request.POST.get('noDia')

                
        vm.name = name
        vm.ip = ip
        vm.color = VmColor.objects.get(id=color)
        vm.user = user
        vm.password= password
        vm.diaUri = dia
        vm.noDiaUri = noDia
        vm.save()


    colors = VmColor.objects.all()
    context = {'vm':vm, 'colors':colors}
    return render(request,'vmanager.html', context=context)

def dVmanager(request):
    if request.method == 'POST':
        vid = int(request.POST.get('id'))
        VManager.objects.get(id=vid).delete()
    return redirect(index)


#_____CRUD USER_______
def cUser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        admin = request.POST.get('admin',False)

        User(userName = email, password=password, isAdmin=(admin=='on')).save()


    return redirect(index)


def rUser(request, id):

    user = User.objects.get(id=id)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        admin = request.POST.get('admin') == 'on'
                            
        user.userName = email
        user.password = password
        user.isAdmin = admin
        user.save()

    
    context = {'user':user}
    return render(request,'user.html',context= context)

def dUser(request):
    
    if request.method == 'POST':
        uid = int(request.POST.get('id'))
        User.objects.get(id=uid).delete()

    return redirect(index)


