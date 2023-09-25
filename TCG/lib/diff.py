import os
import json
import glob
import logging
import pprint
from itertools import chain
from deepdiff import DeepDiff
from collections import OrderedDict

from lib.refactor import CaseRefactor

"""
The `DiffFinder` class provides methods for parsing key paths, searching for schemas in a Swagger/OpenAPI document, and finding APIs that use a given schema name.

Main functionalities:
- Parsing key paths into a list of keys.
- Searching for schemas in a Swagger/OpenAPI document.
- Finding APIs that use a given schema name, as well as other schemas and APIs that reference it.

Methods:
- `parse_key_path(key_path: str) -> list`: Parses a key path string into a list of keys.
- `search_schema(path_list: list, doc: dict) -> dict | None`: Uses the changed key path to search the new schema and return the schema info.
- `found_consequence_api(schema_name: str, doc: dict) -> list`: Finds all APIs that use a given schema name, as well as other schemas that reference it, and other APIs that reference it.
- `search_dict(key, value, node)`: Recursively searches for items in a dictionary that match the given key and value, and returns their path and value.

Fields:
The `DiffFinder` class does not have any fields.
"""

class DiffFinder:
    
    @classmethod
    def parse_key_path(cls, key_path: str) -> list:
        """
        Parse the key path string into a list of keys.

        Args:
        - key_path (str): The key path string to parse.

        Returns:
        - A list of keys.
        """
        
        parsed_path = key_path.replace("root", "")
        parsed_path = parsed_path.replace("']['", ".")
        parsed_path = parsed_path.replace("['", "")
        parsed_path = parsed_path.replace("']", "")
        parsed_path = parsed_path.replace("[", ".")
        parsed_path = parsed_path.replace("]", ".")
        parsed_path = parsed_path.split('.')
        
        return parsed_path

    @classmethod
    def search_schema(cls, path_list: list, doc: dict) -> dict | None:
        """
        Use the changed key path to search the new schema and return the schema info.

        Args:
        - path_list (list): The list of keys representing the path to the schema.
        - doc (dict): The Swagger/OpenAPI document.

        Returns:
        - A dictionary representing the schema info, or None if the schema is not found.
        """
        schema = doc
        for path in path_list:
            try:
                if str(path).isdigit():
                    schema = schema[int(path)]  
                elif path in schema:
                    schema = schema[path]
                else:
                    return None
            except KeyError:
                if path in schema:
                    schema = schema[path]
                else:
                    return None
            except IndexError:
                return None
        return schema
    
    @classmethod
    def search_dict(cls, key, value, node):
        """
        Recursively search for items in a dictionary that match the given key and value, and return their path and value.

        Args:
        - key (any): The key to search for.
        - value (any): The value to search for.
        - node (dict or list): The dictionary or list to search in.

        Yields:
        - Tuple[List, any]: A tuple containing the path and value of the matching item.
        """
        if isinstance(node, dict):
            for k, v in node.items():
                if k == key and v == value:
                    yield [k], v
                elif isinstance(v, dict):
                    for path, val in cls.search_dict(key, value, v):
                        yield [k] + path, val
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        for path, val in cls.search_dict(key, value, item):
                            yield [k, i] + path, val
        elif isinstance(node, list):
            for i, item in enumerate(node):
                for path, val in cls.search_dict(key, value, item):
                    yield [i] + path, val
        
    @classmethod
    def found_reference_api_and_ref_type(cls, schema_name: str, doc: dict) -> list:
        """
        Find all APIs that use a given schema name, as well as other schemas that reference it.

        Args:
        - schema_name (str): The name of the schema to search for.
        - doc (dict): A dictionary representing the OpenAPI document.

        Returns:
        - A list of strings representing the paths of the APIs that use the given schema name, as well as the paths of other schemas that reference it.
        """
        PREFIX_SCHEMA = "#/components/schemas/"
        
        reference_api_list = []
        for path, value in cls.search_dict('$ref', PREFIX_SCHEMA + schema_name, doc):
            if path[0] == 'paths':
                if path[3] == 'requestBody':
                    new_schema_name = f"{path[2].upper()} {path[1]} Request"
                    reference_api_list.append(new_schema_name)
                if path[3] == 'responses':
                    new_schema_name = f"{path[2].upper()} {path[1]} Response"
                    reference_api_list.append(new_schema_name)
                if path[3] == 'parameters':
                    param_info = DiffFinder.search_schema(path[0:5], doc)
                    if 'in' in param_info:
                        if param_info['in'] == 'path':
                            new_schema_name = f"{path[2].upper()} {path[1]} Path"
                            reference_api_list.append(new_schema_name)
                        if param_info['in'] == 'query':
                            new_schema_name = f"{path[2].upper()} {path[1]} Query"
                            reference_api_list.append(new_schema_name)
                        if param_info['in'] == 'header':
                            new_schema_name = f"{path[2].upper()} {path[1]} Header"
                            reference_api_list.append(new_schema_name)
                        if param_info['in'] == 'cookie':
                            new_schema_name = f"{path[2].upper()} {path[1]} Cookie"
                            reference_api_list.append(new_schema_name)
        return reference_api_list

    @classmethod
    def found_consequence_api(cls, schema_name: str, doc: dict) -> list:
        """
        Find all APIs that use a given schema name, as well as other schemas that reference it, and other APIs that reference it.

        Args:
        - schema_name (str): The name of the schema to search for.
        - doc (dict): A dictionary representing the OpenAPI document.

        Returns:
        - A list of strings representing the paths of the APIs that use the given schema name, as well as the paths of other schemas and APIs that reference it.
        """
        
        SCHEMAS_PREFIX = "#/components/schemas/"
        REQUEST_BODIES_PREFIX = "#/components/requestBodies/"

        consequence_api_list = []
        for path, value in cls.search_dict('$ref', schema_name, doc):
            if path[0] == 'paths':
                new_schema_name = f"{path[2].upper()} {path[1]}"
                consequence_api_list.append(new_schema_name)
            elif path[0] == 'components':
                if path[1] == 'schemas':
                    new_schema_name = SCHEMAS_PREFIX + path[2]
                    consequence_api_list.extend(cls.found_consequence_api(new_schema_name, doc))
                elif path[1] == 'requestBodies':
                    new_schema_name = REQUEST_BODIES_PREFIX + path[2]
                    consequence_api_list.extend(cls.found_consequence_api(new_schema_name, doc))
        return consequence_api_list
  
