import json
import pprint
from deepdiff import DeepDiff


def parse_key_path(key_path: str) -> list:
    
    parsed_path = key_path.replace("root", "")
    parsed_path = parsed_path.replace("']['", ".")
    parsed_path = parsed_path.replace("['", "")
    parsed_path = parsed_path.replace("']", "")
    parsed_path = parsed_path.replace("[", ".")
    parsed_path = parsed_path.replace("]", ".")
    parsed_path = parsed_path.split('.')
    
    return parsed_path

def search_schema(path_list: list, doc: dict) -> dict | None:
    "Use the changed key path to search the new schema and return the schema info."
    schema = doc
    for path in path_list:
        if path.isdigit():
            schema = schema[int(path)]
        elif path in schema:
            schema = schema[path]
        else:
            return None
    return schema

def found_consequence_api(schema_name: str, doc: dict) -> list:
    """
    Find all APIs that use a given schema name, as well as other schemas that reference it, and other APIs that reference it.

    Args:
    - schema_name (str): The name of the schema to search for.
    - doc (dict): A dictionary representing the OpenAPI document.

    Returns:
    - A list of strings representing the paths of the APIs that use the given schema name, as well as the paths of other schemas and APIs that reference it.
    """

    consequence_api_list = []
    for path, value in search_dict('$ref', schema_name, doc):
        print("Start Searching...", path)
        if path[0] == 'paths':
            consequence_api_list.append(doc[path[0]][path[1]][path[2]]['operationId'])
        elif path[0] == 'components':
            if path[1] == 'schemas':
                prefix = "#/components/schemas/"
                schema_name = prefix + path[2]
                consequence_api_list.extend(found_consequence_api(schema_name, doc))
            elif path[1] == 'requestBodies':
                prefix = "#/components/requestBodies/"
                schema_name = prefix + path[2]
                consequence_api_list.extend(found_consequence_api(schema_name, doc))
    return consequence_api_list

def search_dict(key, value, node):
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
                for path, val in search_dict(key, value, v):
                    yield [k] + path, val
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    for path, val in search_dict(key, value, item):
                        yield [k, i] + path, val
    elif isinstance(node, list):
        for i, item in enumerate(node):
            for path, val in search_dict(key, value, item):
                yield [i] + path, val
    

# TODO: Pass the old doc and new doc to the function.
with open('./docs/PetStore/petstore_v1.json', 'r') as f:
    old_doc = json.load(f)
with open('./docs/PetStore/petstore_v2.json', 'r') as f:
    new_doc = json.load(f)

diff = DeepDiff(old_doc, new_doc)
print(diff)
issue_list = []
if 'values_changed' in diff:
    for key, value in diff['values_changed'].items():  
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': None,
            'affected_api_list': []
        }
        
        if path_list[0] == 'paths':
            issue['field'] = 'Path: ' + path_list[2].upper() + " " + path_list[1] + " " + path_list[-1]
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
                param_info = search_schema(path_list[0:4], new_doc)
                if 'in' in param_info:
                    if param_info['in'] == 'path':
                        if path_list[5] == 'name':
                            issue['trigger_action'] = "Update Path Name"
                    elif param_info['in'] == 'query':
                        if path_list[5] == 'name':
                            issue['trigger_action'] = "Update Query Parameter Name"
            else:
                issue['field'] = path_list[0].capitalize() + ": " + path_list[-1]
                issue['severity'] = "UN-DEFINED"
        elif path_list[0] == 'components' and path_list[1] == 'schemas':
            issue['field'] = "Components: " + path_list[-1]
            issue['severity'] = "BREAK"
            issue['trigger_action'] = "Update Schema"

            prefix = "#/components/schemas/"
            schema_name = prefix + path_list[2]
            issue['affected_api_list'].extend(found_consequence_api(schema_name, new_doc))
        else:
            issue['field'] = path_list[0].capitalize() + ": " + path_list[-1]
            issue['severity'] = "UN-DEFINED"
            
        issue_list.append(issue)
        
