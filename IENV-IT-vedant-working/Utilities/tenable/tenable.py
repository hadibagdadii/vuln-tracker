#!/usr/local/bin/python3

import requests
import argparse
import csv
import getpass
import ipaddress
import json
import os
import smtplib
import ssl
import time
from pprint import pprint

import infoblox_lookup as infoblox
import mynetwork


def parse_config():
  parser = argparse.ArgumentParser(description='This script creates ServiceNow tickets for Tenable vulnerabilities.')
  parser.add_argument('configfile', help='Use the full file path for the JSON config file or move it to the same directory', type=argparse.FileType('r'))

  args = parser.parse_args()

  with args.configfile as file:
    return json.load(file)


def get_all_vlans(username, password):
  #password = getpass.getpass(prompt="Please enter the password to your %s account: " % username)
  print("Gathering VLAN info from InfoBlox...")
  ib = infoblox.InfoBlox(username, password)
  return ib.vlans


def setup_server_connection(sender):
  smtp_server = 'smtp.office365.com'
  port = 25 #25
  #timeout = 3000 #in seconds
  timeout = 10800 #in seconds; increasing to 3 hours as a test
  password = getpass.getpass(prompt="Please enter the password to the %s account: " % sender)
  
  context = ssl.create_default_context() #context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  #print("Setting up connection to Office365...")
  
  try:
    with smtplib.SMTP(smtp_server, port) as server:
      server.starttls(context=context)
      server.login(sender, password)
      return server
  except Exception as e:
    print(e)
    print("Couldn't connect to Office365 account %s" % sender)
    exit()


def get_tenable_vuln_info(pluginid):
  access_key = os.environ["API_KEY_TENABLE_ACCESS_KEY"]
  secret_key = os.environ["API_KEY_TENABLE_SECRET_KEY"]
  
  url = 'https://security-center.ucdavis.edu/rest/plugin/' + pluginid
  apikey_string = 'accesskey=' + access_key + '; secretkey=' + secret_key + ';'
  headers = { 'x-apikey' : apikey_string }
  
  try:
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    data = r.json()
    return data
  except Exception as e:
    print(e)
    print("Something failed with the get request to Tenable for plugin ID %s" % pluginid)
    exit()


def get_ad_computer_info(hostname):
  coe_it_key = os.environ["API_KEY_COEITADMIN_TOOLS"]

  url = 'https://coeitadmin.engr.ucdavis.edu/api/ucomputer/' + hostname
  headers = { 'coe-api-key' : coe_it_key }

  try:
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    data = r.json()
    return data
  except Exception as e:
    print(e)
    print("Something failed with the get request to coeitadmin tools for computer with hostname %s" % hostname)
    exit()


def get_ucdnetwork_info(ip):
  ucdnetwork_key = os.environ["API_KEY_UCDNETWORK"]
  
  url = 'https://ucdnetwork.engr.ucdavis.edu/devices?ip=' + ip
  headers = { 'accept' : 'application/json' , 'X-APIf-KEY' : ucdnetwork_key }

  try:
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    data = r.json()
    return data
  except Exception as e:
    print(e)
    print("Something failed with the get request to ucdnetwork for computer info for ip %s" % ip)
    exit()


