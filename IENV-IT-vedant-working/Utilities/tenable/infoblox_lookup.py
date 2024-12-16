#!/usr/bin/python3

import urllib3.json
import requests 
import sys
import getpass
import argparse

class InfoBlox:
    def __init__(self, username, password):
        urllib3.disable_warnings()
        self.vlans = {}
        self.username = username
        self.password = password
        self.gather_vlans()

    def restart_services(self):
        try:
            updateurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/member/b25lLnZpcnR1YWxfbm9kZSQw:ib-ns.ucdavis.edu"
            response = requests.post(updateurl, data={'_function': 'restartservices','restart_option':'RESTART_IF_NEEDED','service_option':'DHCP'}, verify=False, auth=(self.username,self.password))
            if response.status_code == 200:
                print("Restarted InfoBlox")
            else:
                print("Failed to restart InfoBlox service, please restart manually to apply changes")

        except Exception as e:
            print("Error parsing json in restart_services()")
            print(e)
            print(response.content)

    def gather_vlans(self):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/network?_return_type=json-pretty&_return_fields=comment,network"
        response = requests.get(searchurl, verify=False, auth=(self.username,self.password))
        networks = {}
        try:
            data = json.loads(response.content)
            for x in data:
                networks[x["network"]] = x["comment"]
            self.vlans = networks
    
        except Exception as e:
            print("Error parsing json in gather_vlans()")
            print(e)
            print(response.content)
    
    def obj_lookup(self, obj):
        action = obj.split('/', 1)[0]
        ip = (obj.split(':', 1)[1]).split('/', 1)[0]
        searchurl = ""
        if action == "fixedaddress":
            searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/fixedaddress?ipv4addr="+ip+"&_return_type=json-pretty&_return_fields=comment,ipv4addr,mac,name,network,match_client"
        elif action == "lease":
            searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/lease?address="+ip+"&_return_type=json-pretty&_return_fields=address,client_hostname,hardware,network"
        else:
            print("object not found")
    
        response = requests.get(searchurl, verify=False, auth=(self.username,self.password))
        try:
            data = json.loads(response.content)[0]
            # empty dicts evaluate to false
            if not self.vlans:
                self.gather_vlans()

            data["vlan"] = self.vlans[data["network"]]
            if (data["_ref"].split('/', 1)[0]) == "fixedaddress":
                data["type"] = "Fixed Address"
            elif (data["_ref"].split('/', 1)[0]) == "lease":
                data["type"] = "Active lease"
            # delete _ref key that it comes with, don't fail if doesn't exist
            a = data.pop('_ref', None)
            data['_ref'] = a
            return data
        except Exception as e:
            print("Error parsing json in obj_lookup() with lease")
            print(e)
            print(response.content)

    def find_all(self, network, match_type):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/fixedaddress?network="+network+"&_return_fields=comment,ipv4addr,mac,name,network,match_client&_return_type=json-pretty"

        if match_type == "reserved":
            searchurl += "&match_client=RESERVED"
        elif match_type == "MAC_ADDRESS":
            searchurl += "&match_client=MAC_ADDRESS"
        else:
            pass

        response = requests.get(searchurl, verify=False, auth=(self.username, self.password))
        try:
            raw_data=json.loads(response.content)
            if len(raw_data) == 0:
                print('Nothing returned for vlan: ' + network)
                return raw_data
            else:
                return raw_data
        except Exception as e:
            print("Error parsing json in ip_lookup():")
            print(e)
            print(raw_data)
     
    def ip_lookup(self, ip):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/ipv4address?ip_address="+ip+'&_return_type=json-pretty&_return_fields=lease_state,objects,status,ip_address,network'
        
        response = requests.get(searchurl, verify=False, auth=(self.username, self.password))
        try:
            raw_data=json.loads(response.content)
            if len(raw_data) == 0:
                print ('Nothing returned')
            else:
                objects = raw_data[0]["objects"]
                return [self.obj_lookup(x) for x in objects]
        except Exception as e:
            print("Error parsing json in ip_lookup():")
            print(e)
            print(raw_data)
    
    def mac_lookup(self, mac):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/search?"+"mac_address="+mac+'&_return_type=json-pretty&_return_fields=address,fqdn,mac_address,objtype,network'
        response = requests.get(searchurl, verify=False, auth=(self.username, self.password))
        try:
            raw_data=json.loads(response.content)
            if len(raw_data) == 0:
                print ('Nothing returned')
            else:
                objects = [ x["_ref"] for x in raw_data ] 
                return [self.obj_lookup(x) for x in objects]
        except Exception as e:
            print("Error parsing json in mac_lookup():")
            print(e)
            print(raw_data)

    def reserve_ip(self, ip):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/fixedaddress?ipv4addr=" + ip + "&_return_type=json-pretty&_return_fields=comment,ipv4addr,mac,name,network,match_client"
        response = requests.get(searchurl, verify=False, auth=(self.username, self.password))

        try: 
            raw_data=json.loads(response.content)
            if len(raw_data) == 0:
                print('Nothing returned')
                print('needs to create reserved ip')
            else:
                objects = [ x["_ref"] for x in raw_data ]
                a = [self.obj_lookup(x) for x in objects]
                if a[0]['match_client'] == 'MAC_ADDRESS':
                    obj_ref = a[0]['_ref']
                    updateurl = 'https://infoblox.ucdavis.edu/wapi/v2.7.1/' + obj_ref
                    response = requests.put(updateurl, data={'match_client':'RESERVED', 'name':'', 'comment':''},verify=False, auth=(self.username, self.password))
                    if response.status_code == 200:
                        print("Reserved ip")
                        self.restart_services()
                    else:
                        return [response.status_code, response.text]
                elif a[0]['match_client'] == 'RESERVED':
                    print("ip already reserved")
                else:
                    print("ip not in a registered state to reserve")
                    print(a)

        except Exception as e:
            print("Error parsing json in reserve_ip():")
            print(e)
            print(raw_data)

    def register_ip(self, ip, mac, name, comment):
        searchurl = "https://infoblox.ucdavis.edu/wapi/v2.7.1/fixedaddress?ipv4addr=" + ip + "&_return_type=json-pretty&_return_fields=comment,ipv4addr,mac,name,network,match_client"
        response = requests.get(searchurl, verify=False, auth=(self.username, self.password))

        try: 
            raw_data=json.loads(response.content)
            if len(raw_data) == 0:
                print('Nothing returned')
                print('needs to create reserved ip')
            else:
                objects = [ x["_ref"] for x in raw_data ]
                a = [self.obj_lookup(x) for x in objects]
                if a[0]['match_client'] == 'RESERVED':
                    obj_ref = a[0]['_ref']
                    updateurl = 'https://infoblox.ucdavis.edu/wapi/v2.7.1/' + obj_ref
                    response = requests.put(updateurl, data={'match_client':'MAC_ADDRESS','mac':mac,'comment':comment,'name':name},verify=False,auth=(self.username,self.password))
                    if response.status_code == 200:
                        print("Registered ip")
                        self.restart_services()
                    else:
                        return [response.status_code, response.text]
                elif a[0]['match_client'] == 'MAC_ADDRESS':
                    print("ip already registered")
                    print(a[0])
                else:
                    print("IP not in a reserved state to register")
                    print(a)
        except Exception as e:
            print("Error parsing json in regester_ip():")
            print(e)
            print(raw_data)