if 'iterable_item_added' in diff:
    for key, value in diff['iterable_item_added'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': None,
        }
        issue_list.append(issue)
        
if 'iterable_item_removed' in diff:
    for key, value in diff['iterable_item_removed'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': None,
        }
        issue_list.append(issue)

if 'dictionary_item_added' in diff:
    for key in diff['dictionary_item_added']:
        path_list = parse_key_path(key)
        new_value = search_schema(path_list, new_doc)
        if path_list[0] == 'paths':
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'WARNING',
                'old_value': None,
                'new_value': new_value,
                'trigger_action': "Add New Field",
            }
        elif path_list[0] == 'components' and path_list[1] == 'schemas':
            issue = {
                'path': key,
                'field': 'Components: ' + path_list[-1],
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

if 'dictionary_item_removed' in diff:
    for key in diff['dictionary_item_removed']:
        path_list = parse_key_path(key)
        old_value = search_schema(path_list, old_doc)
        if path_list[0] == 'paths':
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'BREAK',
                'old_value': old_value,
                'new_value': None,
                'trigger_action': "Remove Field",
            }
        elif path_list[0] == 'components' and path_list[1] == 'schemas':
            issue = {
                'path': key,
                'field': 'Components: ' + path_list[-1],
                'severity': 'BREAK',
                'old_value': old_value,
                'new_value': None,
                'trigger_action': "Remove Schema",
            }
        else:
            issue = {
                'path': key,
                'field': path_list[0].capitalize() + ': ' + path_list[-1],
                'severity': 'UN-DEFINED',
                'old_value': old_value,
                'new_value': None,
                'trigger_action': None,
            }
        issue_list.append(issue)

if 'type_changes' in diff:
    for key, value in diff['type_changes'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'field': path_list[0].capitalize() + ': ' + path_list[-1],
            'severity': 'BREAK',
            'old_value': value['old_type'],
            'new_value': value['new_type'],
            'trigger_action': "Update Field Type",
        }
        issue_list.append(issue)

if 'set_item_added' in diff:
    for key, value in diff['set_item_added'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': None,
        }
        issue_list.append(issue)

if 'set_item_removed' in diff:
    for key, value in diff['set_item_removed'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': None,
        }
        issue_list.append(issue)

if 'attribute_added' in diff:
    for key, value in diff['attribute_added'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'field': path_list[0].capitalize() + ': ' + path_list[-1],
            'severity': 'WARNING',
            'old_value': None,
            'new_value': value['new_value'],
            'trigger_action': "Add New Attribute",
        }
        issue_list.append(issue)

if 'attribute_removed' in diff:
    for key, value in diff['attribute_removed'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'field': path_list[0].capitalize() + ': ' + path_list[-1],
            'severity': 'BREAK',
            'old_value': value['old_value'],
            'new_value': None,
            'trigger_action': "Remove Attribute",
        }
        issue_list.append(issue)

if 'attribute_changed' in diff:
    for key, value in diff['attribute_changed'].items():
        path_list = parse_key_path(key)
        issue = {
            'path': key,
            'field': path_list[0].capitalize() + ': ' + path_list[-1],
            'severity': 'BREAK',
            'old_value': value['old_value'],
            'new_value': value['new_value'],
            'trigger_action': "Update Attribute",
        }
        issue_list.append(issue)

pprint.pprint(issue_list, indent=2)

# Render Issue List on QT GUI

# According to the issue list's trigger action, update the existing test cases.
for issue in issue_list:
    if issue['trigger_action'] == None:
        print(issue['trigger_action'])
        print(f"No trigger action for this '{issue['severity']}' issue '{issue['field']}'. Please update it manually.")
    elif issue['trigger_action'] == 'Update Schema':
        print("Run Update Schema Process...")
        
        
        
        
