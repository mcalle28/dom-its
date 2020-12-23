
from django.urls import path
from . import views

#a

urlpatterns = [
    path('login/', views.login, name='login'),
    path('dashboard/', views.index),
    path('dashboard/<id>', views.dashboard),
    path('dashboard/<id>/remove', views.remove),
    path('dashboard/<id>/move', views.move),
    path('', views.empty),
    path('logout/', views.logout),
    path('deleteDb/', views.deleteDb)
    
]