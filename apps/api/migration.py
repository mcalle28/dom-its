import ipaddress

class migration:
    
    def __init__(self, data, **kwargs):
        self.data = data
        self.args = kwargs
    
    def getVlanBlock(self, vlan):
        index = self.data.find('interface '+vlan)
        crop = self.data[index:]
        index2 = crop.find('!')
        vlanBlock = self.data[index:index+index2]
        return vlanBlock
    
    def vlanIp(self,vlan):
        
        vlanBlock = self.getVlanBlock(vlan)
        
        ipMask = vlanBlock[vlanBlock.find('ip address')+11:].split('\n')[0] 
        ip = ipMask.split(' ')[0]        
        try:
            
            redPrefix = ipaddress.ip_network(ipMask.replace(' ','/'),strict=False)
            redMask = redPrefix.with_netmask
            redPrefixObj = redPrefix
            redPrefix = str(redPrefix)
            
            
        except ValueError as e:
            
            redMask = '198.18.'+vlan[4:]+'.0 255.255.255.0'
            return('198.18.'+vlan[4:]+'.1/24'), redMask.replace('/',' '), '198.18.'+vlan[4:]+'.0/24'
        
        return ip+redPrefix[redPrefix.find('/'):], redMask.replace('/',' '), redPrefixObj
        
    def getDescription(self,vlan):
        vlanBlock = self.getVlanBlock(vlan)        
        if 'description' in vlanBlock:
            index1 = vlanBlock.find('description')+12
            return vlanBlock[index1:].split('\n')[0]
            
        else:
            return 'default'
            
        
    def vlanShutdown(self, vlan):
        vlanBlock = self.getVlanBlock(vlan)
        
        if vlanBlock == '' or 'no ip address' in vlanBlock:
            return 'TRUE'
        
        return str('shutdown' in vlanBlock).upper()
    
    def addressPool(self, redMask, vlan):
        
        
        
        if 'network '+redMask in self.data:
            redPrefix1 = ipaddress.ip_network(redMask.replace(' ','/'),strict=False)
            
            
            index = self.data.find('network '+redMask)
            crop = self.data[index:]
            index2 = crop.find('!')
            dhcpBlock = self.data[index:index+index2]
            
            defaultRouter = dhcpBlock[dhcpBlock.find('default-router'):].split(' ')[1]
            
            
            
            return str(redPrefix1), defaultRouter
            
        else:           
            return '198.18.'+vlan[4:]+'.0/24', '198.18.'+vlan[4:]+'.1'
            
            
        
        
        
    
    def migrate(self):
        
        ip, redMask, redPrefix = self.vlanIp(self.args['vlan'])
        shutdown = self.vlanShutdown(self.args['vlan'])
        addressPool, deafultRouter = self.addressPool(redMask,self.args['vlan'])
        description = self.getDescription(self.args['vlan'])
        
        if not type(redPrefix) == str:   
            excludedAddress = self.excludedAddress(self.args['vlan'], redPrefix)
        else:
            excludedAddress = '198.18.{0}.1-198.18.{0}.254'.format(self.args['vlan'][4:])
        
        if self.args['tipo'] == '1':
            nextHopIfInet, ifInet, ipMaskInet = self.wanTipo1(self.args['interfazInternet'])
            nextHopIfMpls, ifMpls, ipMaskMpls = ('','','')
            
        if self.args['tipo'] == "2":
            nextHopIfInet, ifInet, ipMaskInet = self.wanTipo2(self.args['interfazInternet'], 'internet')
            nextHopIfMpls, ifMpls, ipMaskMpls = self.wanTipo2(self.args['interfazMpls'], 'mpls')
        
        
        res={            
            'ip con prefix':ip,
            'description':description,
            'ip default router':deafultRouter,
            'shutdown':shutdown,
            'redMask':redMask,
            'address':addressPool,
            'excludedAddress': excludedAddress,
            'nextHopIfnet': nextHopIfInet,
            'ifInet': ifInet,
            'ipMaskInet':ipMaskInet,
            'nexHopMpls': nextHopIfMpls,    
            'ifMpls':ifMpls,
            'ipMaskMpls':ipMaskMpls,
        }
           
        
        
        return res
        
        
        
        
    def excludedAddress(self, vlan, redPrefix):
        index = self.data.find('ip dhcp excluded-address')
        index2 = self.data[index:].find('!') + index
        
        block = self.data[index:index2]
        
        res = ''
        
        
        for row in block.split('\n')[:-1]:
            ip1 = row.split(' ')[3]
            
                        
            try:
                ip2 = row.split(' ')[4]
            except:
                if ipaddress.ip_address(ip1) in redPrefix:
                    res = res+ip1+','
                    continue
                
            if ipaddress.ip_address(ip1) in redPrefix:
                res = res+ip1+'-'+ip2+','
        
        
        if res == '':
            return '"198.18.{0}.1-198.18.{0}.254"'.format(vlan[4:])
        
        
        if '"' in res[:-1]:
            return res[:-1]
        return '"'+res[:-1]+'"'
            
        
    
        
    def wanTipo1(self, interfaz):
        
        index = self.data.find('interface '+interfaz)
        index2 = self.data[index:].find('!')
        
        block = self.data[index : index+index2]
        
        index = block.find('ip address')
        index2 = block[index:].find('\n')
        
        ip = block[index:index+index2].split(' ')[2]
        ipMask = block[index:index+index2].split(' ')[3]
        
        
        ipMask = ip + '/30'
        
        
        
        ip = block[index:index+index2].split(' ')[2]
        
        ip = ip.split('.')        
        lastOctect = int(ip[-1])        
        ip[-1] = str(lastOctect - 1)        
        newIp = '.'.join(ip)
        
        
        ifIne = interfaz.split('.')[1]
        ifIne = 'GigabitEthernet0/0/0.'+ifIne
            
        
            
        
        return newIp, ifIne, ipMask
    
    
    def wanTipo2(self, interfaz, color):
        
        index = self.data.find('interface '+interfaz)
        index2 = self.data[index:].find('!')
        
        block = self.data[index : index+index2]

        
        for i in range(0,10):
            if block.count('\n') > 5:
                break
            index = self.data.find('interface '+interfaz, index2)
            index2 = self.data[index:].find('!')
            block = self.data[index : index+index2]  

        index = block.find('ip address')
        index2 = block[index:].find('\n')
        
        ip = block[index:index+index2].split(' ')[2]
        ipMask = block[index:index+index2].split(' ')[3]
        
        ipMask = ip + '/30'  
        
        ip = block[index:index+index2].split(' ')[2]
        
        ip = ip.split('.')        
        lastOctect = int(ip[-1])        
        ip[-1] = str(lastOctect - 1)        
        newIp = '.'.join(ip)
        
        ifIne = ''
        
        if color == "mpls":
            ifIne = interfaz.split('.')[1]
            ifIne = 'GigabitEthernet0/0/0.'+ifIne
            
        if color == "internet":
            ifIne = interfaz.split('.')[1]
            ifIne = 'GigabitEthernet0/0/1.'+ifIne
            
        
        return newIp, ifIne, ipMask
        
        
    def toCSV(self):
                
        if self.args['tipo'] == '1':         
            
            values = [
                self.args['modeloSerial'],
                self.args['deviceIP'],
                self.args['hostName'], 
                self.args['hostName'], 
                self.args['snmpLocation']
            ]
                  
            self.args['vlan'] = 'Vlan80'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])

            
            self.args['vlan'] = 'Vlan12'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan2'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan1'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan74'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan73'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan72'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan71'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan70'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan19'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan18'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan17'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan16'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan15'
            data = self.migrate()
            values.append(data['description'])
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan14'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan13'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            
            values.append(data['nextHopIfnet'])
            values.append(data['ifInet'])
            values.append(data['ipMaskInet'])   
            values.append(self.args['BWInternet'])
            values.append(self.args['BWInternet'])
            values.append(self.args['BWInternet'])            
            values.append(self.args['autoIfInternet'])
            values.append(self.args['hostName'])
            values.append(self.args['latitude'])
            values.append(self.args['longitude'])            
            values.append(self.args['deviceIP'])
            values.append(self.args['siteId'])
            values.append(data['ifInet'])
            values.append(data['address'])
            
            self.args['vlan'] = 'Vlan14'
            data = self.migrate()
            values.append(data['address'])            
            
            return values
            

        if self.args['tipo'] == '2':

            values = [
                self.args['modeloSerial'],
                self.args['deviceIP'],
                self.args['hostName'], 
                self.args['hostName'], 
                self.args['snmpLocation']
            ]
                  
            self.args['vlan'] = 'Vlan80'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])

            
            self.args['vlan'] = 'Vlan12'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan2'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan1'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan74'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan73'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan72'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan71'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan70'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan19'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan18'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan17'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            
            self.args['vlan'] = 'Vlan16'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan15'
            data = self.migrate()
            values.append(data['description'])
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan14'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            
            self.args['vlan'] = 'Vlan13'
            data = self.migrate()
            values.append(data['ip con prefix'])
            values.append(data['shutdown'])
            values.append(data['address'])
            values.append(data['excludedAddress'])
            values.append(data['ip default router'])
            

            values.append(data['nexHopMpls'])
            
            values.append(data['nextHopIfnet'])
            values.append(data['ifInet'])
            values.append(data['ipMaskInet']) 

            values.append(self.args['BWInternet'])
            values.append(self.args['BWInternet'])
                    
            values.append(self.args['autoIfInternet'])
            values.append(data['ifMpls'])


            values.append(data['ipMaskMpls'])
            
            values.append(self.args['BWMpls'])  
            values.append(self.args['BWMpls'])  
            values.append(self.args['BWMpls']) 

            values.append(self.args['autoIfMpls'])            

            values.append(self.args['hostName'])
            values.append(self.args['latitude'])
            values.append(self.args['longitude'])            
            values.append(self.args['deviceIP'])
            values.append(self.args['siteId'])

            
            values.append(data['address'])
            
            self.args['vlan'] = 'Vlan14'
            data = self.migrate()
            values.append(data['address'])
            
            print('***3'*30)
            print()
            print(data)
            
            return values