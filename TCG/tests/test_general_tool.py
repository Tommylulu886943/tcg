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