import yaml
import logging

from lib.general_tool import GeneralTool


class Validator:
    
    @classmethod
    def validate_object_schema(cls, schema : dict, operation_id : str, name : str, missing_restrictions : list) -> None:
        # * If the schema is a reference, retrieve the reference schema.
        if schema.get('type') == 'object':
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                if prop_schema.get('$ref'):
                    ref_path = prop_schema.get('$ref').split('/')
                    ref_schema = spec
                    for path in ref_path[1:]:
                        ref_schema = ref_schema.get(path, {})
                    cls.validate_object_schema(ref_schema, operation_id, prop_name, missing_restrictions)
                else:
                    cls.validate_object_schema(prop_schema, operation_id, prop_name, missing_restrictions)
        else:
            if schema.get('readOnly'):
                return
            elif schema.get('format'):
                return
            elif schema.get('type') == 'string':
                if not schema.get('minLength'):
                    missing_restrictions.append((operation_id, name, 'string', 'minLength'))
                if not schema.get('maxLength'):
                    missing_restrictions.append((operation_id, name, 'string', 'maxLength'))
            elif schema.get('type') == 'integer' or schema.get('type') == 'number':
                if not schema.get('minimum'):
                    missing_restrictions.append((operation_id, name, schema.get('type'), 'minimum'))
                if not schema.get('maximum'):
                    missing_restrictions.append((operation_id, name, schema.get('type'), 'maximum'))
            elif schema.get('type') == 'array':
                if not schema.get('minItems'):
                    missing_restrictions.append((operation_id, name, 'array', 'minItems'))
                if not schema.get('maxItems'):
                    missing_restrictions.append((operation_id, name, 'array', 'maxItems'))
                    
    @classmethod
    def parse_missing_restrictions(cls, missing_restrictions: list) -> list:
        result = []
        index = 1
        for item in missing_restrictions:
            result.append(f"[Issue {index}]\n API: {item[0]}\n Field: {item[1]}\n Type: {item[2]}\n Issue: Missing '{item[3]}'\n")
            index += 1
        return result
                           
    @classmethod
    def validate_schema_restrictions(cls, schema: dict) -> dict:
        missing_restrictions = []
        for uri, path_item in schema['paths'].items():
            for method, operation in path_item.items():
                operation_id = operation['operationId']
                if 'requestBody' in operation:
                    # * WARNING: Only support the first content type now.
                    first_content_type = next(iter(operation['requestBody']['content']))
                    request_body_schema = operation['requestBody']['content'][first_content_type]['schema']
                    request_body_schema = GeneralTool.retrive_ref_schema(schema, request_body_schema)
                    cls.validate_object_schema(request_body_schema, operation_id, "", missing_restrictions)
                    result = cls.parse_missing_restrictions(missing_restrictions)
        return result
