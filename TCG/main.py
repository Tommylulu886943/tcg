import sys
import os
import json
import yaml
import glob
import logging
import copy
import shutil
from json.decoder import JSONDecodeError
from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic, QtWebEngineWidgets
from PyQt6.QtCore import QStringListModel, QBasicTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QCheckBox, QTreeWidget, QTreeWidgetItem, QCompleter, QFileDialog, QComboBox, QPushButton

from lib.test_strategy import TestStrategy
from lib.general_tool import GeneralTool
from lib.DataBuilder import DataBuilder
from lib.render import Render
from lib.UI import CustomForm

DEBUG = False
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.DEBUG)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # * Load the UI Page
        uic.loadUi('lib/tcg_backup.ui', self)
        
        # * Set Icon
        self.btn_import_openapi_doc.setIcon(QIcon("./source/new.png"))
        
        # * Dynamic UI
        self.specialActions = {
            "None": [],
            "Parser - API Parser": ["Response Name", "Data", "Filter", "Last Count", "Field", "Return Type"],
            "Analyzer - Data Analyzer": ["Response Name", "Data", "Filter", "Field", "Last Count", "Verbose", "Return Type", "Result Type"],
            "Analyzer - Config Analyzer": ["Response Name", "Src. Data", "Dest. Data", "Action", "Start Level", "Obj", "Verbose"],
        }        
        self.tab_22 = QtWidgets.QWidget()
        self.tab_22.setObjectName("tab_22")
        self.tabWidget_2.insertTab(4, self.tab_22, "Additional Action")
        
        self.label_additional_action = QtWidgets.QLabel(self.tab_22)
        self.label_additional_action.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.label_additional_action.setText("Action Item :")
        self.additional_action = QComboBox(self.tab_22)
        self.additional_action.addItems(self.specialActions.keys())
        self.additional_action.setGeometry(QtCore.QRect(100, 10, 250, 30))

        self.form = CustomForm(self.tab_22)
        self.form.setGeometry(QtCore.QRect(10, 50, 400, 200))
        self.additional_action.currentTextChanged.connect(self.additional_action_changed)

        self.add_additional_action = QPushButton("Add Action", self.tab_22)
        self.add_additional_action.setGeometry(QtCore.QRect(10, 280, 120, 30))
        self.add_additional_action.clicked.connect(self.btn_add_special_action)
        self.additional_action_changed()
        
        self.remove_additional_action = QPushButton("Remove Action", self.tab_22)
        self.remove_additional_action.setGeometry(QtCore.QRect(140, 280, 120, 30))
        self.remove_additional_action.clicked.connect(self.btn_remove_special_action)
        self.additional_action_changed()
        
        self.table_additional_action = QtWidgets.QTreeWidget(parent=self.tab_22)
        self.table_additional_action.setGeometry(QtCore.QRect(10, 330, 600, 400))
        self.table_additional_action.setObjectName("table_additional_action")
        self.table_additional_action.headerItem().setText(0, "Index")
        self.table_additional_action.headerItem().setText(1, "Action Name")
        
        # *　Dependency Additonal Action
        self.tab_50 = QtWidgets.QWidget()
        self.tab_50.setObjectName("tab_50")
        self.tabWidget_5.insertTab(2, self.tab_50, "Additional Action")
        self.label_additional_action_2 = QtWidgets.QLabel(self.tab_50)
        self.label_additional_action_2.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.label_additional_action_2.setText("Action Item :")
        self.dependency_additional_action = QComboBox(self.tab_50)
        self.dependency_additional_action.addItems(self.specialActions.keys())
        self.dependency_additional_action.setGeometry(QtCore.QRect(100, 10, 250, 30))
        self.dependency_form = CustomForm(self.tab_50)
        self.dependency_form.setGeometry(QtCore.QRect(10, 50, 400, 200))
        self.dependency_additional_action.currentTextChanged.connect(self.dependency_additional_action_changed)
        
        self.add_dependency_additional_action = QPushButton("Add Action", self.tab_50)
        self.add_dependency_additional_action.setGeometry(QtCore.QRect(390, 10, 100, 30))
        self.add_dependency_additional_action.clicked.connect(self.btn_add_dependency_special_action)
        self.remove_dependency_additional_action = QPushButton("Remove Action", self.tab_50)
        self.remove_dependency_additional_action.setGeometry(QtCore.QRect(510, 10, 100, 30))
        self.remove_dependency_additional_action.clicked.connect(self.btn_remove_dependency_special_action)
        self.table_dependency_additional_action = QtWidgets.QTreeWidget(parent=self.tab_50)
        self.table_dependency_additional_action.setGeometry(QtCore.QRect(10, 360, 630, 330))
        self.table_dependency_additional_action.setObjectName("table_dependency_additional_action")
        self.table_dependency_additional_action.headerItem().setText(0, "Index")
        self.table_dependency_additional_action.headerItem().setText(1, "Action Name")
        
        # * Test Plan Additional Action
        self.tab_51 = QtWidgets.QWidget()
        self.tab_51.setObjectName("tab_51")
        self.tabWidget_testPlan.insertTab(4, self.tab_51, "Additional Action")
        self.label_tc_additional_action = QtWidgets.QLabel(self.tab_51)
        self.label_tc_additional_action.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.label_tc_additional_action.setText("Action Item :")
        self.tc_additional_action = QComboBox(self.tab_51)
        self.tc_additional_action.addItems(self.specialActions.keys())
        self.tc_additional_action.setGeometry(QtCore.QRect(100, 10, 250, 30))
        self.tc_form = CustomForm(self.tab_51)
        self.tc_form.setGeometry(QtCore.QRect(10, 50, 400, 200))
        self.tc_additional_action.currentTextChanged.connect(self.tc_additional_action_changed)
        self.add_tc_additional_action = QPushButton("Add Action", self.tab_51)
        self.add_tc_additional_action.setGeometry(QtCore.QRect(10, 280, 120, 30))
        self.add_tc_additional_action.clicked.connect(self.btn_tc_add_special_action)
        self.remove_tc_additional_action = QPushButton("Remove Action", self.tab_51)
        self.remove_tc_additional_action.setGeometry(QtCore.QRect(140, 280, 120, 30))
        self.remove_tc_additional_action.clicked.connect(self.btn_tc_remove_special_action)
        self.table_tc_additional_action = QtWidgets.QTreeWidget(parent=self.tab_51)
        self.table_tc_additional_action.setGeometry(QtCore.QRect(10, 330, 600, 400))
        self.table_tc_additional_action.setObjectName("table_tc_additional_action")
        self.table_tc_additional_action.headerItem().setText(0, "Index")
        self.table_tc_additional_action.headerItem().setText(1, "Action Name")
        
        # * Test Plan Dependency Additional Action
        self.tab_52 = QtWidgets.QWidget()
        self.tab_52.setObjectName("tab_52")
        self.table_tc_dependency_schema_2.insertTab(3, self.tab_52, "Additional Action")
        self.label_tc_dependency_additional_action = QtWidgets.QLabel(self.tab_52)
        self.label_tc_dependency_additional_action.setGeometry(QtCore.QRect(10, 10, 200, 30))
        self.label_tc_dependency_additional_action.setText("Action Item :")
        self.tc_dependency_additional_action = QComboBox(self.tab_52)
        self.tc_dependency_additional_action.addItems(self.specialActions.keys())
        self.tc_dependency_additional_action.setGeometry(QtCore.QRect(100, 10, 250, 30))
        self.tc_dependency_form = CustomForm(self.tab_52)
        self.tc_dependency_form.setGeometry(QtCore.QRect(10, 50, 400, 200))
        self.tc_dependency_additional_action.currentTextChanged.connect(self.tc_dependency_additional_action_changed)
        self.add_tc_dependency_additional_action = QPushButton("Add Action", self.tab_52)
        self.add_tc_dependency_additional_action.setGeometry(QtCore.QRect(390, 10, 100, 30))
        self.add_tc_dependency_additional_action.clicked.connect(self.btn_tc_add_dependency_special_action)
        self.remove_tc_dependency_additional_action = QPushButton("Remove Action", self.tab_52)
        self.remove_tc_dependency_additional_action.setGeometry(QtCore.QRect(510, 10, 100, 30))
        self.remove_tc_dependency_additional_action.clicked.connect(self.btn_tc_remove_dependency_special_action)
        self.table_tc_dependency_additional_action = QtWidgets.QTreeWidget(parent=self.tab_52)
        self.table_tc_dependency_additional_action.setGeometry(QtCore.QRect(10, 360, 630, 330))
        self.table_tc_dependency_additional_action.setObjectName("table_tc_dependency_additional_action")
        self.table_tc_dependency_additional_action.headerItem().setText(0, "Index")
        self.table_tc_dependency_additional_action.headerItem().setText(1, "Action Name")               
            
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
        self.btn_add_path.clicked.connect(self.btn_add_path_clicked)
        self.btn_remove_query.clicked.connect(self.btn_remove_query_clicked)
        self.btn_remove_path.clicked.connect(self.btn_remove_path_clicked)
        self.btn_update_query.clicked.connect(self.btn_update_query_clicked)
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
        self.btn_tc_dependency_update_text_body.clicked.connect(self.btn_tc_dependency_update_text_body_clicked)
        self.btn_tc_remove_dependency_path.clicked.connect(self.btn_tc_remove_dependency_path_clicked)
        self.btn_tc_update_dependency_path.clicked.connect(self.btn_tc_update_dependency_path_clicked)
        self.btn_generate_test_case.clicked.connect(self.btn_generate_test_case_clicked)
        self.btn_clear_dependency_rule.clicked.connect(self.btn_clear_dependency_rule_clicked)
        self.btn_up_dependency_rule.clicked.connect(self.btn_up_dependency_rule_clicked)
        self.btn_down_dependency_rule.clicked.connect(self.btn_down_dependency_rule_clicked)
        self.btn_tc_clear_dependency_rule.clicked.connect(self.btn_tc_clear_dependency_rule_clicked)
        self.btn_tc_up_dependency_rule.clicked.connect(self.btn_tc_up_dependency_rule_clicked)
        self.btn_tc_down_dependency_rule.clicked.connect(self.btn_tc_down_dependency_rule_clicked)
        self.btn_remove_test_case.clicked.connect(self.btn_remove_test_case_clicked)
        self.btn_update_data_rule.clicked.connect(self.btn_update_data_rule_clicked)
        self.btn_dependency_update_data_rule.clicked.connect(self.btn_dependency_update_data_rule_clicked)
        self.btn_tc_dependency_update_data_rule.clicked.connect(self.btn_tc_dependency_update_data_rule_clicked)
        
        # * Table's Item Click Event
        self.table_api_tree.itemClicked.connect(self.api_tree_item_clicked)
        self.table_test_plan_api_list.itemClicked.connect(self.test_plan_api_list_item_clicked)
        self.table_assertion_rule.itemClicked.connect(self.table_assertion_rule_item_clicked)
        self.table_generation_rule.itemClicked.connect(self.table_generation_rule_item_clicked)
        self.table_dependency_generation_rule.itemClicked.connect(self.table_dependency_generation_rule_item_clicked)
        self.table_query.itemClicked.connect(self.table_query_item_clicked)
        self.table_path.itemClicked.connect(self.table_path_item_clicked)
        self.table_tc_query.itemClicked.connect(self.table_tc_query_item_clicked)
        self.table_tc_path.itemClicked.connect(self.table_tc_path_item_clicked)
        self.list_dependency_available_api_list.itemClicked.connect(self.list_dependency_available_api_list_item_clicked)
        self.list_tc_dependency_available_api_list.itemClicked.connect(self.list_tc_dependency_available_api_list_item_clicked)
        self.table_dependency_rule.itemClicked.connect(self.table_dependency_rule_item_clicked)
        self.table_dependency_query.itemClicked.connect(self.table_dependency_query_item_clicked)
        self.table_dependency_path.itemClicked.connect(self.table_dependency_path_item_clicked)
        self.table_tc_dependency_rule.itemClicked.connect(self.table_tc_dependency_item_clicked)
        self.table_tc_assertion_rule.itemClicked.connect(self.table_tc_assertion_rule_item_clicked)
        self.table_tc_dependency_generation_rule.itemClicked.connect(self.table_tc_dependency_generation_rule_item_clicked)
        self.table_tc_dependency_query.itemClicked.connect(self.table_tc_dependency_query_item_clicked)
        self.table_tc_dependency_path.itemClicked.connect(self.table_tc_dependency_path_item_clicked)
        self.table_robot_file_list.itemClicked.connect(self.table_robot_file_list_item_clicked)
        self.btn_export_test_cases.clicked.connect(self.btn_export_test_cases_clicked)
        self.btn_update_info.clicked.connect(self.btn_update_info_clicked)
        
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
        
        # * Convert / Validate Tab
        self.web_page = QtWidgets.QWidget()
        self.web_page_layout = QtWidgets.QVBoxLayout(self.web_page)
        self.web_view = QtWebEngineWidgets.QWebEngineView(self.web_page)
        self.web_view.load(QtCore.QUrl("https://mermade.org.uk/openapi-converter"))
        self.web_page_layout.addWidget(self.web_view)
        self.tabTCG.insertTab(5, self.web_page, "Convert / Validate")
        self.setCentralWidget(self.tabTCG)
        
    def additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        current_action = self.additional_action.currentText()
        fields = self.specialActions[current_action]
        self.form.load_form(current_action, fields)
        
    def dependency_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        current_dependency_action = self.dependency_additional_action.currentText()
        fields = self.specialActions[current_dependency_action]
        self.dependency_form.load_form(current_dependency_action, fields)
        
    def tc_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        current_tc_action = self.tc_additional_action.currentText()
        fields = self.specialActions[current_tc_action]
        self.tc_form.load_form(current_tc_action, fields)
        
    def tc_dependency_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        current_tc_dependency_action = self.tc_dependency_additional_action.currentText()
        fields = self.specialActions[current_tc_dependency_action]
        self.tc_dependency_form.load_form(current_tc_dependency_action, fields)
        
    def btn_tc_add_dependency_special_action(self):
        """ Add the additional action to a dependency. """
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        operation_id = test_plan_parent_item.parent().text(0)
        
        values = self.tc_dependency_form.get_values(self.tc_dependency_additional_action.currentText())
        
        file_path = "./test_plan/" + operation_id + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r+") as f:
                data = json.load(f)
                if data['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type][dependency_sequence_num]['additional_action'] == {}:
                    next_key = str(1)
                else:
                    last_key = int(list(data['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type][dependency_sequence_num]['additional_action'].keys())[-1])
                    next_key = str(last_key + 1)
                result = GeneralTool.add_key_in_json(
                    data,
                    ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, dependency_sequence_num, 'additional_action'],
                    next_key,
                    values,
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully add the additional action to the dependency of {operation_id}.")
                else:
                    logging.error(f"Failed to add the additional action to the dependency of {operation_id}.")
                    
            with open(file_path, "r") as f:
                add_action = json.load(f)
                GeneralTool.parse_tc_dependency_additional_action_rule(
                    operation_id,
                    test_case_id,
                    test_point_id,
                    self.table_tc_dependency_additional_action,
                    dependency_type,
                    dependency_sequence_num,
                )
        else:
            logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_tc_remove_dependency_special_action(self):
        """ Remove the additional action from a dependency. """
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        operation_id = test_plan_parent_item.parent().text(0)
        additional_action_index = self.table_tc_dependency_additional_action.selectedItems()[0].text(0)
        
        file_path = "./test_plan/" + operation_id + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(
                    data,
                    ['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, dependency_sequence_num, 'additional_action', additional_action_index]
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully remove the additional action from the dependency of {operation_id}.")
                else:
                    logging.error(f"Failed to remove the additional action from the dependency of {operation_id}.")
            with open(file_path, "r") as f:
                data = json.load(f)
                GeneralTool.parse_tc_dependency_additional_action_rule(
                    operation_id,
                    test_case_id,
                    test_point_id,
                    self.table_tc_dependency_additional_action,
                    dependency_type,
                    dependency_sequence_num,
                )
        else:
            logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_tc_add_special_action(self):
        """ Add the additional action to a test case. """
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
            action_name = self.tc_additional_action.currentText()
            values = self.tc_form.get_values(action_name)
            
            file_path = "./test_plan/" + operation_id + ".json"
            if os.path.exists(file_path):
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    action_list_len = len(data['test_cases'][test_case_id]['test_point'][test_point_id]["additional_action"])
                    if action_list_len == 0:
                        next_key = str(1)
                    elif action_list_len > 0:
                        last_key = int(list(data['test_cases'][test_case_id]['test_point'][test_point_id]["additional_action"].keys())[-1])
                        next_key = str(last_key + 1)
                        
                    result = GeneralTool.add_key_in_json(
                        data,
                        ['test_cases', test_case_id, 'test_point', test_point_id, 'additional_action'],
                        next_key,
                        values,
                    )
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully add the additional action to the test case of {operation_id}.")
                    else:
                        logging.error(f"Failed to add the additional action to the test case of {operation_id}.")
                        
                with open(file_path, "r") as f:
                    add_action = json.load(f)
                    GeneralTool.parse_tc_additional_action_rule(
                        operation_id,
                        self.table_tc_additional_action,
                        test_case_id,
                        test_point_id,
                    )
            else:
                logging.error(f"Failed to load the test plan of {operation_id}.")
    def btn_tc_remove_special_action(self):
        """ Remove the additional action from a test case. """
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
            action_index = self.table_tc_additional_action.selectedItems()[0].text(0)
            
            file_path = "./test_plan/" + operation_id + ".json"
            if os.path.exists(file_path):
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    result = GeneralTool.remove_key_in_json(
                        data,
                        ['test_cases', test_case_id, 'test_point', test_point_id, 'additional_action', action_index]
                    )
                    if result is not False:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                        logging.info(f"Successfully remove the additional action from the test case of {operation_id}.")
                    else:
                        logging.error(f"Failed to remove the additional action from the test case of {operation_id}.")
                        
                with open(file_path, "r+") as f:
                    add_action = json.load(f)
                    GeneralTool.parse_tc_additional_action_rule(
                        operation_id,
                        self.table_tc_additional_action,
                        test_case_id,
                        test_point_id,
                    )
            else:
                logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_add_dependency_special_action(self):
        """ Add the additional action to a dependency. """
        if len(self.table_dependency_rule.selectedItems()) == 0 or self.table_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        
        values = self.dependency_form.get_values(self.dependency_additional_action.currentText())

        add_action = {}
        file_path = "./DependencyRule/" + operation_id + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r+") as f:
                add_action = json.load(f)
                if "additional_action" not in add_action[dependency_type][dependency_sequence_num]:
                    add_action[dependency_type][dependency_sequence_num]["additional_action"] = {}
                if len(add_action[dependency_type][dependency_sequence_num]["additional_action"]) == 0:
                    next_key = str(1)
                else:
                    key_length = len(add_action[dependency_type][dependency_sequence_num]["additional_action"])
                    last_key = int(list(add_action[dependency_type][dependency_sequence_num]["additional_action"].keys())[-1])
                    next_key = str(last_key + 1)
                    
                result = GeneralTool.add_key_in_json(
                    add_action,
                    [dependency_type, dependency_sequence_num, 'additional_action'],
                    next_key, 
                    values
                )
                if result is not False:
                    f.seek(0)
                    json.dump(add_action, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully add the additional action to the dependency rule of {operation_id}.")
                else:
                    logging.error(f"Failed to add the additional action to the dependency rule of {operation_id}.")
      
            with open(file_path, "r") as f:
                add_action = json.load(f)
                GeneralTool.parse_dependency_additional_action_rule(
                    operation_id,
                    dependency_type,
                    dependency_sequence_num,
                    self.table_dependency_additional_action
                )    
            
    def btn_remove_dependency_special_action(self):
        """ Remove the additional action from a dependency. """
        if len(self.table_dependency_additional_action.selectedItems()) == 0:
            return
        elif self.table_dependency_additional_action.selectedItems()[0].parent() is None:
            return
        elif self.table_dependency_additional_action.selectedItems()[0].parent().parent() is not None:
            return
        
        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        additional_action_sequence_num = self.table_dependency_additional_action.selectedItems()[0].text(0)
        
        file_path = "./DependencyRule/" + operation_id + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r+") as f:
                add_action = json.load(f)
                result = GeneralTool.remove_key_in_json(
                    add_action,
                    [dependency_type, dependency_sequence_num, 'additional_action', additional_action_sequence_num]
                )
                if result is not False:
                    f.seek(0)
                    json.dump(add_action, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully remove the additional action from the dependency rule of {operation_id}.")
                else:
                    logging.error(f"Failed to remove the additional action from the dependency rule of {operation_id}.")
                f.seek(0)
                add_action = json.load(f)
                GeneralTool.parse_dependency_additional_action_rule(
                    operation_id,
                    dependency_type,
                    dependency_sequence_num,
                    self.table_dependency_additional_action
                )                                  
        
    def btn_add_special_action(self):
        """ Add the additional action to a test case. """
        if len(self.table_api_tree.selectedItems()) == 0 or self.table_api_tree.selectedItems()[0].parent() == None:
            return

        selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = self.table_api_tree.selectedItems()[0].text(4)
        values = self.form.get_values(self.additional_action.currentText())
        
        add_action = {}
        file_path = "./AdditionalAction/" + operation_id + ".json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                add_action = json.load(file)
                if len(add_action) == 0:
                    next_key = str(1)
                else:
                    key_length = len(add_action)
                    last_key = int(list(add_action.keys())[-1])
                    next_key = str(last_key + 1)
        
            add_action[next_key] = values
            with open(file_path, "w") as file:
                json.dump(add_action, file, indent=4)
                
            with open(file_path, "r") as file:
                add_action = json.load(file)
                GeneralTool.parse_additional_action_rule(operation_id, self.table_additional_action)

    def btn_remove_special_action(self):
        """ Remove the additional action from a test case. """
        if len(self.table_additional_action.selectedItems()) == 0 or self.table_api_tree.selectedItems()[0] == None:
            return
        elif self.table_additional_action.selectedItems()[0].parent() == None:
            return
        elif self.table_additional_action.selectedItems()[0].parent().parent() != None:
            return

        selected_item = self.table_additional_action.selectedItems()[0]
        parent_item = selected_item.parent()
        operation_id = self.table_api_tree.selectedItems()[0].text(4)
        action_sequence_num = selected_item.text(0)
        
        file_path = "./AdditionalAction/" + operation_id + ".json"
        with open(file_path, "r+") as f:
            add_action = json.load(f)
            result = GeneralTool.remove_key_in_json(
                add_action, 
                [action_sequence_num]
            )
            if result is not False:
                f.seek(0)
                json.dump(add_action, f, indent=4)
                f.truncate()
                logging.info("Remove additional action rule successfully.")
            else:
                logging.error("Remove additional action rule failed.")
        GeneralTool.parse_additional_action_rule(operation_id, self.table_additional_action) 
        
    def btn_update_info_clicked(self):
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
                return
                
        description = self.textbox_tc_description.text()
        request_name = self.textbox_tc_request_name.text()
        response_name = self.textbox_tc_response_name.text()
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]

        file_path = f"./test_plan/{operation_id}.json"
        
        with open(file_path, "r+") as f:
            test_data = json.load(f)
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['description'] = description
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['request_name'] = request_name
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['response_name'] = response_name
        
        with open(file_path, "w") as f:
            json.dump(test_data, f, indent=4)
            logging.info(f"Update {file_path} successfully.")
    
    def btn_remove_test_case_clicked(self):
        selected_items = self.table_test_plan_api_list.selectedItems()
        if not selected_items:
            return

        test_plans_to_remove = []
        test_cases_to_remove = []
        for selected_item in selected_items:
            parent_item = selected_item.parent()

            if parent_item and parent_item.parent():
                test_plan_name = parent_item.parent().text(0)
                test_plan_file = f"./test_plan/{test_plan_name}.json"
                test_case_id, test_point_id = selected_item.text(1).split(".")[0], selected_item.text(1).split(".")[1]
                # * Remove the selected test point from the test plan.
                with open(test_plan_file, "r+") as f:
                    test_plan = json.load(f)
                    result = test_plan["test_cases"][test_case_id]["test_point"].pop(test_point_id)
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Test Case {result} is removed from {test_plan_name}.json")
                    if len(test_plan["test_cases"][test_case_id]["test_point"]) == 0:
                        test_cases_to_remove.append(test_case_id)
            elif parent_item:
                test_plan_name = parent_item.text(0)
                test_plan_file = f"./test_plan/{test_plan_name}.json"
                test_case_id = selected_item.text(1)
                # * Remove the selected test case from the test plan.
                with open(test_plan_file, "r+") as f:
                    test_plan = json.load(f)
                    result = test_plan["test_cases"].pop(test_case_id)
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Test Case {result} is removed from {test_plan_name}.json")
                    if len(test_plan["test_cases"]) == 0:
                        test_plans_to_remove.append(test_plan_name)
            else:
                test_plan_name = selected_item.text(0)
                test_plan_file = f"./test_plan/{test_plan_name}.json"
                if os.path.exists(test_plan_file):
                    os.remove(test_plan_file)
                    logging.info(f"Remove {test_plan_file} successfully")
                    test_plans_to_remove.append(test_plan_name)

        for test_case_id in test_cases_to_remove:
            test_plan_file = f"./test_plan/{test_plan_name}.json"
            with open(test_plan_file, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"].pop(test_case_id)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Test Case {result} is removed from {test_plan_name}.json")

        for test_plan_name in test_plans_to_remove:
            test_plan_file = f"./test_plan/{test_plan_name}.json"
            if os.path.exists(test_plan_file):
                os.remove(test_plan_file)
                logging.info(f"Remove {test_plan_file} successfully")

        GeneralTool.clean_ui_content([
            self.table_test_plan_api_list,
            self.table_tc_assertion_rule,
            self.table_tc_dependency_rule,
            self.table_tc_dependency_path,
            self.table_tc_dependency_generation_rule,
            self.textbox_tc_dependency_requestbody,
            self.table_tc_path,
            self.text_body,
        ])
        GeneralTool.render_test_plan_files(self.table_test_plan_api_list)

    def btn_export_test_cases_clicked(self):
        """ To export the test cases to the local folder. """
        
        export_folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Export", os.path.expanduser("~"))  
        if export_folder_path:
            tcg_folder_path = os.path.join(export_folder_path, "TestCase")
            os.makedirs(tcg_folder_path, exist_ok=True)
            file_list = glob.glob("./TestCases/RESTful_API/*.robot")
            for file in file_list:
                src_path = os.path.join(os.getcwd(), file)
                dst_path = os.path.join(tcg_folder_path, os.path.basename(file))
                shutil.copyfile(src_path, dst_path)
                
            testdata_folder_path = os.path.join(export_folder_path, "TestData")
            os.makedirs(testdata_folder_path, exist_ok=True)
            file_list = glob.glob("./TestData/*.json") + glob.glob("./TestData/Dependency_TestData/*.json")
            for file in file_list:
                src_path = os.path.join(os.getcwd(), file)
                dst_path = os.path.join(testdata_folder_path, os.path.basename(file))
                shutil.copyfile(src_path, dst_path)
                
            logging.info(f"Export test cases to {export_folder_path} successfully")
            GeneralTool.show_info_dialog(f"Export test cases to {export_folder_path} successfully")
            
    def table_robot_file_list_item_clicked(self):
        """ Render the robot file content when the item is clicked. """
        if len(self.table_robot_file_list.selectedItems()) == 0:
            return
        
        file_name = self.table_robot_file_list.selectedItems()[0].text(0)
        with open(f"./TestCases/RESTful_API/{file_name}", "r") as f:
            content = f.read()
        self.text_robot_file.setText(content)
        
    def btn_tc_dependency_update_data_rule_clicked(self):
        if len(self.table_tc_dependency_generation_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
                
        selected_item = self.table_tc_dependency_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        if parent_item is not None and parent_item.parent() is None:
            default_value = self.textbox_tc_dependency_data_rule_value.text()
            data_generator = self.comboBox_tc_dependency_data_rule_data_generator.currentText()
            data_length = self.textbox_tc_dependency_data_rule_data_length.text()
            required_value = self.comboBox_tc_dependency_data_rule_required.currentText()
            nullalbe_value = self.comboBox_tc_dependency_data_rule_nullable.currentText()
            regex_pattern = self.textbox_tc_dependency_data_rule_regex_pattern.text()
            
            with open(f"./test_plan/{operation_id}.json", "r+") as f:
                g_rule = json.load(f)
                g_rule_field = g_rule["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_index]['data_generation_rules'][field_name]
                g_rule_field["Default"] = default_value
                g_rule_field['rule']["Data Generator"] = data_generator
                g_rule_field['rule']["Data Length"] = data_length
                g_rule_field['rule']["Regex Pattern"] = regex_pattern
                if required_value == "True":
                    g_rule_field['rule']["Required"] = True
                elif required_value == "False":
                    g_rule_field['rule']["Required"] = False
                if nullalbe_value == "True":
                    g_rule_field['rule']["Nullable"] = True
                elif nullalbe_value == "False":
                    g_rule_field['rule']["Nullable"] = False
                f.seek(0)
                f.truncate()
                f.write(json.dumps(g_rule, indent=4))
                logging.info(f"Update {field_name} in {operation_id}.json successfully")
                
            GeneralTool.clean_ui_content([
                self.table_tc_dependency_generation_rule,
                self.textbox_tc_dependency_data_rule_type,
                self.textbox_tc_dependency_data_rule_format,
                self.textbox_tc_dependency_data_rule_value,
                self.comboBox_tc_dependency_data_rule_data_generator,
                self.textbox_tc_dependency_data_rule_data_length,
                self.comboBox_tc_dependency_data_rule_required,
                self.comboBox_tc_dependency_data_rule_nullable,
                self.textbox_tc_dependency_data_rule_regex_pattern,
            ])
            GeneralTool.parse_tc_dependency_generation_rule(
                operation_id, 
                self.table_tc_dependency_generation_rule,
                test_case_id,
                test_point_id,
                dependency_type,
                dependency_index
            )
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency_generation_rule)
        
    def btn_dependency_update_data_rule_clicked(self):
        if len(self.table_dependency_generation_rule.selectedItems()) == 0:
            return
        
        selected_item = self.table_dependency_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.table_dependency_rule.selectedItems()[0].text(0)

        if parent_item is not None and parent_item.parent() is None:
            default_value = self.textbox_dependency_data_rule_value.text()
            data_generator = self.comboBox_dependency_data_rule_data_generator.currentText()
            data_length = self.textbox_dependency_data_rule_data_length.text()
            required_value = self.comboBox_dependency_data_rule_required.currentText()
            nullalbe_value = self.comboBox_dependency_data_rule_nullable.currentText()
            regex_pattern = self.textbox_dependency_data_rule_regex_pattern.text()
            
            with open(f"./DependencyRule/{operation_id}.json", "r+") as f:
                g_rule = json.load(f)
                g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]["Default"] = default_value
                g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Data Generator"] = data_generator
                g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Data Length"] = data_length
                g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Regex Pattern"] = regex_pattern
                if required_value == "True":
                    g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Required"] = True
                elif required_value == "False":
                    g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Required"] = False
                if nullalbe_value == "True":
                    g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Nullable"] = True
                elif nullalbe_value == "False":
                    g_rule[dependency_type][dependency_index]['data_generation_rules'][field_name]['rule']["Nullable"] = False
                f.seek(0)
                f.truncate()
                f.write(json.dumps(g_rule, indent=4))
                logging.info(f"Update {field_name} in {operation_id}.json successfully")
                
            GeneralTool.clean_ui_content([
                self.table_dependency_generation_rule,
                self.textbox_dependency_data_rule_type,
                self.textbox_dependency_data_rule_format,
                self.textbox_dependency_data_rule_value,
                self.comboBox_dependency_data_rule_data_generator,
                self.textbox_dependency_data_rule_data_length,
                self.comboBox_dependency_data_rule_required,
                self.comboBox_dependency_data_rule_nullable,
                self.textbox_dependency_data_rule_regex_pattern,
            ])
            GeneralTool.parse_dependency_generation_rule(
                operation_id,
                self.table_dependency_generation_rule,
                dependency_type,
                dependency_index
            )
        
    def btn_update_data_rule_clicked(self):
        """ Update the new data rule to the generation rule. """
        if len(self.table_generation_rule.selectedItems()) == 0:
            return
        
        selected_item = self.table_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)

        if parent_item is not None and parent_item.parent() is None:
            default_value = self.textbox_data_rule_value.text()
            data_generator = self.comboBox_data_rule_data_generator.currentText()
            data_length = self.textbox_data_rule_data_length.text()
            required_value = self.comboBox_data_rule_required.currentText()
            nullalbe_value = self.comboBox_data_rule_nullable.currentText()
            regex_pattern = self.textbox_data_rule_regex_pattern.text()
        
            with open(f"./GenerationRule/{operation_id}.json", "r+") as f:
                g_rule = json.load(f)
                g_rule[field_name]["Default"] = default_value
                g_rule[field_name]['rule']["Data Generator"] = data_generator
                g_rule[field_name]['rule']["Data Length"] = data_length
                g_rule[field_name]['rule']["Regex Pattern"] = regex_pattern
                if required_value == "True":
                    g_rule[field_name]['rule']["Required"] = True
                elif required_value == "False":
                    g_rule[field_name]['rule']["Required"] = False
                if nullalbe_value == "True":
                    g_rule[field_name]['rule']["Nullable"] = True
                elif nullalbe_value == "False":
                    g_rule[field_name]['rule']["Nullable"] = False
                f.seek(0)
                f.truncate()
                f.write(json.dumps(g_rule, indent=4))
                logging.info(f"Update {field_name} in {operation_id}.json successfully")
                
            GeneralTool.clean_ui_content([
                self.table_generation_rule,
                self.textbox_data_rule_type,
                self.textbox_data_rule_format,
                self.textbox_data_rule_value,
                self.comboBox_data_rule_data_generator,
                self.textbox_data_rule_data_length,
                self.comboBox_data_rule_required,
                self.comboBox_data_rule_nullable,
                self.textbox_data_rule_regex_pattern,
            ])
            GeneralTool.parse_generation_rule(operation_id, self.table_generation_rule)
            GeneralTool.expand_and_resize_tree(self.table_generation_rule)
        
    def btn_tc_clear_dependency_rule_clicked(self):
        """ Clear selected dependency rule and table. """
        GeneralTool.clean_ui_content([
            self.line_tc_api_search,
            self.textbox_tc_dependency_return_variable_name,
            self.table_tc_dependency_generation_rule,
            self.textbox_tc_dependency_requestbody,
            self.table_tc_dependency_path,
            self.table_tc_dependency_schema,
        ])
        self.comboBox_tc_dependency_type.setEnabled(True)
        self.line_tc_api_search.setEnabled(True)
        self.list_tc_dependency_available_api_list.clearSelection()
        self.table_tc_dependency_rule.clearSelection()
          
    def btn_clear_dependency_rule_clicked(self):
        """ Clear selected dependency rule and table. """
        GeneralTool.clean_ui_content([
            self.line_api_search,
            self.textbox_dependency_return_variable_name,
            self.table_dependency_generation_rule,
            self.table_dependency_path,
            self.table_dependency_schema,
        ])
        self.comboBox_dependency_type.setEnabled(True)
        self.list_dependency_available_api_list.clearSelection()
        self.table_dependency_rule.clearSelection()
            
    def btn_up_dependency_rule_clicked(self):
        if len(self.table_dependency_rule.selectedItems()) == 0 or self.table_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return

        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.table_dependency_rule.selectedItems()[0].text(0)

        GeneralTool.update_dependency_rule_index(self, operation_id, dependency_type, dependency_index, "up")
        
    def btn_tc_up_dependency_rule_clicked(self):
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.table_tc_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        GeneralTool.update_tc_dependency_rule_index(
            self, operation_id, test_case_id, test_point_id, dependency_type, dependency_sequence_num, "up")
    
    def btn_tc_down_dependency_rule_clicked(self):
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.table_tc_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        GeneralTool.update_tc_dependency_rule_index(
            self, operation_id, test_case_id, test_point_id, dependency_type, dependency_sequence_num, "down")
         
    def btn_down_dependency_rule_clicked(self):
        if len(self.table_dependency_rule.selectedItems()) == 0 or self.table_dependency_rule.selectedItems()[0].parent() is None:
                return
        elif self.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return

        api_selected_item = self.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.table_dependency_rule.selectedItems()[0].text(0)

        GeneralTool.update_dependency_rule_index(self, operation_id, dependency_type, dependency_index, "down")
        
    def btn_generate_test_case_clicked(self):
        
        GeneralTool.teardown_folder_files(["./TestCases/RESTful_API"])  
        Render.generate_robot_test_case()
        self.tabTCG.setCurrentIndex(2)
        GeneralTool.clean_ui_content([self.table_robot_file_list, self.text_robot_file])
        GeneralTool.rander_robot_file_list(self.table_robot_file_list)
        
    def btn_tc_remove_dependency_path_clicked(self):
        if len(self.table_tc_dependency_path.selectedItems()) == 0 or self.table_tc_dependency_path.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.textbox_tc_path_dependency_name.text()
        
        file_path = f"./test_plan/{operation_id}.json"
        with open(file_path, "r+") as f:
            test_plan = json.load(f)
            result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"].pop(name)
            f.seek(0)
            json.dump(test_plan, f, indent=4)
            f.truncate()
            logging.info(f"Dependency Path Rule {result} is removed from {operation_id}.json")
            
        GeneralTool.clean_ui_content([self.table_tc_dependency_path, self.textbox_tc_path_dependency_name, self.textbox_tc_path_dependency_value])
        root_item = QTreeWidgetItem(["path"])
        self.table_tc_dependency_path.addTopLevelItem(root_item)
        path_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.table_tc_dependency_path, level=3)
        
    def btn_tc_update_dependency_path_clicked(self):
        if len(self.table_tc_dependency_path.selectedItems()) == 0 or self.table_tc_dependency_path.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.textbox_tc_path_dependency_name.text()
        value = self.textbox_tc_path_dependency_value.text()
        
        file_path = f"./test_plan/{operation_id}.json"
        with open(file_path, "r+") as f:
            test_plan = json.load(f)
            new_path_data = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"]
            new_path_data[name]["Value"] = value
            result = GeneralTool.update_value_in_json(
                test_plan, 
                ["test_cases", test_case_id ,"test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "path"],
                new_path_data
            )
            if result is not False:
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Update dependency path rule in {file_path} successfully")
            else:
                logging.error(f"Update dependency path rule in {file_path} failed")
        GeneralTool.clean_ui_content([self.table_tc_dependency_path, self.textbox_tc_path_dependency_name, self.textbox_tc_path_dependency_value])
        root_item = QTreeWidgetItem(["path"])
        self.table_tc_dependency_path.addTopLevelItem(root_item)
        path_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.table_tc_dependency_path, level=3)
        
    def table_tc_dependency_path_item_clicked(self):
        selected_item = self.table_tc_dependency_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            name = selected_item.text(0)
            value = selected_item.child(4).text(1) if selected_item.child(4) is not None else ""
            self.textbox_tc_path_dependency_name.setText(name)
            self.textbox_tc_path_dependency_value.setText(value)
            
    def table_tc_dependency_query_item_clicked(self):
        selected_item = self.table_tc_dependency_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            name = selected_item.text(0)
            value = selected_item.child(4).text(1) if selected_item.child(4) is not None else ""
            self.textbox_tc_query_dependency_name.setText(name)
            self.textbox_tc_query_dependency_value.setText(value)
        
    def btn_tc_dependency_update_text_body_clicked(self):
        if len(self.table_test_plan_api_list.selectedItems()) == 0 or len(self.table_tc_dependency_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        selected_item = self.table_tc_dependency_rule.selectedItems()[0]
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        new_value = self.textbox_tc_dependency_requestbody.toPlainText()
        file_path = f"./TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        
        with open(file_path, "r") as f:
            testdata = json.load(f)
        copy_testdata = copy.deepcopy(testdata)
        
        try:
            with open(file_path, "w") as f:
                json.dump(json.loads(new_value), f, indent=4)
        except JSONDecodeError as e:
            with open(file_path, "w") as f:
                json.dump(copy_testdata, f, indent=4)
            error_message = f"Error updating test data with wrong JSON format."
            detailed_message = f"JSONDecodeError: {e}"
            GeneralTool.show_error_dialog(error_message, detailed_message)
            logging.error(f"JSONDecodeError: {e}")
            self.textbox_tc_dependency_requestbody.setPlainText(json.dumps(copy_testdata, indent=4))
            return
        logging.info(f"Update {file_path} successfully")
        return

    def btn_tc_remove_dependency_rule_clicked(self):
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
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
                self.table_tc_dependency_rule,
                self.comboBox_tc_dependency_type,
                self.line_tc_api_search,
                self.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency_rule, level=3)
            
        # * Remove the dependency test data file
        file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        if os.path.exists(f"./TestData/Dependency_TestData/{file_name}"):
            os.remove(f"./TestData/Dependency_TestData/{file_name}")
    
    def btn_tc_update_dependency_rule_clicked(self):
        if len(self.table_tc_dependency_rule.selectedItems()) == 0 or self.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)

            file_path = f"./test_plan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                result = GeneralTool.update_value_in_json(
                    test_plan, 
                    ["test_cases", test_case_id ,"test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "response_name"],
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
                self.table_tc_dependency_rule,
                self.comboBox_tc_dependency_type,
                self.line_tc_api_search,
                self.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency_rule, level=3)
        
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
                obj_name, uri_name = GeneralTool._retrieve_obj_and_action(api)
                file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{sequence_num}.json"
                path = f"./TestData/Dependency_TestData/{file_name}"
                if not os.path.exists(path):
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as test_data_file:
                    json.dump(test_data, test_data_file, indent=4)
                    logging.info(f"Generate dependency test data file: {path}")
                    
                new_value = {
                    "api": api,
                    "object": obj_name,
                    "action": uri_name,
                    "response_name": return_name, 
                    "data_generation_rules": generation_rule if generation_rule is not None else {},
                    "additional_action": {},
                    "path": path_rule if path_rule is not None else {},
                    "config_name": file_name
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
                self.table_tc_dependency_rule
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_tc_dependency_rule, level=3)
        
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
                    "source": self.comboBox_tc_assertion_source.currentText(),
                    "field_expression": self.textbox_tc_assertion_rule_field_expression.text(),
                    "filter_expression": self.textbox_tc_assertion_rule_expression.text(),
                    "assertion_method": self.comboBox_tc_assertion_method.currentText(),
                    "expected_value": self.textbox_tc_assertion_rule_expected_value.text(),
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
                self.textbox_tc_assertion_rule_field_expression,
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
                            key, item['source'], 
                            item['field_expression'],
                            item['filter_expression'], 
                            item['assertion_method'], 
                            item['expected_value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule, level=3)
        
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
                self.textbox_tc_assertion_rule_field_expression,
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
                            key, item['source'],
                            item['field_expression'],
                            item['filter_expression'], 
                            item['assertion_method'], 
                            item['expected_value']
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
                "source": self.comboBox_tc_assertion_source.currentText(),
                "field_expression": self.textbox_tc_assertion_rule_field_expression.text(),
                "filter_expression": self.textbox_tc_assertion_rule_expression.text(),
                "assertion_method": self.comboBox_tc_assertion_method.currentText(),
                "expected_value": self.textbox_tc_assertion_rule_expected_value.text(),
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
                self.textbox_tc_assertion_rule_field_expression,
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
                            key, item['source'],
                            item['field_expression'],
                            item['filter_expression'], 
                            item['assertion_method'], 
                            item['expected_value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule)        
        
    def table_tc_assertion_rule_item_clicked(self, item):
        GeneralTool.clean_ui_content([
            self.comboBox_tc_assertion_source,
            self.textbox_tc_assertion_rule_field_expression,
            self.textbox_tc_assertion_rule_expression,
            self.comboBox_tc_assertion_method,
            self.textbox_tc_assertion_rule_expected_value
        ])
        selected_item = self.table_tc_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.comboBox_tc_assertion_source.setCurrentText(parent_item.text(1))
            self.textbox_tc_assertion_rule_field_expression.setText(selected_item.text(2))
            self.textbox_tc_assertion_rule_expression.setText(selected_item.text(3))
            self.comboBox_tc_assertion_method.setCurrentText(selected_item.text(4))
            self.textbox_tc_assertion_rule_expected_value.setText(selected_item.text(5))
        
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
            GeneralTool.expand_and_resize_tree(self.table_tc_path, level=2)            
    
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
            GeneralTool.expand_and_resize_tree(self.table_tc_path, level=2)
        
        
    def table_tc_path_item_clicked(self):

        selected_item = self.table_tc_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.textbox_tc_path_name.setText(selected_item.text(0))
            self.textbox_tc_path_value.setText(selected_item.text(1))
            
    def table_tc_query_item_clicked(self):
        
        selected_item = self.table_tc_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.textbox_tc_query_name.setText(selected_item.text(0))
            self.textbox_tc_query_value.setText(selected_item.text(1))

    def btn_tc_dependency_generation_rule_remove_clicked(self):
        """ Remove Dependency Generation Rule Field """
        if len(self.table_tc_dependency_generation_rule.selectedItems()) == 0:
            return
        
        # * Retrieve the origin API Operation ID.
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        origin_api_operation_id = test_plan_parent_item.parent().text(0)
        
        # * Retrieve the Dependency Rule Index and Data Generation Rule Field name which should be removed.
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        generation_table_selected_item = self.table_tc_dependency_generation_rule.selectedItems()[0]
        test_case_id = test_plan_selected_item.text(1).split('.')[0]
        test_point_id = test_plan_selected_item.text(1).split('.')[1]
        if generation_table_selected_item.parent() is None or generation_table_selected_item.parent().parent() is not None:
            return
        else:
            generation_rule_field_name = generation_table_selected_item.text(0)
            
        # * Retrieve the Generation Rule List selected items to get the corresponding path
        paths = []
        for item in self.table_tc_dependency_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
        
        # * Update the value in the JSON file
        file_path = f"./test_plan/{origin_api_operation_id}.json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            for path in paths:
                result = GeneralTool.remove_key_in_json(
                    data, 
                    ["test_cases", test_case_id, "test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "data_generation_rules", *path]
                )
                if result is not False:
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, dependency_sequence_num, 'data_generation_rules', *path]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', test_point_id, 'dependency', dependency_type, dependency_sequence_num, 'data_generation_rules', *path]}`.")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        GeneralTool.remove_table_item_from_ui(self.table_tc_dependency_generation_rule)     
       
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
            
        # * Retrieve the Generation Rule List selected items to get the corresponding path
        paths = []
        for item in self.table_dependency_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
                
        # * Update the value in the JSON file
        file_path = f"./DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            for path in paths:
                result = GeneralTool.remove_key_in_json(data, [dependency_type, dependency_sequence_num, "data_generation_rules", *path])
                if result is not False:
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'data_generation_rules', *path]}`.")
                else:
                    logging.debug(f"Error updating JSON file `{file_path}` to remove key `{[dependency_type, dependency_sequence_num, 'data_generation_rules', *path]}`.")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        GeneralTool.remove_table_item_from_ui(self.table_dependency_generation_rule)
        
    def btn_dependency_constraint_rule_apply_clicked(self):
        src_action = self.comboBox_dependency_constraint_rule_src_action.currentText()
        src_path = self.textbox_dependency_constraint_rule_src.text()
        src_condition = self.comboBox_dependency_constraint_rule_condition.currentText()
        src_expected_value = self.textbox_dependency_constraint_rule_expected_value.text()
        dst_action = self.comboBox_dependency_constraint_rule_dst_action.currentText()
        dst_path = self.textbox_dependency_constraint_rule_dst.text()
        dst_action_type = self.comboBox_dependency_constraint_dst_action_type.currentText()
        dst_value = self.textbox_dependency_constraint_rule_dst_value.text()
        dependency_type = self.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_dependency_rule.selectedItems()[0].text(0)
        
        if len(self.table_dependency_rule.selectedItems()) == 0:
            return
        else:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./DependencyRule/{operation_id}.json"
            
        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path,
            dst_action_type, dst_value, dependency_type, dependency_sequence_num, is_general_dependency=True
        )
        
        with open(file_path, "r+") as f:
            data = json.load(f)
        # * Refresh the Dependency Generation Rule Table
        root_item = QTreeWidgetItem(["Data Generation Rule"])
        self.table_dependency_generation_rule.clear()
        self.table_dependency_generation_rule.addTopLevelItem(root_item)
        GeneralTool.parse_request_body(data[dependency_type][dependency_sequence_num]["data_generation_rules"], root_item, editabled=True)
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
        """ Clear the Dependency Constraint Rule UI. """
        GeneralTool.clean_ui_content([
            self.textbox_tc_dependency_constraint_rule_src,
            self.textbox_tc_dependency_constraint_rule_expected_value,
            self.textbox_tc_dependency_constraint_rule_dst,
            self.textbox_tc_dependency_constraint_rule_dst_value,
        ])
    
    def btn_tc_dependency_constraint_rule_apply_clicked(self):
        """ Apply the Dependency Constraint Rule to the selected API. """
        src_action = self.comboBox_tc_dependency_constraint_rule_src_action.currentText()
        src_path = self.textbox_tc_dependency_constraint_rule_src.text()
        src_condition = self.comboBox_tc_dependency_constraint_rule_condition.currentText()
        src_expected_value = self.textbox_tc_dependency_constraint_rule_expected_value.text()
        dst_action = self.comboBox_tc_dependency_constraint_rule_dst_action.currentText()
        dst_path = self.textbox_tc_dependency_constraint_rule_dst.text()
        dst_action_type = self.comboBox_tc_dependency_constraint_dst_action_type.currentText()
        dst_value = self.textbox_tc_dependency_constraint_rule_dst_value.text()
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        if len(self.table_test_plan_api_list.selectedItems()) == 0:
            return
        else:
            test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
    
        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path,
            dst_action_type, dst_value, dependency_type, dependency_sequence_num, True, test_case_id, test_point_id)
        
        with open(f"./test_plan/{operation_id}.json", "r+") as f:
            data = json.load(f)
        # * Refresh the Dependency Generation Rule Table
        root_item = QTreeWidgetItem(["Data Generation Rule"])
        self.table_tc_dependency_generation_rule.clear()
        self.table_tc_dependency_generation_rule.addTopLevelItem(root_item)
        GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["data_generation_rules"], root_item, editabled=True)
        GeneralTool.expand_and_resize_tree(self.table_tc_dependency_generation_rule, 0)
        # * Clear the constraint rule UI
        GeneralTool.clean_ui_content([
            self.textbox_tc_dependency_constraint_rule_src,
            self.textbox_tc_dependency_constraint_rule_expected_value,
            self.textbox_tc_dependency_constraint_rule_dst,
            self.textbox_tc_dependency_constraint_rule_dst_value,
        ])
        self.checkBox_tc_dependency_constraint_rule_wildcard.setChecked(False)
        self.comboBox_tc_dependency_constraint_rule_dst_action.setCurrentText("Then Remove")
        self.comboBox_tc_dependency_constraint_dst_action_type.setCurrentText("")
        self.comboBox_tc_dependency_constraint_dst_action_type.setEnabled(False)
        self.textbox_tc_dependency_constraint_rule_dst_value.setEnabled(False)
    
    def btn_tc_dependency_generation_rule_build_clicked(self):
        
        if len(self.table_tc_dependency_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        selected_item = self.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        dependency_type = self.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        # * Retrieve the dependency data generation rule.
        file_path = f"./test_plan/{operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            generation_rule = data["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["data_generation_rules"]
            testdata = DataBuilder.data_builder(generation_rule)
            
        # * Render the dependency request body. 
        testdata_path = f"./TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        with open(testdata_path, "w+") as f:
            json.dump(testdata, f, indent=4)
        with open(testdata_path, "r+") as f:
            testdata = json.load(f)
        testdata_str = json.dumps(testdata, indent=4)
        self.textbox_tc_dependency_requestbody.setPlainText(testdata_str)
        self.table_tc_dependency_schema_2.setCurrentIndex(1)
        
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
            
    def table_dependency_query_item_clicked(self):
        
        if len(self.table_dependency_query.selectedItems()) == 0:
            return
        
        selected_item = self.table_dependency_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            
            name = selected_item.text(0)
            value = selected_item.child(4).text(1)
            self.textbox_query_dependency_name.setText(name)
            self.textbox_query_dependency_value.setText(value)
        
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
            path = [dependency_type, dependency_sequence_num, "path", name]
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
        path_rule = data[dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.table_path, level=2)
    
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
            path = [dependency_type, dependency_sequence_num, "path", name, "Value"]
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
        path_rule = data[dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.table_path, level=2)
        
    def table_tc_dependency_item_clicked(self):
        
        # * Render the Dependency Action's Data Generation Rule and Path Rule and Schema.
        GeneralTool.clean_ui_content([
            self.table_tc_dependency_generation_rule,
            self.textbox_tc_dependency_requestbody,
            self.table_tc_dependency_path,
            self.table_tc_dependency_schema,
            self.textbox_tc_path_dependency_name,
            self.textbox_tc_path_dependency_value,
            self.table_tc_dependency_additional_action,
        ])
        
        selected_item = self.table_tc_dependency_rule.selectedItems()[0]
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
            if "data_generation_rules" in data and data["data_generation_rules"] != {}:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.table_tc_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["data_generation_rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.table_tc_dependency_generation_rule, level=2)
            else:
                root_item = QTreeWidgetItem(["This API does not have a request body."])
                self.table_dependency_generation_rule.addTopLevelItem(root_item)
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{operation_id}`.")
                
            # * Render the Path Rule
            if "path" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.table_tc_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["path"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_tc_dependency_path, level=2)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{operation_id}`.")
                
            testdata_path = f"./TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{index}.json"
            try:
                with open(testdata_path, "r+") as f:
                    testdata = json.load(f)
                testdata_str = json.dumps(testdata, indent=4)
                self.textbox_tc_dependency_requestbody.setPlainText(testdata_str)
            except FileNotFoundError:
                logging.info(f"Test Data `{testdata_path}` is not exist.")
                
            # * Render the additional action rule
            if 'additional_action' in data:
                root_item = QTreeWidgetItem(["Additional Action"])
                self.table_tc_dependency_additional_action.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["additional_action"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_tc_dependency_additional_action, level=2)
            else:
                logging.info(f"Additional Action is not exist in the dependency rule `{operation_id}`.")
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
            self.table_dependency_additional_action,
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
            if "data_generation_rules" in data and data["data_generation_rules"] != {}:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.table_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["data_generation_rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.table_dependency_generation_rule, level=2)
            else:
                root_item = QTreeWidgetItem(["This API does not have a request body."])
                self.table_dependency_generation_rule.addTopLevelItem(root_item)
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
            
            # * Render the Path Rule
            if "path" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.table_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["path"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_dependency_path, level=2)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
                
            # * Render the additional action rule
            if 'additional_action' in data:
                root_item = QTreeWidgetItem(["Additional Action"])
                self.table_dependency_additional_action.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["additional_action"], root_item)
                GeneralTool.expand_and_resize_tree(self.table_dependency_additional_action, level=2)
                
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
            
            obj_name, action = GeneralTool._retrieve_obj_and_action(api)
            new_value = {"object": obj_name, "action": action, "api": api, "response_name": return_name, "additional_action": {},}
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
        GeneralTool.expand_and_resize_tree(self.table_dependency_rule, level=3)
        
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
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule, level=3)
    
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
                
                updates = {"api": api, "response_name": return_name}
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
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule, level=3)

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
        
    def table_query_item_clicked(self):
        selected_item = self.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is None:
            self.textbox_query_name.setText(selected_item.text(0))
            self.textbox_query_value.setText(selected_item.child(4).text(1))
        
    def btn_add_path_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0:
            return
        
        selected_item = self.table_api_tree.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.textbox_path_name.text(), self.textbox_path_value.text(), self.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./PathRule/{operation_id}.json"
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    json.dump({}, f)
            with open(file_path, "r+") as f:
                data = json.load(f)
                new_value = {
                    "Type": "",
                    "Format": "",
                    "Required": "",
                    "Nullable": "",
                    "Value": value,
                }
                result = GeneralTool.add_key_in_json(data, None, name, new_value)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to add key `{[name, value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to add key `{[name, value]}`.")
                    
            GeneralTool.clean_ui_content([self.textbox_path_name, self.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.table_path)
            GeneralTool.expand_and_resize_tree(self.table_path)
        
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
            
    def btn_update_query_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_query.selectedItems()) == 0:
            return
        
        selected_item = self.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.textbox_query_name.text(), self.textbox_query_value.text(), self.table_api_tree.selectedItems()[0].text(4)      
            file_path = f"./QueryRule/{operation_id}.json"
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
            
            GeneralTool.clean_ui_content([self.textbox_query_name, self.textbox_query_value])
            GeneralTool.parse_query_rule(operation_id, self.table_query)
            GeneralTool.expand_and_resize_tree(self.table_query)

    def btn_remove_query_clicked(self):
        if len(self.table_api_tree.selectedItems()) == 0 or len(self.table_query.selectedItems()) == 0:
            return
        
        selected_item = self.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name = self.textbox_query_name.text()
            operation_id = self.table_api_tree.selectedItems()[0].text(4) 
            file_path = f"./QueryRule/{operation_id}.json"
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
        
            GeneralTool.clean_ui_content([self.textbox_query_name, self.textbox_query_value])
            GeneralTool.parse_path_rule(operation_id, self.table_query)
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
        GeneralTool.clean_ui_content([
            self.textbox_constraint_rule_src, 
            self.textbox_constraint_rule_expected_value, 
            self.textbox_constraint_rule_dst, 
            self.textbox_constraint_rule_dst_value,
        ])
        self.checkBox_constraint_rule_wildcard.setChecked(False)

    def btn_constraint_rule_apply_clicked(self):
        src_action = self.comboBox_constraint_rule_src_action.currentText()
        src_path = self.textbox_constraint_rule_src.text()
        src_condition = self.comboBox_constraint_rule_condition.currentText()
        src_expected_value = self.textbox_constraint_rule_expected_value.text()
        dst_action = self.comboBox_constraint_rule_dst_action.currentText()
        dst_path = self.textbox_constraint_rule_dst.text()
        dst_action_type = self.comboBox_constraint_dst_action_type.currentText()
        dst_value = self.textbox_constraint_rule_dst_value.text()
        
        if len(self.table_api_tree.selectedItems()) == 0 or self.table_api_tree.selectedItems()[0].parent() is None:
            return
        else:
            operation_id = self.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./GenerationRule/{operation_id}.json"
            if os.path.exists(file_path) is False:
                return

        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path, dst_action_type, dst_value)
        
        # * Refresh the Generation Rule Table
        GeneralTool.refresh_generation_rule_table(self.table_api_tree, self.table_generation_rule, file_path)
        GeneralTool.expand_and_resize_tree(self.table_generation_rule, 0)
        GeneralTool.clean_ui_content([self.textbox_constraint_rule_src, self.textbox_constraint_rule_expected_value,
                                        self.textbox_constraint_rule_dst, self.textbox_constraint_rule_dst_value])
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
        GeneralTool.render_data_rule(
            selected_item,
            self.textbox_data_rule_type,
            self.textbox_data_rule_format,
            self.textbox_data_rule_value,
            self.comboBox_data_rule_data_generator,
            self.textbox_data_rule_data_length,
            self.comboBox_data_rule_required,
            self.comboBox_data_rule_nullable,
            self.textbox_data_rule_regex_pattern
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
        GeneralTool.render_data_rule(
            selected_item,
            self.textbox_dependency_data_rule_type,
            self.textbox_dependency_data_rule_format,
            self.textbox_dependency_data_rule_value,
            self.comboBox_dependency_data_rule_data_generator,
            self.textbox_dependency_data_rule_data_length,
            self.comboBox_dependency_data_rule_required,
            self.comboBox_dependency_data_rule_nullable,
            self.textbox_dependency_data_rule_regex_pattern,
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
        GeneralTool.render_data_rule(
            selected_item,
            self.textbox_tc_dependency_data_rule_type,
            self.textbox_tc_dependency_data_rule_format,
            self.textbox_tc_dependency_data_rule_value,
            self.comboBox_tc_dependency_data_rule_data_generator,
            self.textbox_tc_dependency_data_rule_data_length,
            self.comboBox_tc_dependency_data_rule_required,
            self.comboBox_tc_dependency_data_rule_nullable,
            self.textbox_tc_dependency_data_rule_regex_pattern,
        )  

        
    def btn_api_table_add_use_case_clicked(self):
        """ This Add Button is used to duplicate an existing first-level API, and also copy over the Generation Rule, Assertion Rule, and Dependency Request Body. """
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
            for folder in ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule", "AdditionalAction", "QueryRule"]:
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
            self.textbox_assertion_rule_field_expression.setText(selected_item.child(1).text(1))
            self.textbox_assertion_rule_expression.setText(selected_item.child(2).text(1))
            self.comboBox_assertion_method.setCurrentText(selected_item.child(3).text(1))
            self.textbox_assertion_rule_expected_value.setText(selected_item.child(4).text(1))
            self.comboBox_assertion_type.setEnabled(False)
        else:
            self.comboBox_assertion_type.setEnabled(True)
    
    def btn_update_assertion_rule_clicked(self):
        """ Update Assertion Rule Item """
        if len(self.table_assertion_rule.selectedItems()) == 0:
            return
        
        test_type = self.comboBox_assertion_type.currentText()
        source = self.comboBox_assertion_source.currentText()
        filter_expression = self.textbox_assertion_rule_expression.text()
        field_expression = self.textbox_assertion_rule_field_expression.text()
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
                    "source": source, "field_expression": field_expression, "filter_expression": filter_expression, 
                    "assertion_method": method, "expected_value": expected_value
                }
                result = GeneralTool.update_value_in_json(data, path, value)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Update JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
            for clean_item in [self.textbox_assertion_rule_expression, self.textbox_assertion_rule_field_expression, self.textbox_assertion_rule_expected_value, self.table_assertion_rule]:
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
        field_expression = self.textbox_assertion_rule_field_expression.text()
        filter_expression = self.textbox_assertion_rule_expression.text()
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
                "source": source, "field_expression": field_expression, "filter_expression": filter_expression, 
                "assertion_method": method, "expected_value": expected_value
            }
            result = GeneralTool.add_key_in_json(data, path, sequence_num, value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Update JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` with new value `{[test_type, sequence_num, value]}`.")
        for clean_item in [self.textbox_assertion_rule_expression, self.textbox_assertion_rule_field_expression, self.textbox_assertion_rule_expected_value, self.table_assertion_rule]:
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
                try:
                    with open(testdata_path, "r") as file:
                        testdata = json.load(file)
                    copy_testdata = copy.deepcopy(testdata)

                    try:
                        with open(testdata_path, "w") as file:
                            json.dump(json.loads(new_value), file, indent=4)
                    except JSONDecodeError as e:
                        with open(testdata_path, "w") as file:
                            json.dump(copy_testdata, file, indent=4)
                        error_message = f"Error updating test data with wrong JSON format."
                        detailed_message = str(e)
                        GeneralTool.show_error_dialog(error_message, detailed_message)
                        logging.warning(f"Error updating test data file `{testdata_path}` with new value `{new_value}`. Error: {e.msg}")
                        logging.warning(f"Recover the test data file `{testdata_path}` with old value `{copy_testdata}`.")
                        self.text_body.setPlainText(json.dumps(copy_testdata, indent=4))
                        return
                    logging.info(f"Update test data file `{testdata_path}` with new value `{new_value}`.")
                except FileNotFoundError:
                    logging.warning(f"Test data file `{testdata_path}` not found.")
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
        
        if generation_rule != None or generation_rule != {}:
            with open(f"./DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "data_generation_rules" , generation_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'data_generation_rules']}`.")
                else:
                    logging.error(f"Error updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'data_generation_rules']}`.")
                
        if path_rule != None:
            with open(f"./DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "path", path_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'path']}`.")
                else:
                    logging.error(f"Error updating JSON file `./DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'path']}`.")    
        
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
                        
                    # * Create the Query Rule File
                    if 'parameters' in operation:
                        query_rule = GeneralTool.parse_schema_to_query_rule(operation['parameters'])
                        with open(f"./QueryRule/{operation_id}.json", "w") as f:
                            json.dump(query_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have parameters.')
                        
                    # * Create the Dependency Rule File
                    dependency_rule = GeneralTool.init_dependency_rule(operation_id)
                    
                    # * Create the Additional Action Rule File
                    additional_action_rule = GeneralTool.init_additional_action_rule(operation_id)    
         
    def btn_generation_rule_remove_clicked(self):
        """ Remove Generation Rule Item """
        
        # * If no API or Generation Rule is selected, return directly.
        if self.table_api_tree.selectedItems() == [] or self.table_generation_rule.selectedItems() == []:
            return

        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Retrieve the Generation Rule List selected items to get the corresponding paths
        paths = []
        for item in self.table_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
                
        # * Update the value in the JSON file
        file_path = "./GenerationRule/" + operation_id + ".json"
        with open(file_path, 'r+') as f:
            data = json.load(f)
            for path in paths:
                result = GeneralTool.remove_key_in_json(data, path)
                if result is not False:
                    logging.info(f"Successfully removed key `{path}` from JSON file `{file_path}`.")
                else:
                    logging.error(f"Error removing key `{path}` from JSON file `{file_path}`.")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        GeneralTool.remove_table_item_from_ui(self.table_generation_rule)
        
    def btn_api_table_remove_clicked(self):
        """ Remove API Table Item """
        selected_items = self.table_api_tree.selectedItems()
        for item in selected_items:
            if item.parent() is None:
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule", "AdditionalAction", "QueryRule"]
                for folder in teardown_folder:  
                    for child_file in glob.glob(f"./{folder}/{item.text(0)}*.json"):
                        os.remove(child_file)
                self.table_api_tree.takeTopLevelItem(self.table_api_tree.indexOfTopLevelItem(item))
            else:
                file_name = item.text(4)
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule", "AdditionalAction", "QueryRule"]
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
        GeneralTool.teardown_folder_files(["./test_plan", "./TestData", "./TestData/Dependency_TestData"])  
        serial_number = 1
        test_count = self.spinbox_test_case_count.value()
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
                                        tcg_config, TestStrategy, operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata, test_count
                                    )
                                elif api_item.childCount() > 0:
                                    for use_case_i in range(api_item.childCount()):
                                        use_case_item = api_item.child(use_case_i)
                                        use_case_operation_id = use_case_item.text(4)
                                        test_plan_path = TestStrategy.init_test_plan(uri, method, use_case_operation_id)
                                        testdata = DataBuilder.init_test_data(use_case_operation_id)
                                        dependency_testdata = DataBuilder.init_dependency_test_data(use_case_operation_id)
                                        GeneralTool.generate_test_cases(
                                            tcg_config, TestStrategy, use_case_operation_id, uri, method, operation, test_plan_path, serial_number, testdata, dependency_testdata, test_count
                                        )
                                self.tabTCG.setCurrentIndex(1)
        
        # * Render Test Plan to Table
        GeneralTool.clean_ui_content([
            self.table_test_plan_api_list,
            self.table_tc_assertion_rule,
            self.table_tc_dependency_rule,
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
        GeneralTool.teardown_folder_files(["./GenerationRule", "./AssertionRule", "./PathRule", "./DependencyRule", "./AdditionalAction", "./QueryRule"])
        GeneralTool.clean_ui_content([
            self.table_api_tree, 
            self.table_schema,
            self.table_path,
            self.table_query,
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
            self.table_tc_dependency_rule, self.table_tc_assertion_rule, self.text_body, self.textbox_tc_dependency_requestbody, self.table_tc_dependency_path,
            self.table_tc_path, self.textbox_tc_path_name, self.textbox_tc_path_value, self.table_tc_dependency_rule, self.table_tc_dependency_generation_rule,
            self.comboBox_tc_dependency_type, self.line_tc_api_search, self.textbox_tc_dependency_return_variable_name, self.textbox_tc_description,
            self.textbox_tc_request_name, self.textbox_tc_response_name, self.table_tc_additional_action, self.table_tc_dependency_additional_action,])
        self.comboBox_tc_dependency_type.setEnabled(True)
        self.line_tc_api_search.setEnabled(True)
        
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
            
            # * Render the Description and Request/Response Name
            description = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['description']
            request_name = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['request_name']
            response_name = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['response_name']
            self.textbox_tc_description.setText(description)
            self.textbox_tc_request_name.setText(request_name)
            self.textbox_tc_response_name.setText(response_name)
            
            # * Render the Test Case Dependency Rule.
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.table_tc_dependency_rule)
            
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
                            key, item['source'],
                            item['field_expression'],
                            item['filter_expression'], 
                            item['assertion_method'], 
                            item['expected_value']
                        ]
                    )
                )
            GeneralTool.expand_and_resize_tree(self.table_tc_assertion_rule, level=3)
                    
            # * Render the request body in text box.
            serial_num = test_id.split(".")[0]
            test_point = test_id.split(".")[1]
            try:
                with open(f"./TestData/{test_plan_name}_{serial_num}_{test_point}.json") as file:
                    testdata = json.load(file)
                testdata_str = json.dumps(testdata, indent=4)
                self.text_body.setPlainText(testdata_str)
            except FileNotFoundError:
                logging.info(f"Test data file `./TestData/{test_plan_name}_{serial_num}_{test_point}.json` does not exist.")
                
            # * Render Additional Action
            GeneralTool.parse_tc_additional_action_rule(test_plan_name, self.table_tc_additional_action, test_case_id, test_point_id)

    def api_tree_item_clicked(self, item, column):
        """When the api tree item is clicked."""
        # * Clear the table
        GeneralTool.clean_ui_content([
            self.table_schema,
            self.table_generation_rule, 
            self.table_assertion_rule, 
            self.table_path,
            self.table_query,
            self.table_dependency_rule,
            self.table_dependency_path,
            self.table_dependency_generation_rule,
            self.table_dependency_schema,
            self.line_api_search,
            self.textbox_dependency_return_variable_name,
            self.textbox_data_rule_type,
            self.textbox_data_rule_format,
            self.textbox_data_rule_value,
            self.comboBox_data_rule_data_generator,
            self.textbox_data_rule_data_length,
            self.comboBox_data_rule_required,
            self.comboBox_data_rule_nullable,
            self.table_additional_action,
            self.textbox_data_rule_regex_pattern,
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
            operation_id = selected_item.text(4)
            
            # * Render the Generation Rule from the file.
            # * Some API does not have requestBody, so the generation rule file does not exist.
            # * Ex : GET, DELETE, etc.
            GeneralTool.parse_generation_rule(operation_id, self.table_generation_rule)
            
            # * Render the Assertion Rule from the file.
            GeneralTool.parse_assertion_rule(operation_id, self.table_assertion_rule)
            GeneralTool.expand_and_resize_tree(self.table_assertion_rule, level=3)
            
            # * Render the Path Rule from the file.
            GeneralTool.parse_path_rule(operation_id, self.table_path)
            GeneralTool.expand_and_resize_tree(self.table_path, level=3)
            
            # * Render the Query Rule from the file.
            GeneralTool.parse_query_rule(operation_id, self.table_query)
            GeneralTool.expand_and_resize_tree(self.table_query, level=3)
            
            # * Render the Dependency Rule from the file.
            GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.table_dependency_rule, level=3)
            
            # * Render the Additional Action from the file.
            GeneralTool.parse_additional_action_rule(operation_id, self.table_additional_action)
            GeneralTool.expand_and_resize_tree(self.table_additional_action, level=3)
            
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
                        GeneralTool.expand_and_resize_tree(self.table_generation_rule, level=2)
                        GeneralTool.expand_and_resize_tree(self.table_assertion_rule, level=3)
                        GeneralTool.expand_and_resize_tree(self.table_schema, level=2)
                        
                        # * Render the Path Rule from the file.
                        GeneralTool.parse_path_rule(operation_id, self.table_path)
                        GeneralTool.expand_and_resize_tree(self.table_path, level=3)
                        
                        # * Render the Query Rule from the file.
                        GeneralTool.parse_query_rule(operation_id, self.table_query)
                        GeneralTool.expand_and_resize_tree(self.table_query, level=3)
                        
                        # * Render the Dependency Rule from the file.
                        GeneralTool.parse_dependency_rule(operation_id, self.table_dependency_rule)
                        GeneralTool.expand_and_resize_tree(self.table_dependency_rule, level=3)
                        
                        # * Render the Additional Action from the file.
                        GeneralTool.parse_additional_action_rule(operation_id, self.table_additional_action)
                        GeneralTool.expand_and_resize_tree(self.table_additional_action, level=3)
                        
app = QtWidgets.QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec()
