import os
import sys
import logging

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.databuilder import DataBuilder
from lib.diff import DiffFinder, DiffAnalyzer
from lib.refactor import CaseRefactor

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
class TestDiffTEST:
    
    def test_func_test(self):
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

                            },
                            "age": {
                                "type": "integer"
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
                                            "type": "string"
                                        },
                                        "age": {
                                            "type": "integer"
                                        }
                                    }
                                }
                            },
                            "age": {
                                "type": "integer"
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
        
class TestFoundReferenceApiAndRefType:

    # Test with a schema name that is not used in any API or other schema.
    def test_schema_name_not_used(self):
        # Arrange
        schema_name = "Schema2"
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Schema1"
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
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == []

    # Test with an empty schema name.
    def test_empty_schema_name(self):
        # Arrange
        schema_name = ""
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Schema1"
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
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == []

    # Test with an empty document.
    def test_empty_document(self):
        # Arrange
        schema_name = "Schema1"
        doc = {}

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == []
        
    def test_valid_schema_name_in_request_body(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/Schema1"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == ["POST /api1 Request"]
        
    # Test with a valid schema name and a valid document.
    def test_valid_schema_name_in_response_body(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Schema1"
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
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)
        # Assert
        assert result == ["GET /api1 Response"]
        
    def test_valid_schema_name_in_parameters_query(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "parameters": [
                            {
                                "name": "query1",
                                "in": "query",
                                "schema": {
                                    "$ref": "#/components/schemas/Schema1"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == ["GET /api1 Query"]


    def test_valid_schema_name_in_parameters_path(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1/{path1}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "path1",
                                "in": "path",
                                "schema": {
                                    "$ref": "#/components/schemas/Schema1"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == ["GET /api1/{path1} Path"]

    def test_valid_schema_name_in_parameters_cookie(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "parameters": [
                            {
                                "name": "cookie1",
                                "in": "cookie",
                                "schema": {
                                    "$ref": "#/components/schemas/Schema1"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == ["GET /api1 Cookie"]

    def test_valid_schema_name_in_parameters_header(self):
        # Arrange
        schema_name = "Schema1"
        doc = {
            "paths": {
                "/api1": {
                    "get": {
                        "parameters": [
                            {
                                "name": "header1",
                                "in": "header",
                                "schema": {
                                    "$ref": "#/components/schemas/Schema1"
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Schema1": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            }
                        }
                    }
                }
            }
        }

        # Act
        result = DiffFinder.found_reference_api_and_ref_type(schema_name, doc)

        # Assert
        assert result == ["GET /api1 Header"]

