import schedule
from .sdwanUtils import SiteManager
import threading
import time
from ..monitor.models import Webhook, WebhookLog, VManager
import datetime
from ..api.views import sdwan as sdwansObjs

class DiaScheduler:
    
    def __init__(self, color, queueTime, vManager, vid, excluded=[]):
        self.waitingForDevices = False
        self.queue = []
        self.vid = vid
        self.color = color
        self.queueTime = queueTime
        self.vManager = vManager
        self.lastMessage = []
        self.excluded = excluded


    '''Punto de entrada de la clase, las otras clases
    Las otras clases llaman este método, él elige si
    el color coincide con el configurado y procesa
    la petición, añadiéndo el json a la cola
    '''
    def processRequest(self, json):

        if json['values'][0]['site-id'] in self.excluded:
            self.setMessage('Event site: '+json['values'][0]['site-id'])
            self.setMessage('Site: '+json['values'][0]['site-id']+' is excluded')
            self.setMessage('----------------Done----------------')
            return
        
        if self.color != json['values'][0]['color']:
            raise Exception('Color doesnÂ´t match')
        else:
        
            self.vManager = sdwansObjs.sdwans[str(self.vid)]
            
            
            if not self.checkSchedule():
                self.queue.append(json)
                self.waitingForDevices = True
                self.makeSchedule()
            else:
                self.queue.append(json)

            

    def checkQueue(self):
        self.waitingForDevices = True
        if len(self.queue) >= 1:
            self.makeSchedule()

    def checkSchedule(self):
        return len(self.queue) >= 1
    
    def makeSchedule(self):
        schedule.every(self.queueTime).seconds.do(self.createConfig)

        self.setMessage('An event has arrive. 30 seconds timer setted to proccess request')
        
        schedule_thread = threading.Thread(target=self.wait)
        schedule_thread.daemon = True 

        schedule_thread.start()
        
    def wait(self):      

        while self.waitingForDevices:
            schedule.run_pending()
            time.sleep(1)

    def createConfig(self):

        try:        
            arrayToConfig, message = self.getFirstFromArray()
        except:
            return schedule.CancelJob        

        if message == 'A tloc went down':
            self.setMessage('A device went down. config will be sent to vsmart from DIA to NO DIA')
            job_thread = threading.Thread(target=self.fromDiatoNoDia, args=(arrayToConfig,))
            job_thread.daemon = True
            job_thread.start()      
            self.waitingForDevices = False               
        
        if message == 'A tloc came up':
            self.setMessage('A device came up. Config will be sent to vsmart from NO DIA to DIA')
            job_thread = threading.Thread(target=self.fromNoDiatoDia, args=(arrayToConfig,))
            job_thread.daemon = True            
            job_thread.start()
            self.waitingForDevices = False
        
        
        return schedule.CancelJob

    def getFirstFromArray(self):
        try:
            first = self.queue[0]
            outputArray = [x for x in self.queue if x['message'] == first['message']]
            newArray = [x for x in self.queue if x not in outputArray]
            self.queue = newArray
            return outputArray, first['message']

        except IndexError:
            raise Exception('No webhook')


    def fromNoDiatoDia(self, array):
        

        dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        
        self.setMessage('Actual NODIA State sites:')
        self.setMessage(str([a['siteId'] for a in noDia.entries]))

        self.setMessage('Actual DIA State sites:')
        self.setMessage(str([a['siteId'] for a in dia.entries]))

        sitesArray = ''
        for value in array:

            sitesArray += (value['values'][0]['site-id'] + ' ')
            dia.addSite(value['values'][0]['site-id'])
            noDia.removeSite(value['values'][0]['site-id'])

            
            ##Guardar en el registro de site
            
            obj, created = WebhookLog.objects.get_or_create(siteId=value['values'][0]['site-id'] + ' HostName: '+ value['values'][0]['host-name'], vManager=VManager.objects.get(id=self.vid))
            if not created:
                obj.inDia=True
                obj.save()
            else:
                obj.siteId=value['values'][0]['site-id'] + ' HostName: '+ value['values'][0]['host-name']
                obj.inDia=True
                obj.vManager = VManager.objects.get(id=self.vid)
                obj.save()

        self.setMessage('NODIA-TO-DIA Device UP: '+str(sitesArray))        
       
        self.setMessage('NODIA new State')
        self.setMessage(str([a['siteId'] for a in noDia.entries]))

        self.setMessage('DIA new State')
        self.setMessage(str([a['siteId'] for a in dia.entries]))

        noDia.sendToVmanager()
        while noDia.isRunning():
            time.sleep(1)
            pass

        dia.sendToVmanager()
        while dia.isRunning():
            time.sleep(1)
            pass

        self.setMessage('-'*20+'Done'+'-'*20)
        self.checkQueue()        

    def fromDiatoNoDia(self, array):    
         

        dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())

        self.setMessage('Actual DIA State')
        self.setMessage(str([a['siteId'] for a in dia.entries]))

        self.setMessage('Actual NODIA State sites:')
        self.setMessage(str([a['siteId'] for a in noDia.entries]))
        
        sitesArray = ''
        for value in array:

            sitesArray += (value['values'][0]['site-id'] + ' ')
            noDia.addSite(value['values'][0]['site-id'])
            dia.removeSite(value['values'][0]['site-id'])

            ##Guardar en el registro de site
            
            obj, created = WebhookLog.objects.get_or_create(siteId=value['values'][0]['site-id']+ ' HostName: '+ value['values'][0]['host-name'], vManager=VManager.objects.get(id=self.vid))
            if not created:
                obj.inDia=False
                obj.save()
            else:
                obj.siteId=value['values'][0]['site-id'] +' HostName: '+ value['values'][0]['host-name']
                obj.inDia=True
                obj.vManager = VManager.objects.get(id=self.vid)
                obj.save()

                

        self.setMessage('DIA-TO-NODIA Device DOWN: '+str(sitesArray))
        
        self.setMessage('DIA new State')
        self.setMessage(self.setMessage(str([a['siteId'] for a in dia.entries])))

        self.setMessage('NODIA new State')
        self.setMessage(str([a['siteId'] for a in noDia.entries]))

        dia.sendToVmanager()
        while dia.isRunning():
            time.sleep(1)
            pass

        noDia.sendToVmanager()
        while noDia.isRunning():
            time.sleep(1)
            pass
        
        self.setMessage('-'*20+'Done'+'-'*20)     
        self.checkQueue()

    def getLastMessage(self):
        res = self.lastMessage
        self.lastMessage = []
        return '*'.join(res)

    def setMessage(self, message):

        if message is None:
            return
        time = datetime.datetime.now()

        f = open('./static/diaLogs/'+self.vManager.vmanage_ip.split('.')[0]+".log", "a+")
        f.write('\n['+str(time)+']'+message)
        f.close()

        if len(self.lastMessage) >=10:
            self.lastMessage = []

        
        self.lastMessage.append('['+str(time)+'] '+message)