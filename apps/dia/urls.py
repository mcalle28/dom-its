from django.urls import path
from . import views
#aaesraaaa
urlpatterns = [
    path('config/stream/<id>', views.stream),
    path('config/', views.config),
    path('config/<id>', views.configId, name="configDiaDetail"),
    path('webhook/<webhookId>', views.webhook),
    path('config/p/DIAtoNoDIA', views.DIAtoNoDIA),
    path('config/p/NoDIAtoDIA', views.NoDIAtoDIA),
    path('config/<id>/download', views.downloadLog),
    path('config/<id>/noMon', views.excludeSites),
]
