#!/usr/local/bin/python3

import argparse
#import requests
import csv
import getpass
import ipaddress
import json
import os
import smtplib
import ssl
import time
from pprint import pprint
import pathlib

# import infoblox_lookup as infoblox
# import mynetwork


def parse_config():
  parser = argparse.ArgumentParser(description='This script creates ServiceNow tickets for Tenable vulnerabilities.')
  parser.add_argument('configfile', help='Use the full file path for the JSON config file or move it to the same directory', type=argparse.FileType('r'))
  parser.add_argument('--send-emails', action='store_true', help='Flag to send emails')

  args = parser.parse_args()

  with args.configfile as file:
    return json.load(file), args.send_emails


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
  
  # for plugin_id,  in set(asset['Plugin IDs']):
  for plugin_id, severity, name in zip(asset['Plugin IDs'], asset['Severities'], asset['Plugin Names']):
    #data = get_tenable_vuln_info(plugin_id)
    #vuln_name = data['response']['name']
    vuln_name = ""
    # vuln_link = "https://www.tenable.com/plugins/nessus/" + str(plugin_id) + "" + vuln_name + " (Plugin ID: " + str(plugin_id) + ")"
    
    vuln_link = f'[code]<a href="https://www.tenable.com/plugins/nessus/{plugin_id}" target="_blank">{name}</a>[/code] \n PLugin ID: {plugin_id} \n Severity: {severity}\n' 
    vuln_links.append(vuln_link)

  if asset["NetBIOS"]:
    hostname = asset["NetBIOS"].split("\\")[1]
  else:
    hostname = ""

  email_body_pre_vlan =  "" # "System " + asset['IP'] + " needs to be upgraded or the impacted service removed from the network. It is running an exploitable service and is in violation of UC Davis network policy.\nPlease note that COE practice is remediation of critical and high vulnerabilities such as these within 14 days. If you have determined that one or more of the listed vulnerabilities are false positives, please respond to this incident with the specific plugin ID/IP address of each of the false positives along with an explanation of why they are false positives.\n\nIf you need to obtain an exception for a particular vulnerability or device, please follow the Cyber-Safety Exception process outlined at <a href=\"http://kb.ucdavis.edu/?id=0700\">http://kb.ucdavis.edu/?id=0700</a>.\n\n<b><u>Please answer the following questions before closing this ticket:</b></u><ol><li>Does COE IT administrate this system? Who is the primary contact for this system?</li><li>Please have the owner of this system fill out a <a href=\"https://servicehub.ucdavis.edu/servicehub?id=ucd_cat_item&sys_id=945a503c13bd77009c41bb722244b083\">Network Registration form</a> to determine if there is <a href=\"https://kb.ucdavis.edu/?id=6684\">PII</a> or sensitive data on this system as well as the types of data present. If you have questions about data protection levels, please consult <a href=\"https://security.ucop.edu/files/documents/uc-protection-level-classification-guide.pdf\">UCOP's guide on the subject</a>.</li></ol><b><u>Host Information\nIP Address: " + asset['IP']
  
  if vlan_name:
    email_body_vlan = "\nVLAN: " + vlan_name
  else:
    email_body_vlan = ""

  email_body_post_vlan = "NetBIOS Name: " + asset['NetBIOS'] + "\nDNS: " + asset['DNS'] + "\nMAC Address: " + asset['MAC'] + "\n\nVulnerabilities:\n"
  
  separator = "\n"
  email_body_vuln_links = "" + separator.join(vuln_links) + ""


  # [code]<b class="term">Host Information</b>[/code]
  email_body = f"""
  [code]<pre><code>
  IP Address:\t{asset["IP"]} <br>
  NetBIOS Name:\t{asset["NetBIOS"]} <br>
  DNS:\t{asset["DNS"]} <br>
  MAC Address:\t{asset["MAC"]} <br>
  </code></pre>[/code]

  [code]<b class="term">Vulnerabilities:</b>[/code]
  """ + '\n'.join(vuln_links)

  # email_body = email_body_pre_vlan + email_body_vlan + email_body_post_vlan + email_body_vuln_links
  return email_body


