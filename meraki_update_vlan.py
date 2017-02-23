#!/usr/bin/env python
#########################################################################
# Gregory Camp
# grcamp@cisco.com
# meraki_update_vlan.py
#
# Current Version:
#########################################################################

import requests
import json
import os
import logging

import argparse
import sys
import getpass

# Declare global variables
logger = logging.getLogger(__name__)
baseurl = 'https://dashboard.meraki.com/api/v0/'
headers = ""

def warning(msg):
    logger.warning(msg)


def error(msg):
    logger.error(msg)


def fatal(msg):
    logger.fatal(msg)
    exit(1)

#########################################################################
# Class Organization
#
# Container for networks
#########################################################################
class Organization:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.networks = []

    # Method get_networks
    #
    # Input: None
    # Output: None
    # Parameters: None
    #
    # Return Value: None
    #####################################################################
    def get_networks(self):
        myJson = requests.get(baseurl + "organizations/" + self.id + "/networks", headers=headers).text
        output = json.loads(myJson)

        for d in output:
            myNetwork = Network()
            myNetwork.id = str(d['id'])
            myNetwork.name = str(d['name'])
            myNetwork.type = str(d['type'])
            self.networks.append(myNetwork)

        return None

    # Method get_vlans
    #
    # Input: None
    # Output: None
    # Parameters: None
    #
    # Return Value: None
    #####################################################################
    def get_vlans(self):
        # Obtain vlans for each network
        for network in self.networks:
            if (network.type == "combined") or ("security" in network.type):
                network.get_vlans()

        return None

    # Method to_csv_string
    #
    # Input: None
    # Output: None
    # Parameters: None
    #
    # Return Value: None
    #####################################################################
    def to_csv_string(self):
        # Declare variables
        returnVal = ""

        # Gather csv for each network
        for network in self.networks:
            returnVal = returnVal + network.to_csv_string()

        return returnVal


#########################################################################
# Class Network
#
# Container for networks
#########################################################################
class Network:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.type = ""
        self.vlans = []

    # Method get_vlans
    #
    # Input: None
    # Output: None
    # Parameters: None
    #
    # Return Value: None
    #####################################################################
    def get_vlans(self):
        myJson = requests.get(baseurl + "networks/" + self.id + "/vlans", headers=headers).text
        output = json.loads(myJson)

        for d in output:
            myVlan = Vlan()
            myVlan.id = str(d['id'])
            myVlan.name = str(d['name'])
            myVlan.subnet = str(d['subnet'])
            myVlan.applianceIp = str(d['applianceIp'])
            myVlan.dnsNameservers = str(d['dnsNameservers']).replace(',','|')
            self.vlans.append(myVlan)

        return None

    # Method to_csv_string
    #
    # Input: None
    # Output: None
    # Parameters: None
    #
    # Return Value: None
    #####################################################################
    def to_csv_string(self):
        # Declare variables
        returnVal = ""

        # Gather csv for each network
        for vlan in self.vlans:
            returnVal = returnVal + "%s,%s,%s,%s,%s,%s,%s,%s\n" % (self.name, self.id, self.type, vlan.id, vlan.name,
                                                                 vlan.subnet, vlan.applianceIp, vlan.dnsNameservers)

        return returnVal


#########################################################################
# Class Vlan
#
# Container for networks
#########################################################################
class Vlan:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.subnet = ""
        self.applianceIp = ""
        self.dnsNameservers = ""

# Method get_organization
#
# Input: None
# Output: None
# Parameters: None
#
# Return Value: None
#####################################################################
def get_organization(orgId):
    #
    myJson = requests.get(baseurl + "organizations/" + orgId, headers=headers).text
    output = json.loads(myJson)

    myOrg = Organization()
    myOrg.id = str(output['id'])
    myOrg.name = str(output['name'])

    return myOrg


# Method main
#
# Input: None
# Output: None
# Parameters: None
#
# Return Value: None
#####################################################################
def main(**kwargs):
    # Set logging
    global headers
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format="%(asctime)s [%(levelname)8s]:  %(message)s")

    if kwargs:
        args = kwargs
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('apiKey', help='Meraki API Key')
        parser.add_argument('orgId', help='Meraki Organization Id')
        parser.add_argument('-r', '--readMode', help='Pull Network Data into CSV file', action='store_true')
        parser.add_argument('-u', '--updateMode', help='Update Data from CSV file', action='store_true')
        parser.add_argument('-o', '--outFile', help='Output File')
        args = parser.parse_args()

    # Comment!!!

    headers = {'X-Cisco-Meraki-API-Key': args.apiKey,'Content-Type': 'application/json'}

    myOrg = get_organization(args.orgId)

    if args.readMode:
        myOrg.get_networks()
        myOrg.get_vlans()

        logger.info("Writing file %s" % (args.outFile))
        file = open(args.outFile, 'w')
        file.write("Network Name,Network Id,Network Type,VLAN Id,VLAN Name,Subnet,Appliance IP,DNS\n")
        file.write(myOrg.to_csv_string())
        file.close()
    elif args.updateMode:
        return None

    return None

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print str(e)
        os._exit(1)
