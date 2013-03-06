import os
import logging
from ckan.plugins.interfaces import IPackageController
from ckan.plugins import implements, SingletonPlugin
from genshi import Stream

class OttawaPackageListing(SingletonPlugin):
    implements(IPackageController, inherit=True)
    
    def after_search(self, search_results, search_params):
        
        for result in search_results['results']:
            result['titre'] = filter(lambda extra:extra['key']=='titre', 
                                result['extras'])[0]['value'][1:-1:].decode('unicode-escape')
                                     
            result['resume'] =  filter(lambda extra:extra['key']=='resume', 
                                result['extras'])[0]['value'][1:-1:].decode('unicode-escape')
        
        return search_results