def send_email(ip, sender, receiver, message, server):
  try:
    server.sendmail(sender, receiver, message)
  except Exception as e:
    print(e)
    print("Couldn't send email for asset IP: " % ip)


#Necessary imports for sending emails
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

#Function for sending emails with attachments
def send_email_with_attachments(sender_email, password, receiver_email, subject, body):
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    port = 587
    username = sender_email
    password = password

    # Establish connection with SMTP server
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(username, password)

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        print(body)
        # Attach body as email text
        msg.attach(MIMEText(body, 'plain'))

        # Send the email with file contents in the body
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print('Email sent successfully!')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()

def main():
  config_data, send_emails = parse_config()
  username = config_data['kerberosID']
  sender = config_data['sender']
  password = config_data['password']
  receiver = config_data['receiver']
  signature = config_data['signature']
  vuln_filename = config_data['csv_file']
  vuln_folder = config_data['folder']

  # Extracting the CSV file name without the extension
  csv_file_name = os.path.splitext(os.path.basename(vuln_filename))[0] + '/'

  # Assigning the CSV file name to the output folder
  output_folder = os.path.join(vuln_folder, csv_file_name)

  # Create the output folder if it doesn't exist
  os.makedirs(output_folder, exist_ok=True)

  ticket_ips = []
  
  with open("./ticket_ips.txt", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
      ticket_ips = row #file is a list of comma separated ips so row is a list
  
  vlans = None
  # password = "" #default, if username not provided, remains empty
  
  assets = {}
  # MyNetwork_data = None
  # if password:
  #   #added for location data
  #   MyNetwork_data = mynetwork.MyNetwork(username, password, 'testing')
  
  with open(vuln_filename, 'r') as file:
    csv_reader2 = csv.DictReader(file)
    
    for row in csv_reader2:
      ip = row['IP Address']
      # print("This is the IP of the vuln computer: ", ip, "\n")
      if ip in assets.keys():
        assets[ip]['Plugin IDs'].append(row['Plugin'])
        assets[ip]['Severities'].append(row['Severity'])
      else:
        assets.update({ip : {}})
        assets[ip]['IP'] = ip
        assets[ip]['NetBIOS'] = row['NetBIOS Name']
        assets[ip]['DNS'] = row['DNS Name']
        assets[ip]['MAC'] = row['MAC Address']
        # assets[ip]['Email Subject'] = ip + " (" + assets[ip]['NetBIOS'] + ") - Vulnerability List"
        assets[ip]['Email Subject'] = ip + " (" + assets[ip]['NetBIOS'].split('\\')[-1] + ") - Vulnerability List"
        assets[ip]['Plugin IDs'] = [ row['Plugin'] ]
        assets[ip]['Severities'] = [ row['Severity'] ]
        assets[ip]['Plugin Names'] = [ row['Plugin Name'] ]

  count = 0 #server connection
  emails_sent = 0 #number of emails sent
  vlan_name = ""
  
  for ip in assets.keys():
    vlan_cs = "ENG-CMPR-SCI-7" #to fix error/value doesn't matter hopefully?
    
    ### start location code ###
    # if password:
    #   assets[ip]['Location'] = "Unknown"
    #   for item in MyNetwork_data.get_active_macs(vlan_cs):
    #     if item['mac'] == assets[ip]['MAC']:
    #       assets[ip]['Location'] = item['building'] + " " + item['room']
    #       break
    
    ### end location code ###

    ## Checking if output files already exists
    output_file_path = os.path.join(output_folder, assets[ip]['DNS'])
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as f:
            message = f.read()
    else:
        message = "HOST INFORMATION: \n" + "%s\r\n" % assets[ip]['Email Subject'] \
                  + generate_email_body(assets[ip], vlan_name, signature)
        # Write the message to the output file
        with open(output_file_path, 'w') as f:
            f.write(message)

    # Send the email using either the existing or newly created output file
    subject = assets[ip]['Email Subject']
    if send_emails:
        send_email_with_attachments(sender, password, receiver, subject, message)

    emails_sent = emails_sent + 1
    print("%s files created. Exiting..." % emails_sent)




  #   message = "HOST INFORMATION: \n" + "%s\r\n" % assets[ip]['Email Subject'] \
  #               + generate_email_body(assets[ip], vlan_name, signature)
  #   #TODO: test how to fix server connection to send email, for now just printing in terminal
  #   print(message)
  #   # print(output_folder)
  #   with open(os.path.join(output_folder) + assets[ip]['DNS'], 'w') as f:
  #     f.write(message)
  #   #send_email(assets[ip], sender, receiver, message, server)
  #   subject = assets[ip]['Email Subject']
  #   if send_emails:
  #     send_email_with_attachments(sender, password, receiver, subject, message)
  #   emails_sent = emails_sent + 1
  # print("%s files created. Exiting..." % emails_sent)

  
  # coe_body = """
  # The following system needs to be upgraded or the impacted service removed from the network. The list of vulnerabilities below will indicate if it is exploitable. \
  # If it is running an exploitable service, it is in violation of UC Davis network policy.

  # Please note that COE practice is remediation of critical and high vulnerabilities such as these within 14 days. \
  # If you have determined that one or more of the listed vulnerabilities are false positives, please respond to this incident with the specific plugin ID/IP address \
  # of each of the false positives along with an explanation of why they are false positives.

  # If you need to obtain an exception for a particular vulnerability or device, please follow the Cyber-Safety Exception process outlined at http://kb.ucdavis.edu/?id=0700.

  # Please answer the following questions before closing this ticket:
  #   1. Does COE IT administrate this system? Who is the primary contact for this system?
  #   2. Please have the owner of this system fill out a Network Registration form to determine if there is PII or sensitive data on this system as well as the types \
  #      of data present. If you have questions about data protection levels, please consult the UC Protection Level Classification Guide.

  # HOST INFORMATION:

  # """

  # body_html = """
  # <html>
  #   <head></head>
  #   <body>
  #     <p>The following system needs to be upgraded or the impacted service removed from the network. 
  #       The list of vulnerabilities below will indicate if it is exploitable. If it is running an exploitable service, it is in violation of UC Davis network policy. <br><br>
        
  #       Please note that COE practice is remediation of critical and high vulnerabilities such as these within 14 days. If you have determined that one or more of the listed vulnerabilities are false positives, please respond to this incident with the specific plugin ID/IP address of each of the false positives along with an explanation of why they are false positives. <br><br> 
        
  #       If you need to obtain an exception for a particular vulnerability or device, please follow the Cyber-Safety Exception process outlined at <a href="http://kb.ucdavis.edu/?id=0700">http://kb.ucdavis.edu/?id=0700</a>. <br><br> 

  #       Please answer the following questions before closing this ticket: <br>
  #       &emsp 1. Does COE IT administrate this system? Who is the primary contact for this system? <br> 
  #       &emsp 2. Please have the owner of this system fill out a <a href="https://servicehub.ucdavis.edu/servicehub?id=ucd_cat_item&sys_id=945a503c13bd77009c41bb722244b083">Network Registration form</a> to determine if there is <a href="https://kb.ucdavis.edu/?id=6684">PII</a> or sensitive data on this system as well as the types of data present. If you have questions about data protection levels, please consult the <a href="https://security.ucop.edu/files/documents/uc-protection-level-classification-guide.pdf">UC Protection Level Classification Guide</a>. <br><br> 

  #       HOST INFORMATON <br><br>
  #     </p>
  #   </body>
  # </html>
  # """

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

  modified script to store vulns into a separate file per IP into a specified folder as defined by user
'''