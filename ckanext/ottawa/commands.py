from ckan import model
from ckan.lib.cli import CkanCommand
import paste.script
from paste.script.util.logging_config import fileConfig

import os
import json
import time
import sys
import gzip
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
        
    
    base = 'http://maps.ottawa.ca/opendata/'
    
    mapping = {
    'ball-diamonds-2009': {
        'xml': 'XML/PR_Ball_Diamonds.xml',
        'csv': 'Tables/PR_Ball_Diamonds.csv',
        'kmz': 'KMZ/PR_Ball_Diamonds.kmz',
        },
    'basket-ball-courts-2009': {
        'xml': 'XML/PR_Basketball_Courts.xml',
        'csv': 'Tables/PR_Basketball_Courts.csv',
        'kmz': 'KMZ/PR_Basketball_Courts.kmz',
        },
    'lawn-bowling': {
        'xml': 'XML/PR_Lawn_Bowling.xml',
        'csv': 'Tables/PR_Lawn_Bowling.csv',
        'kmz': 'KMZ/PR_Lawn_Bowling.kmz',
        },
    'wading-pools': {
        'xml': 'XML/PR_Outdoor_Pools_Wading.xml',
        'csv': 'Tables/PR_Outdoor_Pools_Wading.csv',
        'kmz': 'KMZ/PR_Outdoor_Pools_Wading.kmz',
        },
    'outdoor-rinks': {
        'xml': 'XML/PR_Outdoor_Rinks.xml',
        'csv': None,
        'kmz': 'KMZ/PR_Outdoor_Rinks.kmz',
        },
    'parks': {
        'xml': 'XML/PR_Parks.xml',
        'csv': 'Tables/PR_Parks.csv',
        'kmz': 'KMZ/PR_Parks.kmz',
        },
    'parks-pathway-links': {
        'xml': 'XML/PR_Pathway_Links.xml',
        'csv': 'Tables/PR_Pathway_Links.csv',
        'kmz': 'KMZ/PR_Pathway_Links.kmz',
        },
    'skateboard-parks': {
        'xml': 'XML/PR_Skateboard_Parks.xml',
        'csv': 'Tables/PR_Skateboard_Parks.csv',
        'kmz': 'KMZ/PR_Skateboard_Parks.kmz',
        },
    'sledding-hills': {
        'xml': 'XML/PR_Sledding_Hills.xml',
        'csv': None,
        'kmz': 'KMZ/PR_Sledding_Hills.kmz',
        },
    'splash-pads': {
        'xml': 'XML/PR_Splash_Pads.xml',
        'csv': 'Tables/PR_Splash_Pads.csv',
        'kmz': 'KMZ/PR_Splash_Pads.kmz',
        },
    'sports-fields': {
        'xml': 'XML/PR_Sports_Fields.xml',
        'csv': 'Tables/PR_Sports_Fields.csv',
        'kmz': 'KMZ/PR_Sports_Fields.kmz',
        },
    'tennis-courts': {
        'xml': 'XML/PR_Tennis_Courts.xml',
        'csv': 'Tables/PR_Tennis_Courts.csv',
        'kmz': 'KMZ/PR_Tennis_Courts.kmz',
        },
    'volleyball-courts': {
        'xml': 'XML/PR_Volleyball_Courts.xml',
        'csv': 'Tables/PR_Volleyball_Courts.csv',
        'kmz': 'KMZ/PR_Volleyball_Courts.kmz',
        }
    }
    
    def command(self):
        print 'test'