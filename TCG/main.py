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
from PyQt6.QtCore import QStringListModel
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem, QCompleter
from lib.test_strategy import TestStrategy
from lib.general_tool import GeneralTool
from lib.DataBuilder import DataBuilder

DEBUG = False
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.DEBUG)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # * Load the UI Page
        uic.loadUi('lib/tcg_backup.ui', self)
        
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
        self.btn_api_table_add_use_case.clicked.connect(self.btn_api_table_add_use_case_clicked)
        self.btn_constraint_rule_apply.clicked.connect(self.btn_constraint_rule_apply_clicked)
        self.btn_constraint_rule_clear.clicked.connect(self.btn_constraint_rule_clear_clicked)
        self.btn_remove_path.clicked.connect(self.btn_remove_path_clicked)
        self.btn_update_path.clicked.connect(self.btn_update_path_clicked)
        self.btn_tc_remove_path.clicked.connect(self.btn_tc_remove_path_clicked)
        self.btn_tc_update_path.clicked.connect(self.btn_tc_update_path_clicked)
        self.btn_add_dependency_rule.clicked.connect(self.btn_add_dependency_rule_clicked)
        self.btn_tc_add_dependency_rule.clicked.connect(self.btn_tc_add_dependency_rule_clicked)
        self.btn_tc_remove_dependency_rule.clicked.connect(self.btn_tc_remove_dependency_rule_clicked)
        self.btn_tc_update_dependency_rule.clicked.connect(self.btn_tc_update_dependency_rule_clicked)
        self.btn_remove_dependency_rule.clicked.connect(self.btn_remove_dependency_rule_clicked)
        self.btn_update_dependency_rule.clicked.connect(self.btn_update_dependency_rule_clicked)
        self.btn_remove_dependency_path.clicked.connect(self.btn_remove_dependency_path_clicked)
        self.btn_update_dependency_path.clicked.connect(self.btn_update_dependency_path_clicked)
        self.btn_dependency_constraint_rule_clear.clicked.connect(self.btn_dependency_constraint_rule_clear_clicked)
        self.btn_dependency_constraint_rule_apply.clicked.connect(self.btn_dependency_constraint_rule_apply_clicked)
        self.btn_dependency_generation_rule_remove.clicked.connect(self.btn_dependency_generation_rule_remove_clicked)
        self.btn_tc_dependency_constraint_rule_clear.clicked.connect(self.btn_tc_dependency_constraint_rule_clear_clicked)
        self.btn_tc_dependency_constraint_rule_apply.clicked.connect(self.btn_tc_dependency_constraint_rule_apply_clicked)
        self.btn_tc_dependency_generation_rule_remove.clicked.connect(self.btn_tc_dependency_generation_rule_remove_clicked)
        self.btn_tc_dependency_generation_rule_build.clicked.connect(self.btn_tc_dependency_generation_rule_build_clicked)
        self.btn_tc_add_assertion_rule.clicked.connect(self.btn_tc_add_assertion_rule_clicked)
        self.btn_tc_update_assertion_rule.clicked.connect(self.btn_tc_update_assertion_rule_clicked)
        self.btn_tc_remove_assertion_rule.clicked.connect(self.btn_tc_remove_assertion_rule_clicked)
        
        # * Table's Item Click Event
        self.table_api_tree.itemClicked.connect(self.api_tree_item_clicked)
        self.table_test_plan_api_list.itemClicked.connect(self.test_plan_api_list_item_clicked)
        self.table_assertion_rule.itemClicked.connect(self.table_assertion_rule_item_clicked)
        self.table_generation_rule.itemClicked.connect(self.table_generation_rule_item_clicked)
        self.table_dependency_generation_rule.itemClicked.connect(self.table_dependency_generation_rule_item_clicked)
        self.table_path.itemClicked.connect(self.table_path_item_clicked)
        self.table_tc_path.itemClicked.connect(self.table_tc_path_item_clicked)
        self.list_dependency_available_api_list.itemClicked.connect(self.list_dependency_available_api_list_item_clicked)
        self.list_tc_dependency_available_api_list.itemClicked.connect(self.list_tc_dependency_available_api_list_item_clicked)
        self.table_dependency_rule.itemClicked.connect(self.table_dependency_rule_item_clicked)
        self.table_dependency_path.itemClicked.connect(self.table_dependency_path_item_clicked)
        self.table_tc_dependency.itemClicked.connect(self.table_tc_dependency_item_clicked)
        self.table_tc_assertion_rule.itemClicked.connect(self.table_tc_assertion_rule_item_clicked)
        self.table_tc_dependency_generation_rule.itemClicked.connect(self.table_tc_dependency_generation_rule_item_clicked)
        
        # * Item Changed Event
        self.table_generation_rule.itemChanged.connect(self.generation_rule_item_changed)
        self.comboBox_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_constraint_rule_src_action_changed)
        self.comboBox_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_constraint_rule_dst_action_changed)
        self.comboBox_dependency_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_dependency_constraint_rule_dst_action_changed)
        self.comboBox_dependency_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_dependency_constraint_rule_src_action_changed)
        self.comboBox_tc_dependency_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_tc_dependency_constraint_rule_src_action_changed)
        self.comboBox_tc_dependency_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_tc_dependency_constraint_rule_dst_action_changed)
        self.line_api_search.textChanged.connect(self.line_api_search_text_changed)
        self.line_tc_api_search.textChanged.connect(self.line_tc_api_search_text_changed)
        
        # * Checkbox Event
        self.checkBox_constraint_rule_wildcard.stateChanged.connect(self.checkBox_constraint_rule_wildcard_changed)
        self.checkBox_dependency_constraint_rule_wildcard.stateChanged.connect(self.checkBox_dependency_constraint_rule_wildcard_changed)
        self.checkBox_tc_dependency_constraint_rule_wildcard.stateChanged.connect(self.checkBox_tc_dependency_constraint_rule_wildcard_changed)
        
        # * Completer Event
        self.search_completer = QCompleter()
        self.line_api_search.setCompleter(self.search_completer)
        self.tc_search_completer = QCompleter()
        self.line_tc_api_search.setCompleter(self.tc_search_completer)
        
    def btn_tc_remove_dependency_rule_clicked(self):
        if len(self.table_tc_dependency.selectedItems()) == 0 or self.table_tc_dependency.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.table_tc_dependency.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.table_tc_dependency.selectedItems()[0].text(0)
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type].pop(dependency_sequence_num)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Dependency Rule {result} is removed from {operation_id}.json")

            self.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.comboBox_tc_dependency_type.setEnabled(True)
            self.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.table_tc_dependency,
                self.comboBox_tc_dependency_type,
                self.line_tc_api_search,
                self.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency)
            
        # * Remove the dependency test data file
        file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        if os.path.exists(f"./TestData/Dependency_TestData/{file_name}"):
            os.remove(f"./TestData/Dependency_TestData/{file_name}")
    
    def btn_tc_update_dependency_rule_clicked(self):
        if len(self.table_tc_dependency.selectedItems()) == 0 or self.table_tc_dependency.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.table_tc_dependency.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.table_tc_dependency.selectedItems()[0].text(0)

            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                result = GeneralTool.update_value_in_json(
                    test_plan, 
                    ["test_cases", test_case_id ,"test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "Response Name"],
                    self.textbox_tc_dependency_return_variable_name.text()
                )
                if result is not False:
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Update dependency rule in {file_path} successfully")
                else:
                    logging.error(f"Update dependency rule in {file_path} failed")

            self.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.comboBox_tc_dependency_type.setEnabled(True)
            self.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.table_tc_dependency,
                self.comboBox_tc_dependency_type,
                self.line_tc_api_search,
                self.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency)
        
    def btn_tc_add_dependency_rule_clicked(self):
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return 
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.comboBox_tc_dependency_type.currentText()
            api = self.line_tc_api_search.text()
            return_name = self.textbox_tc_dependency_return_variable_name.text()
            if api == "" or return_name == "":
                logging.error("API or Return Name is empty.")
                return
            
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                
                # * Generate the sequence number for the next rule
                # * If 'dependency_rules' is empty, the 'max' function will return the value of the 'default' parameter, i.e., 0. We then add 1 to get "1".
                # * If 'dependency_rules' is not empty, it will give us the maximum key value plus one.
                dependency_rules = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type]
                sequence_num = str(max((int(k) for k in dependency_rules.keys()), default=0) + 1)
                generation_rule, path_rule = GeneralTool.generate_dependency_data_generation_rule_and_path_rule(api)
                test_data = DataBuilder.data_builder(generation_rule)
                file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{sequence_num}.json"
                path = f"./TestData/Dependency_TestData/{file_name}"
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as test_data_file:
                    json.dump(test_data, test_data_file, indent=4)
                    logging.info(f"Generate dependency test data file: {path}")
                    
                new_value = {
                    "API": api, 
                    "Response Name": return_name, 
                    "Data Generation Rules": generation_rule if generation_rule is not None else {},
                    "Path Rules": path_rule if path_rule is not None else {},
                }
                result = GeneralTool.add_key_in_json(
                    test_plan,
                    ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type],
                    sequence_num,
                    new_value,
                )
                if result is not False:
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to add key `{['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, sequence_num, new_value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to add key `{['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, sequence_num, new_value]}`.")
                    
            self.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.comboBox_tc_dependency_type.setEnabled(True)
            self.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.textbox_tc_dependency_return_variable_name,
                self.line_tc_api_search,
                self.textbox_tc_dependency_return_variable_name,
                self.table_tc_dependency
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency)
        
    def btn_tc_add_assertion_rule_clicked(self):
        if len(self.table_test_plan_api_list.selectedItems()) == 0 or self.table_test_plan_api_list.selectedItems()[0].parent() is None:
            return
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()   
         
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                # * Generate the sequence number for the next rule
                # * If 'assertion_rules' is empty, the 'max' function will return the value of the 'default' parameter, i.e., 0. We then add 1 to get "1".
                # * If 'assertion_rules' is not empty, it will give us the maximum key value plus one.
                assertion_rules = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
                sequence_num = str(max((int(k) for k in assertion_rules.keys()), default=0) + 1)
                new_value = {
                    "Source": self.comboBox_tc_assertion_source.currentText(),
                    "Filter Expression": self.textbox_tc_assertion_rule_expression.text(),
                    "Assertion Method": self.comboBox_tc_assertion_method.currentText(),
                    "Expected Value": self.textbox_tc_assertion_rule_expected_value.text(),
                }
                result = GeneralTool.add_key_in_json(
                    test_plan,
                    ["test_cases", test_case_id, "test_point", test_point_id, "assertion"],
                    sequence_num,
                    new_value
                )
                if result is not False:
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Update assertion rule in {file_path} successfully")
                else:
                    logging.error(f"Update assertion rule in {file_path} failed")

            GeneralTool.clean_ui_content([
                self.table_tc_assertion_rule,
                self.comboBox_tc_assertion_source,
                self.comboBox_tc_assertion_method,
                self.textbox_tc_assertion_rule_expression,
                self.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.table_tc_assertion_rule.addTopLevelItem(assertion_item)
            assertion_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
            for key, item in assertion_rule.items():
                assertion_item.addChild(
                    QTreeWidgetItem(
                        [
                            key, item['Source'], 
                            item['Filter Expression'], 
                            item['Assertion Method'], 
                            item['Expected Value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule)
        
    def btn_tc_remove_assertion_rule_clicked(self):
        if len(self.table_tc_assertion_rule.selectedItems()) == 0 or self.table_tc_assertion_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            index = self.table_tc_assertion_rule.selectedItems()[0].text(0)
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["assertion"].pop(index)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Assertion Rule {result} is removed from {operation_id}.json")

            GeneralTool.clean_ui_content([
                self.table_tc_assertion_rule,
                self.comboBox_tc_assertion_source,
                self.comboBox_tc_assertion_method,
                self.textbox_tc_assertion_rule_expression,
                self.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.table_tc_assertion_rule.addTopLevelItem(assertion_item)
            assertion_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
            for key, item in assertion_rule.items():
                assertion_item.addChild(
                    QTreeWidgetItem(
                        [
                            key, item['Source'], 
                            item['Filter Expression'], 
                            item['Assertion Method'], 
                            item['Expected Value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule)
       
    def btn_tc_update_assertion_rule_clicked(self):
        if len(self.table_tc_assertion_rule.selectedItems()) == 0 or self.table_tc_assertion_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            index = self.table_tc_assertion_rule.selectedItems()[0].text(0)
            new_value = {
                "Source": self.comboBox_tc_assertion_source.currentText(),
                "Filter Expression": self.textbox_tc_assertion_rule_expression.text(),
                "Assertion Method": self.comboBox_tc_assertion_method.currentText(),
                "Expected Value": self.textbox_tc_assertion_rule_expected_value.text(),
            }
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                result = GeneralTool.update_value_in_json(
                    test_plan, 
                    ["test_cases", test_case_id ,"test_point", test_point_id, "assertion", index],
                    new_value
                )
                if result is not False:
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Update assertion rule in {file_path} successfully")
                else:
                    logging.error(f"Update assertion rule in {file_path} failed")

            GeneralTool.clean_ui_content([
                self.table_tc_assertion_rule,
                self.comboBox_tc_assertion_source,
                self.comboBox_tc_assertion_method,
                self.textbox_tc_assertion_rule_expression,
                self.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.table_tc_assertion_rule.addTopLevelItem(assertion_item)
            assertion_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
            for key, item in assertion_rule.items():
                assertion_item.addChild(
                    QTreeWidgetItem(
                        [
                            key, item['Source'], 
                            item['Filter Expression'], 
                            item['Assertion Method'], 
                            item['Expected Value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule)        
        
    def table_tc_assertion_rule_item_clicked(self, item):
        GeneralTool.clean_ui_content([
            self.comboBox_tc_assertion_source,
            self.textbox_tc_assertion_rule_expression,
            self.comboBox_tc_assertion_method,
            self.textbox_tc_assertion_rule_expected_value
        ])
        selected_item = self.table_tc_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.comboBox_tc_assertion_source.setCurrentText(parent_item.text(1))
            self.textbox_tc_assertion_rule_expression.setText(selected_item.text(2))
            self.comboBox_tc_assertion_method.setCurrentText(selected_item.text(3))
            self.textbox_tc_assertion_rule_expected_value.setText(selected_item.text(4))
        
    def btn_tc_remove_path_clicked(self):
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
    
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id = test_id.split(".")[0]
            use_case_id = test_id.split(".")[1]
            name = self.textbox_tc_path_name.text()
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(
                    data, 
                    ["test_cases", test_case_id ,"test_point", use_case_id, "path", name]
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', use_case_id, 'path', name]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', use_case_id, 'path', name]}`.")
            GeneralTool.clean_ui_content([self.textbox_tc_path_name, self.textbox_tc_path_value, self.table_tc_path])
            root_item = QTreeWidgetItem(["Path Parameter"])
            self.table_tc_path.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["path"], root_item)
            GeneralTool.expand_and_resize_tree(self.table_tc_path, expand=True)            
    
    def btn_tc_update_path_clicked(self):
        
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id, use_case_id = test_id.split(".")[0], test_id.split(".")[1]
            name = self.textbox_tc_path_name.text()
            new_value = self.textbox_tc_path_value.text()
            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.update_value_in_json(
                    data, 
                    ["test_cases", test_case_id ,"test_point", use_case_id, "path", name],
                    new_value
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to update key `{['test_cases', test_case_id, 'test_point', use_case_id, 'path', name, new_value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to update key `{['test_cases', test_case_id, 'test_point', use_case_id, 'path', name, new_value]}`.") 
            
            GeneralTool.clean_ui_content([self.textbox_tc_path_name, self.textbox_tc_path_value, self.table_tc_path])
            root_item = QTreeWidgetItem(["Path Parameter"])
            self.table_tc_path.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["path"], root_item)
            GeneralTool.expand_and_resize_tree(self.table_tc_path, expand=True)
        
        
    def table_tc_path_item_clicked(self):

        selected_item = self.table_tc_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.textbox_tc_path_name.setText(selected_item.text(0))
            self.textbox_tc_path_value.setText(selected_item.text(1))

        
    def btn_dependency_generation_rule_remove_clicked(self):
        """ Remove Generation Rule Item """
        
        # * If no API or Generation Rule is selected, return directly.
        if len(self.table_dependency_generation_rule.selectedItems()) == 0:
            return
        
        # * Retrieve the origin API Operation ID.
        api_selected_item = self.table_api_tree.selectedItems()[0]
        origin_api_operation_id = api_selected_item.text(4)
        
        # * Retrieve the Dependency Rule Index and Data Generation Rule Field name which should be removed.
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        generation_table_selected_item = self.table_dependency_generation_rule.selectedItems()[0]
        if generation_table_selected_item.parent() is None or generation_table_selected_item.parent().parent() is not None:
            return
        else:
            generation_rule_field_name = generation_table_selected_item.text(0)
            
        # * Retrieve the Generation Rule List selected item to get the corresponding path
        for item in self.table_dependency_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
                
        # * Update the value in the JSON file
        file_path = f"./DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            result = GeneralTool.remove_key_in_json(data, [dependency_type, dependency_sequence_num, "Data Generation Rules", *path])
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', *path]}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', *path]}`.")
        GeneralTool.remove_table_item_from_ui(self.table_dependency_generation_rule)
        
    def btn_dependency_constraint_rule_apply_clicked(self):
        src_action = self.comboBox_dependency_constraint_rule_src_action.currentText()
        src_path = self.textbox_dependency_constraint_rule_src.text()
        src_condition = self.comboBox_dependency_constraint_rule_condition.currentText()
        src_expected_value = self.textbox_dependency_constraint_rule_expected_value.text()
        dst_path = self.textbox_dependency_constraint_rule_dst.text()
        dst_action = self.comboBox_dependency_constraint_rule_dst_action.currentText()
        dst_action_type = self.comboBox_dependency_constraint_dst_action_type.currentText()
        dst_value = self.textbox_dependency_constraint_rule_dst_value.text()
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        
        if len(self.table_dependency_rule.selectedItems()) == 0:
            return
        else:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./DependencyRule/{operation_id}.json"
            
        if src_action == "Set":
            if src_condition == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    result = GeneralTool.update_value_in_json(
                        data, 
                        [dependency_type, dependency_sequence_num, "Data Generation Rules", src_path, "Default"],
                        src_expected_value
                    )
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully updating JSON file `{file_path}` to update key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', src_path, 'Value', src_expected_value]}`.")
                    else:
                        logging.error(f"Error updating JSON file `{file_path}` to update key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', src_path, 'Value', src_expected_value]}`.")
        elif src_action == "If":
            pass
        
        # * Post Action
        if dst_action == "Then Remove":
            with open(file_path, "r+") as f:
                data = json.load(f)
                if ".*" in dst_path:
                    result = GeneralTool.remove_key_in_json(data, [dependency_type, dependency_sequence_num, "Data Generation Rules", dst_path.split(".")[0]])
                else:
                    result = GeneralTool.remove_key_in_json(data, [dependency_type, dependency_sequence_num, "Data Generation Rules", dst_path])
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', dst_path]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', dst_path]}`.")
        elif dst_action == "Then Set":
            if dst_action_type == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    result = GeneralTool.update_value_in_json(
                        data,
                        [dependency_type, dependency_sequence_num, "Data Generation Rules", dst_path, "Default"],
                        dst_value
                    )
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully updating JSON file `{file_path}` to update key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', dst_path, 'Value', dst_value]}`.")
                    else:
                        logging.error(f"Error updating JSON file `{file_path}` to update key `{[dependency_type, dependency_sequence_num, 'Data Generation Rules', dst_path, 'Value', dst_value]}`.")
        
        # * Refresh the Dependency Generation Rule Table
        root_item = QTreeWidgetItem(["Data Generation Rule"])
        self.table_dependency_generation_rule.clear()
        self.table_dependency_generation_rule.addTopLevelItem(root_item)
        GeneralTool.parse_request_body(data[dependency_type][dependency_sequence_num]["Data Generation Rules"], root_item, editabled=True)
        GeneralTool.expand_and_resize_tree(self.table_dependency_generation_rule, 0)
        # * Clear the constraint rule UI
        GeneralTool.clean_ui_content([
            self.textbox_dependency_constraint_rule_src,
            self.textbox_dependency_constraint_rule_expected_value,
            self.textbox_dependency_constraint_rule_dst,
            self.textbox_dependency_constraint_rule_dst_value,
        ])
        self.checkBox_dependency_constraint_rule_wildcard.setChecked(False)
        self.comboBox_dependency_constraint_rule_dst_action.setCurrentText("Then Remove")
        self.comboBox_dependency_constraint_dst_action_type.setCurrentText("")
        self.comboBox_dependency_constraint_dst_action_type.setEnabled(False)
        self.textbox_dependency_constraint_rule_dst_value.setEnabled(False)
        
    def btn_dependency_constraint_rule_clear_clicked(self):
        """ Clear the Dependency Constraint Rule UI. """
        GeneralTool.clean_ui_content([
            self.textbox_dependency_constraint_rule_src, 
            self.textbox_dependency_constraint_rule_expected_value, 
            self.textbox_dependency_constraint_rule_dst, 
            self.textbox_dependency_constraint_rule_dst_value,
        ])
        self.checkBox_dependency_constraint_rule_wildcard.setChecked(False)
        
    def btn_tc_dependency_constraint_rule_clear_clicked(self):
        pass
    
    def btn_tc_dependency_constraint_rule_apply_clicked(self):
        pass
    
    def btn_tc_dependency_constraint_rule_remove_clicked(self):
        pass
    
    def btn_tc_dependency_generation_rule_build_clicked(self):
        pass   
        
    def table_dependency_path_item_clicked(self):
        
        if len(self.table_dependency_path.selectedItems()) == 0:
            return
        
        selected_item = self.table_dependency_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
        
            name = selected_item.text(0)
            value = selected_item.child(4).text(1)
            self.textbox_path_dependency_name.setText(name)
            self.textbox_path_dependency_value.setText(value)
        
    def btn_remove_dependency_path_clicked(self):
        
        if len(self.table_dependency_path.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.table_dependency_path.selectedItems()[0]
        
        name = self.textbox_path_dependency_name.text()
        value = self.textbox_path_dependency_value.text()
        
        file_path = f"./DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            path = [dependency_type, dependency_sequence_num, "Path Rules", name]
            result = GeneralTool.remove_key_in_json(data, path)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{path}`.")
                
        GeneralTool.clean_ui_content([self.textbox_path_dependency_name, self.textbox_path_dependency_value, self.table_dependency_path])
        root_item = QTreeWidgetItem(["Path Parameter"])
        self.table_dependency_path.addTopLevelItem(root_item)
        path_rule = data[dependency_type][dependency_sequence_num]["Path Rules"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.table_path, expand=True)
    
    def btn_update_dependency_path_clicked(self):
        
        if len(self.table_dependency_path.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.table_dependency_path.selectedItems()[0]
        
        name = self.textbox_path_dependency_name.text()
        value = self.textbox_path_dependency_value.text()
        
        file_path = f"./DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            path = [dependency_type, dependency_sequence_num, "Path Rules", name, "Value"]
            result = GeneralTool.update_value_in_json(data, path, value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{path}`.")
                
        GeneralTool.clean_ui_content([self.textbox_path_dependency_name, self.textbox_path_dependency_value, self.table_dependency_path])
        root_item = QTreeWidgetItem(["Path Parameter"])
        self.table_dependency_path.addTopLevelItem(root_item)
        path_rule = data[dependency_type][dependency_sequence_num]["Path Rules"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.table_path, expand=True)
        
    def table_tc_dependency_item_clicked(self):
        
        # * Render the Dependency Action's Data Generation Rule and Path Rule and Schema.
        GeneralTool.clean_ui_content([
            self.table_tc_dependency_generation_rule,
            self.textbox_tc_dependency_requestbody,
            self.table_tc_dependency_path,
            self.table_tc_dependency_schema,
            self.textbox_tc_path_dependency_name,
            self.textbox_tc_path_dependency_value,
        ])
        
        selected_item = self.table_tc_dependency.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            # * Render the Dependency Rule Mangement UI for the update action.
            self.comboBox_tc_dependency_type.setCurrentText(parent_item.text(0))
            self.line_tc_api_search.setText(selected_item.child(0).text(1))
            self.textbox_tc_dependency_return_variable_name.setText(selected_item.child(1).text(1))
            self.comboBox_tc_dependency_type.setEnabled(False)
            self.line_tc_api_search.setEnabled(False)
            
            test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_id = test_plan_selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            dependency_type = parent_item.text(0)
            api = selected_item.child(0).text(1)
            index = selected_item.text(0)
            
            with open(f"./test_plan/{operation_id}.json", "r") as f:
                data = json.load(f)["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][index]
                
            # * Render the Data Generation Rule and Path Rule and Schema.
            if "Data Generation Rules" in data:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.table_tc_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["Data Generation Rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.table_tc_dependency_generation_rule, expand=False)
            else:
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{operation_id}`.")
                
            # * Render the Path Rule
            if "Path Rules" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.table_tc_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["Path Rules"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_tc_dependency_path, expand=True)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{operation_id}`.")
        else:
            self.comboBox_tc_dependency_type.setEnabled(True)
            self.line_tc_api_search.setEnabled(True)
        
    def table_dependency_rule_item_clicked(self):
        
        # * Render the Dependency Action's Data Generation Rule and Path Rule and Schema.
        GeneralTool.clean_ui_content([
            self.table_dependency_generation_rule,
            self.table_dependency_path,
            self.table_dependency_schema,
            self.textbox_path_dependency_name,
            self.textbox_path_dependency_value,
        ])

        selected_item = self.table_dependency_rule.selectedItems()[0]
        parent_item = selected_item.parent()

        if parent_item and parent_item.parent() is None:
            # * Render the Dependency Rule Mangement UI for the update action.
            self.comboBox_dependency_type.setCurrentText(parent_item.text(0))
            self.line_api_search.setText(selected_item.child(0).text(1))
            self.textbox_dependency_return_variable_name.setText(selected_item.child(1).text(1))
            self.comboBox_dependency_type.setEnabled(False)
            self.line_api_search.setEnabled(False)
            
            api_tree_selected_item = self.table_api_tree.selectedItems()[0]
            dependency_type = parent_item.text(0)
            sequence_num = selected_item.text(0)
            origin_api_operation_id = api_tree_selected_item.text(4)
            with open(f"./DependencyRule/{origin_api_operation_id}.json", "r") as f:
                data = json.load(f)[dependency_type][sequence_num]
                
            # * Render the Data Generation Rule and Path Rule and Schema.
            if "Data Generation Rules" in data:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.table_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["Data Generation Rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.table_generation_rule, expand=False)
            else:
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
            
            # * Render the Path Rule
            if "Path Rules" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.table_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["Path Rules"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_path, expand=True)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
        else:
            self.comboBox_dependency_type.setEnabled(True)
            self.line_api_search.setEnabled(True)
        
    def btn_add_dependency_rule_clicked(self):
        """Add Dependency Rule Item"""
        
        if len(self.table_api_tree.selectedItems()) == 0:
            return
        
        operation_id = self.table_api_tree.selectedItems()[0].text(4)
        dependency_type = self.comboBox_dependency_type.currentText()
        api = self.line_api_search.text()
        return_name = self.textbox_dependency_return_variable_name.text()
        if api == "" or return_name == "":
            logging.error(f"API or Return Name is empty.")
            return
        
        file_path = f"./DependencyRule/{operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            if data[dependency_type]:
                sequence_num = max(int(key) for key in data[dependency_type].keys()) + 1
                sequence_num = str(sequence_num)
            else:
                sequence_num = '1'
            new_value = {"API": api, "Response Name": return_name,}
            result = GeneralTool.add_key_in_json(data, [dependency_type], sequence_num, new_value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Update JSON file `{file_path}` with new value `{[dependency_type, sequence_num, new_value]}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` with new value `{[dependency_type, sequence_num, new_value]}`.")
                
        self.comboBox_dependency_type.setCurrentText("Setup")
        GeneralTool.clean_ui_content([self.line_api_search, self.textbox_dependency_return_variable_name])
        GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
        GeneralTool.expand_and_resize_tree(self.table_dependency_rule)
        
        # * Generate the Data Generation Rule and Path Rule and Schema.
        self._create_dependency_generation_rule_and_path_rule(api, operation_id, dependency_type, sequence_num)
        
    def btn_remove_dependency_rule_clicked(self):
        """Remove Dependency Rule Item"""
        
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_dependency_rule.selectedItems()) == 0:
            return
        
        selected_item = self.table_dependency_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            dependency_type = self.comboBox_dependency_type.currentText()
            dependency_name = selected_item.text(0)
            file_path = f"./DependencyRule/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(data, [dependency_type, dependency_name])
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_name]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_name]}`.")
            
            self.comboBox_dependency_type.setCurrentText("Setup")
            self.comboBox_dependency_type.setEnabled(True)
            self.line_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([self.line_api_search, self.textbox_dependency_return_variable_name])
            GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule)
    
    def btn_update_dependency_rule_clicked(self):
        """Update Dependency Rule Item"""
            
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_dependency_rule.selectedItems()) == 0:
            return
        
        selected_item = self.table_dependency_rule.selectedItems()[0]
        selected_item_api_name = selected_item.child(0).text(1)
        parent_item = selected_item.parent()

        if parent_item and parent_item.parent() is None:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            dependency_type = self.comboBox_dependency_type.currentText()
            api = self.line_api_search.text()
            if api != selected_item_api_name:
                logging.error(f"API name cannot be changed.")
                return
            return_name = self.textbox_dependency_return_variable_name.text()
            file_path = f"./DependencyRule/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                sequence_num = selected_item.text(0)
                
                updates = {"API": api, "Response Name": return_name}
                for key, value in updates.items():
                    result = GeneralTool.update_value_in_json(data, [dependency_type, sequence_num, key], value)
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully updating JSON file `{file_path}` to update key `{[dependency_type, sequence_num, key, value]}`.")
                    else:
                        logging.error(f"Error updating JSON file `{file_path}` to update key `{[dependency_type, sequence_num, key, value]}`.")
            
            self.comboBox_dependency_type.setCurrentText("Setup")
            self.comboBox_dependency_type.setEnabled(True)
            self.line_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.line_api_search,
                self.textbox_dependency_return_variable_name,
                self.table_dependency_schema,
                self.table_dependency_path,
                self.table_dependency_generation_rule,
                self.textbox_path_dependency_name,
                self.textbox_path_dependency_value,  
            ])
            GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule)

    def line_api_search_text_changed(self):
        """ When the text in the line_api_search is changed to trigger this event. """
        for api in range(self.list_dependency_available_api_list.count()):
            if self.line_api_search.text() in self.list_dependency_available_api_list.item(api).text():
                self.list_dependency_available_api_list.setCurrentItem(self.list_dependency_available_api_list.item(api))
                break
            
    def line_tc_api_search_text_changed(self):
        for api in range(self.list_tc_dependency_available_api_list.count()):
            if self.line_tc_api_search.text() in self.list_tc_dependency_available_api_list.item(api).text():
                self.list_tc_dependency_available_api_list.setCurrentItem(self.list_tc_dependency_available_api_list.item(api))
                break
        
    def list_dependency_available_api_list_item_clicked(self):
        """ When the item in the list_dependency_available_api_list is clicked. """
        api_name = self.list_dependency_available_api_list.selectedItems()[0].text()
        self.line_api_search.setText(api_name)
        
    def list_tc_dependency_available_api_list_item_clicked(self):
        """ When the item in the list_tc_dependency_available_api_list is clicked. """
        api_name = self.list_tc_dependency_available_api_list.selectedItems()[0].text()
        self.line_tc_api_search.setText(api_name)
    
    def table_path_item_clicked(self):
        selected_item = self.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is None:
            self.textbox_path_name.setText(selected_item.text(0))
            self.textbox_path_value.setText(selected_item.child(4).text(1))
        else:
            return
        
    def btn_update_path_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_path.selectedItems()) == 0:
            return
        
        selected_item = self.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.textbox_path_name.text(), self.textbox_path_value.text(), self.table_api_tree.selectedItems()[0].text(4)      
            file_path = f"./PathRule/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.update_value_in_json(data, [name, "Value"], value)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to update key `{[name, value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to update key `{[name, value]}`.")
            
            GeneralTool.clean_ui_content([self.textbox_path_name, self.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.table_path)
            GeneralTool.expand_and_resize_tree(self.table_path)
    
    def btn_remove_path_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_path.selectedItems()) == 0:
            return

        selected_item = self.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name = self.textbox_path_name.text()
            operation_id = self.table_api_tree.selectedItems()[0].text(4) 
            file_path = f"./PathRule/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(data, [name])
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[name]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{[name]}`.")
        
            GeneralTool.clean_ui_content([self.textbox_path_name, self.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.table_path)
            GeneralTool.expand_and_resize_tree(self.table_path)
        
    def checkBox_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.textbox_constraint_rule_dst, self.checkBox_constraint_rule_wildcard, self.textbox_constraint_rule_dst)
        
    def checkBox_dependency_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.textbox_dependency_constraint_rule_dst, self.checkBox_dependency_constraint_rule_wildcard, self.textbox_dependency_constraint_rule_dst)

    def checkBox_tc_dependency_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.textbox_tc_dependency_constraint_rule_dst, self.checkBox_tc_dependency_constraint_rule_wildcard, self.textbox_tc_dependency_constraint_rule_dst)
        
    def comboBox_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.comboBox_constraint_rule_src_action, self.comboBox_constraint_rule_condition)
            
    def comboBox_dependency_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.comboBox_dependency_constraint_rule_src_action, self.comboBox_dependency_constraint_rule_condition)
            
    def comboBox_tc_dependency_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.comboBox_tc_dependency_constraint_rule_src_action, self.comboBox_tc_dependency_constraint_rule_condition)
            
    def comboBox_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.comboBox_constraint_rule_dst_action,
            self.comboBox_constraint_dst_action_type,
            self.textbox_constraint_rule_dst_value,
            self.checkBox_constraint_rule_wildcard
        )
            
    def comboBox_dependency_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.comboBox_dependency_constraint_rule_dst_action,
            self.comboBox_dependency_constraint_dst_action_type,
            self.textbox_dependency_constraint_rule_dst_value,
            self.checkBox_dependency_constraint_rule_wildcard
        )
            
    def comboBox_tc_dependency_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.comboBox_tc_dependency_constraint_rule_dst_action,
            self.comboBox_tc_dependency_constraint_dst_action_type,
            self.textbox_tc_dependency_constraint_rule_dst_value,
            self.checkBox_tc_dependency_constraint_rule_wildcard
        )
      
    def btn_constraint_rule_clear_clicked(self):
        """ Clear the Constraint Rule UI. """
        for clean_item in [
            self.textbox_constraint_rule_src, 
            self.textbox_constraint_rule_expected_value, 
            self.textbox_constraint_rule_dst, 
            self.textbox_constraint_rule_dst_value,
        ]:
            clean_item.clear()
        self.checkBox_constraint_rule_wildcard.setChecked(False)

    def btn_constraint_rule_apply_clicked(self):
        src_action = self.comboBox_constraint_rule_src_action.currentText()
        src_path = self.textbox_constraint_rule_src.text()
        src_condition = self.comboBox_constraint_rule_condition.currentText()
        src_expected_value = self.textbox_constraint_rule_expected_value.text()
        dst_path = self.textbox_constraint_rule_dst.text()
        dst_action = self.comboBox_constraint_rule_dst_action.currentText()
        dst_action_type = self.comboBox_constraint_dst_action_type.currentText()
        dst_value = self.textbox_constraint_rule_dst_value.text()
        
        if len(self.table_api_tree.selectedItems()) == 0 or self.table_api_tree.selectedItems()[0].parent() is None:
            return
        else:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./GenerationRule/{operation_id}.json"
            if os.path.exists(file_path) is False:
                return
            
        # * Pre Action
        if src_action == "Set":
            # * This mode is used to set the fixed value of the field in the generation rule.
            if src_condition == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)     
                    result = GeneralTool.update_value_in_json(data, [src_path, "Default"], src_expected_value)
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Update JSON file `{file_path}` with new value `{[src_path, src_expected_value]}`.")
                    else:
                        logging.error(f"Error updating JSON file `{file_path}` with new value `{[src_path, src_expected_value]}`.")
        elif src_action == "If":
            # * This mode is used to determine whether the field in the generation rule meets the condition.
            pass
        
        # * Post Action   
        if dst_action == "Then Remove":
            with open(file_path, "r+") as f:
                data = json.load(f)
                if ".*" in dst_path:
                    result = GeneralTool.remove_wildcard_field_in_generation_rule(data, [dst_path])
                else:
                    result = GeneralTool.remove_key_in_json(data, [dst_path])
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[dst_path]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{[dst_path]}`.")
        elif dst_action == "Then Set":
            if dst_action_type == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    result = GeneralTool.update_value_in_json(data, [dst_path, "Default"], dst_value)
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully updating JSON file `{file_path}` to set key `{[dst_path, dst_value]}`.")
                    else:
                        logging.error(f"Error updating JSON file `{file_path}` to set key `{[dst_path, dst_value]}`.")
        
        # * Refresh the Generation Rule Table
        GeneralTool.refresh_generation_rule_table(self.table_api_tree, self.table_generation_rule, file_path)
        GeneralTool.expand_and_resize_tree(self.table_generation_rule, 0)
        # * Teardown the Constraint Rule UI
        for clean_item in [
            self.textbox_constraint_rule_src, 
            self.textbox_constraint_rule_expected_value,
            self.textbox_constraint_rule_dst, 
            self.textbox_constraint_rule_dst_value,
        ]:
            clean_item.clear()
        self.checkBox_constraint_rule_wildcard.setChecked(False)
            
    def table_generation_rule_item_clicked(self):
        """ 
        When the user click the item in the table_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.table_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item,
            self.textbox_constraint_rule_src, 
            self.textbox_constraint_rule_expected_value, 
            self.textbox_constraint_rule_dst,
            self.textbox_constraint_rule_dst_value, 
            self.checkBox_constraint_rule_wildcard,
        )
                 
    def table_dependency_generation_rule_item_clicked(self):
        """ 
        When the user click the item in the table_dependency_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.table_dependency_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item, 
            self.textbox_dependency_constraint_rule_src, 
            self.textbox_dependency_constraint_rule_expected_value, 
            self.textbox_dependency_constraint_rule_dst,
            self.textbox_dependency_constraint_rule_dst_value, 
            self.checkBox_dependency_constraint_rule_wildcard
        )
        
    def table_tc_dependency_generation_rule_item_clicked(self):
        selected_item = self.table_tc_dependency_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item,
            self.textbox_tc_dependency_constraint_rule_src,
            self.textbox_tc_dependency_constraint_rule_expected_value,
            self.textbox_tc_dependency_constraint_rule_dst,
            self.textbox_tc_dependency_constraint_rule_dst_value,
            self.checkBox_tc_dependency_constraint_rule_wildcard,
        )
                
    def table_tc_dependency_generation_rule_item_clicked(self):
        """
        When the user click the item in the table_tc_dependency_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.table_tc_dependency_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item,
            self.textbox_tc_dependency_constraint_rule_src,
            self.textbox_tc_dependency_constraint_rule_expected_value,
            self.textbox_tc_dependency_constraint_rule_dst,
            self.textbox_tc_dependency_constraint_rule_dst_value,
            self.checkBox_tc_dependency_constraint_rule_wildcard,
        )

    def btn_api_table_add_use_case_clicked(self):
        """ 這個 Add Button 是用來複製已有的第一層 API 的, 並且要把 Generation Rule 和 Assertion Rule 和 Dependency Request Body 也複製過去. """
        # * To get the selected api item, and copy it.
        if len(self.table_api_tree.selectedItems()) == 0:
            return
        else:
            selected_item = self.table_api_tree.selectedItems()[0]
            parent_item = selected_item.parent()
            
        if parent_item is not None and parent_item.parent() is not None:
            print("This is layer 3 item.")        
        elif parent_item is not None:
            # * Check if the selected item's sub item is already exist.
            if selected_item.childCount() > 0:
                # * To get the last serial number of the selected item's sub item.
                last_serial_num = selected_item.child(selected_item.childCount() - 1).text(1)
                new_serial_num = f"{selected_item.text(1)}.{int(last_serial_num.split('.')[1]) + 1}"
            else:
                new_serial_num = f"{selected_item.text(1)}.1"
            new_operation_id = f"{selected_item.text(4)}_{new_serial_num}"
  
            # * Copy the API Item to the selected item's below
            use_case_item = QtWidgets.QTreeWidgetItem(["", new_serial_num, None, None, new_operation_id])
            selected_item.addChild(use_case_item)
            
            # * Copy the Generation Rule and Assertion Rule and Dependency Request Body and Path Rule
            operation_id = selected_item.text(4)
            for folder in ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule"]:
                file_path = f"./{folder}/{operation_id}.json"
                if os.path.exists(file_path):
                    new_file_path = f"./{folder}/{new_operation_id}.json"
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    with open(new_file_path, "w") as f:
                        json.dump(data, f, indent=4)
                else:
                    continue
            logging.info(f"Create a new use case `{new_operation_id}` from `{operation_id}`.")

    
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
                
    def _create_dependency_generation_rule_and_path_rule(
        self, 
        api_name : str, 
        original_operation_id : str,
        dependency_type : str,
        sequence_num : str,
    ):
        """Create Dependency's Data Generation Rule and Path Rule Files and Schema File.

        Args:
            api_name: Which API to create the G_Rule and P_Rule and Schema File.
            original_operation_id: Which original API to create this dependency API.
        """
        generation_rule, path_rule = GeneralTool.generate_dependency_data_generation_rule_and_path_rule(api_name)
        
        if generation_rule != None:
            with open(f"./DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num],"Data Generation Rules" , generation_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'Data Generation Rules']}`.")
                else:
                    logging.error(f"Error updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'Data Generation Rules']}`.")
                
        if path_rule != None:
            with open(f"./DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "Path Rules", path_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'Path Rules']}`.")
                else:
                    logging.error(f"Error updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'Path Rules']}`.")    
        
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
                        
                    # * Create the Path Rule File
                    if 'parameters' in operation:
                        path_rule = GeneralTool.parse_schema_to_path_rule(operation['parameters'])
                        with open(f"./PathRule/{operation_id}.json", "w") as f:
                            json.dump(path_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have parameters.')
                        
                    # * Create the Dependency Rule File
                    dependency_rule = GeneralTool.init_dependency_rule(operation_id)       
         
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
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule"]
                for folder in teardown_folder:  
                    for child_file in glob.glob(f"./{folder}/{item.text(0)}*.json"):
                        os.remove(child_file)
                self.table_api_tree.takeTopLevelItem(self.table_api_tree.indexOfTopLevelItem(item))
            else:
                file_name = item.text(4)
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule"]
                for folder in teardown_folder:
                    file_path = f"./{folder}/" + file_name + ".json"
                    if os.path.exists(file_path):
                        os.remove(file_path)
                item.parent().takeChild(item.parent().indexOfChild(item))
                # * Clear the table
                teardown_table = [self.table_schema, self.table_generation_rule, self.table_assertion_rule,]
                for table in teardown_table: table.clear()

    def generate_test_plan(self):
        """ Generate Test Plan """
        
        # * Generate TCG Config
        GeneralTool.generate_tcg_config(self.group_test_strategy.findChildren(QCheckBox))
        with open(f"config/tcg_config.json", "r") as f:
            tcg_config = json.load(f)
            
        # * Generate Test Plan
        GeneralTool.teardown_folder_files(["./test_plan", "./TestData"])  
        serial_number = 1
        for i in range(self.table_api_tree.topLevelItemCount()):
            schema_item = self.table_api_tree.topLevelItem(i)
            # * To obtain the Api Doc Path
            exts = ["json", "yaml", "yml"]
            for ext in exts:
                files = glob.glob(f"./schemas/{schema_item.text(0)}.{ext}")
                if files:
                    schema = GeneralTool.load_schema_file(files[0])
                    break
            for api_i in range(schema_item.childCount()):
                api_item = schema_item.child(api_i)
                target_operation_id = api_item.text(4)
                for uri, path_item in schema['paths'].items():
                        for method, operation in path_item.items():
                            operation_id = operation['operationId']
                            if operation_id == target_operation_id:                
                                if api_item.childCount() == 0:
                                    test_plan_path = TestStrategy.init_test_plan(uri, method, operation_id)
                                    testdata = DataBuilder.init_test_data(operation_id)
                                    dependency_testdata = DataBuilder.init_dependency_test_data(operation_id)
                                    GeneralTool.generate_test_cases(
                                        tcg_config, TestStrategy, operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata
                                    )
                                elif api_item.childCount() > 0:
                                    for use_case_i in range(api_item.childCount()):
                                        use_case_item = api_item.child(use_case_i)
                                        use_case_operation_id = use_case_item.text(4)
                                        test_plan_path = TestStrategy.init_test_plan(uri, method, use_case_operation_id)
                                        testdata = DataBuilder.init_test_data(use_case_operation_id)
                                        dependency_testdata = DataBuilder.init_dependency_test_data(use_case_operation_id)
                                        GeneralTool.generate_test_cases(
                                            tcg_config, TestStrategy, use_case_operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata
                                        )
                                self.tabTCG.setCurrentIndex(1)
        
        # * Render Test Plan to Table
        GeneralTool.clean_ui_content([
            self.table_test_plan_api_list,
            self.table_tc_assertion_rule,
            self.table_tc_dependency,
            self.table_tc_dependency_path,
            self.table_tc_dependency_generation_rule,
            self.textbox_tc_dependency_requestbody,
            self.table_tc_path,
            self.text_body,
        ])
        self.table_test_plan_api_list.clear()
        for test_plan in glob.glob("test_plan/*.json"):
            with open(test_plan, "r") as f:
                test_plan = json.load(f)
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
        GeneralTool.teardown_folder_files(["./GenerationRule", "./AssertionRule", "./PathRule", "./DependencyRule"])
        GeneralTool.clean_ui_content([
            self.table_api_tree, 
            self.table_schema, 
            self.table_generation_rule, 
            self.table_assertion_rule, 
            self.list_dependency_available_api_list,
            self.list_tc_dependency_available_api_list,
        ])
        
        self.schema_list = response[0]
        index = 1
        for schema in self.schema_list:
            file_path = schema
            file_name = os.path.basename(file_path).split(".")[0]
            api_doc = GeneralTool.load_schema_file(file_path)
            index = self._render_api_tree(api_doc, index, file_name)
        self._create_generation_rule_and_assertion_files()
        GeneralTool.expand_and_resize_tree(self.table_api_tree)
        
        # * Update Search Completion List
        all_api_list = []
        for i in range(self.list_dependency_available_api_list.count()):
            all_api_list.append(self.list_dependency_available_api_list.item(i).text())
        model = QStringListModel()
        model.setStringList(all_api_list)
        self.search_completer.setModel(model)
        
        all_tc_api_list = []
        for i in range(self.list_tc_dependency_available_api_list.count()):
            all_tc_api_list.append(self.list_tc_dependency_available_api_list.item(i).text())
        tc_model = QStringListModel()
        tc_model.setStringList(all_tc_api_list)
        self.tc_search_completer.setModel(tc_model)     
                     
    def _render_api_tree(self, api_doc, index, file_name):
        """ Render API Tree """
        toplevel_length = self.table_api_tree.topLevelItemCount()
        self.table_api_tree.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
        for uri, path_item in api_doc['paths'].items():
            for method, operation in path_item.items():
                self.table_api_tree.topLevelItem(toplevel_length).addChild(
                    QtWidgets.QTreeWidgetItem(["", str(index), uri, method.upper(), operation['operationId']])
                )
                # * Render the Available API List
                self.list_dependency_available_api_list.addItem(f"{method.upper()} {uri}")
                self.list_tc_dependency_available_api_list.addItem(f"{method.upper()} {uri}")
                index += 1
        return index
    
    def test_plan_api_list_item_clicked(self, item, column):
        """When the test plan api list item is clicked."""
        
        # * Clear the table
        GeneralTool.clean_ui_content([
            self.table_tc_dependency, self.table_tc_assertion_rule, self.text_body, self.textbox_tc_dependency_requestbody, self.table_tc_dependency_path,
            self.table_tc_path, self.textbox_tc_path_name, self.textbox_tc_path_value, self.table_tc_dependency, self.table_tc_dependency_generation_rule
        ])
        
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
            with open(f"test_plan/{test_plan_name}.json", "r") as f:
                test_plan = json.load(f)
            test_case_id = test_id.split(".")[0]
            test_point_id = test_id.split(".")[1]
            
            # * Render the Test Case Dependency Rule.
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency)
            
            # * Render the Path Rule.
            path_item = QTreeWidgetItem(["Path Parameters"])
            self.table_tc_path.addTopLevelItem(path_item)
            path_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['path']
            for key, value in path_rule.items():
                path_item.addChild(QTreeWidgetItem([key, value]))
            GeneralTool.expand_and_resize_tree(self.table_tc_path)
            
            # * Render the Assertion Rule.
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.table_tc_assertion_rule.addTopLevelItem(assertion_item)
            assertion_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
            for key, item in assertion_rule.items():
                assertion_item.addChild(
                    QTreeWidgetItem(
                        [
                            key, item['Source'], 
                            item['Filter Expression'], 
                            item['Assertion Method'], 
                            item['Expected Value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule)
                    
            # * Render the request body in text box.
            serial_num = test_id.split(".")[0]
            test_point = test_id.split(".")[1]
            with open(f"./TestData/{test_plan_name}_{serial_num}_{test_point}.json") as file:
                testdata = json.load(file)
            testdata_str = json.dumps(testdata, indent=4)
            self.text_body.setPlainText(testdata_str)
    
    def api_tree_item_clicked(self, item, column):
        """When the api tree item is clicked."""
        # * Clear the table
        GeneralTool.clean_ui_content([
            self.table_schema,
            self.table_generation_rule, 
            self.table_assertion_rule, 
            self.table_path,
            self.table_dependency_rule,
            self.table_dependency_path,
            self.table_dependency_generation_rule,
            self.table_dependency_schema,
            self.line_api_search,
            self.textbox_dependency_return_variable_name,
        ])
        self.comboBox_dependency_type.setEnabled(True)
        self.line_api_search.setEnabled(True)
        
        # * If the column is top level, return
        if column == 0:
            return
        
        # * If the use case item is clicked.
        selected_item = self.table_api_tree.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is not None:
            
            # * Render the Generation Rule from the file.
            # * Some API does not have requestBody, so the generation rule file does not exist.
            # * Ex : GET, DELETE, etc.
            operation_id = selected_item.text(4)
            generation_rule_file = f"./GenerationRule/{operation_id}.json"
            if os.path.exists(generation_rule_file):
                root_item_2 = QTreeWidgetItem(["Data Generation Rule"])
                self.table_generation_rule.addTopLevelItem(root_item_2)
                with open(generation_rule_file, "r") as f:
                    generation_rule = json.load(f)
                GeneralTool.parse_request_body(generation_rule, root_item_2, editabled=True)
                GeneralTool.expand_and_resize_tree(self.table_generation_rule, expand=False)
            else:
                logging.warning(f"Generation Rule file `{generation_rule_file}` does not exist or not supported.")
            
            # * Render the Assertion Rule from the file.
            GeneralTool.parse_assertion_rule(operation_id, self.table_assertion_rule)
            GeneralTool.expand_and_resize_tree(self.table_assertion_rule)
            
            # * Render the Path Rule from the file.
            GeneralTool.parse_path_rule(operation_id, self.table_path)
            GeneralTool.expand_and_resize_tree(self.table_path)
            
            # * Render the Dependency Rule from the file.
            GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule)
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
                            self.table_schema.addTopLevelItem(root_item)
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
                            self.table_schema.addTopLevelItem(root_item)
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
                        GeneralTool.expand_and_resize_tree(self.table_schema)
                        
                        # * Render the Path Rule from the file.
                        GeneralTool.parse_path_rule(operation_id, self.table_path)
                        GeneralTool.expand_and_resize_tree(self.table_path)
                        
                        # * Render the Dependency Rule from the file.
                        GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
                        GeneralTool.expand_and_resize_tree(self.table_dependency_rule)
                        
app = QtWidgets.QApplication([])
window = MyWindow()
window.show()
app.exec()
