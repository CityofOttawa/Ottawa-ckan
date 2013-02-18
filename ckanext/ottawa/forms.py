import os
import logging
import ckan.lib.base as base
import ckan.authz as authz
import ckan.logic.converters as converters
from ckan.logic import get_action, NotFound
from ckan.logic.schema import package_form_schema, group_form_schema
from ckan.plugins import IDatasetForm, IGroupForm, IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import implements, SingletonPlugin
import ckan.lib.navl.validators as validators
import ckan.plugins.toolkit as toolkit
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
        
        schema.update({'__junk': [validators.ignore]})
        
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
        

    def setup_template_variables(self, context, data_dict):
        data_dict.update({'available_only': True})
        
        toolkit.c.groups_available = toolkit.c.userobj and \
            toolkit.c.userobj.get_groups('organization') or []
        toolkit.c.licences = [('', '')] + base.model.Package.get_license_options()
        toolkit.c.is_sysadmin = authz.Authorizer().is_sysadmin(toolkit.c.user)