def generate_email_body(asset, vlan_name, signature):
  vuln_links = []
  
  for plugin_id in set(asset['Plugin IDs']):
    #data = get_tenable_vuln_info(plugin_id)
    #vuln_name = data['response']['name']
    vuln_name = ""
    vuln_links.append("<a href=\"https://www.tenable.com/plugins/nessus/" + str(plugin_id) + "\">" + vuln_name + "</a> (Plugin ID: " + str(plugin_id) + ")")
  
  if asset["NetBIOS"]:
    hostname = asset["NetBIOS"].split("\\")[1]
  else:
    hostname = ""
  '''
  if hostname:
    coeitadmin_data = get_ad_computer_info(hostname)
    if coeitadmin_data:
      coeitadmin_os = coeitadmin_data.get("os")
      coeitadmin_dn = coeitadmin_data.get("dn")
    else:
      coeitadmin_os = 'No record in Active Directory/coeitadmin'
      coeitadmin_dn = 'No record in Active Directory/coeitadmin'
  else:
    coeitadmin_os = 'No hostname specified'
    coeitadmin_dn = 'No hostname specified'

  ucdnetwork_data = get_ucdnetwork_info(asset['IP'])
  
  print(ucdnetwork_data)
  if ucdnetwork_data:
    ucdn_name = ucdnetwork_data[0].get("name")
    print("hostname" + ucdn_name)
    if ucdnetwork_data[0].get("building"): #accounting for a possible None type
      ucdn_location = ucdnetwork_data[0].get("building") + " " + ucdnetwork_data[0].get("room")
    else:
      ucdn_location = ""
    print("location" + ucdn_location)
    ucdn_mac = ucdnetwork_data[0].get("mac")
    print("mac " + ucdn_mac)
    if ucdnetwork_data[0].get("last_seen"):
      ucdn_last_seen = ucdnetwork_data[0].get("last_seen")
    else:
      ucdn_last_seen = ""
    print("last seen " + ucdn_last_seen)
    ucdn_comment = ucdnetwork_data[0].get("comment")
    print("comment" + ucdn_comment)
  else:
    ucdn_name = 'No record in ucdnetwork'
    ucdn_location = 'No record in ucdnetwork'
    ucdn_mac = 'No record in ucdnetwork'
    ucdn_last_seen = 'No record in ucdnetwork'
    ucdn_comment = 'No record in ucdnetwork'
'''  
  email_body_pre_vlan = "[code]System " + asset['IP'] + " needs to be upgraded or the impacted service removed from the network. It is running an exploitable service and is in violation of UC Davis network policy.<br><br>Please note that COE practice is remediation of critical and high vulnerabilities such as these within 14 days. If you have determined that one or more of the listed vulnerabilities are false positives, please respond to this incident with the specific plugin ID/IP address of each of the false positives along with an explanation of why they are false positives.<br><br>If you need to obtain an exception for a particular vulnerability or device, please follow the Cyber-Safety Exception process outlined at <a href=\"http://kb.ucdavis.edu/?id=0700\">http://kb.ucdavis.edu/?id=0700</a>.<br><br><b><u>Please answer the following questions before closing this ticket:</b></u><ol><li>Does COE IT administrate this system? Who is the primary contact for this system?</li><li>Please have the owner of this system fill out a <a href=\"https://servicehub.ucdavis.edu/servicehub?id=ucd_cat_item&sys_id=945a503c13bd77009c41bb722244b083\">Network Registration form</a> to determine if there is <a href=\"https://kb.ucdavis.edu/?id=6684\">PII</a> or sensitive data on this system as well as the types of data present. If you have questions about data protection levels, please consult <a href=\"https://security.ucop.edu/files/documents/uc-protection-level-classification-guide.pdf\">UCOP's guide on the subject</a>.</li></ol><b><u>Host Information</b></u><br>IP Address: " + asset['IP']
  
  if vlan_name:
    email_body_vlan = "<br>VLAN: " + vlan_name
  else:
    email_body_vlan = ""

  email_body_post_vlan = "<br>NetBIOS Name: " + asset['NetBIOS'] + "<br>DNS: " + asset['DNS'] + "<br>MAC Address: " + asset['MAC'] + "<br><br><b><u>Vulnerabilities</b></u><br>"
  
  separator = "<br>"
  email_body_vuln_links = "" + separator.join(vuln_links) + "[/code]"

  email_body = email_body_pre_vlan + email_body_vlan + email_body_post_vlan + email_body_vuln_links + "[code]<br><br>Thank you,<br>[/code]" + signature
  return email_body


def send_email(ip, sender, receiver, message, server):
  try:
    server.sendmail(sender, receiver, message)
  except Exception as e:
    print(e)
    print("Couldn't send email for asset IP: " % ip)


