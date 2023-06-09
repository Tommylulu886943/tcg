import sys
import os
import json
import yaml
import logging
import glob

from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem

class GeneralTool:
    
    @classmethod
    def collect_items_from_top_level(cls, tree, top_level_text, column_num=0):
        """ To collect all items from a QTreeWidget's top level. """
        for i in range(tree.topLevelItemCount()):
            top_level_item = tree.topLevelItem(i)
            if top_level_item.text(0) == top_level_text:
                return cls.collect_items(top_level_item, column_num)
        return []
    
    @classmethod
    def collect_items(cls, item, column_num=0):
        items = [item.text(column_num)]
        for i in range(item.childCount()):
            items.extend(cls.collect_items(item.child(i), column_num))
        return items
    
    @classmethod
    def remove_table_item_from_ui(cls, table):
        """ To remove selected item from a QTableWidget. """
        for item in table.selectedItems():
            if item.parent() is None:
                table.takeTopLevelItem(table.indexOfTopLevelItem(item))
            else:
                item.parent().takeChild(item.parent().indexOfChild(item))
    
    @classmethod
    def update_value_in_json(cls, data, key_path, new_value):
        value = data
        for key in key_path[:-1]:
            if key in value:
                value = value[key]
            else:
                return False
        if key_path[-1] in value:
            value[key_path[-1]] = new_value
            return True
        return False
    
    @classmethod
    def add_key_in_json(cls, data, key_path, new_key, new_value):
        value = data
        for key in key_path[:-1]:
            if key in value:
                value = value[key]
            else:
                return False
        if key_path[-1] in value:
            value[key_path[-1]][new_key] = new_value
            return True
        return False
    
    @classmethod
    def remove_key_in_json(cls, data, key_path):
        value = data
        for key in key_path[:-1]:
            if key in value:
                value = value[key]
            else:
                return False
        if key_path[-1] in value:
            del value[key_path[-1]]
            return True
        return False
    
    @classmethod
    def expand_and_resize_tree(cls, tree, expand=True):
        """ To expand or collapse all items in a QTreeWidget. """
        if expand:
            tree.expandAll()
        column_count = tree.columnCount()
        for column in range(column_count):
            tree.resizeColumnToContents(column)
    
    @classmethod
    def teardown_folder_files(cls, folder_path: list):
        """ To clean all files in a folder. """
        for folder in folder_path:
            schema_folder = os.path.join(os.getcwd(), folder)
            for file in os.listdir(schema_folder):
                file_path = os.path.join(schema_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    @classmethod
    def load_schema_file(cls, file_path: str):
        """ To load a schema file and return a dict. """
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == ".yaml" or file_extension == ".yml":
            with open(file_path, "r") as f:
                api_doc = yaml.load(f, Loader=yaml.FullLoader)
        elif file_extension == ".json":
            with open(file_path, "r") as f:
                api_doc = json.load(f)
        else:
            logger.error(f"Unsupported file extension: {file_extension}")
            return None
        
        return api_doc
        
    @classmethod
    def parse_schema_to_assertion_rule(cls, responses: dict) -> dict:
        """
        To generate a API's assertion rule file that contains assertion rules of some fields.
        """
        fields = {"positive": {}, "negative": {}}
        counter = {"positive": 1, "negative": 1}
        for status_code, response in responses.items():
            if status_code.startswith('2'):
                test_type = 'positive'
            elif status_code.startswith('4') or status_code.startswith('5') or status_code == 'default':
                test_type = 'negative'
            else:
                logging.warning(f"Unknown status code `{status_code}` in API `{method} {uri}`.")
                continue

            fields[test_type][str(counter[test_type])] = {
                'Source': 'Status Code', 'Filter Expression': '',
                'Assertion Method': '==', 'Expected Value': status_code,   
            }
            counter[test_type] += 1
        return fields


    @classmethod
    def parse_schema_to_generation_rule(cls, schema: dict, path: str = "") -> dict:
        """ 
        To generate a API's generation rule file that cantains value definition of some fields. 
        Like default value, type, etc.
        """
        fields = {}
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if path:
                    new_path = path + "." + prop_name
                else:
                    new_path = prop_name
                fields.update(cls.parse_schema_to_generation_rule(prop_schema, new_path))
        elif "items" in schema:
            if "properties" in schema["items"]:
                for prop_name, prop_schema in schema["items"]["properties"].items():
                    if path:
                        new_path = path + "[0]." + prop_name
                    else:
                        new_path = prop_name
                    fields.update(cls.parse_schema_to_generation_rule(prop_schema, new_path))
            else:
                if path:
                    new_path = path + "[0]"
                else:
                    new_path = "[0]"
                fields.update(cls.parse_schema_to_generation_rule(schema["items"], new_path))
        else:
            genType = None
            if schema["type"] == "string":
                if 'format' in schema:
                    if schema['format'] in ['email', 'ipv4', 'ipv6', 'hostname', 'uuid', 'date-time', 'date', 'uri']:
                        genType = f"Random {schema['format'].upper()}"
                        data_length = ""
                elif 'pattern' in schema:
                    genType = "Random String By Pattern"
                    data_length = ""
                else:
                    genType = "Random String (Without Special Characters)"
                    data_length = [4, 30]
            elif schema["type"] == "integer":
                # TODO : Format
                genType = "Random Integer"
                data_length = [1, 100]
            elif schema["type"] == "number":
                genType = "Random Number (Float)"
                data_length = [1, 100]
            elif schema["type"] == "boolean":
                genType = "Random Boolean"
                data_length = ""
            elif schema["type"] == "object":
                genType = "Random Object"
                data_length = ""
            
            length_condition = ["minLength", "maxLength", "minimum", "maximum"]
            if any(key in schema for key in length_condition):
                if genType == "Random String (Without Special Characters)":
                    if "minLength" in schema:
                        data_length[0] = schema["minLength"]
                    if "maxLength" in schema:
                        data_length[1] = schema["maxLength"]
                elif genType == "Random Integer":
                    if "minimum" in schema:
                        data_length[0] = schema["minimum"]
                    if "maximum" in schema:
                        data_length[1] = schema["maximum"]
                elif genType == "Random Number (Float)":
                    if "minimum" in schema:
                        data_length[0] = schema["minimum"]
                    if "maximum" in schema:
                        data_length[1] = schema["maximum"]
                                   
            nullable = False
            if "nullable" in schema: nullable = schema["nullable"]
                        
            default = ""
            if "default" in schema: default = schema["default"]
                
            data_format = ""
            if "format" in schema: data_format = schema["format"]
            
            logging.debug(f"Type: {schema}")
            fields[path] = {
                "Type": schema["type"],
                "Format": data_format,
                "Default": default,
                "rule": {
                    "Data Generator": genType,
                    "Data Length": str(data_length),
                    "Nullable": nullable,
                }
            }
            
            included_field = [
                "minLength","maxLength", "minItems", "maxItems", "readOnly", "minimum", "maximum",
                "required", "uniqueItems", "nullable", "exclusiveMinimum", "exclusiveMaximum", "pattern",
            ]
            for key in included_field:
                if key in schema:
                    fields[path]['rule'][key] = schema[key]
        return fields
    
    @classmethod
    def parse_assertion_rule(cls, operation_id: str, assertion_rule_table: object) -> None:
        """
        To parse assertion rule files to TreeWidget.
        Ex: (./AssertionRule/{operation_id}.json)
        """

        def _create_child_item(item):
            child_item = QTreeWidgetItem([
                "", item['Source'], item['Filter Expression'], 
                item['Assertion Method'], item['Expected Value']
            ])
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            return child_item

        with open(f"./AssertionRule/{operation_id}.json", "r") as f:
            assertion_rule = json.load(f)

        positive_root_item = QTreeWidgetItem(["Positive"])
        assertion_rule_table.addTopLevelItem(positive_root_item)
        cls.parse_request_body(assertion_rule['positive'], positive_root_item, editabled=True)
            
        negative_root_item = QTreeWidgetItem(["Negative"])
        assertion_rule_table.addTopLevelItem(negative_root_item)
        cls.parse_request_body(assertion_rule['negative'], negative_root_item, editabled=True)

            
    @classmethod
    def parse_request_body(cls, body, parent_item, editabled=False):
        for key, value in body.items():
            if isinstance(value, dict):
                child_item = QTreeWidgetItem([key])
                if editabled:
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                parent_item.addChild(child_item)
                if editabled:
                    cls.parse_request_body(value, child_item, editabled)
                else:
                    cls.parse_request_body(value, child_item)
            elif isinstance(value, list):
                child_item = QTreeWidgetItem([key, 'array'])
                if editabled:
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                parent_item.addChild(child_item)
                for item in value:
                    if isinstance(item, dict):
                        child_item.setText(1, 'array[object]')
                        if editabled:
                            cls.parse_request_body(item, child_item, editabled)
                        else:
                            cls.parse_request_body(item, child_item)
                    else:
                        item_text = QTreeWidgetItem([item])
                        if editabled:
                            item_text.setFlags(item_text.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        child_item.addChild(item_text)
            else:
                child_item = QTreeWidgetItem([key, str(value)])
                if editabled:
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                parent_item.addChild(child_item)
                
    @classmethod
    def retrive_ref_schema_key_type(cls, api_schema):
        request_body = {}
        for key, value in api_schema['properties'].items():
            if value['type'] == 'string':
                request_body[key] = 'string'
            elif value['type'] == 'integer':
                request_body[key] = 'integer'
            elif value['type'] == 'boolean':
                request_body[key] = 'boolean'
            elif value['type'] == 'object':
                request_body[key] = cls.retrive_ref_schema_key_type(value)
            elif value['type'] == 'array':
                if value['items']['type'] == 'object':
                    request_body[key] = [cls.retrive_ref_schema_key_type(value['items'])]
                else:
                    request_body[key] = [value['items']['type']]
        return request_body
    
    @classmethod
    def retrive_ref_schema(cls, api_doc, schema):
        """Retrive all referenced schema in api doc.

        Args:
            api_doc: The api doc.
            schema: The schema to be retrived.

        Returns:
            The schema with all referenced schema resolved.
        """
        if not isinstance(schema, dict):
            return schema
        
        if '$ref' in schema:
            ref_path = schema['$ref'].split('/')[1:]
            resolved_schema = api_doc['components']['schemas'][ref_path[-1]]
            return cls.retrive_ref_schema(api_doc, resolved_schema)

        resolved_schema = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved_schema[key] = cls.retrive_ref_schema(api_doc, value)
            elif isinstance(value, list):
                resolved_schema[key] = [cls.retrive_ref_schema(api_doc, item) for item in value]
            else:
                resolved_schema[key] = value
        return resolved_schema
    