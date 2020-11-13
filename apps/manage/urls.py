from django.urls import path
from . import views
#erda

urlpatterns = [
    path('', views.index),


    path('group/<id>', views.rGroup),
    path('dGroup', views.dGroup),
    path('cGroup', views.cGroup),

    path('vManager/<id>', views.rVmanager),
    path('dVmanager', views.dVmanager),
    path('cVmanager', views.cVmanager),

    path('user/<id>', views.rUser),
    path('dUser', views.dUser),
    path('cUser', views.cUser),


]