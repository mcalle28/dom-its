from .sdwanUtils import sdwan as sd
from ..monitor.models import VManager
import schedule
import threading
import time

class Sdwan:

    def __init__(self):
        self.sdwans = {}               
        self.update()
        schedule.every(28).minutes.do(self.update)
        job_thread = threading.Thread(target=self.pending)
        job_thread.daemon = True            
        job_thread.start()
    
    def wanEdgeHealth(self, vmid):
        return self.sdwans[vmid].wanEdgeHealth()

    def certificate(self, vmid):
        return self.sdwans[vmid].certificate()

    def reboot(self, vmid):
        return self.sdwans[vmid].reboot()

    def wanEdgeHealthDetail(self, vmid, personality):
        return self.sdwans[vmid].health(personality)

    def controlStatus(self, vmid):
        return self.sdwans[vmid].controlStatus()
        
    def controlStatusDetail(self, vmid, detail):        
        return self.sdwans[vmid].controlStatusDetail(detail)

    def generalState(self, vmid):
        return self.sdwans[vmid].generalState()

    def tunnels(self, vmid, ip):
        return self.sdwans[vmid].tunnels(ip)

    def reachable(self, vmid, personality):
        return self.sdwans[vmid].reachable(personality)  

    def unReachable(self, vmid, personality):
        return self.sdwans[vmid].unReachable(personality)            
        
    def certs(self, vmid):
        return self.sdwans[vmid].certs()  

    def boot(self, vmid):
        return self.sdwans[vmid].boot()        

    def update(self):
        for vmanager in VManager.objects.all():
            self.sdwans[str(vmanager.id)] = sd(vmanager.ip, vmanager.user, vmanager.password)

    def pending(self):
        while True:
            schedule.run_pending()
            time.sleep(30)
            
