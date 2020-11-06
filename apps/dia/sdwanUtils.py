import urllib3
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from django.utils import timezone
import sys
from intspan import intspan
import time

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
 
        
        
        response = self.session.put(url, data=json.dumps(self.site), verify=False)
        
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
        self.data = data
        self.ranges = []
        self.to_ranges()        
        
        
        if type(data) == list:            
            self.data = data
        else:
            raise BaseException('Formato invalido')
            
            
    def to_ranges(self):    
        
        for item in self.data:
            if '-' in item['siteId']:
                values = item['siteId'].split('-')
                self.ranges.append([int(values[0]), int(values[1])])
            else:
                self.ranges.append([int(item['siteId']),int(item['siteId'])])

        
            
    def remove(self, rem):
        
        for i, r in enumerate(self.ranges):
            if r[0] <= rem <= r[1]:
                if r[0] == rem:     # range min
                    if r[1] > rem:
                        r[0] += 1
                    else:
                        del self.ranges[i]
                        self.fixRange()
                elif r[1] == rem:   # range max
                    if r[0] < rem:
                        r[1] -= 1
                    else:
                        del self.ranges[i]
                        self.fixRange()
                else:               # inside, range extremes.
                    r[1], splitrange = rem - 1, [rem + 1, r[1]]
                    self.ranges.insert(i + 1, splitrange)
                    self.fixRange()                    
                self.fixRange()
                break
            if r[0] > rem:  # Not in sorted list
                self.fixRange()
                break
        
    def add(self, add):
        
        for i, r in enumerate(self.ranges):
            if r[0] <= add <= r[1]:     # already included
                break
            elif r[0] - 1 == add:      # rough extend to here
                r[0] = add
                break
            elif r[1] + 1 == add:      # rough extend to here
                r[1] = add
                break
            elif r[0] > add:      # rough insert here
                self.ranges.insert(i, [add, add])
                break
        else:
            self.ranges.append([add, add])
            self.fixRange()
        self.fixRange()
    
    
    def consolidate(self):
        "Combine overlapping ranges"
        for this, that in zip(self.ranges, self.ranges[1:]):
            
         
            if this[1] + 1 >= that[0]:  # Ranges interract
                if this[1] >= that[1]:  # this covers that
                    this[:], that[:] = [], this
                else:   # that extends this
                    this[:], that[:] = [], [this[0], that[1]]
        self.ranges[:] = [r for r in self.ranges if r]
        


    def fixRange(self):
        self.ranges.sort()
        self.consolidate()        
        self.formatData()
        pass

    def removeDoubles(self):
        res = []
        for i,item in enumerate(self.ranges):
            if item[1] == item[0]:
                res.insert(i,[item[0]])
            else:
                res.insert(i,item)
                
        return res
        
    

    def formatData(self):
        ran = self.removeDoubles()
        res = []
        for item in ran:
            res.append({'siteId':'-'.join(str(n) for n in item)})  
        self.data = res