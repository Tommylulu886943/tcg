import os
import sys
import logging

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