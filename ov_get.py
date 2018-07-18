###
# Pull down configuration information from an HPE OneView instance
#
# Implemented so far:
# ethernet_networks, fc_networks, fcoe_networks, network_sets, server_profile_templates, firmware_drivers
#
###

from hpOneView.oneview_client import OneViewClient

import json

oneview_client = OneViewClient.from_json_file('config.json')
configuration = {}
nw_resources = ['ethernet_networks', 'fc_networks', 'fcoe_networks']
excluded_keys = ['connectionTemplateUri', 'fabricUri', 'managedSanUri', 'scopesUri', 'status', 'state', 'created', 'modified', 'eTag', 'category', 'uri', 'subnetUri', 'nativeNetworkUri', 'networkUris', 'serverHardwareTypeUri']

# Define functions
def remove_keys(resource, dict):
    configuration[resource][dict['name']] = {k:v for k,v in dict.items() if k not in excluded_keys}

def get_networks(resource):
    configuration[resource] = {}
    for nw in getattr(oneview_client, resource).get_all():
        # Pull the bandwidth information from the connection template and store it with the network
        nw['bandwidth'] = oneview_client.connection_templates.get(nw['connectionTemplateUri'])['bandwidth']
        remove_keys(resource, nw)

def get_network_sets():
    configuration['network_sets'] = {}
    for nws in oneview_client.network_sets.get_all():
        nws['bandwidth'] = oneview_client.connection_templates.get(nws['connectionTemplateUri'])['bandwidth']
        nws['network_names'] = []
        # Find all member networks and save their names
        for nw_uri in nws['networkUris']:
            nw = oneview_client.ethernet_networks.get(nw_uri.replace('/rest/ethernet-networks/',''))
            nws['network_names'].append(nw['name'])
        remove_keys('network_sets', nws)

def get_firmware_drivers():
    configuration['firmware_drivers'] = {}
    for fwd in oneview_client.firmware_drivers.get_all():
        configuration['firmware_drivers'][fwd['name']] = {'baseline': fwd['baselineShortName']}
        # Uncomment to add all firmware information
        # remove_keys('firmware_drivers', fwd)

###
# Even though the following are all the same function,
# there is likely unique processing for each one,
# so I've made them separate in addition to the generic version
###

''''
# Individual functions
def get_server_profile_templates():
    configuration['server_profile_templates'] = {}
    for spt in oneview_client.server_profile_templates.get_all():
        remove_keys('server_profile_templates', spt)

def get_logical_enclosures():
    configuration['logical_enclosures'] = {}
    for le in oneview_client.logical_enclosures.get_all():
        remove_keys('logical_enclosures', le)

def get_enclosure_groups():
    configuration['enclosure_groups'] = {}
    for eg in oneview_client.enclosure_groups.get_all():
        remove_keys('enclosure_groups', eg)

def get_logical_interconnect_groups():
    configuration['logical_interconnect_groups'] = {}
    for lig in oneview_client.logical_interconnect_groups.get_all():
        remove_keys('logical_interconnect_groups', lig)
'''

# Generic function
def get_resource(resource):
    configuration[resource] = {}
    for item in getattr(oneview_client, resource).get_all():
        remove_keys(resource, item)

# Call functions
for resource in nw_resources:
    get_networks(resource)

get_network_sets()
get_firmware_drivers()

'''
## Individual function calls
get_server_profile_templates()
get_logical_enclosures()
get_enclosure_groups()
get_logical_interconnect_groups()
'''

# Generic call
resources = ['server_profile_templates', 'logical_enclosures', 'enclosure_groups', 'logical_interconnect_groups']
for resource in resources:
    get_resource(resource)

# Write out configuration dictionary
# print(json.dumps(configuration, indent=4))
with open('OV_configuration.txt', 'w') as outfile:
    json.dump(configuration, outfile, indent=4)
