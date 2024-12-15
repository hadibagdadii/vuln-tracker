#! /usr/bin/python3

import ipaddress
import csv

import logging
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urlencode
from selenium.common.exceptions import TimeoutException

from duo import MyNetworkDuoLogin


class Error(Exception):
    """Base class for exceptions in this module. """

    pass


class AuthenticationError(Error):
    """Raise when cookies invalid. """

    pass


class MissingDataError(Error):
    """Raise when data missing. """

    pass


class MyNetwork:
    def __init__(self, username, password, environment="production"):
        urllib3.disable_warnings()
        self.base_url = "https://mynetwork.noc.ucdavis.edu/cgi-bin/netadmin.pl"
        self.username = username
        self.password = password
        self.selenium = None
        self.environment = environment
        self.authenticate()
        self.vlans = self.gather_vlans()

    def refresh(self):
        if not self.check_session():
            logging.info("check_session failed, re-authentication with MyNetwork")
            try:
                self.selenium.login(self.username, self.password)
            except Exception:
                raise AuthenticationError("Relogin failed")

    def check_session(self):
        resp = self.selenium.get(self.base_url)
        soup = BeautifulSoup(resp, "html.parser")
        confirmation = soup.title.text

        if confirmation == " VLAN SUMMARY ":
            return True

        logging.debug("ALERT")
        logging.debug(soup)
        logging.debug(soup.title.text)
        return False

    def authenticate(self):
        try:
            self.selenium = MyNetworkDuoLogin(
                self.username, self.password, self.environment
            )
        except TimeoutException:
            raise AuthenticationError("Duo prompt not accepted")
        if not self.check_session():
            raise AuthenticationError("Authentication failed")

    def gather_vlans(self):
        resp = self.selenium.get(self.base_url)
        soup = BeautifulSoup(resp, "html.parser")
        title = soup.title.text
        if title != " VLAN SUMMARY ":
            raise AuthenticationError(
                "gather_vlans() page title not 'VLAN SUMMARY', likely to be an authentication issue"
            )

        raw_vlans_info = soup.find_all("pre")
        # format of start, end, gateway, mask
        vlans = []
        for vlan_info in raw_vlans_info:
            # in format of first, last, gateway, netmask
            subnet_info = (
                vlan_info.contents[0].split("Subnet Mask\n")[1].split("\n")[0].split()
            )
            vlan_arr = vlan_info.contents[0].split("Tag\n")[1].split("____")[0].split()

            subnet = ""
            try:
                subnet = ipaddress.IPv4Network((subnet_info[0], subnet_info[3]), False)
            except Exception:
                subnet = ""


            vlan_tag = vlan_arr[1] if len(vlan_arr) == 2 else ''
            vlan = {"name": vlan_arr[0], "tag": vlan_tag, "subnet": str(subnet)}
            vlans.append(vlan)

        return vlans

    def get_standard_building_names(self):
        filename = "Buildings.csv"
        custom_buildings = "CustomBuildings.csv"
        buildings = []
        with open(filename) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                buildings.append(
                    {"FDX Code": row["FDX Code"], "Building Name": row["Building Name"]}
                )
        with open(custom_buildings) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=",")
            for row in csv_reader:
                buildings.append(
                    {"FDX Code": row["FDX Code"], "Building Name": row["Building Name"]}
                )
        return buildings

    # vlan in the form of ENG-CIVL&ENV-1
    def get_active_macs(self, vlan):
        # https://mynetwork.noc.ucdavis.edu/cgi-bin/netadmin.pl?maclist=ENG-CIVL%26ENV-1&period=Month
        buildings = self.get_standard_building_names()
        macs = []
        payload = {"maclist": vlan, "period": "Month"}
        qstr = urlencode(payload)
        resp = self.selenium.get(self.base_url + "?" + qstr)
        soup = BeautifulSoup(resp, "lxml")
        rows = soup.find_all("tr", {"valign": "center"})
        for row in rows:
            data = {}
            cells = row.find_all("td")
            building = cells[1].text.strip()
            proper_building_name = next(
                (
                    item["Building Name"]
                    for item in buildings
                    if item["FDX Code"] == building
                ),
                building,
            )
            data["nam"] = cells[0].text.strip()
            data["building"] = proper_building_name
            data["room"] = cells[2].text.strip()
            data["switch"] = cells[3].text.strip()
            data["port"] = cells[4].text.strip()
            data["mac"] = cells[5].text.strip()
            data["last_seen"] = cells[6].text.strip()
            macs.append(data)

        return macs

    # vlan in the form of ENG-CIVL&ENV-1
    def get_nams(self, vlan):
        # https://mynetwork.noc.ucdavis.edu/cgi-bin/netadmin.pl?span=ENG-CIVL%26ENV-1

        buildings = self.get_standard_building_names()
        nams = []
        payload = {"span": vlan}
        qstr = urlencode(payload)
        resp = self.selenium.get(self.base_url + "?" + qstr)
        soup = BeautifulSoup(resp, "lxml")
        rows = soup.find_all("tr", {"valign": "center"})
        for row in rows:
            data = {}
            cells = row.find_all("td")

            building = cells[1].text.strip()
            proper_building_name = next(
                (
                    item["Building Name"]
                    for item in buildings
                    if item["FDX Code"] == building
                ),
                building,
            )
            data["nam"] = cells[0].text.strip()
            data["building"] = proper_building_name
            data["room"] = cells[2].text.strip()
            data["switch"] = cells[3].text.strip()
            data["port"] = cells[4].text.strip()
            data["port_state"] = cells[5].text.strip()
            data["configured_speed"] = cells[6].text.strip()
            data["actual_speed"] = cells[7].text.strip()
            nams.append(data)

        return nams