def main():
  config_data = parse_config()
  username = config_data['kerberosID']
  sender = config_data['sender']
  receiver = config_data['receiver']
  signature = config_data['signature']
  vuln_filename = config_data['csv_file']
  #vuln_folder = config_data['folder']
  '''internet_exposed_ips_filename = config_data['internet_exposed_ips']
  
  internet_exposed_ips = []
  
  with open(internet_exposed_ips_filename, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
      internet_exposed_ips = row #file is a list of comma separated ips so row is a list
  '''
  ticket_ips = []
  
  with open("./ticket_ips.txt", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
      ticket_ips = row #file is a list of comma separated ips so row is a list
  
  vlans = None
  password = "" #default, if username not provided, remains empty
  ''''if username.strip():  # if a Kerberos ID with InfoBlox API Access is provided
    try:
      password = getpass.getpass(prompt="Please enter the password to your %s account: " % username)
      vlans = get_all_vlans(username, password)
    except Exception as e:
      print(e)
      print("Couldn't get VLAN information")
      exit()'''
  
  assets = {}
  MyNetwork_data = None
  if password:
    #added for location data
    MyNetwork_data = mynetwork.MyNetwork(username, password, 'testing')
  
  with open(vuln_filename, 'r') as file:
    csv_reader2 = csv.DictReader(file)
    
    for row in csv_reader2:
      ip = row['IP Address']
      if ip in assets.keys():
        assets[ip]['Plugin IDs'].append(row['Plugin'])
      else:
        assets.update({ip : {}})
        assets[ip]['IP'] = ip
        assets[ip]['NetBIOS'] = row['NetBIOS Name']
        assets[ip]['DNS'] = row['DNS Name']
        assets[ip]['MAC'] = row['MAC Address']
        ############################ test ############################################################################
        #assets[ip]['Email Subject'] = "Test " + ip + " (" + assets[ip]['DNS'] + ") - Vulnerability List"
        assets[ip]['Email Subject'] = ip + " (" + assets[ip]['DNS'] + ") - Vulnerability List"
        assets[ip]['Plugin IDs'] = [ row['Plugin'] ]
        '''   if assets[ip]["IP"] in internet_exposed_ips:
            assets[ip]['Internet Exposed'] = "Yes"
          else:
            assets[ip]['Internet Exposed'] = "No"
        '''
  count = 0 #server connection
  emails_sent = 0 #number of emails sent
  vlan_name = ""
  
  for ip in assets.keys():
    vlan_cs = "ENG-CMPR-SCI-7" #to fix error/value doesn't matter hopefully?
    '''if vlans:
      for key in vlans.keys():
        if (ipaddress.ip_address(ip) in ipaddress.ip_network(key)):
          vlan_name = vlans[key]
          vlan_cs = vlans[key]
        if ((ipaddress.ip_address(ip) in ipaddress.ip_network('169.237.4.0/24')) or (ipaddress.ip_address(ip) in ipaddress.ip_network('169.237.10.0/24')) or (ipaddress.ip_address(ip) in ipaddress.ip_network('169.237.6.0/24')) or (ipaddress.ip_address(ip) in ipaddress.ip_network('169.237.7.0/24'))):
          vlan_cs = "ENG-CMPR-SCI-7"
    else:
      vlan_name = ""  '''
    
    ### start location code ###
    if password:
      assets[ip]['Location'] = "Unknown"
      for item in MyNetwork_data.get_active_macs(vlan_cs):
        if item['mac'] == assets[ip]['MAC']:
          assets[ip]['Location'] = item['building'] + " " + item['room']
          break
    
    ### end location code ###
    
    message = "From: %s\r\n" % sender \
                + "To: %s\r\n" % receiver \
                + "Subject: %s\r\n" % assets[ip]['Email Subject'] \
                + "\r\n" \
                + generate_email_body(assets[ip], vlan_name, signature)
    
    if ip not in ticket_ips: # ticket ips should hold list of ips that already have tickets created for them?
      if count == 0:
        server = setup_server_connection(sender)
        count = count + 1
      print(message)
      send_email(assets[ip], sender, receiver, message, server)
      emails_sent = emails_sent + 1
      time.sleep(3) #send an email every 3 seconds; 20 emails per minute which is less than the 30 message per minute message rate limit
    else:
      print("Ticket already opened for %s" %assets[ip]['IP'])
    
    if count == 0:
        server = setup_server_connection(sender)
        count = count + 1
    
    #TODO: test how to fix server connection to send email, for now just printing in terminal
    print(message)
    #send_email(assets[ip], sender, receiver, message, server)
    emails_sent = emails_sent + 1
    time.sleep(3) #send an email every 3 seconds; 20 emails per minute which is less than the 30 message per minute message rate limit
  print("%s email(s) sent. Exiting..." %emails_sent)
  server.quit()
  

if __name__ == "__main__":
  main()

'''
Notes: missing files: 
/Users/shchee/GitHubStuff/coe_tenable_security_vulnerability_tracker/ticket_ips.txt"
internet_exposed_ips_filename = config_data['internet_exposed_ips']
basically ticket_ips is a text file with a list of ips that already have tickets created?
  - should probably need to test, otherwise will have duplicate tickets
internet_exposed_ips is a list of ips that have been exposed on the internet (I don't know how to get this)
  - not necessary to test the program

  to run: .\.venv\Scripts\python.exe .\tenable.py .\config.json
  going to remove internet exposed ips from the config data json 

  updated certifi from 2022.09.24 to 2022.12.07 as dependabot suggested
'''
