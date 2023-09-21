import yaml
import logging
from lib.general_tool import GeneralTool

class Validator:
    
    issue_index = 1
    
    @classmethod
    def validate_object_schema(cls, schema : dict, operation_id : str, issue_list : list, path: str = "") -> None:
        # * If the schema is a reference, retrieve the reference schema.
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                if prop_schema.get('$ref'):
                    ref_path = prop_schema.get('$ref').split('/')
                    if ref_path == "":
                        issue_list.append((operation_id, path, 'object', 'Reference path is not specified.', "MAJOR", ""))
                    ref_schema = spec
                    for path in ref_path[1:]:
                        ref_schema = ref_schema.get(path, {})
                    cls.validate_object_schema(ref_schema, operation_id, issue_list, path + "." + prop_name)
                else:
                    cls.validate_object_schema(prop_schema, operation_id, issue_list, path + "." + prop_name)
        else:
            if schema.get('readOnly'):
                return
            elif schema.get('format'):
                return
            elif schema.get('enum'):
                # * if the schema includes enum, it is not necessary to verify the restrictions.
                return
            elif schema.get('type') == 'string':
                if not schema.get('minLength'):
                    issue_list.append((operation_id, path, 'string', 'String minLength is not specified.', "MINOR", ""))
                if not schema.get('maxLength'):
                    issue_list.append((operation_id, path, 'string', 'String maxLength is not specified.', "MINOR", ""))
            elif schema.get('type') == 'integer' or schema.get('type') == 'number':
                if not schema.get('minimum'):
                    issue_list.append((operation_id, path, schema.get('type'), 'Integer/Number minimum range is not specified.', "MINOR", ""))
                if not schema.get('maximum'):
                    issue_list.append((operation_id, path, schema.get('type'), 'Integer/Number maximum range is not specified.', "MINOR", ""))
            elif schema.get('type') == 'array':
                if not schema.get('minItems'):
                    issue_list.append((operation_id, path, 'array', 'Array minItems is not specified.', "MINOR", ""))
                if not schema.get('maxItems'):
                    issue_list.append((operation_id, path, 'array', 'Array maxItems is not specified.', "MINOR", ""))

    @classmethod          
    def validate_no_content_type(cls, operation_id, issue_list, path):
        return issue_list.append((operation_id, path, "none", "No content type", "MAJOR", "The content type is not specified."))
                    
    @classmethod
    def parse_issue_list(cls, issue_list: list) -> dict:
        result = {}
        for item in issue_list:
            result[cls.issue_index] = {
                "API": item[0],
                "Path": item[1],
                "Data Type": item[2],
                "Description": item[3],
                "Severity": item[4],
                "Details": item[5]
            }
            cls.issue_index += 1
        return result
    
    @classmethod
    def validate_op_id_is_unique_and_not_empty(cls, schema: dict, issue_list: list) -> None:
        op_id_list = []
        recorded_op_id_list = []
        for uri, path_item in schema['paths'].items():
            for method, operation in path_item.items():
                op_id = operation['operationId']
                if op_id is None or op_id == "":
                    issue_list.append((op_id, "", "None", "Operation id is not specified", "MAJOR", f"{method.upper()} {uri}"))
                else:
                    op_id_list.append(op_id)
                           
        # * Check if operation id appears more than twice
        for op_id in op_id_list:
            if op_id_list.count(op_id) > 1:
                paths = []
                for uri, path_item in schema['paths'].items():
                    for method, operation in path_item.items():
                        if operation['operationId'] == op_id:
                            paths.append(f"{method.upper()} {uri}")
                if op_id not in recorded_op_id_list:
                    issue_list.append((op_id, "", "None", "Operation id is not unique", "MAJOR", f"The operation id duplicates in {paths}"))
                    recorded_op_id_list.append(op_id)

    @classmethod
    def validate_schema_restrictions(cls, schema: dict) -> dict:
        issue_list = []
        
        # Validate the operation id is unique.
        cls.validate_op_id_is_unique_and_not_empty(schema, issue_list)
        
        # Validate the restrictions of the schema.
        for uri, path_item in schema['paths'].items():
            for method, operation in path_item.items():
                operation_id = operation['operationId']          
                if 'requestBody' in operation:
                    if 'content' in operation['requestBody']:
                        if operation['requestBody']['content'] == {}:
                            cls.validate_no_content_type(operation_id, issue_list, "requestBody")
                        else:
                            first_content_type = next(iter(operation['requestBody']['content']))
                            request_body_schema = GeneralTool.retrieve_ref_schema(schema, operation['requestBody']['content'][first_content_type]['schema'])
                            if "ERROR" in request_body_schema:
                                if request_body_schema['ERROR'] == "This API reference path can not be found in the API doc. Please check the API doc.": 
                                    issue_list.append((operation_id, "", "None", "Reference path is not found", "MAJOR", f"requestBody.{first_content_type}"))
                                elif request_body_schema['ERROR'] == "ref path is empty. Please check the API doc.":
                                    issue_list.append((operation_id, "", "None", "Reference variable is empty", "MAJOR", f"requestBody.{first_content_type}"))
                            cls.validate_object_schema(request_body_schema, operation_id, issue_list, "requestBody")
                else:
                    if method == 'post' or method == 'put' or method == 'patch':
                        issue_list.append((operation_id, "", "None", "Request body is not specified", "MAJOR", f"requestBody"))
                
                if 'responses' in operation:
                    for status_code, response in operation['responses'].items():
                        if 'content' in response:
                            if response['content'] == {}:
                                cls.validate_no_content_type(operation_id, issue_list, f"responses.{status_code}")
                            else:
                                first_content_type = next(iter(response['content']))
                                response_schema = GeneralTool.retrieve_ref_schema(schema, response['content'][first_content_type]['schema'])
                                if "ERROR" in response_schema:
                                    if response_schema['ERROR'] == "This API reference path can not be found in the API doc. Please check the API doc.": 
                                        issue_list.append((operation_id, "", "None", "Reference path is not found", "MAJOR", f"responses.{status_code}.{first_content_type}"))
                                    elif response_schema['ERROR'] == "ref path is empty. Please check the API doc.":
                                        issue_list.append((operation_id, "", "None", "Reference variable is empty", "MAJOR", f"responses.{status_code}.{first_content_type}"))
                                cls.validate_object_schema(response_schema, operation_id, issue_list, f"responses.{status_code}")

        result = cls.parse_issue_list(issue_list) 
        return result