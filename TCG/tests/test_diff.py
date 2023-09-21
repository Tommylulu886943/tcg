import os
import sys
import logging

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.databuilder import DataBuilder
from lib.diff import DiffFinder

class TestSearchSchema:

    # Return the schema info when the path list is valid and the schema is found in the document.
    def test_valid_path_list_schema_found(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = ['paths', '/pets', 'get', 'responses', '200', 'content', 'application/json', 'schema']
        doc = {
            'paths': {
                '/pets': {
                    'get': {
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'name': {'type': 'string'},
                                                'age': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Define the expected output
        expected_output = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'}
            }
        }

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) == expected_output

    # Return None when the path list is valid but the schema is not found in the document.
    def test_valid_path_list_schema_not_found(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = ['paths', '/pets', 'get', 'responses', '200', 'content', 'application/xml', 'schema']
        doc = {
            'paths': {
                '/pets': {
                    'get': {
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'name': {'type': 'string'},
                                                'age': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) is None

    # Return the root document when the path list is empty.
    def test_empty_path_list(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = []
        doc = {
            'paths': {
                '/pets': {
                    'get': {
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'name': {'type': 'string'},
                                                'age': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) == doc

    # Return None when the path list contains an invalid key.
    def test_invalid_key_in_path_list(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = ['paths', '/pets', 'get', 'responses', '200', 'content', 'application/json', 'invalid_key']
        doc = {
            'paths': {
                '/pets': {
                    'get': {
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'name': {'type': 'string'},
                                                'age': {'type': 'integer'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) is None

    # Return None when the path list contains an index that is out of range.
    def test_out_of_range_index_in_path_list(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = ['paths', '/pets', 'get', 'responses', '200', 'content', 'application/json', 'schema', '1']
        doc = {
            'paths': {
                '/pets': {
                    'get': {
                        'responses': {
                            '200': {
                                'content': {
                                    'application/json': {
                                        'schema': [
                                            {
                                                'type': 'object',
                                                'properties': {
                                                    'name': {'type': 'string'},
                                                    'age': {'type': 'integer'}
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) is None

    # Return None when the document is not a dictionary.
    def test_non_dictionary_document(self):
        # Initialize the class object
        diff_finder = DiffFinder()

        # Define the input data
        path_list = ['paths', '/pets', 'get', 'responses', '200', 'content', 'application/json', 'schema']
        doc = [
            {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'age': {'type': 'integer'}
                }
            }
        ]

        # Call the method and assert the output
        assert diff_finder.search_schema(path_list, doc) is None

class TestFoundConsequenceApi:

    # Search for a schema that is used in a single API path.
    def test_single_api_path(self):
        doc = {
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Successful response",
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
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "age": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        }
        expected_result = ["GET /users"]
        result = DiffFinder.found_consequence_api("#/components/schemas/User", doc)
        assert result == expected_result

    # Search for a schema that is used in multiple API paths.
    def test_multiple_api_paths(self):
        doc = {
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Successful response",
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
                "/posts": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response"
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
                            "name": {
                                "type": "string"
                            },
                            "age": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        }
        expected_result = ["GET /users", "POST /posts"]
        result = DiffFinder.found_consequence_api("#/components/schemas/User", doc)
        assert result == expected_result