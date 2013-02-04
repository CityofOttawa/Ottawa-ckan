import os
import logging
from ckan.authz import Authorizer
from ckan.logic.converters import convert_to_extras,\
    convert_from_extras, convert_to_tags, convert_from_tags, free_tags_only
from ckan.logic import get_action, NotFound
from ckan.logic.schema import package_form_schema, group_form_schema
from ckan.lib.base import c, model
from ckan.plugins import IDatasetForm, IGroupForm, IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import implements, SingletonPlugin
from ckan.lib.navl.validators import ignore_missing, keep_extras, not_empty
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
        return False

    def package_types(self):
        return ["dataset2"]


    def form_to_db_schema(self):
        """
        Returns the schema for mapping package data from a form to a format
        suitable for the database.
        """
        schema = ckan.logic.schema.form_to_db_package_schema()
        
        schema.update({'owner_name': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'owner_organization': [validators.ignore_missing, unicode, converters.convert_to_extras]})
        schema.update({'owner_email_field': [validators.ignore_missing, unicode, converters.convert_to_extras]})

        return schema

    def db_to_form_schema(self):
        """
        Returns the schema for mapping package data from the database into a
        format suitable for the form (optional)
        """
        schema = ckan.logic.schema.db_to_form_package_schema()
        
        schema.update({'owner_name': [converters.convert_from_extras, validators.ignore_missing]})
        schema.update({'owner_organization': [converters.convert_from_extras, validators.ignore_missing]})
        schema.update({'owner_email_field': [converters.convert_from_extras, validators.ignore_missing]})

        return schema

    def check_data_dict(self, data_dict):
        """
        Check if the return data is correct and raises a DataError if not.
        """
        return