import urllib3
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from django.utils import timezone
import sys

class SiteManager:

    def __init__(self, id, base_url_str, session, vm):

        self.vm = vm
        self.base_url_str = base_url_str
        self.session = session
        self.site = self.getSiteList(id)
        self.entries = self.site['entries']
        self.SdRange = SdRange(self.entries)
        self.id = id
        self.pID = ''
        
               
    def getSiteList(self, id):
        if id == 'dia':            
            url = '/dataservice/template/policy/list/site/'+self.vm.diaUri
        if id == 'no dia':
            url = '/dataservice/template/policy/list/site/'+self.vm.noDiaUri

        url = self.base_url_str+url
            
        response = self.session.get(url, verify=False)

        return response.json()

    def sendToVmanager(self):
        
        if self.id == 'dia':
            url = '/dataservice/template/policy/list/site/'+self.vm.diaUri
        if self.id == 'no dia':
            url = '/dataservice/template/policy/list/site/'+self.vm.noDiaUri
        
        url = self.base_url_str+url
        
        urltask = self.base_url_str+'/dataservice/device/action/status/tasks'
        responsetask = self.session.get(urltask, verify=False)

        self.session.headers['Content-Type'] = 'application/json'       
        
        while responsetask.json()['runningTasks']:
            
            time.sleep(30)
            responsetask = self.session.get(urltask, verify=False)
 
        
        print(self.site)
        response = self.session.put(url, data=json.dumps(self.site), verify=False)
        print(response.json())
        masterTemplate = response.json()['masterTemplatesAffected'][0]

        print('%s Put para cambiar Site List de %s' %(str(datetime.now()),self.id))
        self.toConfigInput(masterTemplate)

    def toConfigInput(self, masterTemplate):
        url = '/dataservice/template/device/config/attached/'+masterTemplate
        url = self.base_url_str+url

        response = self.session.get(url, verify=False)

        uuidList = []
        for uuid in response.json()['data']:
            uuidList.append(uuid['uuid'])

        payload = {  "templateId":masterTemplate,"deviceIds":uuidList,"isEdited":True,"isMasterEdited":False}

        url = "/dataservice/template/device/config/input"
        url = self.base_url_str+url

        response = self.session.post(url, data=json.dumps(payload), verify=False)
        
        url = '/dataservice/template/device/config/attachment/'
        url = self.base_url_str+url

        payload = {"deviceTemplateList":[{"templateId":masterTemplate,"device":response.json()['data'],"isEdited":True,"isMasterEdited":False}]}
        response = self.session.post(url, data=json.dumps(payload), verify=False)

        self.pID = response.json()['id']
        
        print('%s Post hacia el vsmart' % str(datetime.now()))

    def isRunning(self):
        
        url = '/dataservice/device/action/status/'+self.pID
        url = self.base_url_str+url        
        response = self.session.get(url, verify=False)
        
        if response.json()['summary']['status'] == 'in_progress':
            return True
        else:
            return False

    def removeSite(self, site):
        site = int(site)
        self.SdRange.remove(site)
        self.entries = self.SdRange.data
        self.site['entries'] = self.entries

    def addSite(self,site):
        site = int(site)
        self.SdRange.add(site)
        self.entries = self.SdRange.data
        self.site['entries'] = self.entries

