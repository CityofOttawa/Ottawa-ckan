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
import zipfile
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
    'cycling-network': {
        'xml': 'XML/PL_CyclingNetwork.xml',
        'csv': 'Tables/PL_CyclingNetwork.csv',
        'kml': 'KMZ/PL_CyclingNetwork.kmz',
        'dwg': 'DWG/PL_CyclingNetwork.dwg',
        'shp': {
                'dbf': 'Shapefiles/PL_CyclingNetwork.dbf',
                'prj': 'Shapefiles/PL_CyclingNetwork.prj',
                'sbn': 'Shapefiles/PL_CyclingNetwork.sbn',
                'sbx': 'Shapefiles/PL_CyclingNetwork.sbx',
                'shp': 'Shapefiles/PL_CyclingNetwork.shp',
                'shp.xml': 'Shapefiles/PL_CyclingNetwork.shp.xml',
                'shx': 'Shapefiles/PL_CyclingNetwork.shx',
            },
        },
    'ball-diamonds-2009': {
        'xml': 'XML/PR_Ball_Diamonds.xml',
        'csv': 'Tables/PR_Ball_Diamonds.csv',
        'kml': 'KMZ/PR_Ball_Diamonds.kmz',
        'dwg': 'DWG/PR_Ball_Diamonds.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Ball_Diamonds.dbf',
                'prj': 'Shapefiles/PR_Ball_Diamonds.prj',
                'sbn': 'Shapefiles/PR_Ball_Diamonds.sbn',
                'sbx': 'Shapefiles/PR_Ball_Diamonds.sbx',
                'shp': 'Shapefiles/PR_Ball_Diamonds.shp',
                'shp.xml': 'Shapefiles/PR_Ball_Diamonds.shp.xml',
                'shx': 'Shapefiles/PR_Ball_Diamonds.shx',
            },
        },
    'basket-ball-courts-2009': {
        'xml': 'XML/PR_Basketball_Courts.xml',
        'csv': 'Tables/PR_Basketball_Courts.csv',
        'kml': 'KMZ/PR_Basketball_Courts.kmz',
        'dwg': 'DWG/PR_Basketball_Courts.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Basketball_Courts.dbf',
                'prj': 'Shapefiles/PR_Basketball_Courts.prj',
                'sbn': 'Shapefiles/PR_Basketball_Courts.sbn',
                'sbx': 'Shapefiles/PR_Basketball_Courts.sbx',
                'shp': 'Shapefiles/PR_Basketball_Courts.shp',
                'shp.xml': 'Shapefiles/PR_Basketball_Courts.shp.xml',
                'shx': 'Shapefiles/PR_Basketball_Courts.shx',
            },
        },
    'lawn-bowling': {
        'xml': 'XML/PR_Lawn_Bowling.xml',
        'csv': 'Tables/PR_Lawn_Bowling.csv',
        'kml': 'KMZ/PR_Lawn_Bowling.kmz',
        'dwg': 'DWG/PR_Lawn_Bowling.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Lawn_Bowling.dbf',
                'prj': 'Shapefiles/PR_Lawn_Bowling.prj',
                'sbn': 'Shapefiles/PR_Lawn_Bowling.sbn',
                'sbx': 'Shapefiles/PR_Lawn_Bowling.sbx',
                'shp': 'Shapefiles/PR_Lawn_Bowling.shp',
                'shp.xml': 'Shapefiles/PR_Lawn_Bowling.shp.xml',
                'shx': 'Shapefiles/PR_Lawn_Bowling.shx',
            },
        },
    'wading-pools': {
        'xml': 'XML/PR_Outdoor_Pools_Wading.xml',
        'csv': 'Tables/PR_Outdoor_Pools_Wading.csv',
        'kml': 'KMZ/PR_Outdoor_Pools_Wading.kmz',
        'dwg': 'DWG/PR_Outdoor_Pools_Wading.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Outdoor_Pools_Wading.dbf',
                'prj': 'Shapefiles/PR_Outdoor_Pools_Wading.prj',
                'sbn': 'Shapefiles/PR_Outdoor_Pools_Wading.sbn',
                'sbx': 'Shapefiles/PR_Outdoor_Pools_Wading.sbx',
                'shp': 'Shapefiles/PR_Outdoor_Pools_Wading.shp',
                'shp.xml': 'Shapefiles/PR_Outdoor_Pools_Wading.shp.xml',
                'shx': 'Shapefiles/PR_Outdoor_Pools_Wading.shx',
            },
        },
    'outdoor-rinks': {
        'xml': 'XML/PR_Outdoor_Rinks.xml',
        #'csv': None,
        'kml': 'KMZ/PR_Outdoor_Rinks.kmz',
        'dwg': 'DWG/PR_Outdoor_Rinks.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Outdoor_Rinks.dbf',
                'prj': 'Shapefiles/PR_Outdoor_Rinks.prj',
                'sbn': 'Shapefiles/PR_Outdoor_Rinks.sbn',
                'sbx': 'Shapefiles/PR_Outdoor_Rinks.sbx',
                'shp': 'Shapefiles/PR_Outdoor_Rinks.shp',
                'shp.xml': 'Shapefiles/PR_Outdoor_Rinks.shp.xml',
                'shx': 'Shapefiles/PR_Outdoor_Rinks.shx',
            },
        },
    'parks': {
        'xml': 'XML/PR_Parks.xml',
        'csv': 'Tables/PR_Parks.csv',
        'kml': 'KMZ/PR_Parks.kmz',
        'dwg': 'DWG/PR_Parks.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Parks.dbf',
                'prj': 'Shapefiles/PR_Parks.prj',
                'sbn': 'Shapefiles/PR_Parks.sbn',
                'sbx': 'Shapefiles/PR_Parks.sbx',
                'shp': 'Shapefiles/PR_Parks.shp',
                'shp.xml': 'Shapefiles/PR_Parks.shp.xml',
                'shx': 'Shapefiles/PR_Parks.shx',
            },
        },
    'parks-pathway-links': {
        'xml': 'XML/PR_Pathway_Links.xml',
        'csv': 'Tables/PR_Pathway_Links.csv',
        'kml': 'KMZ/PR_Pathway_Links.kmz',
        'dwg': 'DWG/PR_Pathway_Links.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Pathway_Links.dbf',
                'prj': 'Shapefiles/PR_Pathway_Links.prj',
                'sbn': 'Shapefiles/PR_Pathway_Links.sbn',
                'sbx': 'Shapefiles/PR_Pathway_Links.sbx',
                'shp': 'Shapefiles/PR_Pathway_Links.shp',
                'shp.xml': 'Shapefiles/PR_Pathway_Links.shp.xml',
                'shx': 'Shapefiles/PR_Pathway_Links.shx',
            },
        },
    'skateboard-parks': {
        'xml': 'XML/PR_Skateboard_Parks.xml',
        'csv': 'Tables/PR_Skateboard_Parks.csv',
        'kml': 'KMZ/PR_Skateboard_Parks.kmz',
        'dwg': 'DWG/PR_Skateboard_Parks.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Skateboard_Parks.dbf',
                'prj': 'Shapefiles/PR_Skateboard_Parks.prj',
                'sbn': 'Shapefiles/PR_Skateboard_Parks.sbn',
                'sbx': 'Shapefiles/PR_Skateboard_Parks.sbx',
                'shp': 'Shapefiles/PR_Skateboard_Parks.shp',
                'shp.xml': 'Shapefiles/PR_Skateboard_Parks.shp.xml',
                'shx': 'Shapefiles/PR_Skateboard_Parks.shx',
            },
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
        'shp': {
                'dbf': 'Shapefiles/PR_Splash_Pads.dbf',
                'prj': 'Shapefiles/PR_Splash_Pads.prj',
                'sbn': 'Shapefiles/PR_Splash_Pads.sbn',
                'sbx': 'Shapefiles/PR_Splash_Pads.sbx',
                'shp': 'Shapefiles/PR_Splash_Pads.shp',
                'shp.xml': 'Shapefiles/PR_Splash_Pads.shp.xml',
                'shx': 'Shapefiles/PR_Splash_Pads.shx',
            },
        },
    'sports-fields': {
        'xml': 'XML/PR_Sports_Fields.xml',
        'csv': 'Tables/PR_Sports_Fields.csv',
        'kml': 'KMZ/PR_Sports_Fields.kmz',
        'dwg': 'DWG/PR_Sports_Fields.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Sports_Fields.dbf',
                'prj': 'Shapefiles/PR_Sports_Fields.prj',
                'sbn': 'Shapefiles/PR_Sports_Fields.sbn',
                'sbx': 'Shapefiles/PR_Sports_Fields.sbx',
                'shp': 'Shapefiles/PR_Sports_Fields.shp',
                'shp.xml': 'Shapefiles/PR_Sports_Fields.shp.xml',
                'shx': 'Shapefiles/PR_Sports_Fields.shx',
            },
        },
    'tennis-courts': {
        'xml': 'XML/PR_Tennis_Courts.xml',
        'csv': 'Tables/PR_Tennis_Courts.csv',
        'kml': 'KMZ/PR_Tennis_Courts.kmz',
        'dwg': 'DWG/PR_Tennis_Courts.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Tennis_Courts.dbf',
                'prj': 'Shapefiles/PR_Tennis_Courts.prj',
                'sbn': 'Shapefiles/PR_Tennis_Courts.sbn',
                'sbx': 'Shapefiles/PR_Tennis_Courts.sbx',
                'shp': 'Shapefiles/PR_Ball_Diamonds.shp',
                'shp.xml': 'Shapefiles/PR_Tennis_Courts.shp.xml',
                'shx': 'Shapefiles/PR_Tennis_Courts.shx',
            },
        },
    'volleyball-courts': {
        'xml': 'XML/PR_Volleyball_Courts.xml',
        'csv': 'Tables/PR_Volleyball_Courts.csv',
        'kml': 'KMZ/PR_Volleyball_Courts.kmz',
        'dwg': 'DWG/PR_Volleyball_Courts.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Volleyball_Courts.dbf',
                'prj': 'Shapefiles/PR_Volleyball_Courts.prj',
                'sbn': 'Shapefiles/PR_Volleyball_Courts.sbn',
                'sbx': 'Shapefiles/PR_Volleyball_Courts.sbx',
                'shp': 'Shapefiles/PR_Volleyball_Courts.shp',
                'shp.xml': 'Shapefiles/PR_Volleyball_Courts.shp.xml',
                'shx': 'Shapefiles/PR_Volleyball_Courts.shx',
            },
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
                        if existing_resource.format == 'shp':
                            resource_path = resource_base_url + resources[existing_resource.format]['shp']
                        else:
                            resource_path = resource_base_url + resources[existing_resource.format]
                            
                        file_name = 'temp_data/' + existing_resource.name + '.' + existing_resource.format
                        resource_exists = self.download_temp_file(resource_path, file_name)
                        if resource_exists and self.update_required(existing_resource, file_name):
                            if existing_resource.format == 'shp':
                                self.replace_shape_files(existing_resource, resources['shp'])
                            else:
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
        if existing_resource.format == 'shp':
            return True
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
        
    def replace_shape_files(self, existing_resource, shape_file_locations):
        #import pdb; pdb.set_trace()
        resource_base_url = config.get('ottawa.geo_url')
        
        shape_destination_dir = os.path.join('temp_data', existing_resource.name + '_shp')
        if not os.path.exists(shape_destination_dir):
            os.makedirs(shape_destination_dir)
        
        for shape_format, shape_location in shape_file_locations.iteritems():
            resource_location = resource_base_url + shape_location
            file_name = existing_resource.name + '.' + shape_format
            download_location = os.path.join(shape_destination_dir, file_name)
            self.download_temp_file(resource_location, download_location)
            
        zip_filename = os.path.join('temp_data', existing_resource.name + '.shp.zip')
        zip = zipfile.ZipFile(zip_filename, 'w')
        for root, dirs, files in os.walk(shape_destination_dir):
            for file in files:
                print 'writing file %s to %s' % (os.path.join(root, file), zip)
                zip.write(os.path.join(root, file), file)
        zip.close()
        
        self.replace_resource(existing_resource, zip_filename)
        
    def replace_resource(self, existing_resource, temp_file):
        geo_storage_dir = config.get('ottawa.geo_storage_dir')
        timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
        timestamp_dir = os.path.join(geo_storage_dir, timestamp)
        if not os.path.exists(timestamp_dir):
            os.makedirs(timestamp_dir)
        
        if existing_resource.format == 'shp':
            new_file_name = existing_resource.name + '.shp.zip'
        else:
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
    
    
        
        