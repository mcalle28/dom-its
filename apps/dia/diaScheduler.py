import schedule
from .sdwanUtils import SiteManager
import threading
import time
from ..monitor.models import Webhook 

class DiaScheduler:
    
    def __init__(self, color, queueTime, vManager):
        self.waitingForDevices = False
        self.queue = []
        self.color = color
        self.queueTime = queueTime
        self.vManager = vManager

    '''Punto de entrada de la clase, las otras clases
    Las otras clases llaman este método, él elige si
    el color coincide con el configurado y procesa
    la petición, añadiéndo el json a la cola
    '''
    def processRequest(self, json):
        print('Se procesa la peticion')
        if self.color != json['values'][0]['color']:
            raise Exception('Color doesn´t match')
        else:
            
            if not self.checkSchedule():
                self.queue.append(json)
                print('Se da la orden de crear el proceso')
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
        print('Se va a esperar: ',self.queueTime,'segundos')

        schedule_thread = threading.Thread(target=self.wait)
        schedule_thread.daemon = True 

        schedule_thread.start()
        

    def wait(self):      

        while self.waitingForDevices:
            schedule.run_pending()
            time.sleep(1)

        print('La espera ha terminado')

    def createConfig(self):
        
        arrayToConfig, message = self.getFirstFromArray()
        print('Se va a crear un proceso')

        if message == 'A tloc went down':
            job_thread = threading.Thread(target=self.fromDiatoNoDia, args=(arrayToConfig,))
            job_thread.daemon = True
            job_thread.start()      
            self.waitingForDevices = False               
        
        if message == 'A tloc came up':
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

        print('Se va a mandar algo al vmanager')

        dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        
        for value in array:


            Webhook(vManager=self.vManager,
            ip=value['values'][0]['system-ip'],
            message='From NoDIA to DIA',
            hostname=value['values'][0]['host-name']).save()

            dia.addSite(value['values'][0]['site-id'])
            noDia.removeSite(value['values'][0]['site-id'])
        
        noDia.sendToVmanager()
        while noDia.isRunning():
            time.sleep(1)
            pass

        dia.sendToVmanager()
        while dia.isRunning():
            time.sleep(1)
            pass

        self.checkQueue()        

    def fromDiatoNoDia(self, array):

        print('Se va a mandar algo al vmanager')

        dia = SiteManager('dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        noDia = SiteManager('no dia', self.vManager.base_url_str, self.vManager.session, self.vManager.getFromDb())
        
        for value in array:

            Webhook(vManager=self.vManager,
            ip=value['values'][0]['system-ip'],
            message='From DIA to NoDIA',
            hostname=value['values'][0]['host-name']).save()

            noDia.addSite(value['values'][0]['site-id'])
            dia.removeSite(value['values'][0]['site-id'])
        
        dia.sendToVmanager()
        while dia.isRunning():
            time.sleep(1)
            pass

        noDia.sendToVmanager()
        while noDia.isRunning():
            time.sleep(1)
            pass
        
        self.checkQueue()
