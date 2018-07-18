###
# Push configuration information to an HPE OneView instance
#
# Implemented so far:
# ethernet_networks, fc_networks, fcoe_networks, network_sets
#
###

from hpOneView.oneview_client import OneViewClient

import json

oneview_client = OneViewClient.from_json_file('config.json')
# Import the configuration file
with open('OV_configuration.txt', 'r') as infile:
    configuration = json.load(infile)
# Create a networking-only configuration file
configuration_nw = {k:v for k,v in configuration.items() if k in ['ethernet_networks', 'fc_networks', 'fcoe_networks', 'network_sets']}

# Define functions

def create_networks(resource, network, bandwidth):
    # Create the network or network set (except bandwidth) and get the connection template URI from the response
    connection_template_uri = getattr(oneview_client, resource).create(network)['connectionTemplateUri'].replace('/rest/connection-templates/','')
    # Get the connection template information and update the bandwidth information
    connection_template = oneview_client.connection_templates.get(connection_template_uri)
    connection_template['bandwidth'] = bandwidth
    oneview_client.connection_templates.update(connection_template)

# Call functions

# Create all network and network sets
for resource in configuration_nw:
    for nw in configuration_nw[resource]:
        # Pull the bandwidth out of the JSON and add in a null connection template URI before adding the network
        bandwidth = configuration_nw[resource][nw]['bandwidth']
        nw_post = {k:v for k,v in configuration_nw[resource][nw].items() if k not in ['bandwidth']}
        nw_post['connectionTemplateUri'] = None
        # For network sets, member network names need to be converted to URIs
        if resource == 'network_sets':
            network_uris = []
            for member in nw_post['network_names']:
                network_uris.append(oneview_client.ethernet_networks.get_all(filter='name='+member)[0]['uri'])
            if 'network_names' in nw_post: del nw_post['network_names']
            nw_post['networkUris'] = network_uris
        create_networks(resource, nw_post, bandwidth)
