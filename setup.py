from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(
	name='ckanext-ottawa',
	version=version,
	description="City of Ottawa CKAN extension",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='City of Ottawa',
	author_email='deniszgonjanin@gmail.com',
	url='',
	license='MIT',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.ottawa'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	    ottawa_public=ckanext.ottawa.plugins:OttawaPublic
	    ottawa_bilingual_dataset=ckanext.ottawa.forms:OttawaDatasetForm
	    ottawa_bilingual_search_listing=ckanext.ottawa.listing:OttawaPackageListing
	    ottawa_route_overrides=ckanext.ottawa.routes:OttawaRoutes
	""",
)
