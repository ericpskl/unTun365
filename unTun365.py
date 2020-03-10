#!/usr/bin/python3
#
# unTun365 -- Builds an OpenVPN-compatible server config file to prevent clients from tunneling their Office 365 Traffic
#
# v0.1: 10 March 2020.  Only exports IPv4 subnets to the config file
#
# (c) 2020 FireOak Strategies, LLC
#          https://fireoakstrategies.com 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import uuid

# Your Office 365 tenant name
tenant='fireoak365'

# Where to write the config file - we recommend dropping the file into the "client-config-dir" specified by your openVPN config file
# Naming this file "DEFAULT" will cause the configurations to be applied to all clients that do not otherwise have a specific config file

ovpnConfigFile="/etc/openvpn/ccd/DEFAULT"

# Microsoft's API endpoint.  Note that you need a UUID (any random UUID will do) to use this service
url = "https://endpoints.office.com/endpoints/worldwide?clientRequestId=" + str(uuid.uuid4()) + "&TenantName=" + tenant

try:
	data=requests.get(url)
	if data.status_code == 200:
		print("Endpoint data downloaded OK")

		configFile=""
		subnets=0

		for service in data.json():
			if 'ips' in service.keys():
				for ip in service['ips']:
					# Check for IPv4
					if "." in ip:
						configFile += 'push "route '+ ip + ' net_gateway"' + "\n"
						subnets += 1

		# OpenVPN clients do not understand CIDR notation (tested under Windows 10, at least), so we have to change the netblocks 
		# received from Microsoft into subnet masks.  The following approach is faster/lazier than doing the conversions back and forth 
		# from string to binary to do the actual math

		cidr2mask = {}

		cidr2mask['/32'] = " 255.255.255.255"
		cidr2mask['/31'] = " 255.255.254.254"
		cidr2mask['/30'] = " 255.255.252.252"
		cidr2mask['/29'] = " 255.255.248.248"
		cidr2mask['/28'] = " 255.255.240.240"
		cidr2mask['/27'] = " 255.255.224.224"
		cidr2mask['/26'] = " 255.255.192.192"
		cidr2mask['/25'] = " 255.255.128.128"

		cidr2mask['/24'] = " 255.255.255.0"
		cidr2mask['/23'] = " 255.255.254.0"
		cidr2mask['/22'] = " 255.255.252.0"
		cidr2mask['/21'] = " 255.255.248.0"
		cidr2mask['/20'] = " 255.255.240.0"
		cidr2mask['/19'] = " 255.255.224.0"
		cidr2mask['/18'] = " 255.255.192.0"
		cidr2mask['/17'] = " 255.255.128.0"

		cidr2mask['/16'] = " 255.255.0.0"
		cidr2mask['/15'] = " 255.254.0.0"
		cidr2mask['/14'] = " 255.252.0.0"
		cidr2mask['/13'] = " 255.248.0.0"
		cidr2mask['/12'] = " 255.240.0.0"
		cidr2mask['/11'] = " 255.224.0.0"
		cidr2mask['/10'] = " 255.192.0.0"
		cidr2mask['/9']  = " 255.128.0.0"
		cidr2mask['/8']  = " 255.0.0.0"

		for mask in cidr2mask.keys():
			configFile=configFile.replace(mask, cidr2mask[mask])

		a=open(ovpnConfigFile,'w')
		a.write(configFile)
		a.close()

		print(str(subnets) + " routes written to " + ovpnConfigFile)
		
except:
	print("Unable to retrieve the endpoint data from Microsoft")
