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
        self.acum = 1
        self.onProcess = False



    def update(self):


        if self.onProcess:
            acum += 1
            return

        self.vManager = sdwansObjs.sdwans[str(self.vid)]
        utc = datetime.timedelta(hours=5)
        start = datetime.datetime.now() 
        summ = datetime.timedelta(seconds=self.cTime * self.acum)

        start = start + utc

        end = start - summ
        start = start.strftime("%Y-%m-%dT%H:%M:%S")
        end = end.strftime("%Y-%m-%dT%H:%M:%S")

        print('Alarmas entre: '+end+' y '+start)
        
        alerts = self.vManager.alerts(start, end)
        down, up = self.filterAlerts(alerts)
        self.setMessage('Between: '+end+' and '+start + ' got '+str(len(down))+' down devices and '+str(len(up))+ ' up devices')
        



        if len(down) > 0 or len(up)>0:
            self.onProcess = True
            
        
            
               
        self.operate(down, up)
                  
        

    def operate(self, down, up):

        downSites = ''
        if(len(down) != 0):
        
            dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
            noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
            

            #self.setMessage('Actual NODIA State sites:')
            #self.setMessage(str([a['siteId'] for a in noDia.entries]))
            #self.setMessage('Actual DIA State sites:')
            #self.setMessage(str([a['siteId'] for a in dia.entries]))


            downSites = ''
            for value in down:
                downSites += (value['values'][0]['site-id'] + ' ')
                noDia.addSite(value['values'][0]['site-id'])
                dia.removeSite(value['values'][0]['site-id'])
                self.makeLog(value, True)

            self.setMessage('.'*10+'Down sites: '+downSites+'.'*10)
            
            dia.sendToVmanager()
            while dia.isRunning():
                time.sleep(1)
                pass
                
                
            noDia.sendToVmanager()
            while noDia.isRunning():
                time.sleep(1)
                pass

            self.setMessage('DIA-TO-NODIA Sites: '+str(downSites))        
        

            #self.setMessage('NODIA new State')
            #self.setMessage(str([a['siteId'] for a in noDia.entries]))

            #self.setMessage('DIA new State')
            #self.setMessage(str([a['siteId'] for a in dia.entries]))

            self.setMessage('-'*20+'Done (down: '+downSites+')'+'-'*20)
            
            
        upSites = ''
        if (len(up) != 0):
            dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
            noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())

            
            #self.setMessage('Actual NODIA State sites:')
            #self.setMessage(str([a['siteId'] for a in noDia.entries]))
            #self.setMessage('Actual DIA State sites:')
            #self.setMessage(str([a['siteId'] for a in dia.entries]))


            upSites = ''
            for value in up:
                upSites += (value['values'][0]['site-id'] + ' ')
                noDia.removeSite(value['values'][0]['site-id'])
                dia.addSite(value['values'][0]['site-id'])
                self.makeLog(value, False)          

            self.setMessage('.'*10+'Up sites: '+upSites+'.'*10)

            noDia.sendToVmanager()
            while noDia.isRunning():
                time.sleep(1)
                pass
                
            dia.sendToVmanager()
            while dia.isRunning():
                time.sleep(1)
                pass


            self.setMessage('NODIA-TO-DIA Sites: '+str(upSites))        
        

            #self.setMessage('NODIA new State')
            #self.setMessage(str([a['siteId'] for a in noDia.entries]))

            #self.setMessage('DIA new State')
            #self.setMessage(str([a['siteId'] for a in dia.entries]))

            self.setMessage('-'*20+'Done (up: '+upSites+')'+'-'*20)
            self.setMessage('\n\n')

        self.onProcess = False
        self.acum = 1

            




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
        down = [a for a in alerts if ( a['message'] == "A tloc went down" or a['message'] == "All BFD sessions for the tloc are down" )  and a['values'][0]['color'] == self.color]
        up = [a for a in alerts if ( a['message'] == "A tloc came up" or a['message'] == "BFD sessions for the tloc came up" ) and a['values'][0]['color'] == self.color]

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


    def setMessage(self, message):

        time = datetime.datetime.now()

        f = open('./static/diaLogs/'+self.vManager.vmanage_ip.split('.')[0]+".log", "a+")
        f.write('\n['+str(time)+']'+message)
        f.close()
        