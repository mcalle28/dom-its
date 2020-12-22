from ..monitor.models import Webhook, ExcludeSite
from .diaWatcher import DiaWatcher
import schedule
import time 
import threading

class Dia:
    def __init__(self, color, cTime):
        self.color = color
        self.cTime = cTime
        self.watchers = []
        schedule.every(self.cTime).seconds.do(self.update)

        self.start()
        self.startDia()

    def start(self):
        wh = Webhook.objects.all()
        for obj in wh:
            excluded = ExcludeSite.objects.filter(webhook=obj.webhookId).values('siteId')
            self.watchers.append(DiaWatcher(self.color, self.cTime, obj.vManager.id, excluded=excluded))

    def startDia(self):
        job_thread = threading.Thread(target=self.thread)
        job_thread.daemon = True
        job_thread.start()  

    def thread(self):        
        while 1:
            schedule.run_pending()
            time.sleep(1)

    def update(self):
        for i in self.watchers:
            i.update()

    def manual(self, vm, data):

        obj = None

        for i in self.watchers:

            if str(i.vid) == vm:
                obj = i
                break

        if obj is None:

            return
        
        obj.setManual(data)





        
        



        