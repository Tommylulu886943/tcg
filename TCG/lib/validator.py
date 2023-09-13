import yaml
import logging
from lib.general_tool import GeneralTool

class Validator:
    
    issue_index = 1
    
    @classmethod
    def validate_object_schema(cls, schema : dict, operation_id : str, missing_restrictions : list, path: str = "") -> None:
        # * If the schema is a reference, retrieve the reference schema.
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                if prop_schema.get('$ref'):
                    ref_path = prop_schema.get('$ref').split('/')
                    ref_schema = spec
                    for path in ref_path[1:]:
                        ref_schema = ref_schema.get(path, {})
                    cls.validate_object_schema(ref_schema, operation_id, missing_restrictions, path + "." + prop_name)
                else:
                    cls.validate_object_schema(prop_schema, operation_id, missing_restrictions, path + "." + prop_name)
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
                    missing_restrictions.append((operation_id, path, 'string', 'minLength'))
                if not schema.get('maxLength'):
                    missing_restrictions.append((operation_id, path, 'string', 'maxLength'))
            elif schema.get('type') == 'integer' or schema.get('type') == 'number':
                if not schema.get('minimum'):
                    missing_restrictions.append((operation_id, path, schema.get('type'), 'minimum'))
                if not schema.get('maximum'):
                    missing_restrictions.append((operation_id, path, schema.get('type'), 'maximum'))
            elif schema.get('type') == 'array':
                if not schema.get('minItems'):
                    missing_restrictions.append((operation_id, path, 'array', 'minItems'))
                if not schema.get('maxItems'):
                    missing_restrictions.append((operation_id, path, 'array', 'maxItems'))

    @classmethod          
    def _add_no_content_type_issue(cls, operation_id, missing_restrictions):
        return missing_restrictions.append((operation_id, "", "", "No content type"))
                    
    @classmethod
    def parse_missing_restrictions(cls, missing_restrictions: list) -> dict:
        result = {}
        for item in missing_restrictions:
            result[f"Issue {cls.issue_index}"] = {
                "API": item[0],
                "Path": item[1],
                "Data Type": item[2],
                "Description": item[3]
            }
            cls.issue_index += 1
        return result
    

    @classmethod
    def validate_schema_restrictions(cls, schema: dict) -> dict:
        missing_restrictions = []
        for uri, path_item in schema['paths'].items():
            for method, operation in path_item.items():
                operation_id = operation['operationId']
                logging.debug(f"URI: {uri}")
                logging.debug(f"Method: {method}")
                logging.debug(f"Operation: {operation}")
                if 'requestBody' in operation:
                    try:
                        # * WARNING: Only support the first content type now.
                        first_content_type = next(iter(operation['requestBody']['content']))
                        request_body_schema = GeneralTool.retrieve_ref_schema(schema, operation['requestBody']['content'][first_content_type]['schema'])
                        cls.validate_object_schema(request_body_schema, operation_id, missing_restrictions)
                    except KeyError:
                        # * If no any content type, add an issue.
                        cls._add_no_content_type_issue(operation_id, missing_restrictions)
                if 'responses' in operation:
                    for status_code, response in operation['responses'].items():
                        if 'content' in response:
                            try:
                                # * WARNING: Only support the first content type now.
                                first_content_type = next(iter(response['content']))
                                response_schema = GeneralTool.retrieve_ref_schema(schema, response['content'][first_content_type]['schema'])
                                cls.validate_object_schema(response_schema, operation_id, missing_restrictions)
                            except KeyError:
                                # * If no any content type, add an issue.
                                cls._add_no_content_type_issue(operation_id, missing_restrictions)

        result = cls.parse_missing_restrictions(missing_restrictions)
        return result