class SdRange:
    
    def __init__(self, data):
        
        self.data = ''
        if type(data) == list:            
            self.data = data
            self.sort()
        else:
            raise BaseException('Formato invalido')
          
    def sort(self):
        self.data = sorted(self.data, key=lambda k: k.get('siteId', 0), reverse=False)
    
    def contains(self, value):
        for obj in self.data:
            
            values = obj['siteId'].split('-')
            values = [ int(x) for x in values ]

            if len(values) == 1:
                if values[0] == value:
                    return True
                
            else:
                if value >= values[0] and value <= values[1]:
                    return True
                
        return False
    
    def add(self, value):
        if self.contains(value):
            return
        
        newData=[]
        added = False
        joined = False
        
        for i in range(len(self.data)):
            values = self.data[i]['siteId'].split('-')
            values = [ int(x) for x in values ]
            
            if joined:
                joined = False
                continue
                 
            if len(values) == 1:
                if values[0]-value == 1:
                    nObj = self.data[i]
                    nObj['siteId'] = str(value)+'-'+str(values[0])
                    newData.append(nObj)
                    added = True
                    
                elif value-values[0] == 1:
                    nObj = self.data[i]
                    nObj['siteId'] = str(values[0])+'-'+str(value)
                    newData.append(nObj)
                    added = True
                    
                else:
                    newData.append(self.data[i])

            else: 
                if values[0] - value == 1:
                    nObj = self.data[i]
                    nObj['siteId'] = str(values[0]-1)+'-'+str(values[1])
                    newData.append(nObj)
                    added = True
                    
                elif values[1] - value == -1:
                    
                    try:
                        second = self.data[i+1]['siteId'].split('-')                        
                        second = [ int(x) for x in second ]

                        if value - second[0] == -1:
                            nObj = self.data[i]
                            nObj['siteId'] = str(values[0])+'-'+str(second[1])

                            added= True
                            joined = True
                            newData.append(nObj)
                            continue
                    except Exception as e:
                        print(str(e))
                            
                            
                    nObj = self.data[i]
                    nObj['siteId'] = str(values[0])+'-'+str(values[1]+1)
                    newData.append(nObj)
                    added = True
                    
                elif value > values[1]:
                    newData.append(self.data[i])
                    
                elif value < values[1]:
                    if added:
                        newData.append(self.data[i])
                        added = True
                        continue
                    added = True
                    newData.append({'siteId':str(value)})
                    newData.append(self.data[i])
                
                
        if not added:
            newData.append({'siteId':str(value)})
                        
        self.data = newData
        
    def remove(self, value):
        if not self.contains(value):
            return
        
        newRange = []
        removed = False
        
        for obj in self.data:
            values = obj['siteId'].split('-')
            values = [ int(x) for x in values ]
            
            if len(values) == 1:
                
                if value == values[0]:
                    continue
                else:
                    newRange.append({'siteId':str(values[0])})
                    
                
            else:
                if value >= values[0] and value <= values[1]:
                    
                    if value == values[0]:
                        nObj = obj                        
                        nObj['siteId'] = str(values[0]+1)+'-'+str(values[1])
                        newRange.append(nObj)

                    elif value == values[1]:
                        nObj = obj
                        

                        nObj['siteId'] = str(values[0])+'-'+str(values[1]-1)
                        newRange.append(nObj)
                        
                    else:
                        if values[1] - values[0] == 1:
                            if values[0] == value:
                                newRange.append({'siteId':str(value[1])})
                            if values[1] == value:
                                newRange.append({'siteId':str(value[0])}) 
                        else:
                            newRange.append({'siteId':str(values[0])+'-'+str(value-1)})
                            newRange.append({'siteId':str(value+1)+'-'+str(values[1])})
                    
                else:                    
                    newRange.append(obj)
                    
        self.data = newRange
        self.removeDoubles()

    def removeDoubles(self):

        newRange = []

        for obj in self.data:
            values = obj['siteId'].split('-')
            values = [ int(x) for x in values ]
            
            if len(values) == 1 or values[0] == values[1]:
                newRange.append({'siteId':str(values[0])})
                continue

           
            newRange.append(obj)    
        self.data = newRange

    def getData(self):
        self.removeDoubles()
        self.sort()
        return self.data

class VManager:

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
            print ("Login Failed")         

        base_url_str = self.base_url_str
        url = base_url_str+'/dataservice/client/token'
        response = sess.get(url, verify=False)
        print("EXITO-"*17)
        print(response.text)
        print("EXITO-"*17)
        sess.headers['X-XSRF-TOKEN'] = response.text
        self.session = sess

    def getSiteId(self, ip):
        url = '/dataservice/system/device/vedges?deviceIP='+ip
        url = self.base_url_str+url
        payload = {}
        headers = {}
        response = self.session.get(url, headers=headers, data=payload, verify=False)

        return response.json()['data'][0]['site-id']

    def getDevice(self, ip):

        url = '/dataservice/system/device/vedges?deviceIP='+ip
        url = self.base_url_str+url
        payload = {}
        headers = {}
        response = self.session.get(url, headers=headers, data=payload, verify=False)
        return response.json()['data'][0]
