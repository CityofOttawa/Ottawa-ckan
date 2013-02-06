import os
import logging
from ckan.authz import Authorizer
import ckan.logic.converters as converters
from ckan.logic import get_action, NotFound
from ckan.logic.schema import package_form_schema, group_form_schema
from ckan.lib.base import c, model
from ckan.plugins import IDatasetForm, IGroupForm, IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import implements, SingletonPlugin
import ckan.lib.navl.validators as validators
import ckan.lib.plugins

log = logging.getLogger(__name__)

class OttawaDatasetForm(SingletonPlugin, ckan.lib.plugins.DefaultDatasetForm):
    implements(IDatasetForm, inherit=True)
    implements(IConfigurer, inherit=True)

    def update_config(self, config):
        """
        This IConfigurer implementation causes CKAN to look in the
        ```templates``` directory when looking for the package_form()
        """
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        template_dir = os.path.join(rootdir, 'ckanext',
                                    'ottawa', 'theme', 'templates')
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

    def package_form(self):
        return 'forms/ottawa_dataset_form.html'
        
    def read_template(self):
        return 'package/read.html'

    def is_fallback(self):
        return True

    def package_types(self):
        return ["dataset"]


    def form_to_db_schema(self):
        """
        Returns the schema for mapping package data from a form to a format
        suitable for the database.
        """
        schema = ckan.logic.schema.form_to_db_package_schema()
        
        schema.update({'titre': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'organisme': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'resume': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'date_published': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'update_frequency': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'frequence_a_jour': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'accuracy': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'exactitude': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'attributes': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'supplementaires': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        
        return schema

    def db_to_form_schema(self):
        """
        Returns the schema for mapping package data from the database into a
        format suitable for the form (optional)
        """
        schema = ckan.logic.schema.db_to_form_package_schema()
        
        schema.update({'titre': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'organisme': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'resume': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'date_published': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'update_frequency': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'frequence_a_jour': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'accuracy': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'exactitude': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'attributes': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        schema.update({'supplementaires': [converters.convert_from_extras, unicode, validators.ignore_missing]})
        
        return schema