class DiffAnalyzer:
    """
	A class that provides methods for analyzing the diff dictionary and generating a list of issues.
    A class that provides methods for handling different types of diffs.

    Methods:
        analyze_api_diff(diff: dict) -> list:
            Analyze the diff dictionary and generate a list of issues.
    """

    @classmethod
    def analyze_api_diff(cls, old_doc: dict, new_doc: dict) -> list:
        """
        Analyze the diff dictionary and generate a list of issues.

        Args:
            old_doc (dict): The old Swagger/OpenAPI document.
            new_doc (dict): The new Swagger/OpenAPI document.

        Returns:
            list: A list of issues found in the difference between the two objects.
        """
        diff = DeepDiff(old_doc, new_doc)
        issue_list = []
        handlers = {
            'values_changed': cls._value_change_handler,
            'iterable_item_added': cls._iterable_item_added_handler,
            'iterable_item_removed': cls._iterable_item_removed_handler,
            'dictionary_item_added': cls._dictionary_item_added_handler,
            'dictionary_item_removed': cls._dictionary_item_removed_handler,
            'type_changes': cls._type_changes_handler,
            'set_item_added': cls._set_item_added_handler,
            'set_item_removed': cls._set_item_removed_handler,
            'attribute_added': cls._attribute_added_handler,
            'attribute_removed': cls._attribute_removed_handler,
            'attribute_changed': cls._attribute_changed_handler
        }
        for handler_name, handler_func in handlers.items():
            if handler_name in diff:
                issue_list.extend(handler_func(diff, new_doc, old_doc))
            else:
                continue
        return issue_list
    
    @classmethod
    def _value_change_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['values_changed'].items():  
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': None,
                'affected_api_list': []
            }
            
            if path_list[0] == 'paths':
                api_name = path_list[2].upper() + " " + path_list[1]
                issue['field'] = 'Path: ' + api_name + " " + path_list[-1]
                if path_list[3] in ['summary', 'description', 'tags']:
                    issue['severity'] = "INFO"
                elif path_list[3] in ['requestBody', 'responses', 'operationId']:
                    issue['severity'] = "BREAK"
                    if path_list[3] == 'requestBody':
                        issue['trigger_action'] = "Update Request Body"
                    elif path_list[3] == 'responses':
                        issue['trigger_action'] = "Update Response"
                    elif path_list[3] == 'operationId':
                        issue['trigger_action'] = "Update Operation ID"
                elif path_list[3] == 'parameters':
                    issue['severity'] = "BREAK"
                    # * Check if parametere is in path or query to determine trigger aciton type.
                    param_info = DiffFinder.search_schema(path_list[0:5], new_doc)
                    if 'in' in param_info:
                        if param_info['in'] == 'path':
                            if path_list[5] == 'name':
                                issue['trigger_action'] = "Update Path Name"
                        elif param_info['in'] == 'query':
                            issue['affected_api_list'].append(api_name)
                            if path_list[5] == 'name':
                                issue['trigger_action'] = "Update Query Parameter Name"
                            elif path_list[5] == 'required':
                                issue['trigger_action'] = "Update Query Parameter Required"
                            elif path_list[5] == 'schema':
                                if path_list[6] == 'type':
                                    issue['trigger_action'] = "Update Query Parameter Type"
                                elif path_list[6] == 'enum':
                                    issue['trigger_action'] = "Update Query Parameter Enum Name"
                    else:
                        issue['field'] = path_list[0].capitalize() + ": " + path_list[-1]
                        issue['severity'] = "UN-DEFINED"
                                
                else:
                    issue['field'] = path_list[0].capitalize() + ": " + path_list[-1]
                    issue['severity'] = "UN-DEFINED"
            elif path_list[0] == 'components' and path_list[1] == 'schemas':
                issue['field'] = path_list[-1]
                issue['severity'] = "BREAK"
                issue['trigger_action'] = "Update Schema"

                prefix = "#/components/schemas/"
                schema_name = prefix + path_list[2]
                issue['affected_api_list'].extend(DiffFinder.found_consequence_api(schema_name, new_doc))
            else:
                issue['field'] = path_list[0].capitalize() + ": " + path_list[-1]
                issue['severity'] = "UN-DEFINED"
                
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _iterable_item_added_handler(self, diff, new_doc, old_doc):
        for key, value in diff['iterable_item_added'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': None,
            }
            issue_list.append(issue)

    @classmethod
    def _iterable_item_removed_handler(self, diff, new_doc, old_doc):
        for key, value in diff['iterable_item_removed'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': None,
            }
            issue_list.append(issue)

    @classmethod
    def _dictionary_item_added_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key in diff['dictionary_item_added']:
            path_list = DiffFinder.parse_key_path(key)
            new_value = DiffFinder.search_schema(path_list, new_doc)
            if path_list[0] == 'paths':
                if path_list[3] == 'requestBody':
                    issue = {
                        'path': key,
                        'field': path_list[-1],
                        'severity': 'WARNING',
                        'old_value': None,
                        'new_value': new_value,
                        'trigger_action': "Add New Fields to Request Body",
                    }
                elif path_list[3] == 'responses':
                    issue = {
                        'path': key,
                        'field': path_list[-1],
                        'severity': 'BREAK',
                        'old_value': None,
                        'new_value': new_value,
                        'trigger_action': "Add New Response",
                    }
                elif path_list[3] == 'parameters':
                    issue = {
                        'path': key,
                        'field': path_list[-1],
                        'severity': 'BREAK',
                        'old_value': None,
                        'new_value': new_value,
                        'trigger_action': "Add New Query Parameter",
                    }
                else:
                    issue = {
                        'path': key,
                        'field': path_list[0].capitalize() + ': ' + path_list[-1],
                        'severity': 'UN-DEFINED',
                        'old_value': None,
                        'new_value': new_value,
                        'trigger_action': None,
                    }
            elif path_list[0] == 'components' and path_list[1] == 'schemas':
                issue = {
                    'path': key,
                    'field': path_list[-1],
                    'severity': 'WARNING',
                    'old_value': None,
                    'new_value': new_value,
                    'trigger_action': "Add New Schema",
                }
            else:
                issue = {
                    'path': key,
                    'field': path_list[0].capitalize() + ': ' + path_list[-1],
                    'severity': 'UN-DEFINED',
                    'old_value': None,
                    'new_value': new_value,
                    'trigger_action': None,
                }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _dictionary_item_removed_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        
        for key in diff['dictionary_item_removed']:
            path_list = DiffFinder.parse_key_path(key)
            old_value = DiffFinder.search_schema(path_list, old_doc)
            if path_list[0] == 'paths':
                issue = {
                    'path': key,
                    'field': path_list[-1],
                    'severity': 'BREAK',
                    'old_value': old_value,
                    'new_value': None,
                    'trigger_action': "Remove Field",
                }
            elif path_list[0] == 'components' and path_list[1] == 'schemas':
                PREFIX = '#/components/schemas/'
                schema_name = PREFIX + path_list[2]
                issue = {
                    'path': key,
                    'field': path_list[-1],
                    'severity': 'BREAK',
                    'old_value': old_value,
                    'new_value': None,
                    'trigger_action': "Remove Schema",
                    'affected_api_list': DiffFinder.found_consequence_api(schema_name, new_doc)
                }
            else:
                issue = {
                    'path': key,
                    'field': path_list[-1],
                    'severity': 'UN-DEFINED',
                    'old_value': old_value,
                    'new_value': None,
                    'trigger_action': None,
                }
            issue_list.append(issue)
            
        return issue_list

    @classmethod
    def _type_changes_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['type_changes'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'BREAK',
                'old_value': value['old_type'],
                'new_value': value['new_type'],
                'trigger_action': "Update Field Type",
            }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _set_item_added_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['set_item_added'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': None,
            }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _set_item_removed_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['set_item_removed'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': None,
            }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _attribute_added_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['attribute_added'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'WARNING',
                'old_value': None,
                'new_value': value['new_value'],
                'trigger_action': "Add New Attribute",
            }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _attribute_removed_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['attribute_removed'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'BREAK',
                'old_value': value['old_value'],
                'new_value': None,
                'trigger_action': "Remove Attribute",
            }
            issue_list.append(issue)
        return issue_list

    @classmethod
    def _attribute_changed_handler(cls, diff, new_doc, old_doc):
        issue_list = []
        for key, value in diff['attribute_changed'].items():
            path_list = DiffFinder.parse_key_path(key)
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'BREAK',
                'old_value': value['old_value'],
                'new_value': value['new_value'],
                'trigger_action': "Update Attribute",
            }
            issue_list.append(issue)
        return issue_list
            

