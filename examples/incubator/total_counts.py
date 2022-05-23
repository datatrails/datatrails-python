import os
import argparse
import json
from datetime import datetime
import shutil
import logging

from archivist.archivist import Archivist


def main():
    """
    Summarize usage of RKVST. 
    """

    parser = argparse.ArgumentParser(description='RKVST Diagnostic Tool')
    
    parser.add_argument('--url', '-u', default='https://app.rkvst.io', help='RKVST URL to access')
    parser.add_argument('--client_id', '-c', help='Specify Application CLIENT_ID inline')
    parser.add_argument('--client_secret', '-s', help='Specify Application CLIENT_SECRET inline')

    args = parser.parse_args()

    for envopt in 'client_id client_secret'.split():
        if getattr(args, envopt) is None:
            try:
                setattr(args, envopt, os.environ[f"RKVST_{envopt.upper()}"])
            except KeyError:
                print(f"use --{envopt} or set RKVST_{envopt.upper()} as an envvar")

    arch = Archivist(
        args.url,
        (args.client_id, args.client_secret),
    )

    #Specify if you would like estate details returned along with usage summary
    return_estate = True
    sanitization = ''

    props = {"confirmation_status": "CONFIRMED"}
    attrs = {}  #attributes can be added to filer by name, type, etc.

    #Total Number of Assets
    assets = list(arch.assets.list(props=props, attrs=attrs))

    #Assets with Extended Attributes
    extended_attributes_asset = []
    for asset in assets:
        for item in asset['attributes']:
            if "arc_" not in item and asset not in extended_attributes_asset:
                extended_attributes_asset.append(asset)

    #Assets with Associated Location
    assets_with_location = list(arch.assets.list(props=props, attrs= attrs | {"arc_home_location_identity":"*"})) 

    #Assets with Attachments
    total_attachments = []
    assets_with_attachments = list(arch.assets.list(props=props, attrs= attrs | {"arc_attachments":"*"}))
    for asset in assets_with_attachments:
        for item in asset['attributes']['arc_attachments']:
            if item['arc_attachment_identity'] not in total_attachments:
                total_attachments.append(item['arc_attachment_identity'])

    #Total Number of Events
    events = list(arch.events.list(props=props, attrs=attrs))

    #Events with Extended Attributes
    extended_attributes_event = []
    for event in events:
        for item in event['event_attributes']:
            if "arc_" not in item and event not in extended_attributes_event:
                extended_attributes_event.append(event)

    #Events with Attachments
    events_with_attachments = list(arch.events.list(props=props, attrs= attrs | {"arc_attachments":"*"}))
    for event in events_with_attachments:
        for item in event['event_attributes']['arc_attachments']:
            if item['arc_attachment_identity'] not in total_attachments:
                total_attachments.append(item['arc_attachment_identity'])

    #Average Events per Asset
    avg_events_per_asset = len(events)/len(assets)

    #Total Number of Subjects
    subjects = list(arch.subjects.list())

    #Total Number of Access Policies 
    access_policies = list(arch.access_policies.list())

    #Values will be automatically output in JSON file 'summary.json'
    summary_output = {"Date of Scan": str(datetime.now()), 
                "Number of Assets": len(assets),
                "Assets with Extended Attributes": len(extended_attributes_asset),
                "Assets with Associated Location": len(assets_with_location),
                "Number of Events": len(events),
                "Events with Extended Attributes": len(extended_attributes_event),
                "Events with Attachments": len(events_with_attachments),
                "Average Events per Asset": round(avg_events_per_asset),
                "Total Number of Attachments": len(total_attachments),
                "Number of Subjects": len(subjects),
                "Number of Access Policies": len(access_policies),
                }

    with open("summary.json", "w") as outfile:
        json.dump(summary_output, outfile, indent=4)

    if return_estate == True:

        ####JSON Sanitization####
        if sanitization is not None:
            #Level 1 - remove values from custom attribute fields
            if sanitization == 'Level 1':
                for asset in assets:
                    dict_a = asset['attributes']
                    for key, value in dict_a.items():
                        if "arc_" not in key:
                            dict_a[key] = '##########'  
            #Level 2 - remove values of all attributes
            if sanitization == 'Level 2':
                for asset in assets:
                    dict_a = asset['attributes']
                    for key, value in dict_a.items():
                        dict_a[key] = '##########' 
            #Level 3 - remove all custom keys and all values
            if sanitization == 'Level 3':
                for asset in assets:
                    dict_a = asset['attributes']
                    all_keys = []
                    all_values = []
                    for key, value in dict_a.items():
                        all_keys.append(key)
                        all_values.append(value)
                        for i in range(len(all_keys)):
                            if "arc_" not in all_keys[i]:
                                all_keys[i] = '#'*len(all_keys[i])
                        for i in range(len(all_values)):
                            all_values[i] = '##########'
                    dict_a.clear()
                    for k in all_keys:
                        for v in all_values:
                            dict_a[k] = v
            #Level 4 - remove all atrribute keys and values
            if sanitization == 'Level 4':
                for asset in assets:
                    dict_a = asset['attributes']
                    all_keys = []
                    all_values = []
                    for key, value in dict_a.items():
                        all_keys.append(key)
                        all_values.append(value)
                        for i in range(len(all_keys)):
                            all_keys[i] = '#'*len(all_keys[i])
                        for i in range(len(all_values)):
                            all_values[i] = '##########'
                    dict_a.clear()
                    for k in all_keys:
                        for v in all_values:
                            dict_a[k] = v      
            #Level 5 - remove all attributes entirely
            if sanitization == 'Level 5':
                for asset in assets:
                    dict_a = asset['attributes']
                    dict_a.clear()

        private_keys= list(["owner", "at_time", "chain_id"])
        for asset in assets: 
            for key in private_keys:
                asset[key] = '##########'

        #Create directories for output storage
        directory_a = 'total_estate'
        directory_b = 'assets_with_associated_events'
        parent_directory = os.path.abspath(os.getcwd())
        path_a = os.path.join(parent_directory, directory_a)
        path_b = os.path.join(path_a, directory_b)
        os.makedirs(path_a, exist_ok=True)
        os.makedirs(path_b, exist_ok=True)

        #Create a zip file containing detials of each asset, event, etc. 
        estate_list = [assets, events, subjects, access_policies, summary_output]
        file_list = ['assets', 'events', 'subjects', 'access_policies','summary']
        for item, name in zip(estate_list, file_list):
            with open(f'{name}.json','w') as outfile:
                json.dump(item, outfile, indent=4)
            if os.path.exists(os.path.join(path_a,f'{name}.json')):
                os.remove(os.path.join(path_a,f'{name}.json'))
            shutil.move(os.path.join(parent_directory,f'{name}.json'),path_a)
        
        #Create folder with files for each asset and associated events.
        list_groups = []
        for asset in assets:
            event_list = []
            for event in events:
                if asset['identity'] == event['asset_identity']:
                    event_list.append(event)
            list_groups.append({str(asset['identity']): event_list})

        for row in list_groups:
            id_list = list(row.keys())
            file_name = [x.replace('/','_') for x in id_list]
            with open(f'{file_name}.json','w') as outfile:
                json.dump(row, outfile, indent=4)
            if os.path.exists(os.path.join(path_b,f'{file_name}.json')):
                os.remove(os.path.join(path_b,f'{file_name}.json'))
            shutil.move(os.path.join(parent_directory,f'{file_name}.json'),path_b)

        shutil.make_archive('total_estate', 'zip', 'total_estate')

    logging.basicConfig(filename='logfile.log',level=logging.DEBUG)
    logging.debug(summary_output)

if __name__ == "__main__":
    main()