import requests
import urllib3
from ..monitor.models import VManager

class sdwan:

    def __init__(self, vmanage_ip, username, password):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.vmanage_ip = vmanage_ip
        self.session = {}
        self.base_url_str = 'https://%s:443'%vmanage_ip
        self.login(self.vmanage_ip, username, password)
        
    def login(self, vmanage_ip, username, password):
        
        base_url_str = self.base_url_str
        login_action = '/j_security_check'        
        login_data = {'j_username' : username, 'j_password' : password}        
        login_url = base_url_str + login_action        

        sess = requests.session()

        login_response = sess.post(url=login_url, data=login_data, verify=False)

    
        if b'<html>' in login_response.content:
            print ("*************Login Failed************")
            print (self.vmanage_ip)
            print ("*************Login Failed************")
 
            

        base_url_str = self.base_url_str
        url = base_url_str+'/dataservice/client/token'
        response = sess.get(url, verify=False)
        
        
        
        sess.headers['X-XSRF-TOKEN'] = response.text

        self.session = sess

    def getFromDb(self):
        return VManager.objects.get(ip=self.vmanage_ip)


    def wanEdgeHealth(self):        
        url = '/dataservice/device/hardwarehealth/summary'
        url = self.base_url_str+url
        response = self.session.get(url, verify=False)
        return response.json()['data'][0]

    def controlStatus(self):        
        url = '/dataservice/device/control/count'
        url = self.base_url_str+url
        response = self.session.get(url, verify=False)
        return response.json()['data'][0]


    def controlStatusDetail(self, detail):        
        url = '/dataservice/device/control/networksummary?state='+detail
        url = self.base_url_str+url
        response = self.session.get(url, verify=False)
        return response.json()['data']
    

    def generalState(self):
        url = '/dataservice/network/connectionssummary'
        url = self.base_url_str+url
        response = self.session.get(url, verify=False)

        return response.json()['data']


    def certificate(self):        
        url = '/dataservice/certificate/stats/summary'
        url = self.base_url_str+url 
        response = self.session.get(url, verify=False)
        return response.json()['data'][0]


    def reboot(self):        
        url = '/dataservice/network/issues/rebootcount'
        url = self.base_url_str+url 
        response = self.session.get(url, verify=False)
        return response.json()['data'][0]

  
    def tunnels(self, ip):
        url = '/dataservice/statistics/approute/fec/aggregation'
        url = self.base_url_str+url

        payload = '{ "query": { "condition": "AND", "rules": [ { "value": [ "1" ], "field": "entry_time", "type": "date", "operator": "last_n_hours" }, { "value": [ "'+ip+'" ], "field": "vdevice_name", "type": "string", "operator": "in" } ] }, "aggregation": { "field": [ { "property": "name", "sequence": 1, "size": 6000 }, { "property": "src_ip", "sequence": 1, "size": 6000 }, { "property": "dst_ip", "sequence": 1, "size": 6000 }  , { "property": "local_color", "sequence": 1, "size": 6000 }, { "property": "remote_color", "sequence": 1, "size": 6000 }, { "property": "local_system_ip", "sequence": 1, "size": 6000 }, { "property": "remote_system_ip", "sequence": 1, "size": 6000 } ], "metrics": [ { "property": "loss_percentage", "type": "avg" }, { "property": "vqoe_score", "type": "avg" }, { "property": "latency", "type": "avg" }, { "property": "jitter", "type": "avg" }, { "property": "tx_octets", "type": "avg" },  { "property": "rx_octets", "type": "avg" } ] } }'
        response = self.session.post(url, data=payload, headers={'Content-Type': 'application/json'}, verify=False)
        
        return response.json()['data']            


    def reachable(self, personality):
        url = '/dataservice/device/reachable?personality='+personality
        url = self.base_url_str+url 

        response = self.session.get(url, verify=False)

        return response.json()['data']


    def unReachable(self, personality):
        url = '/dataservice/device/unreachable?personality='+personality
        url = self.base_url_str+url 
        response = self.session.get(url, verify=False)

        return response.json()['data']

    def health(self, personality):
        url = '/dataservice/device/hardwarehealth/detail?state='+personality
        url = self.base_url_str+url 

        response = self.session.get(url, verify=False)

        return response.json()['data']

        
    def network(self, personality):
        url = '/dataservice/device/control/networksummary?state='+personality

        url = self.base_url_str+url
        response = self.session.get(url, verify=False)
        return response.json()['data']

    def certs(self):
        url = '/dataservice/certificate/stats/detail?status=warning'
        url = self.base_url_str+url
        response = self.session.get(url, verify=False)
        return response.json()['data']


