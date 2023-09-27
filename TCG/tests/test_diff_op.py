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
        CaseRefactor.update_test_cases(issue_list, new_doc)
        
class TestRemoveRuleFromGenerationRule:

    @pytest.mark.reliability
    def test_remove_request_body_from_generation_rule_single_file_not_found(self, mocker):
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
        CaseRefactor.remove_rule_from_generation_rule("createUser", ["serverName"], "request_body")

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/GenerationRule/createUser.json', 'r+')

        # Assert that the json.loads function is called correctly
        dumps_mock.assert_not_called()
        
    @pytest.mark.sanity
    def test_remove_query_rule_from_generation_rule_single_file(self, mocker):
        """
        Let's test removing a path rule from a generation rule that already exists in the file.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/QueryRule/MonitorOpenApi_Create.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.load function
        load_mock = mocker.patch('json.load', return_value={
            "id": {
                "Type": "string",
                "Format": "",
                "Required": False,
                "Nullable": False,
                "Value": ""
            },
            "other_field": {}
        })

        # Mock the json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_rule_from_generation_rule("MonitorOpenApi_Create", ["id"], "query")

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/QueryRule/MonitorOpenApi_Create.json', 'r+')

        # Assert that the json.load function is called correctly
        load_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "other_field": {}
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()  

    @pytest.mark.sanity
    def test_remove_path_rule_from_generation_rule_single_file(self, mocker):
        """
        Let's test removing a path rule from a generation rule that already exists in the file.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/PathRule/MonitorOpenApi_Create.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.load function
        load_mock = mocker.patch('json.load', return_value={
            "id": {
                "Type": "string",
                "Format": "",
                "Required": True,
                "Nullable": False,
                "Value": ""
            },
            "name": {
                "Type": "string",
                "Format": "int32",
                "Required": True,
                "Nullable": False,
                "Value": "Test"
            }
        })

        # Mock the json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_rule_from_generation_rule("MonitorOpenApi_Create", ["id"], "path")

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/PathRule/MonitorOpenApi_Create.json', 'r+')

        # Assert that the json.load function is called correctly
        load_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "name": {
                "Type": "string",
                "Format": "int32",
                "Required": True,
                "Nullable": False,
                "Value": "Test"
            }
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()    

    @pytest.mark.sanity
    def test_remove_path_rule_from_generation_rule_multiple_files(self, mocker):
        """
        Let's test removing a path rule from multiple generation rules that exist in multiple files.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=[
            '../artifacts/PathRule/MonitorOpenApi_Create.json',
            '../artifacts/PathRule/MonitorOpenApi_Update.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.load function
        load_mock = mocker.patch('json.load', side_effect=[
            {
                "id": {
                    "Type": "string",
                    "Format": "",
                    "Required": True,
                    "Nullable": False,
                    "Value": ""
                },
                "name": {
                    "Type": "string",
                    "Format": "int32",
                    "Required": True,
                    "Nullable": False,
                    "Value": "Test"
                }
            },
            {
                "id": {
                    "Type": "string",
                    "Format": "",
                    "Required": True,
                    "Nullable": False,
                    "Value": ""
                },
                "name2": {
                    "Type": "string",
                    "Format": "int32",
                    "Required": True,
                    "Nullable": False,
                    "Value": "Test"
                }
            }
        ])

        # Mock the json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_rule_from_generation_rule("MonitorOpenApi_Create", ["id"], 'path')

        # Assert that the open function is called twice, once for each file
        open_mock.assert_has_calls([
            mocker.call('../artifacts/PathRule/MonitorOpenApi_Create.json', 'r+'),
            mocker.call().__enter__(),
            mocker.call().seek(0),
            mocker.call().write(dumps_mock.return_value),
            mocker.call().truncate(),
            mocker.call().__exit__(None, None, None),
            mocker.call('../artifacts/PathRule/MonitorOpenApi_Update.json', 'r+'),
            mocker.call().__enter__(),
            mocker.call().seek(0),
            mocker.call().write(dumps_mock.return_value),
            mocker.call().truncate(),
            mocker.call().__exit__(None, None, None)
        ])

        # Assert that the json.load function is called twice, once for each file
        load_mock.assert_has_calls([
            mocker.call(open_mock.return_value),
            mocker.call(open_mock.return_value)
        ])

        # Assert that the json.dumps function is called twice, once for each file
        dumps_mock.assert_has_calls([
            mocker.call({
                "name": {
                    "Type": "string",
                    "Format": "int32",
                    "Required": True,
                    "Nullable": False,
                    "Value": "Test"
                }
            }, indent=4),
            mocker.call({
                "name2": {
                    "Type": "string",
                    "Format": "int32",
                    "Required": True,
                    "Nullable": False,
                    "Value": "Test"
                }
            }, indent=4)
        ])

        # Assert that the opened file objects are truncated and closed
        open_mock.return_value.truncate.assert_has_calls([
            mocker.call(),
            mocker.call()
        ])

class TestRemoveRuleFromDependencyRule:
    
    def test_remove_request_body_from_dependency_rule_single_file(self, mocker):
        """
        Remove a existing field from the dependency rule
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/GenerationRule/MonitorOpenApi_Create.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.loads function
        loads_mock = mocker.patch('json.loads', return_value={
            "Setup": {
                "1": {
                    "operation_id": "MonitorOpenApi_Create",
                    "object": "monitor",
                    "action": "POST MONITORCREATE",
                    "api": "POST /api/v1/monitors",
                    "response_name": "resp1",
                    "additional_action": {},
                    "dynamic_overwrite_data": {},
                    "data_generation_rules": {
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
                    }
                }
            },
            "Teardown": {}
        })

        # Mock json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_rule_from_dependency_rule("MonitorOpenApi_Create", ["name"], "request_body")

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/GenerationRule/MonitorOpenApi_Create.json', 'r+')

        # Assert that the json.loads function is called correctly
        loads_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "Setup": {
                "1": {
                    "operation_id": "MonitorOpenApi_Create",
                    "object": "monitor",
                    "action": "POST MONITORCREATE",
                    "api": "POST /api/v1/monitors",
                    "response_name": "resp1",
                    "additional_action": {},
                    "dynamic_overwrite_data": {},
                    "data_generation_rules": {
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
                    }
                }
            },
            "Teardown": {}
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()        

    def test_remove_path_rule_from_dependency_rule_single_file(self, mocker):
        """
        Let's test removing a path rule from a dependency rule that exists in a single file.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/DependencyRule/MonitorOpenApi_Create.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.load function
        load_mock = mocker.patch('json.load', return_value={
            "Setup": {
                "1": {
                    "operation_id": "op_id_1",
                    "path": {
                        "id": {
                            "Type": "string",
                            "Format": "",
                            "Required": True,
                            "Nullable": False,
                            "Value": "2"
                        },
                        "other_field": {}
                    }
                }
            },
            "Teardown": {}
        })

        # Mock json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method
        CaseRefactor.remove_rule_from_dependency_rule("op_id_1", ["id"], 'path')

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/DependencyRule/MonitorOpenApi_Create.json', 'r+')

        # Assert that the json.load function is called correctly
        load_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "Setup": {
                "1": {
                    "operation_id": "op_id_1",
                    "path": {
                        "other_field": {}
                    }
                }
            },
            "Teardown": {}
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()
    
    def test_remove_query_rule_from_dependency_rule_single_file(self, mocker):
        """
        Let's test removing a query rule from a dependency rule that exists in a single file.
        """
        # Mock glob.glob function to return a file path list
        mocker.patch('glob.glob', return_value=['../artifacts/DependencyRule/MonitorOpenApi_Create.json'])

        # Mock the open function
        open_mock = mocker.patch('builtins.open', mocker.mock_open())

        # Mock the json.load function
        load_mock = mocker.patch('json.load', return_value={
            "Setup": {
                "1": {
                    "operation_id": "op_id_1",
                    "query": {
                        "alertFilter": {
                            "Type": "string",
                            "Format": "",
                            "Required": False,
                            "Nullable": False,
                            "Value": ""
                        },
                        "other_field": {}
                    },
                }
            },
            "Teardown": {}
        })

        # Mock json.dumps function
        dumps_mock = mocker.patch('json.dumps')

        # Call the method with query rule type
        CaseRefactor.remove_rule_from_dependency_rule("op_id_1", ["alertFilter"], 'query')

        # Assert that the open function is called correctly
        open_mock.assert_called_once_with('../artifacts/DependencyRule/MonitorOpenApi_Create.json', 'r+')

        # Assert that the json.load function is called correctly
        load_mock.assert_called_once()

        # Assert that the json.dumps function is called correctly
        dumps_mock.assert_called_once_with({
            "Setup": {
                "1": {
                    "operation_id": "op_id_1",
                    "query": {
                        "other_field": {}
                    }
                }
            },
            "Teardown": {}
        }, indent=4)

        # Assert that the opened file object is truncated and closed
        open_mock.return_value.truncate.assert_called_once()
    