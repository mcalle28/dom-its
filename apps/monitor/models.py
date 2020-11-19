from django.db import models
import uuid


class User(models.Model):
    userName = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    isAdmin = models.BooleanField(default=False)
    def __str__(self):
        return self.userName

class Dashboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    widgets = models.ManyToManyField('Widget', through='Component')
    def __str__(self):
        return self.name

class Component(models.Model):
    widget = models.ForeignKey('Widget', on_delete=models.CASCADE)
    dashboard = models.ForeignKey('Dashboard', on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.IntegerField()
    h = models.IntegerField()
    vManager = models.ForeignKey("VManager", on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)

class Widget(models.Model):
    name = models.CharField(max_length=64)
    html = models.TextField()
    minH = models.IntegerField()
    minW = models.IntegerField()
    def __str__(self):
        return self.name
    
class VmColor(models.Model):
    color = models.CharField(max_length=64)
    def __str__(self):
        return self.color


class VManager(models.Model):
    name = models.CharField(max_length=64)
    color = models.ForeignKey('VmColor', on_delete=models.CASCADE)
    ip = models.CharField(max_length=64)
    user = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    diaUri = models.CharField(max_length=200, blank=True, null=True)
    noDiaUri = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name


class Webhook(models.Model):
    
    webhookId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vManager = models.ForeignKey("VManager", on_delete=models.CASCADE)

class WebhookLog(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    siteId = models.CharField(max_length=200)
    inDia = models.BooleanField(default=True)
    vManager = models.ForeignKey('VManager', on_delete=models.CASCADE)
    hostName = models.CharField(max_length=64, blank=True, null=True)


    

class Group(models.Model):
    name = models.CharField(max_length=200)
    users = models.ManyToManyField('User', related_name='userGp')
    vManagers = models.ManyToManyField('VManager', related_name='vmGp')

    def __str__(self):
        return self.name

class ExcludeSite(models.Model):
    webhook = models.ForeignKey('Webhook', on_delete=models.CASCADE)
    siteId = models.CharField(max_length=200)