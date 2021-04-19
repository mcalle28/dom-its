import requests
import urllib3
from ..monitor.models import VManager
import sys
import datetime

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

    
    def log_conn(self, mensaje):
        date_time = datetime.datetime.now()
        current = date_time.strftime("%Y-%b-%d %H:%M")
        path = "/home/dom-its/dom-its/log_conn.txt"
        original_stdout = sys.stdout
        with open(path, 'w') as f:
            sys.stdout = f
            print(current + " : " + mensaje)
            sys.stdout = original_stdout


    def wanEdgeHealth(self):
        try:        
            url = '/dataservice/device/hardwarehealth/summary'
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data'][0]
        except Exception as e:
            self.log_conn("wanEdgeHealth conection is down. %s" %e)
            return {"error":-1}

    def controlStatus(self):
        try:        
            url = '/dataservice/device/control/count'
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data'][0]
        except Exception as e:
            self.log_conn("controlStatus conection is down. %s" %e)
            return {}

    def controlStatusDetail(self, detail):
        try:        
            url = '/dataservice/device/control/networksummary?state='+detail
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("controlStatusDetail conection is down. %s" %e)
            return {}
    

    def generalState(self):
        try:
            url = '/dataservice/network/connectionssummary'
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("generalState conection is down. %s" %e)
            return {}


    def certificate(self):
        try:        
            url = '/dataservice/certificate/stats/summary'
            url = self.base_url_str+url 
            response = self.session.get(url, verify=False)
            return response.json()['data'][0]
        except Exception as e:
            self.log_conn("certificate conection is down. %s" %e)
            return {}


    def reboot(self):
        try:        
            url = '/dataservice/network/issues/rebootcount'
            url = self.base_url_str+url 
            response = self.session.get(url, verify=False)
            return response.json()['data'][0]
        except Exception as e:
            self.log_conn("reboot conection is down. %s" %e)
            return {}

  
    def tunnels(self, ip):
        try:
            url = '/dataservice/statistics/approute/fec/aggregation'
            url = self.base_url_str+url
            payload = '{ "query": { "condition": "AND", "rules": [ { "value": [ "3" ], "field": "entry_time", "type": "date", "operator": "last_n_hours" }, { "value": [ "'+ip+'" ], "field": "vdevice_name", "type": "string", "operator": "in" } ] }, "aggregation": { "field": [ { "property": "name", "sequence": 1, "size": 6000 }, { "property": "src_ip", "sequence": 1, "size": 6000 }, { "property": "dst_ip", "sequence": 1, "size": 6000 }  , { "property": "local_color", "sequence": 1, "size": 6000 }, { "property": "remote_color", "sequence": 1, "size": 6000 }, { "property": "local_system_ip", "sequence": 1, "size": 6000 }, { "property": "remote_system_ip", "sequence": 1, "size": 6000 } ], "metrics": [ { "property": "loss_percentage", "type": "avg" }, { "property": "vqoe_score", "type": "avg" }, { "property": "latency", "type": "avg" }, { "property": "jitter", "type": "avg" }, { "property": "tx_octets", "type": "avg" },  { "property": "rx_octets", "type": "avg" } ] } }'
            response = self.session.post(url, data=payload, headers={'Content-Type': 'application/json'}, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("tunnels conection is down. %s" %e)
            return {}


    def reachable(self, personality):
        try:
            url = '/dataservice/device/reachable?personality='+personality
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("reachable conection is down. %s" %e)
            return {}


    def unReachable(self, personality):
        try:
            url = '/dataservice/device/unreachable?personality='+personality
            url = self.base_url_str+url 
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("unReachable conection is down. %s" %e)
            return {}


    def health(self, personality):
        try:
            url = '/dataservice/device/hardwarehealth/detail?state='+personality
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("health conection is down. %s" %e)
            return {}

        
    def network(self, personality):
        try:
            url = '/dataservice/device/control/networksummary?state='+personality
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("network conection is down. %s" %e)
            return {}

    def certs(self):
        try:
            url = '/dataservice/certificate/stats/detail?status=warning'
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("certs conection is down. %s" %e)
            return {}

    
    def boot(self):
        try:
            url = '/dataservice/device/reboothistory/details'
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("boot conection is down. %s" %e)
            return {}


    def alerts(self, start, end, count='10000'):
        try:
            url = '/dataservice/data/device/statistics/alarm?startDate='+str(end)+'&endDate='+str(start)+'&count='+count
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return  response.json()['data']
        except Exception as e:
            self.log_conn("alerts conection is down. %s" %e)
            return {}
        

    def alertsEx(self, count='10000'):
        try:
            url = '/dataservice/data/device/statistics/alarm?startDate=2020-11-26T10:10:59&endDate=2020-11-26T10:20:59&count='+count
            url = self.base_url_str+url
            response = self.session.get(url, verify=False)
            return response.json()['data']
        except Exception as e:
            self.log_conn("alertsEx conection is down. %s" %e)
            return {}