import sys
import os
import json
import yaml
import glob
import logging
import copy
from json.decoder import JSONDecodeError
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem
from lib.test_strategy import TestStrategy
from lib.general_tool import GeneralTool
from lib.DataBuilder import DataBuilder

DEBUG = False
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.DEBUG)

class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        # * Load the UI Page
        uic.loadUi('lib/tcg.ui', self)
        
        # * Set Icon
        self.btn_import_openapi_doc.setIcon(QIcon("./source/new.png"))
        
        # * Define the Button Event
        self.btn_import_openapi_doc.clicked.connect(self.import_openapi_doc)
        self.btn_generate_test_plan.clicked.connect(self.generate_test_plan)
        self.btn_api_table_remove.clicked.connect(self.btn_api_table_remove_clicked)
        self.btn_generation_rule_remove.clicked.connect(self.btn_generation_rule_remove_clicked)
        self.btn_update_text_body.clicked.connect(self.btn_update_text_body_clicked)
        self.btn_add_assertion_rule.clicked.connect(self.btn_add_assertion_rule_clicked)
        self.btn_update_assertion_rule.clicked.connect(self.btn_update_assertion_rule_clicked)
        self.btn_remove_assertion_rule.clicked.connect(self.btn_remove_assertion_rule_clicked)
        
        # * Table's Item Click Event
        self.table_api_tree.itemClicked.connect(self.api_tree_item_clicked)
        self.table_test_plan_api_list.itemClicked.connect(self.test_plan_api_list_item_clicked)
        self.table_assertion_rule.itemClicked.connect(self.table_assertion_rule_item_clicked)
        
        # * Item Changed Event
        self.table_generation_rule.itemChanged.connect(self.generation_rule_item_changed)
        #self.table_assertion_rule.itemChanged.connect(self.assertion_rule_item_changed)
    
    def table_assertion_rule_item_clicked(self):
        """ When the assertion rule item is clicked. """
        selected_item = self.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            self.comboBox_assertion_type.setCurrentText(parent_item.text(0))
            self.comboBox_assertion_source.setCurrentText(selected_item.child(0).text(1))
            self.textbox_assertion_rule_expression.setText(selected_item.child(1).text(1))
            self.comboBox_assertion_method.setCurrentText(selected_item.child(2).text(1))
            self.textbox_assertion_rule_expected_value.setText(selected_item.child(3).text(1))
            self.comboBox_assertion_type.setEnabled(False)
        else:
            self.comboBox_assertion_type.setEnabled(True)
    
    def btn_update_assertion_rule_clicked(self):
        """ Update Assertion Rule Item """
        if len(self.table_assertion_rule.selectedItems()) == 0:
            return
        
        test_type = self.comboBox_assertion_type.currentText()
        source = self.comboBox_assertion_source.currentText()
        path_expression = self.textbox_assertion_rule_expression.text()
        method = self.comboBox_assertion_method.currentText()
        expected_value = self.textbox_assertion_rule_expected_value.text()
                
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Retrieve the Rule Sequence Number
        assertion_selected_item = [item.text(0) for item in self.table_assertion_rule.selectedItems()]
        sequence_num = assertion_selected_item[0]

        # * To obtain the selected item's parent item
        selected_item = self.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item and parent_item.parent() is None:
            # * Update the value in the JSON file
            file_path = "./AssertionRule/" + operation_id + ".json"
            with open(file_path, 'r+') as f:
                data = json.load(f)
                path = [test_type.lower(), sequence_num]
                value = {
                    "Source": source, "Filter Expression": path_expression, 
                    "Assertion Method": method, "Expected Value": expected_value
                }
                result = GeneralTool.update_value_in_json(data, path, value)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Update JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
            for clean_item in [self.textbox_assertion_rule_expression, self.textbox_assertion_rule_expected_value, self.table_assertion_rule]:
                clean_item.clear()
            GeneralTool.parse_assertion_rule(operation_id, self.table_assertion_rule)
            GeneralTool.expand_and_resize_tree(self.table_assertion_rule)
            self.comboBox_assertion_type.setEnabled(True)
        else:
            return

    def btn_remove_assertion_rule_clicked(self):
        """ Remove Assertion Rule Item """
        
        if len(self.table_assertion_rule.selectedItems()) == 0:
            return

        selected_item = self.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            # * Get the JSON Path of the selected item
            path = [parent_item.text(0).lower(), selected_item.text(0)]
            # * Retrieve the API List selected item to get the corresponding operation id
            api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
            operation_id = api_selected_item[0]
            assertion_file_path = f"./AssertionRule/{operation_id}.json"
            with open(assertion_file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(data, path)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{assertion_file_path}` to remove key `{path}`.")
                else:
                    logging.error(f"Error updating JSON file `{assertion_file_path}` to remove key `{path}`.")
            GeneralTool.remove_table_item_from_ui(self.table_assertion_rule)
            self.comboBox_assertion_type.setEnabled(True)

    def btn_add_assertion_rule_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0:
            return
        
        test_type = self.comboBox_assertion_type.currentText()
        source = self.comboBox_assertion_source.currentText()
        path_expression = self.textbox_assertion_rule_expression.text()
        method = self.comboBox_assertion_method.currentText()
        expected_value = self.textbox_assertion_rule_expected_value.text()
        
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Add the value in the JSON file
        file_path = "./AssertionRule/" + operation_id + ".json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            path = [test_type.lower()]
            if data[test_type.lower()]:
                sequence_num = max(int(key) for key in data[test_type.lower()].keys()) + 1
            else:
                sequence_num = 1
            value = {
                "Source": source, "Filter Expression": path_expression, 
                "Assertion Method": method, "Expected Value": expected_value
            }
            result = GeneralTool.add_key_in_json(data, path, sequence_num, value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Update JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
        for clean_item in [self.textbox_assertion_rule_expression, self.textbox_assertion_rule_expected_value, self.table_assertion_rule]:
            clean_item.clear()
        GeneralTool.parse_assertion_rule(operation_id, self.table_assertion_rule)
        GeneralTool.expand_and_resize_tree(self.table_assertion_rule)
    
    def btn_update_text_body_clicked(self):
        selected_items = self.table_test_plan_api_list.selectedItems()
        parent = None
        if len(selected_items) > 0:
            parent = selected_items[0].parent()
            if parent is not None and parent.parent() is not None:
                test_id = selected_items[0].text(1)
                serial_num = test_id.split(".")[0]
                test_point = test_id.split(".")[1]
                operation_id = parent.parent().text(0)
                new_value = self.text_body.toPlainText()
                testdata_path = f"./TestData/{operation_id}_{serial_num}_{test_point}.json"
                
                # * Prepare the copy of the test data file for recovering.
                with open(testdata_path, "r") as file:
                    testdata = json.load(file)
                copy_testdata = copy.deepcopy(testdata)

                try:
                    with open(testdata_path, "w") as file:
                        json.dump(json.loads(new_value), file, indent=4)
                except JSONDecodeError as e:
                    with open(testdata_path, "w") as file:
                        json.dump(copy_testdata, file, indent=4)
                    logging.warning(f"Error updating test data file `{testdata_path}` with new value `{new_value}`. Error: {e.msg}")
                    logging.warning(f"Recover the test data file `{testdata_path}` with old value `{copy_testdata}`.")
                    return
                logging.info(f"Update test data file `{testdata_path}` with new value `{new_value}`.")
            else:
                return   
    
    # def assertion_rule_item_changed(self, item, column):
    #     # * Retrieve the dictionary path of the new value item changed in the table.
    #     source, json_path, method, expected_value = item.text(1), item.text(2), item.text(3), item.text(4)
    #     new_value = [source, json_path, method, expected_value]
    #     key_list = ["Source", "Filter Expression", "Assertion Method", "Expected Value"]
        
    #     # * Retrieve the parent item of the item changed
    #     parent_item_name = item.parent().text(0).replace(" ", "_").lower()
    #     index = item.parent().indexOfChild(item)
        
    #     # * Retrieve the API List selected item to get the corresponding operation id
    #     api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
    #     operation_id = api_selected_item[0]
        
    #     # * Update the value in the JSON file
    #     file_path = "./AssertionRule/" + operation_id + ".json"
    #     with open(file_path, 'r+') as f:
    #         data = json.load(f)
    #         for key, value in zip(key_list, new_value):
    #             result = GeneralTool.update_value_in_json(data, [parent_item_name, index, key], value)
    #             if result is not False:
    #                 f.seek(0)
    #                 json.dump(data, f, indent=4)
    #                 f.truncate()
    #                 logging.info(f"Update JSON file `{file_path}` with new value `{new_value}` at path `{[parent_item_name, index]}`.")
    #             else:
    #                 logging.error(f"Error updating JSON file `{file_path}` with new value `{new_value}` at path `{[parent_item_name, index]}`.")
            
    def generation_rule_item_changed(self, item, column):
        # * Retrieve the dictionary path of the new value item changed in the table.
        new_value = item.text(1)
        path = []
        while item.parent() is not None:
            path.insert(0, item.text(0))
            item = item.parent()
            
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Update the value in the JSON file
        file_path = "./GenerationRule/" + operation_id + ".json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            result = GeneralTool.update_value_in_json(data, path, new_value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Update JSON file `{file_path}` with new value `{new_value}` at path `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` with new value `{new_value}` at path `{path}`.")
        
    def _create_generation_rule_and_assertion_files(self):
        """ Create Generation Rule and Assertion Files """
        for schema in self.schema_list:
            api_doc = GeneralTool.load_schema_file(schema)
            for uri, path_item in api_doc['paths'].items():
                for method, operation in path_item.items():
                    operation_id = operation['operationId']
                    
                    # * Create the Generation Rule File
                    if 'requestBody' in operation:
                        # * WARNING: Only support the first content type now.
                        first_content_type = next(iter(operation['requestBody']['content']))
                        request_body_schema = operation['requestBody']['content'][first_content_type]['schema']
                        request_body_schema = GeneralTool().retrive_ref_schema(api_doc, request_body_schema)
                        generation_rule = GeneralTool().parse_schema_to_generation_rule(request_body_schema)              
                        with open(f"./GenerationRule/{operation_id}.json", "w") as f:
                            json.dump(generation_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have requestBody.')
                    
                    # * Create the Assertion Rule File
                    if 'responses' in operation:
                        assertion_rule = GeneralTool.parse_schema_to_assertion_rule(operation['responses'])
                        with open(f"./AssertionRule/{operation_id}.json", "w") as f:
                            json.dump(assertion_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have responses.')
         
    def btn_generation_rule_remove_clicked(self):
        """ Remove Generation Rule Item """
        
        # * If no API or Generation Rule is selected, return directly.
        if self.table_api_tree.selectedItems() == [] or self.table_generation_rule.selectedItems() == []:
            return
        
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Retrieve the Generation Rule List selected item to get the corresponding path
        for item in self.table_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
                
        # * Update the value in the JSON file
        file_path = "./GenerationRule/" + operation_id + ".json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            result = GeneralTool.remove_key_in_json(data, path)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{path}`.")
        GeneralTool.remove_table_item_from_ui(self.table_generation_rule)
        
    def btn_api_table_remove_clicked(self):
        """ Remove API Table Item """
        selected_items = self.table_api_tree.selectedItems()
        for item in selected_items:
            if item.parent() is None:
                teardown_folder = ["GenerationRule", "AssertionRule"]
                for folder in teardown_folder:  
                    for child_file in glob.glob(f"./{folder}/{item.text(0)}*.json"):
                        os.remove(child_file)
                self.table_api_tree.takeTopLevelItem(self.table_api_tree.indexOfTopLevelItem(item))
            else:
                file_name = item.text(4)
                teardown_folder = ["GenerationRule", "AssertionRule"]
                for folder in teardown_folder:
                    file_path = f"./{folder}/" + file_name + ".json"
                    if os.path.exists(file_path):
                        os.remove(file_path)
                item.parent().takeChild(item.parent().indexOfChild(item))
                # * Clear the table
                teardown_table = [self.table_requestbody_schema, self.table_generation_rule, self.table_assertion_rule,]
                for table in teardown_table: table.clear()

    def generate_test_plan(self):
        """ Generate Test Plan """
        
        # * Generate TCG Config
        config_file_path = "config/tcg_config.json"
        test_strategies = self.group_test_strategy.findChildren(QCheckBox)
        tcg_config = {
            "config": {
                "test_strategy": {
                    "positive_test": [],
                    "negative_test": []
                }
            }
        }
        for strategy in test_strategies:
            if strategy.isChecked():
                test_type = strategy.parent().title()
                name = strategy.text()
            else:
                continue
            
            if test_type == "Positive Test":
                test_type = "positive_test"
                if name == "Parameter Min./Max.":
                    name = "parameter_min_max_test"
            elif test_type == "Negative Test":
                test_type = "negative_test"
                if name == "Parameter Min./Max.":
                    name = "parameter_min_max_test" 
                    
            tcg_config["config"]["test_strategy"][test_type].append(name)
        
        with open(config_file_path, "w") as f:
            json.dump(tcg_config, f, indent=4)
            
        # * Generate Test Plan
        GeneralTool.teardown_folder_files(["./test_plan", "./TestData"])  
        serial_number = 1
        # * To obtain the included Schema List
        included_api_doc = [self.table_api_tree.topLevelItem(i).text(0) for i in range(self.table_api_tree.topLevelItemCount())]
        for openapi_file in included_api_doc:
            # * To obtain the Api Doc Path
            exts = ["json", "yaml", "yml"]
            for ext in exts:
                files = glob.glob(f"./schemas/{openapi_file}.{ext}")
                if files:
                    api_doc = GeneralTool.load_schema_file(files[0])
                    break
            # * To obtain the included api list
            included_api = GeneralTool.collect_items_from_top_level(self.table_api_tree, openapi_file, 4)
            included_api = list(filter(None, included_api))
            for uri, path_item in api_doc['paths'].items():
                for method, operation in path_item.items():
                    operation_id = operation['operationId']
                    # * If the operation id is not in the included api list, skip it.
                    if operation_id not in included_api:
                        continue
                    test_plan_path = TestStrategy.init_test_plan(uri, method, operation_id)
                    # * Call the data builder to generate base test data.
                    testdata = DataBuilder.init_test_data(operation_id)
                    for test_type in tcg_config['config']['test_strategy']:
                        for test_strategy in tcg_config['config']['test_strategy'][test_type]:
                            test_strategy_func = getattr(TestStrategy, test_strategy)
                            serial_number = test_strategy_func(test_type, operation_id ,uri, method, operation, test_plan_path, serial_number, testdata)
                            logging.info(f'Generate "{method} {uri}" "{test_type} - {test_strategy}" test case for successfully.')
                            self.tabTCG.setCurrentIndex(1)
        
        # * Render Test Plan to Table
        self.table_test_plan_api_list.clear()
        for test_plan in glob.glob("test_plan/*.yaml"):
            with open(test_plan, "r") as f:
                test_plan = yaml.load(f, Loader=yaml.FullLoader)
            file_name = test_plan['test_info']['operationId']
            toplevel_length = self.table_test_plan_api_list.topLevelItemCount()
            self.table_test_plan_api_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
            for index, test_case in test_plan['test_cases'].items():
                testcase_child = QtWidgets.QTreeWidgetItem(["", str(index), test_case['test_strategy'], test_case['test_type']])
                self.table_test_plan_api_list.topLevelItem(toplevel_length).addChild(testcase_child)
                for tp_index, test_point in test_case['test_point'].items():
                    tp_index = str(index) + "." + str(tp_index)
                    testcase_child.addChild(QtWidgets.QTreeWidgetItem(["", tp_index, "", "", test_point['parameter']['name']]))

    def import_openapi_doc(self):
        """ Import OpenAPI Doc """
        file_filter = "OpenAPI Doc (*.yaml *.yml *.json)"
        response = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self.tab, caption="Open OpenAPI Doc", directory=os.getcwd(), filter=file_filter
        )
        
        # * Clean Environment
        GeneralTool.teardown_folder_files(["./GenerationRule", "./AssertionRule"])
        teardown_table = [self.table_api_tree, self.table_requestbody_schema, self.table_generation_rule, self.table_assertion_rule,]
        for table in teardown_table: table.clear()
        
        self.schema_list = response[0]
        index = 1
        for schema in self.schema_list:
            file_path = schema
            file_name = os.path.basename(file_path).split(".")[0]
            api_doc = GeneralTool.load_schema_file(file_path)
            index = self._render_api_tree(api_doc, index, file_name)
        self._create_generation_rule_and_assertion_files()
        GeneralTool.expand_and_resize_tree(self.table_api_tree)

                    
    def _render_api_tree(self, api_doc, index, file_name):
        """ Render API Tree """
        toplevel_length = self.table_api_tree.topLevelItemCount()
        self.table_api_tree.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
        for uri, path_item in api_doc['paths'].items():
            for method, operation in path_item.items():
                self.table_api_tree.topLevelItem(toplevel_length).addChild(
                    QtWidgets.QTreeWidgetItem(["", str(index), uri, method.upper(), operation['operationId']])
                )
                index += 1
        return index
    
    def test_plan_api_list_item_clicked(self, item, column):
        """When the test plan api list item is clicked."""
        
        # * Clear the table
        tables = [self.table_setup, self.table_teardown, self.table_assertion_rule_2, self.text_body, self.textbox_dependency_requestbody]
        for table in tables:
            table.clear()
        
        # * Determine the column is top level or not
        parent = item.parent()
        if parent is None:
            test_plan_name = item.text(0)
            logging.debug(f"Test Plan Name: {test_plan_name}")
        elif parent.parent() is None:
            test_plan_name = parent.text(0)
            test_id, test_strategy, test_type = item.text(1), item.text(2), item.text(3)
            logging.debug(f"Test Case Index: {test_id}")
        else:
            test_plan_name = parent.parent().text(0)
            test_id, test_strategy, test_type, test_point = item.text(1), parent.text(2), parent.text(3), item.text(4)
            logging.debug(f"Test Point Index: {test_id}")
            with open(f"test_plan/{test_plan_name}.yaml", "r") as f:
                test_plan = yaml.load(f, Loader=yaml.FullLoader)
            test_case_id = int(test_id.split(".")[0])
            test_point_id = test_id.split(".")[1]
            
            setup_set = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['action']['setup']
            if setup_set is not None:
                for index, test_setup in setup_set.items():
                    logging.debug(f"Test Setup: {test_setup}, Index: {index}")
                    self.table_setup.addTopLevelItem(
                        QtWidgets.QTreeWidgetItem([test_setup['action_type'], test_setup['object']])
                    )
                    
            teardown_set = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['action']['teardown']
            if teardown_set is not None:
                for index, test_teardown in teardown_set.items():
                    logging.debug(f"Test Teardown: {test_teardown}, Index: {index}")
                    self.table_teardown.addTopLevelItem(
                        QtWidgets.QTreeWidgetItem([test_teardown['action_type'], test_teardown['object']])
                    )
                    
            # * Render the request body in text box.
            serial_num = test_id.split(".")[0]
            test_point = test_id.split(".")[1]
            with open(f"./TestData/{test_plan_name}_{serial_num}_{test_point}.json") as file:
                testdata = json.load(file)
            testdata_str = json.dumps(testdata, indent=4)
            self.text_body.setPlainText(testdata_str)
    
    def api_tree_item_clicked(self, item, column):
        teardown_table = [self.table_requestbody_schema, self.table_generation_rule, self.table_assertion_rule,]
        for table in teardown_table: table.clear()

        # * If the column is top level, return
        if column == 0:
            return
        
        table_path, table_method = item.text(2), item.text(3)
        logging.debug(f"Table Path: {table_path}, Table Method: {table_method}, Table Column: {column}")
        
        for schema in self.schema_list:
            file_path = schema
            api_doc = GeneralTool.load_schema_file(file_path)   
            for uri, path_item in api_doc['paths'].items():
                for method, operation in path_item.items():
                    if uri == table_path and method.upper() == table_method:
                        operation_id = operation['operationId']
                        if 'requestBody' in operation:
                            # * WARNING: Only support the first content type now.
                            first_content_type = next(iter(operation['requestBody']['content']))
                            request_body_schema = operation['requestBody']['content'][first_content_type]['schema']
                            request_body_schema = GeneralTool().retrive_ref_schema(api_doc, request_body_schema)                                
                            root_item = QTreeWidgetItem(["Request Body"])
                            self.table_requestbody_schema.addTopLevelItem(root_item)
                            GeneralTool.parse_request_body(request_body_schema, root_item, editabled=True)
                            
                            root_item_2 = QTreeWidgetItem(["Data Generation Rule"])
                            self.table_generation_rule.addTopLevelItem(root_item_2)
                            with open(f"./GenerationRule/{operation_id}.json", "r") as f:
                                generation_rule = json.load(f)
                            GeneralTool.parse_request_body(generation_rule, root_item_2, editabled=True)
                        else:
                            logging.info(f"This API {uri} does not have requestBody.")
                            
                        if 'responses' in operation:
                            root_item = QTreeWidgetItem(["Response Body"])
                            self.table_requestbody_schema.addTopLevelItem(root_item)
                            for status_code, response in operation['responses'].items():
                                if len(status_code) == 3 or status_code == 'default':
                                    # * WARNING: Only support the first content type now.
                                    first_content_type = next(iter(operation['responses'][status_code]['content']))
                                    response_body_schema = response['content'][first_content_type]['schema']
                                    response_body_schema = GeneralTool().retrive_ref_schema(api_doc, response_body_schema)
                                    sub_root_item = QTreeWidgetItem([status_code])
                                    root_item.addChild(sub_root_item)
                                    GeneralTool.parse_request_body(response_body_schema, sub_root_item, editabled=False)
                                else:
                                    logging.warning(f"API {uri} has a wrong status code {status_code}.")
                                    
                        # * Render the assertion rule from the file.
                        GeneralTool.parse_assertion_rule(operation_id, self.table_assertion_rule)
                        GeneralTool.expand_and_resize_tree(self.table_generation_rule, expand=False)
                        GeneralTool.expand_and_resize_tree(self.table_assertion_rule)
                        GeneralTool.expand_and_resize_tree(self.table_requestbody_schema)

app = QtWidgets.QApplication([])
window = MyWindow()
window.show()
app.exec()