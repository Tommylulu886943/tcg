import sys
import os
import json
import yaml
import logging
import glob

from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem, QLineEdit, QListWidget, QPlainTextEdit, QMessageBox, QTextBrowser, QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QAbstractItemView, QFileDialog

class GeneralTool:
    
    @classmethod
    def rander_robot_file_list(
        cls, 
        robot_file_list: object,
    ) -> None:
        """ To render the all robot files in the Robot File List. """
        
        for robot_file in glob.glob("./TestCases/RESTful_API/*.robot"):
            file_name = os.path.basename(robot_file)
            root_item = QTreeWidgetItem([file_name])
            robot_file_list.addTopLevelItem(root_item)    
    
    @classmethod
    def update_tc_dependency_rule_index(
        cls, ui, operation_id, test_case_id, test_point_id, dependency_type, src_key, swap_type
    ):
        with open(f"./test_plan/{operation_id}.json", "r") as f:
            d_rule = json.load(f)
        
        dependency_keys = list(d_rule['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type].keys())
        key1_index = dependency_keys.index(src_key)
        if swap_type == "up":
            replace_key = dependency_keys[key1_index - 1] if key1_index - 1 >= 0 else None
        elif swap_type == "down":
            replace_key = dependency_keys[key1_index + 1] if key1_index < len(dependency_keys) - 1 else None

        if replace_key is None:
            logging.warning(f"The dependency rule index can't be swapped.")
            return
             
        d_type_rule = d_rule['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type]
        d_type_rule = cls.swap_dict_keys(d_type_rule, src_key, replace_key)
        
        with open(f"./test_plan/{operation_id}.json", "w") as f:
            json.dump(d_rule, f, indent=4)

        cls.clean_ui_content([
            ui.line_tc_api_search,
            ui.textbox_tc_dependency_return_variable_name,
            ui.table_tc_dependency_generation_rule,
            ui.textbox_tc_dependency_requestbody,
            ui.table_tc_dependency_path,
            ui.table_tc_dependency_schema,
        ])
        ui.comboBox_tc_dependency_type.setEnabled(True)
        ui.line_tc_api_search.setEnabled(True)
        ui.list_tc_dependency_available_api_list.clearSelection()
        ui.table_tc_dependency_rule.clearSelection()
        cls.render_dependency_rule(d_rule, test_case_id, test_point_id, ui.table_tc_dependency_rule)
        cls.expand_and_resize_tree(ui.table_tc_dependency_rule)
                
    @classmethod
    def update_dependency_rule_index(cls, ui, operation_id, dependency_type, src_key, swap_type):
        with open(f"./DependencyRule/{operation_id}.json", "r") as f:
            d_rule = json.load(f)

        dependency_keys = list(d_rule[dependency_type].keys())
        key1_index = dependency_keys.index(src_key)
        if swap_type == "up":
            replace_key = dependency_keys[key1_index - 1] if key1_index - 1 >= 0 else None
        elif swap_type == "down":
            replace_key = dependency_keys[key1_index + 1] if key1_index < len(dependency_keys) - 1 else None

        if replace_key is None:
            logging.warning(f"The dependency rule index can't be swapped.")
            return

        d_rule[dependency_type] = cls.swap_dict_keys(d_rule[dependency_type], src_key, replace_key)

        with open(f"./DependencyRule/{operation_id}.json", "w") as f:
            json.dump(d_rule, f, indent=4)

        cls.clean_ui_content([
            ui.line_api_search,
            ui.textbox_dependency_return_variable_name,
            ui.table_dependency_generation_rule,
            ui.table_dependency_path,
            ui.table_dependency_schema,
            ui.table_dependency_rule
        ])
        ui.comboBox_dependency_type.setEnabled(True)
        ui.list_dependency_available_api_list.clearSelection()
        cls.parse_dependency_rule(operation_id, ui.table_dependency_rule)
        cls.expand_and_resize_tree(ui.table_dependency_rule)
        
    @classmethod
    def swap_dict_keys(cls, dict_data, key1, key2):
        if key1 in dict_data and key2 in dict_data:
            dict_data[key1], dict_data[key2] = dict_data[key2], dict_data[key1]
        return dict_data
        
    @classmethod
    def _retrieve_obj_and_action(cls, api: str) -> str:
        """ Use the OpenAPI notation to retrieve the object name and action name from obj_mapping. """
        
        with open('./config/obj_mapping.json', 'r') as f:
            obj_mapping = json.load(f)
            
        expected_method = api.split(" ")[0].lower()
        expected_uri = api.split(" ")[1]
        
        # If the uri included the path variable. Should add the $ before the path variable.
        if "{" in expected_uri and "}" in expected_uri:
            expected_uri = expected_uri.replace("{", "${")

        for obj_name, action_set in obj_mapping.items():
            for action, uri in action_set.items():
                method = action.split(' ')[0].lower()
                if uri == expected_uri and method == expected_method:
                    return obj_name, action
    
    @classmethod
    def show_error_dialog(cls, error_message: str, detailed_message: str) -> None:
        """ Pop up an error dialog. """
        app = QApplication.instance()
        
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(error_message)
        error_box.setDetailedText(detailed_message)
        error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_box.exec()
        
    @classmethod
    def show_info_dialog(cls, info_message: str) -> None:
        """ Pop up an information dialog. """
        
        info = QMessageBox()
        info.setIcon(QMessageBox.Icon.Information)
        info.setWindowTitle("Information")
        info.setText(info_message)
        info.setStandardButtons(QMessageBox.StandardButton.Ok)
        info.exec()

    @classmethod
    def apply_constraint_rule(
        cls,
        operation_id: str,
        src_action: str,
        src_path: str,
        src_condition: str,
        src_expected_value: str,
        dst_action: str,
        dst_path: str,
        dst_action_type: str,
        dst_value: str,
        dependency_type: str = None,
        dependency_sequence_num: str = None,
        is_dependency: bool = False,
        test_case_id: str = None,
        test_point_id: str = None,
        is_general_dependency: bool = False,
    ) -> None:
        
        if is_general_dependency:
            file_path = f"./DependencyRule/{operation_id}.json"
        elif is_dependency:
            file_path = f"./test_plan/{operation_id}.json"
        else:
            file_path = f"./GenerationRule/{operation_id}.json"
        
        if src_action == "Set":
            if src_condition == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    if is_general_dependency:
                        path = [dependency_type, dependency_sequence_num, "data_generation_rules", src_path, "Default"]
                    elif is_dependency:
                        path = ["test_cases", test_case_id, "test_point", test_point_id, "dependency", 
                                    dependency_type, dependency_sequence_num, "data_generation_rules", src_path, "Default"]
                    else:
                        path = [src_path, "Default"]
                    result = cls.update_value_in_json(data, path, src_expected_value)
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Update constraint rule: {path} = {src_expected_value}")
                    else:
                        logging.error(f"Update constraint rule failed: {path} = {src_expected_value}")

        if dst_action == "Then Remove":
            with open(file_path, "r+") as f:
                data = json.load(f)
                if is_general_dependency:
                    if ".*" in dst_path:
                        path = [dependency_type, dependency_sequence_num, "data_generation_rules", dst_path.split('.*')[0]]
                    else:
                        path = [dependency_type, dependency_sequence_num, "data_generation_rules", dst_path]
                elif is_dependency:
                    if ".*" in dst_path:
                        path = ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', 
                                    dependency_type, dependency_sequence_num, 'data_generation_rules', dst_path.split('.*')[0]]
                    else:
                        path = ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', 
                                    dependency_type, dependency_sequence_num, 'data_generation_rules', dst_path]

                else:
                    path = [dst_path]
                if ".*" in dst_path:
                    if is_general_dependency or is_dependency:
                        result = cls.remove_key_in_json(data, path)
                    else:
                        result = cls.remove_wildcard_field_in_generation_rule(data, path)
                else:
                    result = cls.remove_key_in_json(data, path)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Remove constraint rule: {path}")
                else:
                    logging.error(f"Remove constraint rule failed: {path}")

        elif dst_action == "Then Set":
            if dst_action_type == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    if is_general_dependency:
                        path = [dependency_type, dependency_sequence_num, "data_generation_rules", dst_path, "Default"]
                    elif is_dependency:
                        path = ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency',
                                    dependency_type, dependency_sequence_num, 'data_generation_rules', dst_path, 'Default']
                    else:
                        path = [dst_path, "Default"]
                    result = cls.update_value_in_json(data, path, dst_value)
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Update constraint rule: {path} = {dst_value}")
                    else:
                        logging.error(f"Update constraint rule failed: {path} = {dst_value}")

    @classmethod
    def update_dependency_wildcard(
        cls,
        constraint_rule_dst: object,
        checkbox_wildcard: object,
        textbox_dst_rule: object,
    ) -> None:
        dst_path = constraint_rule_dst.text()
        if checkbox_wildcard.isChecked():
            if dst_path != "":
                dst_path = dst_path.split(".")[0] + ".*"
        else:
            if ".*" in dst_path:
                dst_path = dst_path.replace(".*", "")
        textbox_dst_rule.setText(dst_path)
        
    @classmethod
    def update_constraint_actions_src(
        cls,
        src_action: object,
        constraint_rule_condition: object,
    ) -> None:
        
        current_text = src_action.currentText()
        constraint_rule_condition.clear()
        if current_text == "If":
            constraint_rule_condition.addItems(["==", "!=", ">", "<", ">=", "<="])
        elif current_text == "Set":
            constraint_rule_condition.addItems(["WITH"])        
    
    @classmethod
    def update_constraint_actions_dst(
        cls,
        dst_action: object,
        dst_action_type: object,
        dst_value: object,
        wildcard: object, 
    ) -> None:
        
        current_text = dst_action.currentText()
        cls.clean_ui_content([dst_action_type, dst_value, wildcard])
        if current_text == "Then Set":
            dst_action_type.setEnabled(True)
            index = dst_action_type.findText("WITH")
            if index >= 0:
                dst_action_type.setCurrentIndex(index)
            else:
                dst_action_type.addItems(["WITH"])
                dst_action_type.setCurrentIndex(index)
            dst_value.setEnabled(True)
            wildcard.setEnabled(False)
            
        elif current_text == "Then Remove":
            dst_action_type.setCurrentIndex(0)
            dst_action_type.setEnabled(False)
            dst_value.setEnabled(False)
            wildcard.setEnabled(True)
            
    @classmethod
    def generate_dependency_data_generation_rule_and_path_rule(cls, api_name: str) -> dict | None:
        try:
            api_method, api_uri = api_name.split(" ")[0].lower(), api_name.split(" ")[1]
        except Exception as e:
            logging.error(f"API name format error: {api_name}")
            return None
        for schema in glob.glob("./schemas/*.json") + glob.glob("./schemas/*.yaml"):
            api_doc = cls.load_schema_file(schema)
            for uri, path_item in api_doc['paths'].items():
                if uri == api_uri:
                    for method, operation in path_item.items():
                        if method == api_method:
                            operation_id = operation['operationId']
                            
                            # * Create the Data Generation Rule File
                            generation_rule = None
                            if method in ["post", "put", "patch", "delete"] and 'requestBody' in operation:
                                # * WARNING: Only support the first content type now.
                                first_content_type = next(iter(operation['requestBody']['content']))
                                request_body_schema = operation['requestBody']['content'][first_content_type]['schema']
                                request_body_schema = cls.retrive_ref_schema(api_doc, request_body_schema)
                                generation_rule = cls.parse_schema_to_generation_rule(request_body_schema)
                                
                            # * Create the Path Rule File
                            path_rule = None
                            if "{" in uri and "}" in uri and 'parameters' in operation:
                                path_rule = cls.parse_schema_to_path_rule(operation['parameters'])
                            
                            return generation_rule, path_rule
                        
    @classmethod
    def render_data_rule(
        cls, 
        selected_item: object,
        textbox_type: object, 
        textbox_format: object, 
        combobox_readonly: object, 
        textbox_default: object,
        combobox_data_generator: object, 
        textbox_range: object, 
        combobox_required: object, 
        combobox_nullable: object,
    ) -> None:
        """ When the user clicks on a field in the Data Generation Rule Table,
            the field properties will be rendered in the corresponding text box.
            For quick editing, the user can click on the text box to edit the field directly.

        Args:
            selected_item: The selected item in the Data Generation Rule table.
            textbox_type: The text box for the type field.
            textbox_format: The text box for the format field.
            combobox_readonly: The combobox for the readonly field.
            textbox_default: The text box for the default field.
            combobox_data_generator: The combobox for the data generator field.
            textbox_range: The text box for the range field.
            combobox_required: The combobox for the required field.
            combobox_nullable: The combobox for the nullable field.
        """        
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None: 
            textbox_type.setText(selected_item.child(0).text(1))
            textbox_format.setText(selected_item.child(1).text(1))
            combobox_readonly.setCurrentText(selected_item.child(2).text(1))
            textbox_default.setText(selected_item.child(3).text(1))
            combobox_data_generator.setCurrentText(selected_item.child(4).child(0).text(1))
            textbox_range.setText(selected_item.child(4).child(1).text(1))
            combobox_required.setCurrentText(selected_item.child(4).child(2).text(1))
            combobox_nullable.setCurrentText(selected_item.child(4).child(3).text(1)) 
            
    @classmethod
    def render_constraint_rule(
        cls,
        selected_item: object,
        textbox_src: object,
        textbox_expected_value: object,
        textbox_dst: object,
        textbox_dst_value: object,
        checkbox_wildcard: object,
    ) -> None:
        """ When the user clicks on a field in the Data Generation Rule table, 
            the field will be rendered in the corresponding text box.
            For quick editing, the user can click on the text box to edit the field directly.

        Args:
            selected_item: The selected item in the Data Generation Rule table.
            textbox_src: The text box for the source field.
            textbox_expected_value: The text box for the expected value field.
            textbox_dst: The text box for the destination field.
            textbox_dst_value: The text box for the destination value field.
            checkbox_wildcard: The checkbox for the wildcard field.
        """
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            src_path = textbox_src.text()
            dst_path = textbox_dst.text()
            field = selected_item.text(0)
            src_value = selected_item.child(3).text(1)
            
            if src_path == "" or (src_path != "" and dst_path != ""):
                textbox_src.setText(field)
                textbox_expected_value.setText(src_value)
                textbox_dst.clear()
                textbox_dst_value.clear()
                checkbox_wildcard.setChecked(False)
            elif dst_path == "":
                textbox_dst.setText(field)        
    
    @classmethod
    def collect_items_from_top_level(cls, tree, top_level_text, column_num=0):
        """
         Collects all items from a QTreeWidget's top level. This is a convenience method for
         
         Args:
         	 cls: The class to use for collection
         	 tree: The QTreeWidget to search for items
         	 top_level_text: The text of the top level
         	 column_num: The column number to start collecting from
         
         Returns: 
         	 A list of items that were found in the Q
        """
        # Collect all items in the tree.
        for i in range(tree.topLevelItemCount()):
            top_level_item = tree.topLevelItem(i)
            # Collect items from top level item.
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
    def update_table_item_from_ui(cls, table, new_value):
        """ To update selected item from a QTableWidget. """
        for item in table.selectedItems():
            item.setText(new_value)
    
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
    def remove_wildcard_field_in_generation_rule(cls, data: object, key_path: list):
        """
        Remove wildcard fields from the given data.

        Args:
            data : The data dictionary to operate on.
            key_path : The field path containing the wildcard.

        Returns:
            None

        """
        matched_name = key_path[0].split('.*')[0]
        for key in list(data.keys()):
            if matched_name in key:
                del data[key]
                
    @classmethod
    def generate_tcg_config(cls, test_strategies):
        config_file_path = "config/tcg_config.json"
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
                elif name == "Required Field Test":
                    name = "required_parameter_test"

            tcg_config["config"]["test_strategy"][test_type].append(name)

        with open(config_file_path, "w") as f:
            json.dump(tcg_config, f, indent=4)
                
    @classmethod
    def generate_test_cases(cls, tcg_config, TestStrategy, operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata):
        for test_type in tcg_config['config']['test_strategy']:
            for test_strategy in tcg_config['config']['test_strategy'][test_type]:
                test_strategy_func = getattr(TestStrategy, test_strategy)
                serial_number = test_strategy_func(
                    test_type, operation_id ,uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata
                )
                logging.info(f'Generate "{method} {uri}" "{test_type} - {test_strategy}" test case for successfully.')
        return serial_number
    
    @classmethod
    def generate_dependency_test_data_file(cls, dependency_testdata: dict, operation_id: str, serial_number: str, test_point_num: str) -> dict:
        """ Generate dependency base test data files according to the sequence of setup/teardown in the test plan.

        Args:
            dependency_testdata: The dependency test data
            operation_id: The API operation id.
            serial_number: The test case serial number.
            test_point_num: The test strategy serial number.

        Returns:
            A dict containing the dependency information and the test data file name.
        """        
        
        # Get the general dependency rule.
        with open(f"./DependencyRule/{operation_id}.json", "r") as f:
            dependency_rule = json.load(f)

        # Generate dependency test data file for all the dependencies.
        for action_type in ['Setup', 'Teardown']:
            for index, data in dependency_testdata[action_type].items():
                file_name = f"{operation_id}_{serial_number}_{test_point_num}_{action_type}_{index}"
                path = f"./TestData/Dependency_TestData/{file_name}.json"
                dependency_rule[action_type][index]['config_name'] = file_name
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                    logging.info(f"Generate dependency test data file: {path}")
        return dependency_rule
     
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
            if not os.path.exists(schema_folder):
                os.makedirs(schema_folder)
            for file in os.listdir(schema_folder):
                file_path = os.path.join(schema_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    
    @classmethod
    def clean_ui_content(cls, ui: list):
        for clean_widget in ui:
            if isinstance(clean_widget, QCheckBox):
                clean_widget.setChecked(False)
            elif isinstance(clean_widget, (QTreeWidget, QLineEdit, QListWidget, QPlainTextEdit, QTextBrowser)):
                clean_widget.clear()

    @classmethod
    def load_schema_file(cls, file_path: str):
        """ To load a schema file and return a dict. """
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == ".yaml" or file_extension == ".yml":
            with open(file_path, "r", encoding='utf-8') as f:
                api_doc = yaml.load(f, Loader=yaml.FullLoader)
        elif file_extension == ".json":
            with open(file_path, "r") as f:
                api_doc = json.load(f)
        else:
            logger.error(f"Unsupported file extension: {file_extension}")
            return None
        
        return api_doc
    
    @classmethod
    def refresh_generation_rule_table(cls, api_tree: object, generation_rule_table: object, file_path: str) -> None:
        selected_api = api_tree.selectedItems()[0]
        api_parent = selected_api.parent()
        if api_parent is not None:
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.clear()
            generation_rule_table.addTopLevelItem(root_item)
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            
    @classmethod
    def init_dependency_rule(cls, operation_id: str):
        """ To initialize dependency rule file. """
        dependency_rule = {"Setup": {}, "Teardown": {}}
        with open(f"./DependencyRule/{operation_id}.json", "w") as f:
            json.dump(dependency_rule, f, indent=4)
        
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
                'source': 'Status Code', 'filter_expression': '',
                'assertion_method': 'Should Be Equal', 'expected_value': status_code,   
            }
            counter[test_type] += 1
        return fields
    
    @classmethod
    def parse_schema_to_path_rule(cls, parameters: dict) -> dict:
        """ To generate a API's path rule file that contains path rules of some fields. """
        path_rule = {}
        for parameter in parameters:
            if parameter['in'] == 'path':
                fields = {
                    'Type': parameter['schema']['type'],
                    'Format': parameter['schema']['format'] if 'format' in parameter['schema'] else "",
                    'Required': parameter['required'] if 'required' in parameter else False,
                    "Nullable": parameter['schema']['nullable'] if 'nullable' in parameter['schema'] else False,
                    'Value': parameter['default'] if 'default' in parameter else "",
                }
                path_rule[parameter['name']] = fields
        return path_rule

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
            
            required = False
            if "required" in schema: required = schema["required"]
            
            readonly = False
            if "readOnly" in schema: readonly = schema["readOnly"]
                        
            default = ""
            if "default" in schema: default = schema["default"]
                
            data_format = ""
            if "format" in schema: data_format = schema["format"]
            
            logging.debug(f"Type: {schema}")
            fields[path] = {
                "Type": schema["type"],
                "Format": data_format,
                "ReadOnly": readonly,
                "Default": default,
                "rule": {
                    "Data Generator": genType,
                    "Data Length": str(data_length),
                    "Required": required,
                    "Nullable": nullable,
                }
            }
            
            included_field = [
                "minLength","maxLength", "minItems", "maxItems", "minimum", "maximum",
                "uniqueItems", "exclusiveMinimum", "exclusiveMaximum", "pattern",
            ]
            for key in included_field:
                if key in schema:
                    fields[path]['rule'][key] = schema[key]
        return fields
    
    @classmethod
    def parse_dependency_rule(cls, operation_id: str, dependency_rule_table: object) -> None:
        """To parse dependency rule files to TreeWidget.

        Args:
            operation_id: The API operation id.
            dependency_rule_table: QTreeWidget instance to be parsed.

        Returns:
            None
        """
        file_path = f"./DependencyRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                dependency_rule = json.load(f)
                
            # * Exclude the Data Generation Rules and Path Rules from the Dependency Rule Table.
            for section in ['Setup', 'Teardown']:
                for key in dependency_rule[section]:
                    if 'data_generation_rules' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['data_generation_rules']
                    if 'path' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['path']
                    if 'config_name' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['config_name']
                    if 'object' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['object']
                    if 'action' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['action']
                        
            setup_list, teardown_list = dependency_rule['Setup'], dependency_rule['Teardown']
            setup_item, teardown_item = QTreeWidgetItem(["Setup"]), QTreeWidgetItem(["Teardown"])
            
            dependency_rule_table.clear()
            dependency_rule_table.addTopLevelItem(setup_item)
            dependency_rule_table.addTopLevelItem(teardown_item)
            cls.parse_request_body(setup_list, setup_item, editabled=True)
            cls.parse_request_body(teardown_list, teardown_item, editabled=True)
            
    @classmethod
    def render_dependency_rule(cls, test_plan, test_case_id, test_point_id, table):
        """ To render dependency rule to the Test Plan Table. """
        
        # * Render the Test Case Dependency Rule.
        dependency_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['dependency']
        for section in ['Setup', 'Teardown']:
            for key in dependency_rule[section]:
                if 'data_generation_rules' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['data_generation_rules']
                if 'path' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['path']
                if 'config_name' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['config_name']
                if 'object' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['object']
                if 'action' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['action']
                                                            
        setup_list, teardown_list = dependency_rule['Setup'], dependency_rule['Teardown']
        setup_item, teardown_item = QTreeWidgetItem(["Setup"]), QTreeWidgetItem(["Teardown"]) 
        table.clear()
        table.addTopLevelItem(setup_item)
        table.addTopLevelItem(teardown_item)            
        cls.parse_request_body(setup_list, setup_item, editabled=True)
        cls.parse_request_body(teardown_list, teardown_item, editabled=True)
        cls.expand_and_resize_tree(table)
    
    @classmethod
    def parse_path_rule(cls, operation_id: str, path_rule_table: object) -> None:
        """
        To parse path rule files to TreeWidget.
        Ex: (./PathRule/{operation_id}.json)
        """
        
        file_path = f"./PathRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                path_rule = json.load(f)
            path_rule_table.clear()
            root_item = QTreeWidgetItem(["Path Parameter"])
            path_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(path_rule, root_item, editabled=True)
        else:
            logging.warning(f"Path rule file not found: {file_path}")
            
    @classmethod
    def parse_generation_rule(cls, operation_id: str, generation_rule_table: object) -> None:
        """
        To parse generation rule files to TreeWidget.
        Ex: (./GenerationRule/{operation_id}.json)
        """
        
        file_path = f"./GenerationRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            generation_rule_table.clear()
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            cls.expand_and_resize_tree(generation_rule_table, expand=False)
        else:
            logging.warning(f"Generation rule file not found: {file_path}")
  
    @classmethod
    def parse_assertion_rule(cls, operation_id: str, assertion_rule_table: object) -> None:
        """
        To parse assertion rule files to TreeWidget.
        Ex: (./AssertionRule/{operation_id}.json)
        """

        def _create_child_item(item):
            child_item = QTreeWidgetItem([
                "", item['source'], item['filter_expression'], 
                item['assertion_method'], item['expected_value']
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
    