from django.contrib import admin
from .models import User, WebhookLog, VmColor, Dashboard, Widget, Component, VManager, Group, Webhook
# Register your models here.aa


admin.site.site_header = 'DOM ITS'
admin.site.register(User)
admin.site.register(Dashboard)
admin.site.register(Widget)
admin.site.register(Component)
admin.site.register(VManager)
admin.site.register(VmColor)
admin.site.register(Group)
admin.site.register(WebhookLog)
admin.site.register(Webhook)
