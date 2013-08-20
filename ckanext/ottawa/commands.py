from ckan import model
from ckan.lib.cli import CkanCommand
from ckan.config.environment import config
import paste.script
from paste.script.util.logging_config import fileConfig

import os
import json
import time
import sys
import gzip
import requests
import hashlib
import shutil
from datetime import datetime, timedelta

class ImportGeoCommand(CkanCommand):
    
    """
    CKAN Ottawa Extension

    Usage::

        paster import_geo

    Options::

        -c/--config <ckan config>   use named ckan config file
                                    (available to all commands)
    """
    
    summary = __doc__.split('\n')[0]
    usage = __doc__
    
    parser = paste.script.command.Command.standard_parser(verbose=True)
    parser.add_option('-c', '--config', dest='config',
        default='development.ini', help='Config file to use.')
    
        
    mapping = {
    'ball-diamonds-2009': {
        'xml': 'XML/PR_Ball_Diamonds.xml',
        'csv': 'Tables/PR_Ball_Diamonds.csv',
        'kml': 'KMZ/PR_Ball_Diamonds.kmz',
        'dwg': 'DWG/PR_Ball_Diamonds.dwg',
        },
    'basket-ball-courts-2009': {
        'xml': 'XML/PR_Basketball_Courts.xml',
        'csv': 'Tables/PR_Basketball_Courts.csv',
        'kml': 'KMZ/PR_Basketball_Courts.kmz',
        'dwg': 'DWG/PR_Basketball_Courts.dwg',
        },
    'lawn-bowling': {
        'xml': 'XML/PR_Lawn_Bowling.xml',
        'csv': 'Tables/PR_Lawn_Bowling.csv',
        'kml': 'KMZ/PR_Lawn_Bowling.kmz',
        'dwg': 'DWG/PR_Lawn_Bowling.dwg',
        },
    'wading-pools': {
        'xml': 'XML/PR_Outdoor_Pools_Wading.xml',
        'csv': 'Tables/PR_Outdoor_Pools_Wading.csv',
        'kml': 'KMZ/PR_Outdoor_Pools_Wading.kmz',
        'dwg': 'DWG/PR_Outdoor_Pools_Wading.dwg',
        },
    'outdoor-rinks': {
        'xml': 'XML/PR_Outdoor_Rinks.xml',
        #'csv': None,
        'kml': 'KMZ/PR_Outdoor_Rinks.kmz',
        'dwg': 'DWG/PR_Outdoor_Rinks.dwg',
        },
    'parks': {
        'xml': 'XML/PR_Parks.xml',
        'csv': 'Tables/PR_Parks.csv',
        'kml': 'KMZ/PR_Parks.kmz',
        'dwg': 'DWG/PR_Parks.dwg',
        },
    'parks-pathway-links': {
        'xml': 'XML/PR_Pathway_Links.xml',
        'csv': 'Tables/PR_Pathway_Links.csv',
        'kml': 'KMZ/PR_Pathway_Links.kmz',
        'dwg': 'DWG/PR_Pathway_Links.dwg',
        },
    'skateboard-parks': {
        'xml': 'XML/PR_Skateboard_Parks.xml',
        'csv': 'Tables/PR_Skateboard_Parks.csv',
        'kml': 'KMZ/PR_Skateboard_Parks.kmz',
        'dwg': 'DWG/PR_Skateboard_Parks.dwg',
        },
    'sledding-hills': {
        'xml': 'XML/PR_Sledding_Hills.xml',
        #'csv': None,
        'kml': 'KMZ/PR_Sledding_Hills.kmz',
        'dwg': 'DWG/PR_Sledding_Hills.dwg',
        },
    'splash-pads': {
        'xml': 'XML/PR_Splash_Pads.xml',
        'csv': 'Tables/PR_Splash_Pads.csv',
        'kml': 'KMZ/PR_Splash_Pads.kmz',
        'dwg': 'DWG/PR_Splash_Pads.dwg',
        },
    'sports-fields': {
        'xml': 'XML/PR_Sports_Fields.xml',
        'csv': 'Tables/PR_Sports_Fields.csv',
        'kml': 'KMZ/PR_Sports_Fields.kmz',
        'dwg': 'DWG/PR_Sports_Fields.dwg',
        },
    'tennis-courts': {
        'xml': 'XML/PR_Tennis_Courts.xml',
        'csv': 'Tables/PR_Tennis_Courts.csv',
        'kml': 'KMZ/PR_Tennis_Courts.kmz',
        'dwg': 'DWG/PR_Tennis_Courts.dwg',
        },
    'volleyball-courts': {
        'xml': 'XML/PR_Volleyball_Courts.xml',
        'csv': 'Tables/PR_Volleyball_Courts.csv',
        'kml': 'KMZ/PR_Volleyball_Courts.kmz',
        'dwg': 'DWG/PR_Volleyball_Courts.dwg',
        }
    }
    
    def command(self): 
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        cmd = self.args[0]
        self._load_config()
        
        resource_base_url = config.get('ottawa.geo_url')
        dirty = False
        writelog("running geo update...")
        
        model.repo.new_revision()
        for dataset, resources in self.mapping.iteritems():
            package = model.Package.get(dataset)
            if package is not None:
                for existing_resource in package.resources:
                    if existing_resource.format in resources:
                        resource_path = resource_base_url + resources[existing_resource.format]
                        file_name = 'temp_data/' + existing_resource.name + '.' + existing_resource.format
                        resource_exists = self.download_temp_file(resource_path, file_name)
                        if resource_exists and self.update_required(existing_resource, file_name):
                            self.replace_resource(existing_resource, file_name)
                            self.update_checksum(existing_resource, file_name)
                            self.update_dates(existing_resource)
                            dirty = True
         
        if dirty:
            model.Session.commit()  
            writelog("geo update commited")     
        else:
            writelog("no new resources detected")           
        
    def download_temp_file(self, resource_path, file_name):
        r = requests.get(resource_path, stream=True)
        if r.status_code == 200:
            if r.headers['content-type'] == 'text/xml':
                with open(file_name, 'w') as f:
                    f.write(r.content)
                    f.close()
                return True
            else:
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                    f.close()
                return True
        else:
            return False
        
        
    def update_required(self, existing_resource, temp_file):
        temp_file_hash = 'md5:' + hashlib.md5(open(temp_file, 'rb').read()).hexdigest()
        if temp_file_hash == existing_resource.hash:
            return False
        else:
            writelog("update required: %s.%s. old hash: %s, new hash: %s" % (
                                                existing_resource.name,
                                                existing_resource.format,
                                                existing_resource.hash,
                                                temp_file_hash,
                                                ))
            return True
        
        
    def update_checksum(self, existing_resource, temp_file):
        existing_resource.hash = 'md5:' + hashlib.md5(open(temp_file, 'rb').read()).hexdigest()
        
    def update_dates(self, existing_resource):
        existing_resource.last_modified = datetime.now()
        
    def replace_resource(self, existing_resource, temp_file):
        geo_storage_dir = config.get('ottawa.geo_storage_dir')
        timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
        timestamp_dir = os.path.join(geo_storage_dir, timestamp)
        if not os.path.exists(timestamp_dir):
            os.makedirs(timestamp_dir)
        
        new_file_name = existing_resource.name + '.' + existing_resource.format
        
        end_path = os.path.join(timestamp_dir, new_file_name)
        shutil.copyfile(temp_file, end_path)
        
        geo_storage_url = config.get('ottawa.geo_storage_url')
        existing_resource.url = "%s%s/%s" % (
                                geo_storage_url,
                                timestamp, 
                                new_file_name,
                            )
                                
        writelog("saved new resource for %s" % existing_resource.id)
        return ""
        
        
def writelog(message):
    log = open('import_geo.log', 'a')
    m = "[%s] %s \n" % (datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z'), message)
    print m
    log.write(m)
    log.flush()
    
    
        
        