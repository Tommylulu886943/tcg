import os
import sys
import re
import json
import random
import string
import genrex
import uuid
import pytest
import logging
from datetime import datetime, timedelta

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.general_tool import GeneralTool

class TestGeneralTool_RetrieveRefSchema:

    def test_retrieve_ref_schema_request_with_empty_ref_link(self):
        doc = {
                "paths": {
                    "/pet": {
                        "put": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": ""
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {}
                }
            }
        ref_result = GeneralTool.retrieve_ref_schema(doc, {"$ref": ""})
        assert ref_result == {"ERROR": "ref path is empty. Please check the API doc."}
        
    def test_reftrieve_ref_schema_request_with_invalid_ref_link(self):
        doc = {
                "paths": {
                    "/pet": {
                        "put": {
                            "requestBody": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/invalid"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {}
                }
            }
        ref_result = GeneralTool.retrieve_ref_schema(doc, {"$ref": "#/components/schemas/invalid"})
        assert ref_result == {"ERROR": "This API reference path can not be found in the API doc. Please check the API doc."}
        
    def test_retrieve_ref_schema_response_with_empty_ref_link(self):
        doc = {
                "paths": {
                    "/pet": {
                        "put": {
                            "responses": {
                                "200": {
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": ""
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {}
                }
            }

        ref_result = GeneralTool.retrieve_ref_schema(doc, {"$ref": ""})
        assert ref_result == {"ERROR": "ref path is empty. Please check the API doc."}
        
    def test_reftrieve_ref_schema_response_with_invalid_ref_link(self):
        doc = {
                "paths": {
                    "/pet": {
                        "put": {
                            "responses": {
                                "200": {
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/invalid"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {}
                }
            }
        ref_result = GeneralTool.retrieve_ref_schema(doc, {"$ref": "#/components/schemas/invalid"})
        assert ref_result == {"ERROR": "This API reference path can not be found in the API doc. Please check the API doc."}
        
class TestParseFieldPathToKey:

    # Given a list of field path, when all the field path elements are valid and in the expected order, then the method should return the expected key string.
    def test_valid_field_path_elements_in_order(self):
        key_path = ['components', 'schemas', 'User', 'properties', 'dnsServer', 'domains', 'type']
        key, last_key = GeneralTool.parse_field_path_to_key(key_path)
        assert key == 'dnsServer.domains.type'
        assert last_key == 'type'

    # Given a list of field path, when the last element is not 'properties', then the method should return the expected key string.
    def test_last_element_not_properties(self):
        key_path = ['components', 'schemas', 'User', 'properties', 'dnsServer', 'properties', 'domains']
        key, last_key = GeneralTool.parse_field_path_to_key(key_path)
        assert key == 'dnsServer.domains'
        assert last_key == 'domains'

    # Given a list of field path, when the last element is 'properties', then the method should return the expected key string.
    def test_last_element_properties(self):
        key_path = ['components', 'schemas', 'User', 'properties', 'name', 'properties', 'testType']
        key, last_key = GeneralTool.parse_field_path_to_key(key_path)
        assert key == 'name.testType'
        assert last_key == 'testType'

    # Given an empty list of field path, then the method should return an empty key string.
    def test_empty_field_path(self):
        key_path = []
        key, last_key = GeneralTool.parse_field_path_to_key(key_path)
        assert key == ''
        assert last_key == ''

    # Given a list of field path, when the first element is not 'components', then the method should return the expected key string.
    def test_field_without_prefix(self):
        key_path = ['test', 'properties', 'name', 'properties', 'testType']
        key, last_key = GeneralTool.parse_field_path_to_key(key_path)
        assert key == 'test.name.testType'
        assert last_key == 'testType'
