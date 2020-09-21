from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.config),
    path('config/<id>', views.configId),
    path('webhook/<webhookId>', views.webhook),
    path('config/p/DIAtoNoDIA', views.DIAtoNoDIA),
    path('config/p/NoDIAtoDIA', views.NoDIAtoDIA),

]