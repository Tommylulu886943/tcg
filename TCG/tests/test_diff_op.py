import os
import sys
import logging
import json
import pytest

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.databuilder import DataBuilder
from lib.diff import DiffFinder, DiffAnalyzer
from lib.refactor import CaseRefactor

class TestDiffTEST:
    
    def test_schema_change_field_type(self):
        # Import the old and new documents
        old_doc = {
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "content": {}
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "list": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "integer",
                                            "format": "int64",
                                            "required": False 
                                        },
                                        "age": {
                                            "type": "integer"
                                        }
                                    }
                                }       
                            }
                        }
                    }
                }
            }
        }
        new_doc = {
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "content": {}
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "list": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "format": "int32",
                                            "required": True
                                        },
                                        "age": {
                                            "type": "integer"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Execute the Run Diff
        issue_list = DiffAnalyzer.analyze_api_diff(old_doc, new_doc)
        CaseRefactor.update_test_cases(issue_list, new_doc)
        
    def test_remove_field_from_schema(self):
        # Import the old and new documents
        old_doc = {
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "content": {}
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "list": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "integer" 
                                        },
                                        "age": {
                                            "type": "integer"
                                        }
                                    }
                                }       
                            }
                        }
                    }
                }
            }
        }
        new_doc = {
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "content": {}
                            }
                        },
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "list": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "integer"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Execute the Run Diff
        issue_list = DiffAnalyzer.analyze_api_diff(old_doc, new_doc)
        logging.debug(f"issue_list: {issue_list}")
        CaseRefactor.update_test_cases(issue_list, new_doc)
        
class TestRemoveRequestBodyWithNewSchema:

    def test_remove_a_existing_field(self, mocker):
        """
        Remove a existing field from the request body schema
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/GenerationRule/createUser.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.loads function
        loads_mock = mocker.patch('json.loads', return_value={
            "name": {
                "Type": "string",
                "Format": "",
                "Default": "",
                "rule": {
                    "Data Generator": "Random String (Without Special Characters)",
                    "Data Length": "[1, 10]",
                    "Required": False,
                    "Nullable": False,
                    "Regex Pattern": ""
                }
            },
            "description": {
                "Type": "string",
                "Format": "",
                "Default": "",
                "rule": {
                    "Data Generator": "Random String (Without Special Characters)",
                    "Data Length": "[1, 10]",
                    "Required": False,
                    "Nullable": False,
                    "Regex Pattern": ""
                }
            }
        })

        # Mock json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_request_body_with_new_schema("createUser", ["name"])

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/GenerationRule/createUser.json', 'r+')

        # Assert that the json.loads function is called correctly
        loads_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "description": {
                "Type": "string",
                "Format": "",
                "Default": "",
                "rule": {
                    "Data Generator": "Random String (Without Special Characters)",
                    "Data Length": "[1, 10]",
                    "Required": False,
                    "Nullable": False,
                    "Regex Pattern": ""
                }
            }
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()
        open_mock.return_value.close.assert_called_once()

    def test_path_not_found(self, mocker):
        """
        If the path is not found, it should not dump the json file, skip it.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/GenerationRule/createUser.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.loads function
        loads_mock = mocker.patch('json.loads', return_value={
            "name": {
                "Type": "string",
                "Format": "",
                "Default": "",
                "rule": {
                    "Data Generator": "Random String (Without Special Characters)",
                    "Data Length": "[1, 10]",
                    "Required": False,
                    "Nullable": False,
                    "Regex Pattern": ""
                }
            }
        })

        # Mock json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_request_body_with_new_schema("createUser", ["serverName"])

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/GenerationRule/createUser.json', 'r+')

        # Assert that the json.loads function is called correctly
        dumps_mock.assert_not_called()
