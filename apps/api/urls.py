from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('wanEdgeHealth/<id>',views.wanEdgeHealth),
    path('controlStatus/<id>',views.controlStatus),
    path('controlStatusDetail/<id>',views.controlStatusDetail),
    path('generalState/<id>',views.generalState),
    path('tunnels/<id>/<ip>', views.tunnels),
    path('reachable/<id>',views.reachable),
    path('unReachable/<id>',views.unReachable),
    path('wanEdgeHealthDetail/<id>',views.wanEdgeHealthDetail),
    path('certificate/<id>', views.certificate),
    path('reboot/<id>', views.reboot),
    path('certs/<id>', views.certs),
    path('boot/<id>', views.boot),
    path('alerts/<id>', views.alerts),
    path('alertsEx/<id>', views.alertsEx),

    path('network/<personality>', views.network),
    path('health/<personality>', views.health),
    
    path('get', views.get),
    path('register', views.register),
    path('operate/csv/', views.csv),

    path('webhook/<id>/', views.webhook),
]