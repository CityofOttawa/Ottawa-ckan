import os
import logging
from ckan.plugins.interfaces import IPackageController
from ckan.plugins import implements, SingletonPlugin
from genshi import Stream

class OttawaPackageListing(SingletonPlugin):
    implements(IPackageController, inherit=True)
    
    def after_search(self, search_results, search_params):
        
        if search_results['count'] > 0:
            for result in search_results['results']:
            
                titre = filter(lambda extra:extra['key']=='titre', result['extras'])
                if len(titre) > 0:
                    result['titre'] = titre[0]['value'][1:-1:].decode('unicode-escape')
                                     
                resume = filter(lambda extra:extra['key']=='resume', result['extras'])
                if len(resume) > 0:
                    result['resume'] =  resume[0]['value'][1:-1:].decode('unicode-escape')
        
        return search_results