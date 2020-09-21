
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login, name='login'),
    path('dashboard/', views.index),
    path('dashboard/<id>', views.dashboard),
    path('dashboard/<id>/remove', views.remove),
    path('dashboard/<id>/move', views.move),
    
]