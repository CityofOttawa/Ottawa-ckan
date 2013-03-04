import os
import logging
from ckan.plugins.interfaces import IRoutes
from ckan.plugins import implements, SingletonPlugin

class OttawaRoutes(SingletonPlugin):
    implements(IRoutes, inherit=True)
    
    def before_map(self, map):
        map.connect('/', controller='package', action='search')
        map.connect('/help', controller='home', action='index')
        
        return map