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
        'kmz': 'KMZ/PL_CyclingNetwork.kmz',
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
    'ball-diamonds': {
        'xml': 'XML/PR_Ball_Diamonds.xml',
        'csv': 'Tables/PR_Ball_Diamonds.csv',
        'kmz': 'KMZ/PR_Ball_Diamonds.kmz',
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
    'basketball-courts': {
        'xml': 'XML/PR_Basketball_Courts.xml',
        'csv': 'Tables/PR_Basketball_Courts.csv',
        'kmz': 'KMZ/PR_Basketball_Courts.kmz',
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
        'kmz': 'KMZ/PR_Lawn_Bowling.kmz',
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
        'xml': 'XML/PR_Outdoor_Pools_Wading_ext.xml',
        'csv': 'Tables/PR_Outdoor_Pools_Wading_ext.csv',
        'kmz': 'KMZ/PR_Outdoor_Pools_Wading_ext.kmz',
        'dwg': 'DWG/PR_Outdoor_Pools_Wading_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.dbf',
                'prj': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.prj',
                'sbn': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.sbn',
                'sbx': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.sbx',
                'shp': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.shp',
                'shp.xml': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.shp.xml',
                'shx': 'Shapefiles/PR_Outdoor_Pools_Wading_ext.shx',
            },
        },
    'outdoor-rinks': {
        'xml': 'XML/PR_Outdoor_Rinks_ext.xml',
        'csv': 'Tables/PR_Outdoor_Rinks_ext.csv',
        'kmz': 'KMZ/PR_Outdoor_Rinks_ext.kmz',
        'dwg': 'DWG/PR_Outdoor_Rinks_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Outdoor_Rinks_ext.dbf',
                'prj': 'Shapefiles/PR_Outdoor_Rinks_ext.prj',
                'sbn': 'Shapefiles/PR_Outdoor_Rinks_ext.sbn',
                'sbx': 'Shapefiles/PR_Outdoor_Rinks_ext.sbx',
                'shp': 'Shapefiles/PR_Outdoor_Rinks_ext.shp',
                'shp.xml': 'Shapefiles/PR_Outdoor_Rinks_ext.shp.xml',
                'shx': 'Shapefiles/PR_Outdoor_Rinks_ext.shx',
            },
        },
    'parks': {
        'xml': 'XML/PR_Parks_ext.xml',
        'csv': 'Tables/PR_Parks_ext.csv',
        'kmz': 'KMZ/PR_Parks_ext.kmz',
        'dwg': 'DWG/PR_Parks_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Parks_ext.dbf',
                'prj': 'Shapefiles/PR_Parks_ext.prj',
                'sbn': 'Shapefiles/PR_Parks_ext.sbn',
                'sbx': 'Shapefiles/PR_Parks_ext.sbx',
                'shp': 'Shapefiles/PR_Parks_ext.shp',
                'shp.xml': 'Shapefiles/PR_Parks_ext.shp.xml',
                'shx': 'Shapefiles/PR_Parks_ext.shx',
            },
        },
    'parks-pathway-links': {
        'xml': 'XML/PR_Pathway_Links.xml',
        'csv': 'Tables/PR_Pathway_Links.csv',
        'kmz': 'KMZ/PR_Pathway_Links.kmz',
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
        'kmz': 'KMZ/PR_Skateboard_Parks.kmz',
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
    'splash-pads': {
        'xml': 'XML/PR_Splash_Pads_ext.xml',
        'csv': 'Tables/PR_Splash_Pads_ext.csv',
        'kmz': 'KMZ/PR_Splash_Pads_ext.kmz',
        'dwg': 'DWG/PR_Splash_Pads_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Splash_Pads_ext.dbf',
                'prj': 'Shapefiles/PR_Splash_Pads_ext.prj',
                'sbn': 'Shapefiles/PR_Splash_Pads_ext.sbn',
                'sbx': 'Shapefiles/PR_Splash_Pads_ext.sbx',
                'shp': 'Shapefiles/PR_Splash_Pads_ext.shp',
                'shp.xml': 'Shapefiles/PR_Splash_Pads_ext.shp.xml',
                'shx': 'Shapefiles/PR_Splash_Pads_ext.shx',
            },
        },
    'sports-fields': {
        'xml': 'XML/PR_Sports_Fields.xml',
        'csv': 'Tables/PR_Sports_Fields.csv',
        'kmz': 'KMZ/PR_Sports_Fields.kmz',
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
        'kmz': 'KMZ/PR_Tennis_Courts.kmz',
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
        'kmz': 'KMZ/PR_Volleyball_Courts.kmz',
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
        },
    'wards-2010': {
        'xml': 'XML/SAM_wards2010.xml',
        'csv': 'Tables/SAM_wards2010.csv',
        'kmz': 'KMZ/SAM_wards2010.kmz',
        'dwg': 'DWG/SAM_wards2010.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_wards2010.dbf',
                'prj': 'Shapefiles/SAM_wards2010.prj',
                'sbn': 'Shapefiles/SAM_wards2010.sbn',
                'sbx': 'Shapefiles/SAM_wards2010.sbx',
                'shp': 'Shapefiles/SAM_wards2010.shp',
                'shp.xml': 'Shapefiles/SAM_wards2010.shp.xml',
                'shx': 'Shapefiles/SAM_wards2010.shx',
            },
        },
    'wards-2006': {
        'xml': 'XML/SAM_wards2006.xml',
        'csv': 'Tables/SAM_wards2006.csv',
        'kmz': 'KMZ/SAM_wards2006.kmz',
        'dwg': 'DWG/SAM_wards2006.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_wards2006.dbf',
                'prj': 'Shapefiles/SAM_wards2006.prj',
                'sbn': 'Shapefiles/SAM_wards2006.sbn',
                'sbx': 'Shapefiles/SAM_wards2006.sbx',
                'shp': 'Shapefiles/SAM_wards2006.shp',
                'shp.xml': 'Shapefiles/SAM_wards2006.shp.xml',
                'shx': 'Shapefiles/SAM_wards2006.shx',
            },
        },
    'wards-2003': {
        'xml': 'XML/SAM_wards2003.xml',
        'csv': 'Tables/SAM_wards2003.csv',
        'kmz': 'KMZ/SAM_wards2003.kmz',
        'dwg': 'DWG/SAM_wards2003.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_wards2003.dbf',
                'prj': 'Shapefiles/SAM_wards2003.prj',
                'sbn': 'Shapefiles/SAM_wards2003.sbn',
                'sbx': 'Shapefiles/SAM_wards2003.sbx',
                'shp': 'Shapefiles/SAM_wards2003.shp',
                'shp.xml': 'Shapefiles/SAM_wards2003.shp.xml',
                'shx': 'Shapefiles/SAM_wards2003.shx',
            },
        },
    'trans-canada-trail': {
        'xml': 'XML/SAM_transCanadaTrail.xml',
        'csv': 'Tables/SAM_transCanadaTrail.csv',
        'kmz': 'KMZ/SAM_transCanadaTrail.kmz',
        'dwg': 'DWG/SAM_transCanadaTrail.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_transCanadaTrail.dbf',
                'prj': 'Shapefiles/SAM_transCanadaTrail.prj',
                'sbn': 'Shapefiles/SAM_transCanadaTrail.sbn',
                'sbx': 'Shapefiles/SAM_transCanadaTrail.sbx',
                'shp': 'Shapefiles/SAM_transCanadaTrail.shp',
                'shp.xml': 'Shapefiles/SAM_transCanadaTrail.shp.xml',
                'shx': 'Shapefiles/SAM_transCanadaTrail.shx',
            },
        },

    'former-townships': {
        'xml': 'XML/SAM_townships_Former.xml',
        'csv': 'Tables/SAM_townships_Former.csv',
        'kmz': 'KMZ/SAM_townships_Former.kmz',
        'dwg': 'DWG/SAM_townships_Former.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_townships_Former.dbf',
                'prj': 'Shapefiles/SAM_townships_Former.prj',
                'sbn': 'Shapefiles/SAM_townships_Former.sbn',
                'sbx': 'Shapefiles/SAM_townships_Former.sbx',
                'shp': 'Shapefiles/SAM_townships_Former.shp',
                'shp.xml': 'Shapefiles/SAM_townships_Former.shp.xml',
                'shx': 'Shapefiles/SAM_townships_Former.shx',
            },
        },

    'township-lot-centroids': {
        'xml': 'XML/SAM_townshipLotsCentroids.xml',
        'csv': 'Tables/SAM_townshipLotsCentroids.csv',
        'kmz': 'KMZ/SAM_townshipLotsCentroids.kmz',
        'dwg': 'DWG/SAM_townshipLotsCentroids.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_townshipLotsCentroids.dbf',
                'prj': 'Shapefiles/SAM_townshipLotsCentroids.prj',
                'sbn': 'Shapefiles/SAM_townshipLotsCentroids.sbn',
                'sbx': 'Shapefiles/SAM_townshipLotsCentroids.sbx',
                'shp': 'Shapefiles/SAM_townshipLotsCentroids.shp',
                'shp.xml': 'Shapefiles/SAM_townshipLotsCentroids.shp.xml',
                'shx': 'Shapefiles/SAM_townshipLotsCentroids.shx',
            },
        },
    'rideau-trail': {
        'xml': 'XML/SAM_rideauTrail.xml',
        'csv': 'Tables/SAM_rideauTrail.csv',
        'kmz': 'KMZ/SAM_rideauTrail.kmz',
        'dwg': 'DWG/SAM_rideauTrail.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_rideauTrail.dbf',
                'prj': 'Shapefiles/SAM_rideauTrail.prj',
                'sbn': 'Shapefiles/SAM_rideauTrail.sbn',
                'sbx': 'Shapefiles/SAM_rideauTrail.sbx',
                'shp': 'Shapefiles/SAM_rideauTrail.shp',
                'shp.xml': 'Shapefiles/SAM_rideauTrail.shp.xml',
                'shx': 'Shapefiles/SAM_rideauTrail.shx',
            },
        },
    'o-train-stations': {
        'xml': 'XML/SAM_oTrainStations.xml',
        'csv': 'Tables/SAM_oTrainStations.csv',
        'kmz': 'KMZ/SAM_oTrainStations.kmz',
        'dwg': 'DWG/SAM_oTrainStations.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_oTrainStations.dbf',
                'prj': 'Shapefiles/SAM_oTrainStations.prj',
                'sbn': 'Shapefiles/SAM_oTrainStations.sbn',
                'sbx': 'Shapefiles/SAM_oTrainStations.sbx',
                'shp': 'Shapefiles/SAM_oTrainStations.shp',
                'shp.xml': 'Shapefiles/SAM_oTrainStations.shp.xml',
                'shx': 'Shapefiles/SAM_oTrainStations.shx',
            },
        },
    'o-train-tracks': {
        'xml': 'XML/SAM_oTrainCentreline.xml',
        'csv': 'Tables/SAM_oTrainCentreline.csv',
        'kmz': 'KMZ/SAM_oTrainCentreline.kmz',
        'dwg': 'DWG/SAM_oTrainCentreline.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_oTrainCentreline.dbf',
                'prj': 'Shapefiles/SAM_oTrainCentreline.prj',
                'sbn': 'Shapefiles/SAM_oTrainCentreline.sbn',
                'sbx': 'Shapefiles/SAM_oTrainCentreline.sbx',
                'shp': 'Shapefiles/SAM_oTrainCentreline.shp',
                'shp.xml': 'Shapefiles/SAM_oTrainCentreline.shp.xml',
                'shx': 'Shapefiles/SAM_oTrainCentreline.shx',
            },
        },
    'neighbourhood-names': {
        'xml': 'XML/SAM_neighbourhoodNames.xml',
        'csv': 'Tables/SAM_neighbourhoodNames.csv',
        'kmz': 'KMZ/SAM_neighbourhoodNames.kmz',
        'dwg': 'DWG/SAM_neighbourhoodNames.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_neighbourhoodNames.dbf',
                'prj': 'Shapefiles/SAM_neighbourhoodNames.prj',
                'sbn': 'Shapefiles/SAM_neighbourhoodNames.sbn',
                'sbx': 'Shapefiles/SAM_neighbourhoodNames.sbx',
                'shp': 'Shapefiles/SAM_neighbourhoodNames.shp',
                'shp.xml': 'Shapefiles/SAM_neighbourhoodNames.shp.xml',
                'shx': 'Shapefiles/SAM_neighbourhoodNames.shx',
            },
        },
    'water': {
        'xml': 'XML/SAM_CITYWIDE_water.xml',
        'csv': 'Tables/SAM_CITYWIDE_water.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_water.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_water.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_water.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_water.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_water.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_water.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_water.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_water.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_water.shx',
            },
        },
    'trails': {
        'xml': 'XML/SAM_CITYWIDE_trails.xml',
        'csv': 'Tables/SAM_CITYWIDE_trails.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_trails.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_trails.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_trails.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_trails.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_trails.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_trails.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_trails.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_trails.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_trails.shx',
            },
        },
    'swamps': {
        'xml': 'XML/SAM_CITYWIDE_swamps.xml',
        'csv': 'Tables/SAM_CITYWIDE_swamps.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_swamps.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_swamps.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_swamps.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_swamps.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_swamps.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_swamps.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_swamps.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_swamps.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_swamps.shx',
            },
        },
    'airport-runways': {
        'xml': 'XML/SAM_CITYWIDE_runways.xml',
        'csv': 'Tables/SAM_CITYWIDE_runways.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_runways.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_runways.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_runways.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_runways.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_runways.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_runways.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_runways.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_runways.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_runways.shx',
            },
        },
    'rivers': {
        'xml': 'XML/SAM_CITYWIDE_rivers.xml',
        'csv': 'Tables/SAM_CITYWIDE_rivers.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_rivers.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_rivers.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_rivers.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_rivers.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_rivers.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_rivers.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_rivers.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_rivers.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_rivers.shx',
            },
        },
    'rapids': {
        'xml': 'XML/SAM_CITYWIDE_rapids.xml',
        'csv': 'Tables/SAM_CITYWIDE_rapids.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_rapids.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_rapids.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_rapids.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_rapids.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_rapids.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_rapids.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_rapids.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_rapids.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_rapids.shx',
            },
        },
    'hydrolines': {
        'xml': 'XML/SAM_CITYWIDE_hydrolines.xml',
        'csv': 'Tables/SAM_CITYWIDE_hydrolines.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_hydrolines.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_hydrolines.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_hydrolines.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_hydrolines.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_hydrolines.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_hydrolines.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_hydrolines.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_hydrolines.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_hydrolines.shx',
            },
        },
    'fences': {
        'xml': 'XML/SAM_CITYWIDE_fences.xml',
        'csv': 'Tables/SAM_CITYWIDE_fences.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_fences.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_fences.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_fences.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_fences.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_fences.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_fences.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_fences.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_fences.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_fences.shx',
            },
        },
    'drainage': {
        'xml': 'XML/SAM_CITYWIDE_drainage.xml',
        'csv': 'Tables/SAM_CITYWIDE_drainage.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_drainage.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_drainage.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_drainage.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_drainage.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_drainage.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_drainage.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_drainage.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_drainage.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_drainage.shx',
            },
        },
    'ditches': {
        'xml': 'XML/SAM_CITYWIDE_ditches.xml',
        'csv': 'Tables/SAM_CITYWIDE_ditches.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_ditches.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_ditches.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_ditches.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_ditches.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_ditches.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_ditches.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_ditches.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_ditches.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_ditches.shx',
            },
        },
    'large-buildings': {
        'xml': 'XML/SAM_CITYWIDE_buildingsLarge.xml',
        'csv': 'Tables/SAM_CITYWIDE_buildingsLarge.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_buildingsLarge.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_buildingsLarge.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_buildingsLarge.shx',
            },
        },
    'accessways': {
        'xml': 'XML/SAM_CITYWIDE_accessways.xml',
        'csv': 'Tables/SAM_CITYWIDE_accessways.csv',
        'kmz': 'KMZ/SAM_CITYWIDE_accessways.kmz',
        'dwg': 'DWG/SAM_CITYWIDE_accessways.dwg',
        'shp': {
                'dbf': 'Shapefiles/SAM_CITYWIDE_accessways.dbf',
                'prj': 'Shapefiles/SAM_CITYWIDE_accessways.prj',
                'sbn': 'Shapefiles/SAM_CITYWIDE_accessways.sbn',
                'sbx': 'Shapefiles/SAM_CITYWIDE_accessways.sbx',
                'shp': 'Shapefiles/SAM_CITYWIDE_accessways.shp',
                'shp.xml': 'Shapefiles/SAM_CITYWIDE_accessways.shp.xml',
                'shx': 'Shapefiles/SAM_CITYWIDE_accessways.shx',
            },
        },
    'garbage-and-recycling-schedules': {
        'xml': 'XML/SW_Calendar.xml',
        'kmz': 'KMZ/SW_Calendar.kmz',
        'dwg': 'DWG/SW_Calendar.dwg',
        'shp': {
                'dbf': 'Shapefiles/SW_Calendar.dbf',
                'prj': 'Shapefiles/SW_Calendar.prj',
                'sbn': 'Shapefiles/SW_Calendar.sbn',
                'sbx': 'Shapefiles/SW_Calendar.sbx',
                'shp': 'Shapefiles/SW_Calendar.shp',
                'shp.xml': 'Shapefiles/SW_Calendar.shp.xml',
                'shx': 'Shapefiles/SW_Calendar.shx',
            },
        },
    'pedestrian-network': {
        'xml': 'XML/PL_PedestrianNetwork.xml',
        'csv': 'Tables/PL_PedestrianNetwork.csv',
        'kmz': 'KMZ/PL_PedestrianNetwork.kmz',
        'dwg': 'DWG/PL_PedestrianNetwork.dwg',
        'shp': {
                'dbf': 'Shapefiles/PL_PedestrianNetwork.dbf',
                'prj': 'Shapefiles/PL_PedestrianNetwork.prj',
                'sbn': 'Shapefiles/PL_PedestrianNetwork.sbn',
                'sbx': 'Shapefiles/PL_PedestrianNetwork.sbx',
                'shp': 'Shapefiles/PL_PedestrianNetwork.shp',
                'shp.xml': 'Shapefiles/PL_PedestrianNetwork.shp.xml',
                'shx': 'Shapefiles/PL_PedestrianNetwork.shx',
            },
        },
    'beaches': {
        'xml': 'XML/PR_Beaches_ext.xml',
        'csv': 'Tables/PR_Beaches_ext.csv',
        'kmz': 'KMZ/PR_Beaches_ext.kmz',
        'dwg': 'DWG/PR_Beaches_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Beaches_ext.dbf',
                'prj': 'Shapefiles/PR_Beaches_ext.prj',
                'sbn': 'Shapefiles/PR_Beaches_ext.sbn',
                'sbx': 'Shapefiles/PR_Beaches_ext.sbx',
                'shp': 'Shapefiles/PR_Beaches_ext.shp',
                'shp.xml': 'Shapefiles/PR_Beaches_ext.shp.xml',
                'shx': 'Shapefiles/PR_Beaches_ext.shx',
            },
        },
    'outdoor-pools': {
        'xml': 'XML/PR_Outdoor_Pools_Full_ext.xml',
        'csv': 'Tables/PR_Outdoor_Pools_Full_ext.csv',
        'kmz': 'KMZ/PR_Outdoor_Pools_Full_ext.kmz',
        'dwg': 'DWG/PR_Outdoor_Pools_Full_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Outdoor_Pools_Full_ext.dbf',
                'prj': 'Shapefiles/PR_Outdoor_Pools_Full_ext.prj',
                'sbn': 'Shapefiles/PR_Outdoor_Pools_Full_ext.sbn',
                'sbx': 'Shapefiles/PR_Outdoor_Pools_Full_ext.sbx',
                'shp': 'Shapefiles/PR_Outdoor_Pools_Full_ext.shp',
                'shp.xml': 'Shapefiles/PR_Outdoor_Pools_Full_ext.shp.xml',
                'shx': 'Shapefiles/PR_Outdoor_Pools_Full_ext.shx',
            },
        },
    'parking-city-parks': {
        'xml': 'XML/PR_Park_Parking.xml',
        'csv': 'Tables/PR_Park_Parking.csv',
        'kmz': 'KMZ/PR_Park_Parking.kmz',
        'dwg': 'DWG/PR_Park_Parking.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Park_Parking.dbf',
                'prj': 'Shapefiles/PR_Park_Parking.prj',
                'sbn': 'Shapefiles/PR_Park_Parking.sbn',
                'sbx': 'Shapefiles/PR_Park_Parking.sbx',
                'shp': 'Shapefiles/PR_Park_Parking.shp',
                'shp.xml': 'Shapefiles/PR_Park_Parking.shp.xml',
                'shx': 'Shapefiles/PR_Park_Parking.shx',
            },
        },
    'play-structures-and-areas': {
        'xml': 'XML/PR_Play_Structures.xml',
        'csv': 'Tables/PR_Play_Structures.csv',
        'kmz': 'KMZ/PR_Play_Structures.kmz',
        'dwg': 'DWG/PR_Play_Structures.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Play_Structures.dbf',
                'prj': 'Shapefiles/PR_Play_Structures.prj',
                'sbn': 'Shapefiles/PR_Play_Structures.sbn',
                'sbx': 'Shapefiles/PR_Play_Structures.sbx',
                'shp': 'Shapefiles/PR_Play_Structures.shp',
                'shp.xml': 'Shapefiles/PR_Play_Structures.shp.xml',
                'shx': 'Shapefiles/PR_Play_Structures.shx',
            },
        },
    'sledding-hills': {
        'xml': 'XML/PR_Sledding_Hills.xml',
        'csv': 'Tables/PR_Sledding_Hills.csv',
        'kmz': 'KMZ/PR_Sledding_Hills.kmz',
        'dwg': 'DWG/PR_Sledding_Hills.dwg',
        'shp': {
                'dbf': 'Shapefiles/PR_Sledding_Hills.dbf',
                'prj': 'Shapefiles/PR_Sledding_Hills.prj',
                'sbn': 'Shapefiles/PR_Sledding_Hills.sbn',
                'sbx': 'Shapefiles/PR_Sledding_Hills.sbx',
                'shp': 'Shapefiles/PR_Sledding_Hills.shp',
                'shp.xml': 'Shapefiles/PR_Sledding_Hills.shp.xml',
                'shx': 'Shapefiles/PR_Sledding_Hills.shx',
            },
        },
    'city-facilities': {
        'xml': 'XML/RE_CityFacilities_ext.xml',
        'csv': 'Tables/RE_CityFacilities_ext.csv',
        'kmz': 'KMZ/RE_CityFacilities_ext.kmz',
        'dwg': 'DWG/RE_CityFacilities_ext.dwg',
        'shp': {
                'dbf': 'Shapefiles/RE_CityFacilities_ext.dbf',
                'prj': 'Shapefiles/RE_CityFacilities_ext.prj',
                'sbn': 'Shapefiles/RE_CityFacilities_ext.sbn',
                'sbx': 'Shapefiles/RE_CityFacilities_ext.sbx',
                'shp': 'Shapefiles/RE_CityFacilities_ext.shp',
                'shp.xml': 'Shapefiles/RE_CityFacilities_ext.shp.xml',
                'shx': 'Shapefiles/RE_CityFacilities_ext.shx',
            },
        },
    'heritage-conservation-districts': {
        'xml': 'XML/PL_HeritageConsDistrict.xml',
        'csv': 'Tables/PL_HeritageConsDistrict.csv',
        'kmz': 'KMZ/PL_HeritageConsDistrict.kmz',
        'dwg': 'DWG/PL_HeritageConsDistrict.dwg',
        'shp': {
                'dbf': 'Shapefiles/PL_HeritageConsDistrict.dbf',
                'prj': 'Shapefiles/PL_HeritageConsDistrict.prj',
                'sbn': 'Shapefiles/PL_HeritageConsDistrict.sbn',
                'sbx': 'Shapefiles/PL_HeritageConsDistrict.sbx',
                'shp': 'Shapefiles/PL_HeritageConsDistrict.shp',
                'shp.xml': 'Shapefiles/PL_HeritageConsDistrict.shp.xml',
                'shx': 'Shapefiles/PL_HeritageConsDistrict.shx',
            },
        },
    'tree-inventory-street-trees': {
        'xml': 'XML/FS_TreeInventory.xml',
        'csv': 'Tables/FS_TreeInventory.csv',
        'shp': {
                'dbf': 'Shapefiles/FS_TreeInventory.dbf',
                'prj': 'Shapefiles/FS_TreeInventory.prj',
                'sbn': 'Shapefiles/FS_TreeInventory.sbn',
                'sbx': 'Shapefiles/FS_TreeInventory.sbx',
                'shp': 'Shapefiles/FS_TreeInventory.shp',
                'shp.xml': 'Shapefiles/FS_TreeInventory.shp.xml',
                'shx': 'Shapefiles/FS_TreeInventory.shx',
            },
        },
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

            if package is None:
                writelog("no such package: %s" % dataset)
                continue

            writelog("%s" % package.name)
            for existing_resource in package.resources:
                if existing_resource.format in resources:
                    if existing_resource.format == 'shp':
                        resource_path = resource_base_url + resources[existing_resource.format]['shp']
                    else:
                        resource_path = resource_base_url + resources[existing_resource.format]

                    file_name = 'temp_data/' + existing_resource.name + '.' + existing_resource.format
                    resource_exists = self.download_temp_file(resource_path, file_name)

                    if not resource_exists:
                        writelog("resource cannot be found in data repository: %s" % resource_path)
                        continue

                    if self.update_required(existing_resource, file_name):
                        writelog("Updating resource: %s" % resource_path)
                        if existing_resource.format == 'shp':
                            self.replace_shape_files(existing_resource, resources['shp'])
                        else:
                            self.replace_resource(existing_resource, file_name)

                        self.update_checksum(existing_resource, file_name)
                        self.update_dates(existing_resource)
                        dirty = True
                    else:
                        writelog("update not required for: %s" % resource_path)

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
