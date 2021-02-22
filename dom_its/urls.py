"""dom_its URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import  include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.monitor.urls')),
    path('api/', include('apps.api.urls')),
    path('dia/', include('apps.dia.urls')),
    path('reporting/', include('apps.reporting.urls')),
    path('manage/', include('apps.manage.urls')),
    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    
    
]
