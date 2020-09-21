from .sdwanUtils import sdwan as sd
from ..monitor.models import VManager

class Sdwan:

    def __init__(self):
        self.sdwans = {}               
        for vmanager in VManager.objects.all():
            self.sdwans[str(vmanager.id)] = sd(vmanager.ip, vmanager.user, vmanager.password)

    
    def wanEdgeHealth(self, vmid):
        return self.sdwans[vmid].wanEdgeHealth()
            

    def controlStatus(self, vmid):
        return self.sdwans[vmid].controlStatus()


    def generalState(self, vmid):
        return self.sdwans[vmid].generalState()

    def tunnels(self, vmid, ip):
        return self.sdwans[vmid].tunnels(ip)


            