from .sdwanUtils import SiteManager
import threading
import time
from ..monitor.models import Webhook, WebhookLog, VManager
import datetime
from ..api.views import sdwan as sdwansObjs

class DiaWatcher:

    
    def __init__(self, color, cTime, vid, excluded=[]):

        self.queue = []
        self.vid = vid
        self.color = color
        self.cTime = cTime
        self.vManager = sdwansObjs.sdwans[str(self.vid)]
        self.excluded = excluded
        self.manual = []



    def update(self):

        self.vManager = sdwansObjs.sdwans[str(self.vid)]
        utc = datetime.timedelta(hours=5)
        start = datetime.datetime.now() 
        summ = datetime.timedelta(seconds=self.cTime)

        start = start + utc

        end = start - summ
        start = start.strftime("%Y-%m-%dT%H:%M:%S")
        end = end.strftime("%Y-%m-%dT%H:%M:%S")

        print('Alarmas entre: '+end+' y '+start,len(self.manual))

        alerts = self.vManager.alerts(start, end)
        a = alerts
        

        down, up = self.filterAlerts(alerts)

        print(len(down) > 0 or len(up)>0 )
        
       
        self.operate(down, up)
        

    def operate(self, down, up):

        if(len(down) != 0):
        
            dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
            noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())

            downSites = ''
            for value in down:
                downSites += (value['values'][0]['site-id'] + ' ')
                noDia.addSite(value['values'][0]['site-id'])
                dia.removeSite(value['values'][0]['site-id'])
                self.makeLog(value, True)

            
            
            dia.sendToVmanager()
            while dia.isRunning():
                time.sleep(1)
                pass
                
                
            noDia.sendToVmanager()
            while noDia.isRunning():
                time.sleep(1)
                pass

            


        if (len(up) != 0):
            dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
            noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())

            upSites = ''
            for value in up:
                upSites += (value['values'][0]['site-id'] + ' ')
                noDia.removeSite(value['values'][0]['site-id'])
                dia.addSite(value['values'][0]['site-id'])
                self.makeLog(value, False)          

            

            noDia.sendToVmanager()
            while noDia.isRunning():
                time.sleep(1)
                pass
                
            dia.sendToVmanager()
            while dia.isRunning():
                time.sleep(1)
                pass

            




    def makeLog(self,value,inDia):
        obj, created = WebhookLog.objects.get_or_create(siteId=value['values'][0]['site-id'], vManager=VManager.objects.get(id=self.vid))
        if not created:
            obj.inDia=inDia
            obj.hostName = value['values'][0]['host-name'] 
            obj.time = datetime.datetime.now()
            obj.save()
        else:
            obj.siteId=value['values'][0]['site-id']
            obj.inDia=inDia
            obj.hostName = value['values'][0]['host-name'] 
            obj.vManager = VManager.objects.get(id=self.vid)
            obj.save()


    def filterAlerts(self, alerts):
        down = [a for a in alerts if a['message'] == "A tloc went down" and a['values'][0]['color'] == self.color]
        up = [a for a in alerts if a['message'] == "A tloc came up" and a['values'][0]['color'] == self.color]

        if len(self.manual) > 0:
            for man in self.manual:
                if man['message'] == "A tloc went down":
                    down.append(man)
                else:
                    up.append(man)

            self.manual = []

        return down, up

        
    def setManual(self, data):
        self.manual.append(data)


       