import sys
import os
import json
import yaml
import logging
import glob

from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem, QLineEdit, QListWidget, QPlainTextEdit, QMessageBox, QTextBrowser, QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QAbstractItemView, QFileDialog

DEBUG = False

class GeneralTool:
    
    @classmethod
    def parse_field_path_to_key(cls, key_path: list) -> str:
        """
        Parse the field path to the key.
        Ex: # ['components', 'schemas', 'User', 'name', 'properties', 'dnsServer', 'domains', 'type'] -> dnsServer.domains[0].type
        """
        if key_path == []:
            return '', ''      
          
        key = ''
        if key_path[0] == 'components' and key_path[1] == 'schemas':
            key_path = key_path[3:]
        elif key_path[0] == 'paths':
            if key_path[3] == 'requestBody':
                key_path = key_path[5:]

        for element in key_path:
            if element == 'items' or element == 'properties':
                continue
            else:
                if element != key_path[-1]:
                    key += element + '.'
                else:
                    key += element
                if element != key_path[-1] and key_path[key_path.index(element) + 1] == 'items':
                    key += '[0].'
                elif element == key_path[-1] and element != 'properties':
                    continue
        
        return key, key_path[-1]
    
    @classmethod
    def obtain_assertion_type(cls, key: str) -> str:
        """
        To obtain the assertion type from the key.

        Args:
            key (str): The key of the assertion rule.

        Returns:
            str: The assertion type.
        """

        if key.startswith("2"):
            return "positive"
        else:
            return "negative"
        
    @classmethod
    def calculate_dict_key_index(cls, data):
        """
        Calculate the index of the key in the dict.
        """
        
        if data:
            return str(max([int(key) for key in data.keys()]) + 1)
        else:
            return str(1)
    
    @classmethod
    def render_test_plan_files(cls, table_test_plan_api_list: object) -> None:
        cls.clean_ui_content([table_test_plan_api_list])
        for test_plan in glob.glob("./artifacts/TestPlan/*.json"):
            with open(test_plan, "r") as f:
                test_plan = json.load(f)
            file_name = test_plan['test_info']['operationId']
            toplevel_length = table_test_plan_api_list.topLevelItemCount()
            table_test_plan_api_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
            for index, test_case in test_plan['test_cases'].items():
                testcase_child = QtWidgets.QTreeWidgetItem(["", str(index), test_case['test_strategy'], test_case['test_type']])
                table_test_plan_api_list.topLevelItem(toplevel_length).addChild(testcase_child)
                for tp_index, test_point in test_case['test_point'].items():
                    tp_index = str(index) + "." + str(tp_index)
                    testcase_child.addChild(QtWidgets.QTreeWidgetItem(["", tp_index, "", "", test_point['parameter']['name']]))
        cls.expand_and_resize_tree(table_test_plan_api_list, level=2)
    
    @classmethod
    def rander_robot_file_list(
        cls, 
        robot_file_list: object,
    ) -> None:
        """ To render the all robot files in the Robot File List. """
        
        for robot_file in glob.glob("./artifacts/TestCase/RESTful_API/*.robot"):
            file_name = os.path.basename(robot_file)
            root_item = QTreeWidgetItem([file_name])
            robot_file_list.addTopLevelItem(root_item)    
    
    @classmethod
    def update_tc_dependency_rule_index(
        cls, ui, operation_id, test_case_id, test_point_id, dependency_type, src_key, swap_type
    ):
        with open(f"./artifacts/TestPlan/{operation_id}.json", "r") as f:
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
        
        with open(f"./artifacts/TestPlan/{operation_id}.json", "w") as f:
            json.dump(d_rule, f, indent=4)

        cls.clean_ui_content([
            ui.line_tc_api_search,
            ui.textbox_tc_dependency_return_variable_name,
            ui.table_tc_dependency_generation_rule,
            ui.textbox_tc_dependency_requestbody,
            ui.table_tc_dependency_path,
        ])
        ui.comboBox_tc_dependency_type.setEnabled(True)
        ui.line_tc_api_search.setEnabled(True)
        ui.list_tc_dependency_available_api_list.clearSelection()
        ui.table_tc_dependency_rule.clearSelection()
        cls.render_dependency_rule(d_rule, test_case_id, test_point_id, ui.table_tc_dependency_rule)
        cls.expand_and_resize_tree(ui.table_tc_dependency_rule, level=3)
                
    @classmethod
    def update_dependency_rule_index(cls, ui, operation_id, dependency_type, src_key, swap_type):
        with open(f"./artifacts/DependencyRule/{operation_id}.json", "r") as f:
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

        with open(f"./artifacts/DependencyRule/{operation_id}.json", "w") as f:
            json.dump(d_rule, f, indent=4)

        cls.clean_ui_content([
            ui.line_api_search,
            ui.textbox_dependency_return_variable_name,
            ui.table_dependency_generation_rule,
            ui.table_dependency_path,
            ui.table_dependency_rule
        ])
        ui.comboBox_dependency_type.setEnabled(True)
        ui.list_dependency_available_api_list.clearSelection()
        cls.parse_dependency_rule(operation_id, ui.table_dependency_rule)
        cls.expand_and_resize_tree(ui.table_dependency_rule, level=3)
        
    @classmethod
    def swap_dict_keys(cls, dict_data, key1, key2):
        if key1 in dict_data and key2 in dict_data:
            dict_data[key1], dict_data[key2] = dict_data[key2], dict_data[key1]
        return dict_data
        
    @classmethod
    def _retrieve_obj_and_action(cls, api: str) -> str:
        """ Use the OpenAPI notation to retrieve the object name and action name from obj_mapping. """
        
        try:
            with open('./config/obj_mapping.json', 'r') as f:
                obj_mapping = json.load(f)
        except FileNotFoundError:
            cls.show_error_dialog("Object Mapping File Not Found.", "Please import the Object Mapping File first.")
            return None, None
            
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
        else:
            GeneralTool.show_error_dialog(
                f"API {expected_method} {expected_uri} Not Found on the Object Mapping File.",
                f"Please check the API name or add the API to the Object Mapping File.")
            raise Exception(f"API {expected_method} {expected_uri} Not Found on the Object Mapping File.")
    
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
        is_test_plan: bool = False,
    ) -> None:
        
        if is_general_dependency:
            file_path = f"./artifacts/DependencyRule/{operation_id}.json"
        elif is_dependency or is_test_plan:
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
        else:
            file_path = f"./artifacts/GenerationRule/{operation_id}.json"
        
        if src_action == "Set":
            if src_condition == "WITH":
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    if is_general_dependency:
                        path = [dependency_type, dependency_sequence_num, "data_generation_rules", src_path, "Default"]
                    elif is_test_plan:
                        path = ["test_cases", test_case_id, "test_point", test_point_id, "parameter", 
                                "data_generation_rules", src_path, "Default"]
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
                elif is_test_plan:
                    if ".*" in dst_path:
                        path = ['test_cases', test_case_id, 'test_point', test_point_id, 'parameter', 
                                   'data_generation_rules', dst_path.split('.*')[0]]
                    else:
                        path = ['test_cases', test_case_id, 'test_point', test_point_id, 'parameter', 
                                    'data_generation_rules', dst_path]
                else:
                    path = [dst_path]
                    
                if ".*" in dst_path:
                    # BUG: The wildcard not work for the general dependency rule and test plan.
                    if is_general_dependency or is_dependency or is_test_plan:
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
                    elif is_test_plan:
                        path = ["test_cases", test_case_id, "test_point", test_point_id, "parameter", 
                                "data_generation_rules", src_path, "Default"]
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
    def generate_dependency_data_generation_and_path_and_query_rule(cls, api_name: str) -> dict | None:
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
                                request_body_schema = cls.retrieve_ref_schema(api_doc, request_body_schema)
                                generation_rule = cls.parse_schema_to_generation_rule(request_body_schema)
                                
                            # * Create the Path Rule File
                            path_rule = None
                            if "{" in uri and "}" in uri and 'parameters' in operation:
                                path_rule = cls.parse_schema_to_path_rule(operation['parameters'])
                                
                            # * Create the Query Rule File
                            query_rule = None
                            if "parameters" in operation:
                                query_rule = cls.parse_schema_to_query_rule(operation['parameters'])
                                
                            if DEBUG:
                                logging.debug(f"Query Rule: {query_rule}")
                            
                            return generation_rule, path_rule, query_rule
                        
    @classmethod
    def render_data_rule(
        cls, 
        selected_item: object,
        textbox_type: object, 
        textbox_format: object,
        comboBox_data_rule_value: object,
        combobox_data_generator: object, 
        textbox_range: object, 
        combobox_required: object, 
        combobox_nullable: object,
        textbox_regex_pattern: object,
    ) -> None:
        """ When the user clicks on a field in the Data Generation Rule Table,
            the field properties will be rendered in the corresponding text box.
            For quick editing, the user can click on the text box to edit the field directly.

        Args:
            selected_item: The selected item in the Data Generation Rule table.
            textbox_type: The text box for the type field.
            textbox_format: The text box for the format field.
            comboBox_data_rule_value: The text box for the default field.
            combobox_data_generator: The combobox for the data generator field.
            textbox_range: The text box for the range field.
            combobox_required: The combobox for the required field.
            combobox_nullable: The combobox for the nullable field.
            textbox_regex_pattern: The text box for the regex pattern field.
        """        
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None: 
            textbox_type.setText(selected_item.child(0).text(1))
            textbox_format.setText(selected_item.child(1).text(1))
            
            comboBox_data_rule_value.clear()
            comboBox_data_rule_value.addItems(
                ['', '{Ture}', '{False}', '{Null}', '{"key1": "value1", "key2": "value2"}', '["item1", "item2"]'
                , '[1,2,3]', '[1.1,2.2,3.3]', '["1","2","3"]'])
            enum_item = []
            comboBox_data_rule_value.setCurrentText(selected_item.child(2).text(1))
            combobox_data_generator.setCurrentText(selected_item.child(3).child(0).text(1))
            textbox_range.setText(selected_item.child(3).child(1).text(1))
            combobox_required.setCurrentText(selected_item.child(3).child(2).text(1))
            combobox_nullable.setCurrentText(selected_item.child(3).child(3).text(1))
            textbox_regex_pattern.setText(selected_item.child(3).child(4).text(1))
            try:
                for i in range(selected_item.child(3).child(5).childCount()):
                    child_item = selected_item.child(3).child(5).child(i).text(1)
                    enum_item.append(child_item)
                comboBox_data_rule_value.addItems(enum_item)
            except AttributeError:
                pass
                
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
    def render_dynamic_overwrite_data(
        cls,
        selected_item: object,
        textbox_name: object,
    ):
        """ When the user clicks on a field in the Data Generation Rule table, 
            the field will be rendered in the corresponding text box.
            For quick editing, the user can click on the text box to edit the field directly.

        Args:
            selected_item: The selected item in the Data Generation Rule table.
            textbox_name: The text box for the name field.
        """
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name = selected_item.text(0)
            if '[0]' in name:
                name = name.replace('[0]', '.0')
            textbox_name.setText(name)
    
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
        if not key_path:
            value[new_key] = new_value
            return True
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

        TEST_TYPE_MAP = {
            "Positive Test": "positive_test",
            "Negative Test": "negative_test",
        }

        NAME_MAP = {
            "Parameter Min./Max.": "parameter_min_max_test",
            "Enum Value Test": "enum_value_test",
            "Null Value Test": "null_value_test",
            "Functional Test": "functional_test",
            "Required Field Test": "required_parameter_test",
        }
        
        def map_test_type(test_type):
            return TEST_TYPE_MAP.get(test_type)

        def map_test_name(test_name):
            return NAME_MAP.get(test_name)

        for strategy in test_strategies:
            if strategy.isChecked():
                test_type = strategy.parent().title()
                name = strategy.text()
                if test_type in TEST_TYPE_MAP:
                    test_type = map_test_type(test_type)
                    name = map_test_name(name)
                    tcg_config["config"]["test_strategy"][test_type].append(name)
            else:
                continue
            
        try:
            with open(config_file_path, "w") as f:
                json.dump(tcg_config, f, indent=4)
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_file_path}")
            raise FileNotFoundError
                
    @classmethod
    def generate_test_cases(cls, tcg_config, TestStrategy, operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata, test_count):
            for test_type in tcg_config['config']['test_strategy']:
                for test_strategy in tcg_config['config']['test_strategy'][test_type]:
                    for count in range(test_count):
                        test_strategy_func = getattr(TestStrategy, test_strategy)
                        logging.info(f'Generate "{method} {uri}" "{test_type} - {test_strategy}" test case for start.')
                        serial_number = test_strategy_func(
                            test_type, operation_id ,uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata
                        )
                        logging.info(f'Generate "{method} {uri}" "{test_type} - {test_strategy}" test case for successfully.')
    
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
        with open(f"./artifacts/DependencyRule/{operation_id}.json", "r") as f:
            dependency_rule = json.load(f)

        # Generate dependency test data file for all the dependencies.
        for action_type in ['Setup', 'Teardown']:
            for index, data in dependency_testdata[action_type].items():
                file_name = f"{operation_id}_{serial_number}_{test_point_num}_{action_type}_{index}"
                path = f"./artifacts/TestData/Dependency_TestData/{file_name}.json"
                dependency_rule[action_type][index]['config_name'] = file_name
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                    logging.info(f"Generate dependency test data file: {path}")
        return dependency_rule
     
    @classmethod
    def expand_and_resize_tree(cls, tree, level=2):
        """ To expand or collapse all items in a QTreeWidget up to a certain level. """
        def expand_items(item, level):
            if level > 0:
                item.setExpanded(True)
                for i in range(item.childCount()):
                    expand_items(item.child(i), level - 1)
        
        expand_items(tree.invisibleRootItem(), level)
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
            with open(file_path, "r", encoding='utf-8') as f:
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
        with open(f"./artifacts/DependencyRule/{operation_id}.json", "w") as f:
            json.dump(dependency_rule, f, indent=4)
            
    @classmethod
    def init_additional_action_rule(cls, operation_id: str):
        """ To initialize additional action rule file. """
        additional_action_rule = {}
        with open(f"./artifacts/AdditionalAction/{operation_id}.json", "w") as f:
            json.dump(additional_action_rule, f, indent=4)
        
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
                'source': 'Status Code', 'field_expression': '', 'filter_expression': '',
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
    def parse_schema_to_query_rule(cls, parameters: dict) -> dict:
        """ To generate a API's query rule file that contains query rules of some fields. """
        query_rule = {}
        for parameter in parameters:
            if parameter['in'] == 'query':
                fields = {
                    'Type': parameter['schema']['type'],
                    'Format': parameter['schema']['format'] if 'format' in parameter['schema'] else "",
                    'Required': parameter['required'] if 'required' in parameter else False,
                    "Nullable": parameter['schema']['nullable'] if 'nullable' in parameter['schema'] else False,
                    'Value': parameter['default'] if 'default' in parameter else "",
                }
                query_rule[parameter['name']] = fields
        return query_rule
    
    @classmethod
    def updated_generation_rule_by_type(cls, rule: dict, path: str, schema: dict):

        cls.set_generation_rule_by_schema(schema, rule, path)

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
                if "readOnly" in prop_schema and prop_schema["readOnly"] == True:
                    continue
                fields.update(cls.parse_schema_to_generation_rule(prop_schema, new_path))
                
                # Detect the required list.
                if "required" in schema and prop_name in schema["required"]:
                    try:
                        fields[new_path]['rule']['Required'] = True
                    except KeyError:
                        # If the field is an object, the field name will be the key of the object.
                        for fields_key in fields.keys():
                            if fields_key.startswith(new_path):
                                sub_field_name = fields_key.split('.')[-1]
                                if 'required' in schema['properties'][prop_name]:
                                    if sub_field_name in schema['properties'][prop_name]['required']:
                                        fields[fields_key]['rule']['Required'] = True
                                    else:
                                        fields[fields_key]['rule']['Required'] = False
                                elif 'properties' in schema['properties'][prop_name] and 'required' in schema['properties'][prop_name]['properties'][sub_field_name]:
                                    if sub_field_name in schema['properties'][prop_name]['properties'][sub_field_name]['required']:
                                        fields[fields_key]['rule']['Required'] = True
                                    else:
                                        fields[fields_key]['rule']['Required'] = False

        elif "items" in schema:
            if "properties" in schema["items"]:
                for prop_name, prop_schema in schema["items"]["properties"].items():
                    if path:
                        new_path = path + "[0]." + prop_name
                    else:
                        new_path = prop_name
                    if "readOnly" in prop_schema and prop_schema["readOnly"] == True:
                        continue
                    fields.update(cls.parse_schema_to_generation_rule(prop_schema, new_path))
                    # * Detect the required list.
                    if "required" in schema["items"] and prop_name in schema["items"]["required"]:
                            try:
                                fields[new_path]['rule']['Required'] = True
                            except KeyError:
                                # * if the field is an object, the field name will be the key of the object.
                                for fields_key in fields.keys():
                                    if fields_key.startswith(new_path):
                                        sub_field_name = fields_key.split('.')[-1]
                                        if 'required' in schema['properties'][prop_name]:
                                            if sub_field_name in schema['properties'][prop_name]['required']:
                                                fields[fields_key]['rule']['Required'] = True
                                            else:
                                                fields[fields_key]['rule']['Required'] = False
                                        elif 'properties' in schema['properties'][prop_name] and 'required' in schema['properties'][prop_name]['properties'][sub_field_name]:
                                            if sub_field_name in schema['properties'][prop_name]['properties'][sub_field_name]['required']:
                                                fields[fields_key]['rule']['Required'] = True
                                            else:
                                                fields[fields_key]['rule']['Required'] = False
            else:
                if path:
                    new_path = path + "[0]"
                else:
                    new_path = "[0]"
                fields.update(cls.parse_schema_to_generation_rule(schema["items"], new_path))
        else:
            cls.set_generation_rule_by_schema(schema, fields, path)
        return fields
    
    @classmethod
    def set_generation_rule_by_schema(cls, schema, fields, path):
        genType = None
        if "ERROR" in schema:
            return {}
        elif "enum" in schema and schema["enum"] != []:
            genType = "Random Enumeration Value"
            data_length = ""
        elif schema["type"] == "string":
            if 'format' in schema:
                if schema['format'] in ['email', 'ipv4', 'ipv6', 'hostname', 'uuid', 'date-time', 'date', 'uri', 'int64', 'int32', 'binary', 'byte']:
                    genType = f"Random {schema['format'].upper()}"
                    data_length = ""
                else:
                    genType = "Random String (Without Special Characters)"
                    data_length = [1, 30]
            elif 'pattern' in schema:
                genType = "Random String By Pattern"
                data_length = ""
            else:
                genType = "Random String (Without Special Characters)"
                data_length = [1, 30]
        elif schema["type"] == "integer":
            if 'format' in schema:
                if schema['format'] in ['int64', 'int32']:
                    genType = f"Random {schema['format'].upper()}"
                    data_length = ""
                else:
                    genType = "Random Integer"
                    data_length = [1, 100]
            else:
                genType = "Random Integer"
                data_length = [1, 100]
        elif schema["type"] == "number":
            genType = "Random Number (Float)"
            data_length = [1, 100]
        elif schema["type"] == "boolean":
            genType = "Random Boolean"
            data_length = ""
        elif schema["type"] == "object":
            logging.warning(f"This field is an empty object: {path}")
            return {}
        
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
        
        regex_pattern = ""
        if "pattern" in schema: regex_pattern = schema["pattern"]
                    
        default = ""
        if "default" in schema: default = schema["default"]
            
        data_format = ""
        if "format" in schema: data_format = schema["format"]
        
        enum = []
        if "enum" in schema: enum = schema["enum"]
        
        fields[path] = {
            "Type": schema["type"],
            "Format": data_format,
            "Default": default,
            "rule": {
                "Data Generator": genType,
                "Data Length": str(data_length),
                "Required": required,
                "Nullable": nullable,
                "Regex Pattern": regex_pattern,
                "Enum": enum,
            }
        }
        if fields[path]['rule']['Enum'] == []:
            del fields[path]['rule']['Enum']
        
        included_field = [
            "minLength","maxLength", "minItems", "maxItems", "minimum", "maximum",
            "uniqueItems", "exclusiveMinimum", "exclusiveMaximum",]
        for key in included_field:
            if key in schema:
                fields[path]['rule'][key] = schema[key]
        return fields  
    
    @classmethod
    def parse_additional_action_rule(cls, operation_id: str, additional_action_rule_table: object) -> None:
        """To parse additional action rule files to TreeWidget.
        
        Args:
            operation_id: The API operation id.
            additional_action_rule_table: QTreeWidget instance to be parsed.
            
        Returns:
            None
        """
        file_path = f"./artifacts/AdditionalAction/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

            additional_action_rule_table.clear()
            root_item = QTreeWidgetItem(["Action Rule"])
            additional_action_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(data, root_item)
            cls.expand_and_resize_tree(additional_action_rule_table, level=2)
        else:
            logging.warning(f"Additional Action File Not Found: {file_path}")
            
    @classmethod
    def parse_tc_additional_action_rule(
        cls,
        operation_id: str, 
        tc_additional_action_rule_table: object,
        test_case_id: str,
        test_point_id: str,
    ) -> None:

        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data = data['test_cases'][test_case_id]['test_point'][test_point_id]['additional_action']
            
            tc_additional_action_rule_table.clear()
            root_item = QTreeWidgetItem(["Additional Action"])
            tc_additional_action_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(data, root_item)
            cls.expand_and_resize_tree(tc_additional_action_rule_table, level=2)
        else:
            logging.warning(f"Additional Action File Not Found: {file_path}")
            
    @classmethod
    def parse_tc_dynamic_overwrite_data(
        cls,
        operation_id: str,
        tc_dynamic_overwrite_data_table: object,
        test_case_id: str,
        test_point_id: str,
    ) -> None:
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data = data['test_cases'][test_case_id]['test_point'][test_point_id]['dynamic_overwrite_data']
            tc_dynamic_overwrite_data_table.clear()
            root_item = QTreeWidgetItem(["Dynamic Overwrite Data"])
            tc_dynamic_overwrite_data_table.addTopLevelItem(root_item)
            cls.parse_request_body(data, root_item)
            cls.expand_and_resize_tree(tc_dynamic_overwrite_data_table)
        else:
            logging.warning(f"Dynamic Overwrite Data File Not Found: {file_path}")
            
    @classmethod
    def parse_tc_dependency_additional_action_rule(
        cls,
        operation_id: str,
        test_case_id: str,
        test_point_id: str,
        tc_dependency_additional_action_table: object,
        dependency_type: str,
        dependency_sequence_num: str,
    ) -> None:

        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data = data['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type][dependency_sequence_num]['additional_action']
            tc_dependency_additional_action_table.clear()
            root_item = QTreeWidgetItem(["Additional Action"])
            tc_dependency_additional_action_table.addTopLevelItem(root_item)
            cls.parse_request_body(data, root_item)
            cls.expand_and_resize_tree(tc_dependency_additional_action_table, level=2)
        else:
            logging.warning(f"Additional Action File Not Found: {file_path}")
            
    @classmethod
    def parse_dependency_additional_action_rule(
        cls, operation_id: str, dependecy_type: str, sequence_num: str , dependency_aditional_action_table: object) -> None:  
        
        file_path = f"./artifacts/DependencyRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data = data[dependecy_type][sequence_num]["additional_action"]
                
            dependency_aditional_action_table.clear()
            root_item = QTreeWidgetItem(["Additional Action"])
            dependency_aditional_action_table.addTopLevelItem(root_item)
            cls.parse_request_body(data, root_item)
            cls.expand_and_resize_tree(dependency_aditional_action_table, level=2)
        else:
            logging.warning(f"Dependency Action File Not Found: {file_path}") 
    
    @classmethod
    def parse_dependency_rule(cls, operation_id: str, dependency_rule_table: object) -> None:
        """To parse dependency rule files to TreeWidget.

        Args:
            operation_id: The API operation id.
            dependency_rule_table: QTreeWidget instance to be parsed.

        Returns:
            None
        """
        file_path = f"./artifacts/DependencyRule/{operation_id}.json"
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
                    if 'additional_action' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['additional_action']
                    if 'query' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['query']
                    if 'dynamic_overwrite_data' in dependency_rule[section][key]:
                        del dependency_rule[section][key]['dynamic_overwrite_data']
                                                                                     
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
                    dependency_rule[section][key]['object']
                if 'action' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['action']
                if 'additional_action' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['additional_action']
                if 'query' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['query']
                if 'dynamic_overwrite_data' in dependency_rule[section][key]:
                    del dependency_rule[section][key]['dynamic_overwrite_data']
                                                             
        setup_list, teardown_list = dependency_rule['Setup'], dependency_rule['Teardown']
        setup_item, teardown_item = QTreeWidgetItem(["Setup"]), QTreeWidgetItem(["Teardown"]) 
        table.clear()
        table.addTopLevelItem(setup_item)
        table.addTopLevelItem(teardown_item)            
        cls.parse_request_body(setup_list, setup_item, editabled=True)
        cls.parse_request_body(teardown_list, teardown_item, editabled=True)
        cls.expand_and_resize_tree(table, level=3)
        
    @classmethod
    def parse_dynamic_overwrite_data(cls, operation_id: str, dynamic_overwrite_table: object) -> None:
        """To parse dynamic overwrite data files to TreeWidget.

        Args:
            operation_id: The API operation id.
            dynamic_overwrite_table: QTreeWidget instance to be parsed.

        Returns:
            None
        """
        file_path = f"./artifacts/DynamicOverwrite/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                dynamic_overwrite = json.load(f)
                
            dynamic_overwrite_table.clear()
            root_item = QTreeWidgetItem(["Dynamic Overwrite Data"])
            dynamic_overwrite_table.addTopLevelItem(root_item)
            cls.parse_request_body(dynamic_overwrite, root_item, editabled=True)
            cls.expand_and_resize_tree(dynamic_overwrite_table, level=2)
        else:
            logging.warning(f"Dynamic Overwrite File Not Found: {file_path}")
    
    @classmethod
    def parse_path_rule(cls, operation_id: str, path_rule_table: object) -> None:
        """
        To parse path rule files to TreeWidget.
        Ex: (./artifacts/PathRule/{operation_id}.json)
        """
        file_path = f"./artifacts/PathRule/{operation_id}.json"
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
    def parse_query_rule(cls, operation_id: str, query_rule_table: object) -> None:
        """
        To parse query rule files to TreeWidget.
        Ex: (./artifacts/QueryRule/{operation_id}.json)
        """
        
        file_path = f"./artifacts/QueryRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                query_rule = json.load(f)
            query_rule_table.clear()
            root_item = QTreeWidgetItem(["Query Parameter"])
            query_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(query_rule, root_item, editabled=True)
        else:
            logging.warning(f"Query rule file not found: {file_path}")
            
    @classmethod
    def parse_generation_rule(cls, operation_id: str, generation_rule_table: object) -> None:
        """
        To parse generation rule files to TreeWidget.
        Ex: (./artifacts/GenerationRule/{operation_id}.json)
        """
        
        file_path = f"./artifacts/GenerationRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            generation_rule_table.clear()
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            cls.expand_and_resize_tree(generation_rule_table, level=2)
        else:
            logging.warning(f"Generation rule file not found: {file_path}")
            
    @classmethod
    def parse_dependency_generation_rule(
        cls, 
        operation_id: str, 
        generation_rule_table: object,
        dependency_type: str,
        dependency_index: str,
    ) -> None:
        """
        To parse dependency generation rule files to TreeWidget.
        Ex: (./artifacts/GenerationRule/{operation_id}.json)
        """
        
        file_path = f"./artifacts/DependencyRule/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            generation_rule = generation_rule[dependency_type][dependency_index]['data_generation_rules']
            generation_rule_table.clear()
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            cls.expand_and_resize_tree(generation_rule_table, level=2)
        else:
            logging.warning(f"Generation rule file not found: {file_path}")

    @classmethod
    def parse_tc_generation_rule(
        cls, 
        operation_id: str, 
        generation_rule_table: object,
        test_case_id: str,
        test_point_id: str,
    ) -> None:
        """
        To parse Test Plan generation rule files to TreeWidget.
        Ex: (./artifacts/GenerationRule/{operation_id}.json)
        """
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            generation_rule = generation_rule['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['data_generation_rules']
            generation_rule_table.clear()
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            cls.expand_and_resize_tree(generation_rule_table, level=2)
        else:
            logging.warning(f"Generation rule file not found: {file_path}")
            
    @classmethod
    def parse_tc_dependency_generation_rule(
        cls, 
        operation_id: str, 
        generation_rule_table: object,
        test_case_id: str,
        test_point_id: str,
        dependency_type: str,
        dependency_index: str,
    ) -> None:
        """
        To parse dependency generation rule files to TreeWidget.
        Ex: (./artifacts/GenerationRule/{operation_id}.json)
        """
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                generation_rule = json.load(f)
            generation_rule = generation_rule['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type][dependency_index]['data_generation_rules']
            generation_rule_table.clear()
            root_item = QTreeWidgetItem(["Data Generation Rule"])
            generation_rule_table.addTopLevelItem(root_item)
            cls.parse_request_body(generation_rule, root_item, editabled=True)
            cls.expand_and_resize_tree(generation_rule_table, level=2)
        else:
            logging.warning(f"Generation rule file not found: {file_path}")
  
    @classmethod
    def parse_assertion_rule(cls, operation_id: str, assertion_rule_table: object) -> None:
        """
        To parse assertion rule files to TreeWidget.
        Ex: (./artifacts/AssertionRule/{operation_id}.json)
        """

        def _create_child_item(item):
            child_item = QTreeWidgetItem([
                "", item['source'], item['field_expression'], item['filter_expression'], 
                item['assertion_method'], item['expected_value']
            ])
            child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            return child_item

        with open(f"./artifacts/AssertionRule/{operation_id}.json", "r") as f:
            assertion_rule = json.load(f)

        positive_root_item = QTreeWidgetItem(["Positive"])
        assertion_rule_table.addTopLevelItem(positive_root_item)
        cls.parse_request_body(assertion_rule['positive'], positive_root_item, editabled=True)
            
        negative_root_item = QTreeWidgetItem(["Negative"])
        assertion_rule_table.addTopLevelItem(negative_root_item)
        cls.parse_request_body(assertion_rule['negative'], negative_root_item, editabled=True)
            
    @classmethod
    def parse_request_body(cls, body, parent_item, editabled=False):
        if body is None:
            parent_item.setText(1, 'This API does not have a request body.')
            return
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
                        item_text = QTreeWidgetItem(['', 'object'])
                        if editabled:
                            item_text.setFlags(item_text.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        child_item.addChild(item_text)
                        if editabled:
                            cls.parse_request_body(item, item_text, editabled)
                        else:
                            cls.parse_request_body(item, item_text)
                    elif isinstance(item, list):
                        item_text = QTreeWidgetItem(['', 'array'])
                        if editabled:
                            item_text.setFlags(item_text.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        child_item.addChild(item_text)
                        if editabled:
                            cls.parse_request_body({'item': item}, item_text, editabled)
                        else:
                            cls.parse_request_body({'item': item}, item_text)
                    else:
                        item_text = QTreeWidgetItem(['', str(item)])
                        if editabled:
                            item_text.setFlags(item_text.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                        child_item.addChild(item_text)
            else:
                child_item = QTreeWidgetItem([key, str(value)])
                if editabled:
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
                parent_item.addChild(child_item)
                
    @classmethod            
    def parse_api_name_to_op_id(cls, api_name: str, doc: dict) -> str:
        """
        Parse the API name to operation ID.

        Args:
        - api_name (str): The name of the API.
        - doc (dict): The Swagger/OpenAPI document.

        Returns:
        - The operation ID.
        """
        
        method = api_name.split()[0].lower()
        path = api_name.split()[1]
        op_id = doc['paths'][path][method]['operationId']
        
        return op_id   
                 
    @classmethod
    def retrieve_ref_schema_key_type(cls, api_schema):
        request_body = {}
        for key, value in api_schema['properties'].items():
            if value['type'] == 'string':
                request_body[key] = 'string'
            elif value['type'] == 'integer':
                request_body[key] = 'integer'
            elif value['type'] == 'boolean':
                request_body[key] = 'boolean'
            elif value['type'] == 'object':
                request_body[key] = cls.retrieve_ref_schema_key_type(value)
            elif value['type'] == 'array':
                if value['items']['type'] == 'object':
                    request_body[key] = [cls.retrieve_ref_schema_key_type(value['items'])]
                else:
                    request_body[key] = [value['items']['type']]
        return request_body
    
    @classmethod
    def retrieve_ref_schema(cls, api_doc, schema):
        """Retrieve all referenced schema in api doc.

        Args:
            api_doc: The api doc.
            schema: The schema to be retrieved.

        Returns:
            The schema with all referenced schema resolved.
        """
        if not isinstance(schema, dict):
            return schema
        
        if '$ref' in schema:
            try:
                ref_path = schema['$ref'].split('/')[1:]
                resolved_schema = api_doc['components']['schemas'][ref_path[-1]]
            except IndexError as e:
                error_message = f"ref path is empty. Please check the API doc."
                logging.warning(error_message)
                return {"ERROR": error_message}
            except KeyError as e:
                error_message = f"This API reference path can not be found in the API doc. Please check the API doc."
                logging.error(error_message)
                return {"ERROR": error_message}
            return cls.retrieve_ref_schema(api_doc, resolved_schema)

        resolved_schema = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved_schema[key] = cls.retrieve_ref_schema(api_doc, value)
            elif isinstance(value, list):
                resolved_schema[key] = [cls.retrieve_ref_schema(api_doc, item) for item in value]
            else:
                resolved_schema[key] = value
        return resolved_schema
    
    @classmethod
    def get_value_by_path(cls, dict_data, path):
        """
        Get the value of a dictionary by the path.
        """
        
        current_dict = dict_data
        for key in path:
            if key in current_dict:
                current_dict = current_dict[key]
            else:
                return None
        return current_dict