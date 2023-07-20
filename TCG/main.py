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
from lib.databuilder import DataBuilder
from lib.render import Render
from lib.display import CustomForm
from lib.UI import Ui_MainWindow

basedir = os.path.dirname(__file__)

DEBUG = False
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.DEBUG)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # * Load the UI Page
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        # * Set Icon
        self.ui.btn_import_openapi_doc.setIcon(QIcon("./icons/new.png"))
        self.setWindowIcon(QIcon(os.path.join(basedir, './icons/fortinet.png')))
        
        # * Set Window Title
        self.setWindowTitle('FortiTCG (Test Case Generator)')
        
        # * Dynamic UI
        self.ui.specialActions = {
            "None": [],
            "Parser": {
                "API Parser": ["Response Name", "Data", "Filter", "Last Count", "Field", "Return Type"]
            },
            "Analyzer": {
                "Data Analyzer": ["Response Name", "Data", "Filter", "Field", "Last Count", "Verbose", "Return Type", "Result Type"],
                "Config Analyzer": ["Response Name", "Src. Data", "Dest. Data", "Action", "Start Level", "Obj", "Verbose"]
            }
        }
        
        self.ui.tab_22 = QtWidgets.QWidget()
        self.ui.tab_22.setObjectName("tab_22")
        self.ui.tabWidget_2.insertTab(4, self.ui.tab_22, "Additional Action")
        self.ui.specialActionCategory = ["None", "Parser", "Analyzer"]
        
        self.ui.groupBox = QGroupBox(self.ui.tab_22)
        self.ui.groupBox.setGeometry(QtCore.QRect(10, 10, 600, 70))
        self.ui.groupBox.setTitle("Action")
        self.ui.label_action_type = QtWidgets.QLabel(self.ui.groupBox)
        self.ui.label_action_type.setGeometry(QtCore.QRect(10, 30, 230, 30))
        self.ui.label_action_type.setText("Category :")
        self.ui.action_type = QComboBox(self.ui.groupBox)
        self.ui.action_type.addItems(self.ui.specialActionCategory)
        self.ui.action_type.setGeometry(QtCore.QRect(100, 30, 120, 30))
        self.ui.action_type.currentTextChanged.connect(self.action_type_changed)
        self.ui.label_additional_action = QtWidgets.QLabel(self.ui.groupBox)
        self.ui.label_additional_action.setGeometry(QtCore.QRect(250, 30, 230, 30))
        self.ui.label_additional_action.setText("Action :")
        self.ui.additional_action = QComboBox(self.ui.groupBox)
        self.ui.additional_action.setGeometry(QtCore.QRect(320, 30, 240, 30))
        self.ui.form = CustomForm(self.ui.tab_22)
        self.ui.form.setGeometry(QtCore.QRect(10, 90, 400, 200))
        self.ui.additional_action.currentTextChanged.connect(self.additional_action_changed)
        self.ui.add_additional_action = QPushButton("Add Action", self.ui.tab_22)
        self.ui.add_additional_action.setGeometry(QtCore.QRect(10, 300, 120, 30))
        self.ui.add_additional_action.clicked.connect(self.btn_add_special_action)
        self.ui.remove_additional_action = QPushButton("Remove Action", self.ui.tab_22)
        self.ui.remove_additional_action.setGeometry(QtCore.QRect(140, 300, 120, 30))
        self.ui.remove_additional_action.clicked.connect(self.btn_remove_special_action)
        self.ui.table_additional_action = QtWidgets.QTreeWidget(parent=self.ui.tab_22)
        self.ui.table_additional_action.setGeometry(QtCore.QRect(10, 340, 600, 400))
        self.ui.table_additional_action.setObjectName("table_additional_action")
        self.ui.table_additional_action.headerItem().setText(0, "Index")
        self.ui.table_additional_action.headerItem().setText(1, "Action Name")
            
        # *　Dependency Additonal Action
        self.ui.tab_50 = QtWidgets.QWidget()
        self.ui.tab_50.setObjectName("tab_50")
        self.ui.tabWidget_5.insertTab(3, self.ui.tab_50, "Additional Action")
        self.ui.groupBox_2 = QGroupBox(self.ui.tab_50)
        self.ui.groupBox_2.setGeometry(QtCore.QRect(10, 10, 600, 70))
        self.ui.groupBox_2.setTitle("Action")
        self.ui.label_action_type_2 = QtWidgets.QLabel(self.ui.groupBox_2)
        self.ui.label_action_type_2.setGeometry(QtCore.QRect(10, 26, 230, 30))
        self.ui.label_action_type_2.setText("Category :")
        self.ui.dependency_action_type = QComboBox(self.ui.groupBox_2)
        self.ui.dependency_action_type.addItems(self.ui.specialActionCategory)
        self.ui.dependency_action_type.setGeometry(QtCore.QRect(100, 26, 120, 30))
        self.ui.dependency_action_type.currentTextChanged.connect(self.dependency_action_type_changed) 
        self.ui.label_additional_action_2 = QtWidgets.QLabel(self.ui.tab_50)
        self.ui.label_additional_action_2.setGeometry(QtCore.QRect(250, 35, 230, 30))
        self.ui.label_additional_action_2.setText("Action :")
        self.ui.dependency_additional_action = QComboBox(self.ui.tab_50)
        self.ui.dependency_additional_action.setGeometry(QtCore.QRect(320, 35, 240, 30))
        self.ui.dependency_form = CustomForm(self.ui.tab_50)
        self.ui.dependency_form.setGeometry(QtCore.QRect(10, 80, 400, 200))
        self.ui.dependency_additional_action.currentTextChanged.connect(self.dependency_additional_action_changed)
        self.ui.add_dependency_additional_action = QPushButton("Add Action", self.ui.tab_50)
        self.ui.add_dependency_additional_action.setGeometry(QtCore.QRect(630, 10, 100, 30))
        self.ui.add_dependency_additional_action.clicked.connect(self.btn_add_dependency_special_action)
        self.ui.remove_dependency_additional_action = QPushButton("Remove Action", self.ui.tab_50)
        self.ui.remove_dependency_additional_action.setGeometry(QtCore.QRect(630, 50, 100, 30))
        self.ui.remove_dependency_additional_action.clicked.connect(self.btn_remove_dependency_special_action)
        self.ui.table_dependency_additional_action = QtWidgets.QTreeWidget(parent=self.ui.tab_50)
        self.ui.table_dependency_additional_action.setGeometry(QtCore.QRect(10, 360, 630, 330))
        self.ui.table_dependency_additional_action.setObjectName("table_dependency_additional_action")
        self.ui.table_dependency_additional_action.headerItem().setText(0, "Index")
        self.ui.table_dependency_additional_action.headerItem().setText(1, "Action Name")
        
        # * Test Plan Additional Action
        self.ui.tab_51 = QtWidgets.QWidget()
        self.ui.tab_51.setObjectName("tab_51")
        self.ui.tabWidget_testPlan.insertTab(4, self.ui.tab_51, "Additional Action")
        self.ui.groupBox_3 = QGroupBox(self.ui.tab_51)
        self.ui.groupBox_3.setGeometry(QtCore.QRect(10, 10, 600, 70))
        self.ui.groupBox_3.setTitle("Action")   
        self.ui.label_action_type_3 = QtWidgets.QLabel(self.ui.groupBox_3)
        self.ui.label_action_type_3.setGeometry(QtCore.QRect(10, 26, 230, 30))
        self.ui.label_action_type_3.setText("Category :")
        self.ui.tc_action_type = QComboBox(self.ui.groupBox_3)
        self.ui.tc_action_type.addItems(self.ui.specialActionCategory)
        self.ui.tc_action_type.setGeometry(QtCore.QRect(100, 26, 120, 30))
        self.ui.tc_action_type.currentTextChanged.connect(self.tc_action_type_changed)
        self.ui.label_tc_additional_action = QtWidgets.QLabel(self.ui.tab_51)
        self.ui.label_tc_additional_action.setGeometry(QtCore.QRect(240, 35, 200, 30))
        self.ui.label_tc_additional_action.setText("Action :")
        self.ui.tc_additional_action = QComboBox(self.ui.tab_51)
        self.ui.tc_additional_action.setGeometry(QtCore.QRect(300, 35, 250, 30))
        self.ui.tc_form = CustomForm(self.ui.tab_51)
        self.ui.tc_form.setGeometry(QtCore.QRect(10, 80, 400, 200))
        self.ui.tc_additional_action.currentTextChanged.connect(self.tc_additional_action_changed)
        self.ui.add_tc_additional_action = QPushButton("Add Action", self.ui.tab_51)
        self.ui.add_tc_additional_action.setGeometry(QtCore.QRect(10, 300, 120, 30))
        self.ui.add_tc_additional_action.clicked.connect(self.btn_tc_add_special_action)
        self.ui.remove_tc_additional_action = QPushButton("Remove Action", self.ui.tab_51)
        self.ui.remove_tc_additional_action.setGeometry(QtCore.QRect(140, 300, 120, 30))
        self.ui.remove_tc_additional_action.clicked.connect(self.btn_tc_remove_special_action)
        self.ui.table_tc_additional_action = QtWidgets.QTreeWidget(parent=self.ui.tab_51)
        self.ui.table_tc_additional_action.setGeometry(QtCore.QRect(10, 350, 600, 400))
        self.ui.table_tc_additional_action.setObjectName("table_tc_additional_action")
        self.ui.table_tc_additional_action.headerItem().setText(0, "Index")
        self.ui.table_tc_additional_action.headerItem().setText(1, "Action Name")
        
        # * Test Plan Dependency Additional Action
        self.ui.tab_52 = QtWidgets.QWidget()
        self.ui.tab_52.setObjectName("tab_52")
        self.ui.table_tc_dependency_schema_2.insertTab(4, self.ui.tab_52, "Additional Action")
        self.ui.groupBox_4 = QGroupBox(self.ui.tab_52)
        self.ui.groupBox_4.setGeometry(QtCore.QRect(10, 10, 600, 70))
        self.ui.groupBox_4.setTitle("Action")   
        self.ui.label_action_type_4 = QtWidgets.QLabel(self.ui.groupBox_4)
        self.ui.label_action_type_4.setGeometry(QtCore.QRect(10, 26, 230, 30))
        self.ui.label_action_type_4.setText("Category :")
        self.ui.tc_dependency_action_type = QComboBox(self.ui.groupBox_4)
        self.ui.tc_dependency_action_type.addItems(self.ui.specialActionCategory)
        self.ui.tc_dependency_action_type.setGeometry(QtCore.QRect(100, 26, 120, 30))
        self.ui.tc_dependency_action_type.currentTextChanged.connect(self.tc_dependency_action_type_changed)
        self.ui.label_tc_dependency_additional_action = QtWidgets.QLabel(self.ui.tab_52)
        self.ui.label_tc_dependency_additional_action.setGeometry(QtCore.QRect(250, 35, 230, 30))
        self.ui.label_tc_dependency_additional_action.setText("Action :")
        self.ui.tc_dependency_additional_action = QComboBox(self.ui.tab_52)
        self.ui.tc_dependency_additional_action.setGeometry(QtCore.QRect(320, 35, 240, 30))
        self.ui.tc_dependency_form = CustomForm(self.ui.tab_52)
        self.ui.tc_dependency_form.setGeometry(QtCore.QRect(10, 80, 400, 200))
        self.ui.tc_dependency_additional_action.currentTextChanged.connect(self.tc_dependency_additional_action_changed)
        self.ui.add_tc_dependency_additional_action = QPushButton("Add Action", self.ui.tab_52)
        self.ui.add_tc_dependency_additional_action.setGeometry(QtCore.QRect(630, 10, 100, 30))
        self.ui.add_tc_dependency_additional_action.clicked.connect(self.btn_tc_add_dependency_special_action)
        self.ui.remove_tc_dependency_additional_action = QPushButton("Remove Action", self.ui.tab_52)
        self.ui.remove_tc_dependency_additional_action.setGeometry(QtCore.QRect(630, 50, 100, 30))
        self.ui.remove_tc_dependency_additional_action.clicked.connect(self.btn_tc_remove_dependency_special_action)
        self.ui.table_tc_dependency_additional_action = QtWidgets.QTreeWidget(parent=self.ui.tab_52)
        self.ui.table_tc_dependency_additional_action.setGeometry(QtCore.QRect(10, 360, 630, 330))
        self.ui.table_tc_dependency_additional_action.setObjectName("table_tc_dependency_additional_action")
        self.ui.table_tc_dependency_additional_action.headerItem().setText(0, "Index")
        self.ui.table_tc_dependency_additional_action.headerItem().setText(1, "Action Name")               
            
        # * Define the Button Event
        self.ui.btn_import_openapi_doc.clicked.connect(self.import_openapi_doc)
        self.ui.btn_import_object_mapping_file.clicked.connect(self.import_object_mapping_file)
        self.ui.btn_generate_test_plan.clicked.connect(self.generate_test_plan)
        self.ui.btn_api_table_remove.clicked.connect(self.btn_api_table_remove_clicked)
        self.ui.btn_generation_rule_remove.clicked.connect(self.btn_generation_rule_remove_clicked)
        self.ui.btn_update_text_body.clicked.connect(self.btn_update_text_body_clicked)
        self.ui.btn_add_assertion_rule.clicked.connect(self.btn_add_assertion_rule_clicked)
        self.ui.btn_update_assertion_rule.clicked.connect(self.btn_update_assertion_rule_clicked)
        self.ui.btn_remove_assertion_rule.clicked.connect(self.btn_remove_assertion_rule_clicked)
        self.ui.btn_api_table_add_use_case.clicked.connect(self.btn_api_table_add_use_case_clicked)
        self.ui.btn_constraint_rule_apply.clicked.connect(self.btn_constraint_rule_apply_clicked)
        self.ui.btn_constraint_rule_clear.clicked.connect(self.btn_constraint_rule_clear_clicked)
        self.ui.btn_add_path.clicked.connect(self.btn_add_path_clicked)
        self.ui.btn_remove_query.clicked.connect(self.btn_remove_query_clicked)
        self.ui.btn_update_query.clicked.connect(self.btn_update_query_clicked)
        self.ui.btn_remove_path.clicked.connect(self.btn_remove_path_clicked)
        self.ui.btn_update_path.clicked.connect(self.btn_update_path_clicked)
        self.ui.btn_tc_remove_query.clicked.connect(self.btn_tc_remove_query_clicked)
        self.ui.btn_tc_update_query.clicked.connect(self.btn_tc_update_query_clicked)
        self.ui.btn_tc_remove_path.clicked.connect(self.btn_tc_remove_path_clicked)
        self.ui.btn_tc_update_path.clicked.connect(self.btn_tc_update_path_clicked)
        self.ui.btn_add_dependency_rule.clicked.connect(self.btn_add_dependency_rule_clicked)
        self.ui.btn_tc_add_dependency_rule.clicked.connect(self.btn_tc_add_dependency_rule_clicked)
        self.ui.btn_tc_remove_dependency_rule.clicked.connect(self.btn_tc_remove_dependency_rule_clicked)
        self.ui.btn_tc_update_dependency_rule.clicked.connect(self.btn_tc_update_dependency_rule_clicked)
        self.ui.btn_remove_dependency_rule.clicked.connect(self.btn_remove_dependency_rule_clicked)
        self.ui.btn_update_dependency_rule.clicked.connect(self.btn_update_dependency_rule_clicked)
        self.ui.btn_remove_dependency_path.clicked.connect(self.btn_remove_dependency_path_clicked)
        self.ui.btn_update_dependency_path.clicked.connect(self.btn_update_dependency_path_clicked)
        self.ui.btn_remove_dependency_query.clicked.connect(self.btn_remove_dependency_query_clicked)
        self.ui.btn_update_dependency_query.clicked.connect(self.btn_update_dependency_query_clicked)
        self.ui.btn_dependency_constraint_rule_clear.clicked.connect(self.btn_dependency_constraint_rule_clear_clicked)
        self.ui.btn_dependency_constraint_rule_apply.clicked.connect(self.btn_dependency_constraint_rule_apply_clicked)
        self.ui.btn_dependency_generation_rule_remove.clicked.connect(self.btn_dependency_generation_rule_remove_clicked)
        self.ui.btn_tc_dependency_constraint_rule_clear.clicked.connect(self.btn_tc_dependency_constraint_rule_clear_clicked)
        self.ui.btn_tc_dependency_constraint_rule_apply.clicked.connect(self.btn_tc_dependency_constraint_rule_apply_clicked)
        self.ui.btn_tc_dependency_generation_rule_remove.clicked.connect(self.btn_tc_dependency_generation_rule_remove_clicked)
        self.ui.btn_tc_dependency_generation_rule_build.clicked.connect(self.btn_tc_dependency_generation_rule_build_clicked)
        self.ui.btn_tc_add_assertion_rule.clicked.connect(self.btn_tc_add_assertion_rule_clicked)
        self.ui.btn_tc_update_assertion_rule.clicked.connect(self.btn_tc_update_assertion_rule_clicked)
        self.ui.btn_tc_remove_assertion_rule.clicked.connect(self.btn_tc_remove_assertion_rule_clicked)
        self.ui.btn_tc_dependency_update_text_body.clicked.connect(self.btn_tc_dependency_update_text_body_clicked)
        self.ui.btn_tc_remove_dependency_path.clicked.connect(self.btn_tc_remove_dependency_path_clicked)
        self.ui.btn_tc_update_dependency_path.clicked.connect(self.btn_tc_update_dependency_path_clicked)
        self.ui.btn_tc_remove_dependency_query.clicked.connect(self.btn_tc_remove_dependency_query_clicked)
        self.ui.btn_tc_update_dependency_query.clicked.connect(self.btn_tc_update_dependency_query_clicked)
        self.ui.btn_generate_test_case.clicked.connect(self.btn_generate_test_case_clicked)
        self.ui.btn_clear_dependency_rule.clicked.connect(self.btn_clear_dependency_rule_clicked)
        self.ui.btn_up_dependency_rule.clicked.connect(self.btn_up_dependency_rule_clicked)
        self.ui.btn_down_dependency_rule.clicked.connect(self.btn_down_dependency_rule_clicked)
        self.ui.btn_tc_clear_dependency_rule.clicked.connect(self.btn_tc_clear_dependency_rule_clicked)
        self.ui.btn_tc_up_dependency_rule.clicked.connect(self.btn_tc_up_dependency_rule_clicked)
        self.ui.btn_tc_down_dependency_rule.clicked.connect(self.btn_tc_down_dependency_rule_clicked)
        self.ui.btn_remove_test_case.clicked.connect(self.btn_remove_test_case_clicked)
        self.ui.btn_update_data_rule.clicked.connect(self.btn_update_data_rule_clicked)
        self.ui.btn_dependency_update_data_rule.clicked.connect(self.btn_dependency_update_data_rule_clicked)
        self.ui.btn_tc_dependency_update_data_rule.clicked.connect(self.btn_tc_dependency_update_data_rule_clicked)
        
        # * Table's Item Click Event
        self.ui.table_api_tree.itemClicked.connect(self.api_tree_item_clicked)
        self.ui.table_test_plan_api_list.itemClicked.connect(self.test_plan_api_list_item_clicked)
        self.ui.table_assertion_rule.itemClicked.connect(self.table_assertion_rule_item_clicked)
        self.ui.table_generation_rule.itemClicked.connect(self.table_generation_rule_item_clicked)
        self.ui.table_dependency_generation_rule.itemClicked.connect(self.table_dependency_generation_rule_item_clicked)
        self.ui.table_query.itemClicked.connect(self.table_query_item_clicked)
        self.ui.table_path.itemClicked.connect(self.table_path_item_clicked)
        self.ui.table_tc_query.itemClicked.connect(self.table_tc_query_item_clicked)
        self.ui.table_tc_path.itemClicked.connect(self.table_tc_path_item_clicked)
        self.ui.list_dependency_available_api_list.itemClicked.connect(self.list_dependency_available_api_list_item_clicked)
        self.ui.list_tc_dependency_available_api_list.itemClicked.connect(self.list_tc_dependency_available_api_list_item_clicked)
        self.ui.table_dependency_rule.itemClicked.connect(self.table_dependency_rule_item_clicked)
        self.ui.table_dependency_query.itemClicked.connect(self.table_dependency_query_item_clicked)
        self.ui.table_dependency_path.itemClicked.connect(self.table_dependency_path_item_clicked)
        self.ui.table_tc_dependency_rule.itemClicked.connect(self.table_tc_dependency_item_clicked)
        self.ui.table_tc_assertion_rule.itemClicked.connect(self.table_tc_assertion_rule_item_clicked)
        self.ui.table_tc_dependency_generation_rule.itemClicked.connect(self.table_tc_dependency_generation_rule_item_clicked)
        self.ui.table_tc_dependency_query.itemClicked.connect(self.table_tc_dependency_query_item_clicked)
        self.ui.table_tc_dependency_path.itemClicked.connect(self.table_tc_dependency_path_item_clicked)
        self.ui.table_robot_file_list.itemClicked.connect(self.table_robot_file_list_item_clicked)
        self.ui.btn_export_test_cases.clicked.connect(self.btn_export_test_cases_clicked)
        self.ui.btn_export_test_plans.clicked.connect(self.btn_export_test_plans_clicked)
        self.ui.btn_update_info.clicked.connect(self.btn_update_info_clicked)
        
        # * Item Changed Event
        self.ui.table_generation_rule.itemChanged.connect(self.generation_rule_item_changed)
        self.ui.comboBox_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_constraint_rule_src_action_changed)
        self.ui.comboBox_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_constraint_rule_dst_action_changed)
        self.ui.comboBox_dependency_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_dependency_constraint_rule_dst_action_changed)
        self.ui.comboBox_dependency_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_dependency_constraint_rule_src_action_changed)
        self.ui.comboBox_tc_dependency_constraint_rule_src_action.currentTextChanged.connect(self.comboBox_tc_dependency_constraint_rule_src_action_changed)
        self.ui.comboBox_tc_dependency_constraint_rule_dst_action.currentTextChanged.connect(self.comboBox_tc_dependency_constraint_rule_dst_action_changed)
        self.ui.line_api_search.textChanged.connect(self.line_api_search_text_changed)
        self.ui.line_tc_api_search.textChanged.connect(self.line_tc_api_search_text_changed)
        
        # * Checkbox Event
        self.ui.checkBox_constraint_rule_wildcard.stateChanged.connect(self.checkBox_constraint_rule_wildcard_changed)
        self.ui.checkBox_dependency_constraint_rule_wildcard.stateChanged.connect(self.checkBox_dependency_constraint_rule_wildcard_changed)
        self.ui.checkBox_tc_dependency_constraint_rule_wildcard.stateChanged.connect(self.checkBox_tc_dependency_constraint_rule_wildcard_changed)
        
        # * Completer Event
        self.ui.search_completer = QCompleter()
        self.ui.line_api_search.setCompleter(self.ui.search_completer)
        self.ui.tc_search_completer = QCompleter()
        self.ui.line_tc_api_search.setCompleter(self.ui.tc_search_completer)
        
        # # * Convert / Validate Tab
        # self.ui.web_page = QtWidgets.QWidget()
        # self.ui.web_page_layout = QtWidgets.QVBoxLayout(self.ui.web_page)
        # self.ui.web_view = QtWebEngineWidgets.QWebEngineView(self.ui.web_page)
        # self.ui.web_view.load(QtCore.QUrl("https://mermade.org.uk/openapi-converter"))
        # self.ui.web_page_layout.addWidget(self.ui.web_view)
        # self.ui.tabTCG.insertTab(5, self.ui.web_page, "Convert / Validate")
        # self.setCentralWidget(self.ui.tabTCG)
        
    def action_type_changed(self):
        """ When the action type is changed by the user, the form will be reloaded. """
        self.ui.additional_action.clear()
        category = self.ui.action_type.currentText()
        if category != "None":
            actions = self.ui.specialActions[category].keys()
            self.ui.additional_action.addItems(actions)
        
    def additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        category = self.ui.action_type.currentText()
        action = self.ui.additional_action.currentText()
        if category != "None" and action != "":
            self.ui.form.clear_form()
            fields = self.ui.specialActions[category][action]
            self.ui.form.load_form(action, fields)
            
    def dependency_action_type_changed(self):
        """ When the action type is changed by the user, the form will be reloaded. """
        self.ui.dependency_additional_action.clear()
        category = self.ui.dependency_action_type.currentText()
        if category != "None":
            actions = self.ui.specialActions[category].keys()
            self.ui.dependency_additional_action.addItems(actions)
        
    def dependency_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        category = self.ui.dependency_action_type.currentText()
        action = self.ui.dependency_additional_action.currentText()
        if category != "None" and action != "":
            self.ui.dependency_form.clear_form()
            fields = self.ui.specialActions[category][action]
            self.ui.dependency_form.load_form(action, fields)
            
    def tc_action_type_changed(self):
        """ When the action type is changed by the user, the form will be reloaded. """
        self.ui.tc_additional_action.clear()
        category = self.ui.tc_action_type.currentText()
        if category != "None":
            actions = self.ui.specialActions[category].keys()
            self.ui.tc_additional_action.addItems(actions)
        
    def tc_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        category = self.ui.tc_action_type.currentText()
        action = self.ui.tc_additional_action.currentText()
        if category != "None" and action != "":
            self.ui.tc_form.clear_form()
            fields = self.ui.specialActions[category][action]
            self.ui.tc_form.load_form(action, fields)

    def tc_dependency_action_type_changed(self):
        """ When the action type is changed by the user, the form will be reloaded. """
        self.ui.tc_dependency_additional_action.clear()
        category = self.ui.tc_dependency_action_type.currentText()
        if category != "None":
            actions = self.ui.specialActions[category].keys()
            self.ui.tc_dependency_additional_action.addItems(actions)
        
    def tc_dependency_additional_action_changed(self):
        """ When the additional action is changed by the user, the form will be reloaded. """
        category = self.ui.tc_dependency_action_type.currentText()
        action = self.ui.tc_dependency_additional_action.currentText()
        if category != "None" and action != "":
            self.ui.tc_dependency_form.clear_form()
            fields = self.ui.specialActions[category][action]
            self.ui.tc_dependency_form.load_form(action, fields)
        
    def btn_tc_add_dependency_special_action(self):
        """ Add the additional action to a dependency. """
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        operation_id = test_plan_parent_item.parent().text(0)
        
        values = self.ui.tc_dependency_form.get_values(self.ui.tc_dependency_additional_action.currentText())
        
        file_path = "./artifacts/TestPlan/" + operation_id + ".json"
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
                    self.ui.table_tc_dependency_additional_action,
                    dependency_type,
                    dependency_sequence_num,
                )
        else:
            logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_tc_remove_dependency_special_action(self):
        """ Remove the additional action from a dependency. """
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        operation_id = test_plan_parent_item.parent().text(0)
        additional_action_index = self.ui.table_tc_dependency_additional_action.selectedItems()[0].text(0)
        
        file_path = "./artifacts/TestPlan/" + operation_id + ".json"
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
                    self.ui.table_tc_dependency_additional_action,
                    dependency_type,
                    dependency_sequence_num,
                )
        else:
            logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_tc_add_special_action(self):
        """ Add the additional action to a test case. """
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
            action_name = self.ui.tc_additional_action.currentText()
            values = self.ui.tc_form.get_values(action_name)
            
            file_path = "./artifacts/TestPlan/" + operation_id + ".json"
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
                        self.ui.table_tc_additional_action,
                        test_case_id,
                        test_point_id,
                    )
            else:
                logging.error(f"Failed to load the test plan of {operation_id}.")
    def btn_tc_remove_special_action(self):
        """ Remove the additional action from a test case. """
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
            action_index = self.ui.table_tc_additional_action.selectedItems()[0].text(0)
            
            file_path = "./artifacts/TestPlan/" + operation_id + ".json"
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
                        self.ui.table_tc_additional_action,
                        test_case_id,
                        test_point_id,
                    )
            else:
                logging.error(f"Failed to load the test plan of {operation_id}.")
    
    def btn_add_dependency_special_action(self):
        """ Add the additional action to a dependency. """
        if len(self.ui.table_dependency_rule.selectedItems()) == 0 or self.ui.table_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.ui.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        
        values = self.ui.dependency_form.get_values(self.ui.dependency_additional_action.currentText())

        add_action = {}
        file_path = "./artifacts/DependencyRule/" + operation_id + ".json"
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
                    self.ui.table_dependency_additional_action
                )    
            
    def btn_remove_dependency_special_action(self):
        """ Remove the additional action from a dependency. """
        if len(self.ui.table_dependency_additional_action.selectedItems()) == 0:
            return
        elif self.ui.table_dependency_additional_action.selectedItems()[0].parent() is None:
            return
        elif self.ui.table_dependency_additional_action.selectedItems()[0].parent().parent() is not None:
            return
        
        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        additional_action_sequence_num = self.ui.table_dependency_additional_action.selectedItems()[0].text(0)
        
        file_path = "./artifacts/DependencyRule/" + operation_id + ".json"
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
                    self.ui.table_dependency_additional_action
                )                                  
        
    def btn_add_special_action(self):
        """ Add the additional action to a test case. """
        if len(self.ui.table_api_tree.selectedItems()) == 0 or self.ui.table_api_tree.selectedItems()[0].parent() == None:
            return

        selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        values = self.ui.form.get_values(self.ui.additional_action.currentText())
        
        add_action = {}
        file_path = "./artifacts/AdditionalAction/" + operation_id + ".json"
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
                GeneralTool.parse_additional_action_rule(operation_id, self.ui.table_additional_action)

    def btn_remove_special_action(self):
        """ Remove the additional action from a test case. """
        if len(self.ui.table_additional_action.selectedItems()) == 0 or self.ui.table_api_tree.selectedItems()[0] == None:
            return
        elif self.ui.table_additional_action.selectedItems()[0].parent() == None:
            return
        elif self.ui.table_additional_action.selectedItems()[0].parent().parent() != None:
            return

        selected_item = self.ui.table_additional_action.selectedItems()[0]
        parent_item = selected_item.parent()
        operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        action_sequence_num = selected_item.text(0)
        
        file_path = "./artifacts/AdditionalAction/" + operation_id + ".json"
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
        GeneralTool.parse_additional_action_rule(operation_id, self.ui.table_additional_action) 
        
    def btn_update_info_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
                return
                
        description = self.ui.textbox_tc_description.text()
        request_name = self.ui.textbox_tc_request_name.text()
        response_name = self.ui.textbox_tc_response_name.text()
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]

        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        
        with open(file_path, "r+") as f:
            test_data = json.load(f)
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['description'] = description
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['request_name'] = request_name
        test_data['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['response_name'] = response_name
        
        with open(file_path, "w") as f:
            json.dump(test_data, f, indent=4)
            logging.info(f"Update {file_path} successfully.")
    
    def btn_remove_test_case_clicked(self):
        selected_items = self.ui.table_test_plan_api_list.selectedItems()
        if not selected_items:
            return

        test_plans_to_remove = []
        test_cases_to_remove = []
        for selected_item in selected_items:
            parent_item = selected_item.parent()

            if parent_item and parent_item.parent():
                test_plan_name = parent_item.parent().text(0)
                test_plan_file = f"./artifacts/TestPlan/{test_plan_name}.json"
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
                test_plan_file = f"./artifacts/TestPlan/{test_plan_name}.json"
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
                test_plan_file = f"./artifacts/TestPlan/{test_plan_name}.json"
                if os.path.exists(test_plan_file):
                    os.remove(test_plan_file)
                    logging.info(f"Remove {test_plan_file} successfully")
                    test_plans_to_remove.append(test_plan_name)

        for test_case_id in test_cases_to_remove:
            test_plan_file = f"./artifacts/TestPlan/{test_plan_name}.json"
            with open(test_plan_file, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"].pop(test_case_id)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Test Case {result} is removed from {test_plan_name}.json")

        for test_plan_name in test_plans_to_remove:
            test_plan_file = f"./artifacts/TestPlan/{test_plan_name}.json"
            if os.path.exists(test_plan_file):
                os.remove(test_plan_file)
                logging.info(f"Remove {test_plan_file} successfully")

        GeneralTool.clean_ui_content([
            self.ui.table_test_plan_api_list,
            self.ui.table_tc_assertion_rule,
            self.ui.table_tc_dependency_rule,
            self.ui.table_tc_dependency_path,
            self.ui.table_tc_dependency_generation_rule,
            self.ui.textbox_tc_dependency_requestbody,
            self.ui.table_tc_path,
            self.ui.text_body,
        ])
        GeneralTool.render_test_plan_files(self.ui.table_test_plan_api_list)

    def btn_export_test_plans_clicked(self):
        """ To export the test plans to the local folder. """
        
        export_folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Export", os.path.expanduser("~"))
        if export_folder_path:
            test_plan_folder_path = os.path.join(export_folder_path, "TestPlan")
            os.makedirs(test_plan_folder_path, exist_ok=True)
            file_list = glob.glob("./artifacts/TestPlan/*.json")
            for file in file_list:
                src_path = os.path.join(os.getcwd(), file)
                dst_path = os.path.join(test_plan_folder_path, os.path.basename(file))
                shutil.copyfile(src_path, dst_path)
                
            logging.info(f"Export test plans to {export_folder_path} successfully")
            GeneralTool.show_info_dialog(f"Export test plans to {export_folder_path} successfully")

    def btn_export_test_cases_clicked(self):
        """ To export the test cases to the local folder. """
        
        export_folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Export", os.path.expanduser("~"))  
        if export_folder_path:
            tcg_folder_path = os.path.join(export_folder_path, "TestCase")
            os.makedirs(tcg_folder_path, exist_ok=True)
            file_list = glob.glob("./artifacts/TestCase/RESTful_API/*.robot")
            for file in file_list:
                src_path = os.path.join(os.getcwd(), file)
                dst_path = os.path.join(tcg_folder_path, os.path.basename(file))
                shutil.copyfile(src_path, dst_path)
                
            testdata_folder_path = os.path.join(export_folder_path, "TestData")
            os.makedirs(testdata_folder_path, exist_ok=True)
            file_list = glob.glob("./artifacts/TestData/*.json") + glob.glob("./artifacts/TestData/Dependency_TestData/*.json")
            for file in file_list:
                src_path = os.path.join(os.getcwd(), file)
                dst_path = os.path.join(testdata_folder_path, os.path.basename(file))
                shutil.copyfile(src_path, dst_path)
                
            logging.info(f"Export test cases to {export_folder_path} successfully")
            GeneralTool.show_info_dialog(f"Export test cases to {export_folder_path} successfully")
            
    def table_robot_file_list_item_clicked(self):
        """ Render the robot file content when the item is clicked. """
        if len(self.ui.table_robot_file_list.selectedItems()) == 0:
            return
        
        file_name = self.ui.table_robot_file_list.selectedItems()[0].text(0)
        with open(f"./artifacts/TestCase/RESTful_API/{file_name}", "r") as f:
            content = f.read()
        self.ui.text_robot_file.setText(content)
        
    def btn_tc_dependency_update_data_rule_clicked(self):
        if len(self.ui.table_tc_dependency_generation_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
                
        selected_item = self.ui.table_tc_dependency_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        if parent_item is not None and parent_item.parent() is None:
            default_value = self.ui.textbox_tc_dependency_data_rule_value.text()
            data_generator = self.ui.comboBox_tc_dependency_data_rule_data_generator.currentText()
            data_length = self.ui.textbox_tc_dependency_data_rule_data_length.text()
            required_value = self.ui.comboBox_tc_dependency_data_rule_required.currentText()
            nullalbe_value = self.ui.comboBox_tc_dependency_data_rule_nullable.currentText()
            regex_pattern = self.ui.textbox_tc_dependency_data_rule_regex_pattern.text()
            
            with open(f"./artifacts/TestPlan/{operation_id}.json", "r+") as f:
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
                self.ui.table_tc_dependency_generation_rule,
                self.ui.textbox_tc_dependency_data_rule_type,
                self.ui.textbox_tc_dependency_data_rule_format,
                self.ui.textbox_tc_dependency_data_rule_value,
                self.ui.comboBox_tc_dependency_data_rule_data_generator,
                self.ui.textbox_tc_dependency_data_rule_data_length,
                self.ui.comboBox_tc_dependency_data_rule_required,
                self.ui.comboBox_tc_dependency_data_rule_nullable,
                self.ui.textbox_tc_dependency_data_rule_regex_pattern,
            ])
            GeneralTool.parse_tc_dependency_generation_rule(
                operation_id, 
                self.ui.table_tc_dependency_generation_rule,
                test_case_id,
                test_point_id,
                dependency_type,
                dependency_index
            )
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_generation_rule)
        
    def btn_dependency_update_data_rule_clicked(self):
        if len(self.ui.table_dependency_generation_rule.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_dependency_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.ui.table_dependency_rule.selectedItems()[0].text(0)

        if parent_item is not None and parent_item.parent() is None:
            default_value = self.ui.textbox_dependency_data_rule_value.text()
            data_generator = self.ui.comboBox_dependency_data_rule_data_generator.currentText()
            data_length = self.ui.textbox_dependency_data_rule_data_length.text()
            required_value = self.ui.comboBox_dependency_data_rule_required.currentText()
            nullalbe_value = self.ui.comboBox_dependency_data_rule_nullable.currentText()
            regex_pattern = self.ui.textbox_dependency_data_rule_regex_pattern.text()
            
            with open(f"./artifacts/DependencyRule/{operation_id}.json", "r+") as f:
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
                self.ui.table_dependency_generation_rule,
                self.ui.textbox_dependency_data_rule_type,
                self.ui.textbox_dependency_data_rule_format,
                self.ui.textbox_dependency_data_rule_value,
                self.ui.comboBox_dependency_data_rule_data_generator,
                self.ui.textbox_dependency_data_rule_data_length,
                self.ui.comboBox_dependency_data_rule_required,
                self.ui.comboBox_dependency_data_rule_nullable,
                self.ui.textbox_dependency_data_rule_regex_pattern,
            ])
            GeneralTool.parse_dependency_generation_rule(
                operation_id,
                self.ui.table_dependency_generation_rule,
                dependency_type,
                dependency_index
            )
        
    def btn_update_data_rule_clicked(self):
        """ Update the new data rule to the generation rule. """
        if len(self.ui.table_generation_rule.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_generation_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        field_name = selected_item.text(0)
        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)

        if parent_item is not None and parent_item.parent() is None:
            default_value = self.ui.textbox_data_rule_value.text()
            data_generator = self.ui.comboBox_data_rule_data_generator.currentText()
            data_length = self.ui.textbox_data_rule_data_length.text()
            required_value = self.ui.comboBox_data_rule_required.currentText()
            nullalbe_value = self.ui.comboBox_data_rule_nullable.currentText()
            regex_pattern = self.ui.textbox_data_rule_regex_pattern.text()
        
            with open(f"./artifacts/GenerationRule/{operation_id}.json", "r+") as f:
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
                self.ui.table_generation_rule,
                self.ui.textbox_data_rule_type,
                self.ui.textbox_data_rule_format,
                self.ui.textbox_data_rule_value,
                self.ui.comboBox_data_rule_data_generator,
                self.ui.textbox_data_rule_data_length,
                self.ui.comboBox_data_rule_required,
                self.ui.comboBox_data_rule_nullable,
                self.ui.textbox_data_rule_regex_pattern,
            ])
            GeneralTool.parse_generation_rule(operation_id, self.ui.table_generation_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_generation_rule)
        
    def btn_tc_clear_dependency_rule_clicked(self):
        """ Clear selected dependency rule and table. """
        GeneralTool.clean_ui_content([
            self.ui.line_tc_api_search,
            self.ui.textbox_tc_dependency_return_variable_name,
            self.ui.table_tc_dependency_generation_rule,
            self.ui.textbox_tc_dependency_requestbody,
            self.ui.table_tc_dependency_path,
        ])
        self.ui.comboBox_tc_dependency_type.setEnabled(True)
        self.ui.line_tc_api_search.setEnabled(True)
        self.ui.list_tc_dependency_available_api_list.clearSelection()
        self.ui.table_tc_dependency_rule.clearSelection()
          
    def btn_clear_dependency_rule_clicked(self):
        """ Clear selected dependency rule and table. """
        GeneralTool.clean_ui_content([
            self.ui.line_api_search,
            self.ui.textbox_dependency_return_variable_name,
            self.ui.table_dependency_generation_rule,
            self.ui.table_dependency_path,
        ])
        self.ui.comboBox_dependency_type.setEnabled(True)
        self.ui.list_dependency_available_api_list.clearSelection()
        self.ui.table_dependency_rule.clearSelection()
            
    def btn_up_dependency_rule_clicked(self):
        if len(self.ui.table_dependency_rule.selectedItems()) == 0 or self.ui.table_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.ui.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return

        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.ui.table_dependency_rule.selectedItems()[0].text(0)

        GeneralTool.update_dependency_rule_index(self.ui, operation_id, dependency_type, dependency_index, "up")
        
    def btn_tc_up_dependency_rule_clicked(self):
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.ui.table_tc_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        GeneralTool.update_tc_dependency_rule_index(
            self.ui, operation_id, test_case_id, test_point_id, dependency_type, dependency_sequence_num, "up")
    
    def btn_tc_down_dependency_rule_clicked(self):
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return
        elif self.ui.table_tc_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        GeneralTool.update_tc_dependency_rule_index(
            self.ui, operation_id, test_case_id, test_point_id, dependency_type, dependency_sequence_num, "down")
         
    def btn_down_dependency_rule_clicked(self):
        if len(self.ui.table_dependency_rule.selectedItems()) == 0 or self.ui.table_dependency_rule.selectedItems()[0].parent() is None:
                return
        elif self.ui.table_dependency_rule.selectedItems()[0].parent().parent() is not None:
            return

        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        operation_id = api_selected_item.text(4)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_index = self.ui.table_dependency_rule.selectedItems()[0].text(0)

        GeneralTool.update_dependency_rule_index(self.ui, operation_id, dependency_type, dependency_index, "down")
        
    def btn_generate_test_case_clicked(self):
        
        GeneralTool.teardown_folder_files(["./artifacts/TestCase/RESTful_API"])  
        Render.generate_robot_test_case()
        self.ui.tabTCG.setCurrentIndex(2)
        GeneralTool.clean_ui_content([self.ui.table_robot_file_list, self.ui.text_robot_file])
        GeneralTool.rander_robot_file_list(self.ui.table_robot_file_list)
        
    def btn_tc_remove_dependency_query_clicked(self):
        if len(self.ui.table_tc_dependency_query.selectedItems()) == 0 or self.ui.table_tc_dependency_query.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.ui.textbox_tc_query_dependency_name.text()
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        with open(file_path, "r+") as f:
            test_plan = json.load(f)
            result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["query"].pop(name)
            f.seek(0)
            json.dump(test_plan, f, indent=4)
            f.truncate()
            logging.info(f"Dependency Query Rule {result} is removed from {operation_id}.json")
            
        GeneralTool.clean_ui_content([self.ui.table_tc_dependency_query, self.ui.textbox_tc_query_dependency_name, self.ui.textbox_tc_query_dependency_value])
        root_item = QTreeWidgetItem(["query"])
        self.ui.table_tc_dependency_query.addTopLevelItem(root_item)
        query_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["query"]
        GeneralTool.parse_request_body(query_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_query, level=3)
        
    def btn_tc_update_dependency_query_clicked(self):
        if len(self.ui.table_tc_dependency_query.selectedItems()) == 0 or self.ui.table_tc_dependency_query.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.ui.textbox_tc_query_dependency_name.text()
        value = self.ui.textbox_tc_query_dependency_value.text()
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        with open(file_path, "r+") as f:
            test_plan = json.load(f)
            new_query_data = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["query"]
            new_query_data[name]["Value"] = value
            result = GeneralTool.update_value_in_json(
                test_plan, 
                ["test_cases", test_case_id ,"test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "query"],
                new_query_data
            )
            if result is not False:
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Update dependency query rule in {file_path} successfully")
            else:
                logging.error(f"Update dependency query rule in {file_path} failed")
        
        GeneralTool.clean_ui_content([self.ui.table_tc_dependency_query, self.ui.textbox_tc_query_dependency_name, self.ui.textbox_tc_query_dependency_value])
        root_item = QTreeWidgetItem(["query"])
        self.ui.table_tc_dependency_query.addTopLevelItem(root_item)
        query_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["query"]
        GeneralTool.parse_request_body(query_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_query, level=3)
        
    def btn_tc_remove_dependency_path_clicked(self):
        if len(self.ui.table_tc_dependency_path.selectedItems()) == 0 or self.ui.table_tc_dependency_path.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.ui.textbox_tc_path_dependency_name.text()
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        with open(file_path, "r+") as f:
            test_plan = json.load(f)
            result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"].pop(name)
            f.seek(0)
            json.dump(test_plan, f, indent=4)
            f.truncate()
            logging.info(f"Dependency Path Rule {result} is removed from {operation_id}.json")
            
        GeneralTool.clean_ui_content([self.ui.table_tc_dependency_path, self.ui.textbox_tc_path_dependency_name, self.ui.textbox_tc_path_dependency_value])
        root_item = QTreeWidgetItem(["path"])
        self.ui.table_tc_dependency_path.addTopLevelItem(root_item)
        path_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_path, level=3)
        
    def btn_tc_update_dependency_path_clicked(self):
        if len(self.ui.table_tc_dependency_path.selectedItems()) == 0 or self.ui.table_tc_dependency_path.selectedItems()[0].parent() is None:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_selected_item_parent = test_plan_selected_item.parent()
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        operation_id = test_plan_selected_item_parent.parent().text(0)
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        name = self.ui.textbox_tc_path_dependency_name.text()
        value = self.ui.textbox_tc_path_dependency_value.text()
        
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
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
        GeneralTool.clean_ui_content([self.ui.table_tc_dependency_path, self.ui.textbox_tc_path_dependency_name, self.ui.textbox_tc_path_dependency_value])
        root_item = QTreeWidgetItem(["path"])
        self.ui.table_tc_dependency_path.addTopLevelItem(root_item)
        path_rules = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rules, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_path, level=3)
        
    def table_tc_dependency_path_item_clicked(self):
        selected_item = self.ui.table_tc_dependency_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            name = selected_item.text(0)
            value = selected_item.child(4).text(1) if selected_item.child(4) is not None else ""
            self.ui.textbox_tc_path_dependency_name.setText(name)
            self.ui.textbox_tc_path_dependency_value.setText(value)
            
    def table_tc_dependency_query_item_clicked(self):
        selected_item = self.ui.table_tc_dependency_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            name = selected_item.text(0)
            value = selected_item.child(4).text(1) if selected_item.child(4) is not None else ""
            self.ui.textbox_tc_query_dependency_name.setText(name)
            self.ui.textbox_tc_query_dependency_value.setText(value)
        
    def btn_tc_dependency_update_text_body_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0 or len(self.ui.table_tc_dependency_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        selected_item = self.ui.table_tc_dependency_rule.selectedItems()[0]
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        new_value = self.ui.textbox_tc_dependency_requestbody.toPlainText()
        file_path = f"./artifacts/TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        
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
            self.ui.textbox_tc_dependency_requestbody.setPlainText(json.dumps(copy_testdata, indent=4))
            return
        logging.info(f"Update {file_path} successfully")
        return

    def btn_tc_remove_dependency_rule_clicked(self):
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type].pop(dependency_sequence_num)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Dependency Rule {result} is removed from {operation_id}.json")

            self.ui.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.ui.comboBox_tc_dependency_type.setEnabled(True)
            self.ui.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.ui.table_tc_dependency_rule,
                self.ui.comboBox_tc_dependency_type,
                self.ui.line_tc_api_search,
                self.ui.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.ui.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_rule, level=3)
            
        # * Remove the dependency test data file
        file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        if os.path.exists(f"./artifacts/TestData/Dependency_TestData/{file_name}"):
            os.remove(f"./artifacts/TestData/Dependency_TestData/{file_name}")
    
    def btn_tc_update_dependency_rule_clicked(self):
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0 or self.ui.table_tc_dependency_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
            dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)

            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                result = GeneralTool.update_value_in_json(
                    test_plan, 
                    ["test_cases", test_case_id ,"test_point", test_point_id, "dependency", dependency_type, dependency_sequence_num, "response_name"],
                    self.ui.textbox_tc_dependency_return_variable_name.text()
                )
                if result is not False:
                    f.seek(0)
                    json.dump(test_plan, f, indent=4)
                    f.truncate()
                    logging.info(f"Update dependency rule in {file_path} successfully")
                else:
                    logging.error(f"Update dependency rule in {file_path} failed")

            self.ui.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.ui.comboBox_tc_dependency_type.setEnabled(True)
            self.ui.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.ui.table_tc_dependency_rule,
                self.ui.comboBox_tc_dependency_type,
                self.ui.line_tc_api_search,
                self.ui.textbox_tc_dependency_return_variable_name
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.ui.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_rule, level=3)
        
    def btn_tc_add_dependency_rule_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return 
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            dependency_type = self.ui.comboBox_tc_dependency_type.currentText()
            api = self.ui.line_tc_api_search.text()
            return_name = self.ui.textbox_tc_dependency_return_variable_name.text()
            if api == "" or return_name == "":
                logging.error("API or Return Name is empty.")
                return
            
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                
                # * Generate the sequence number for the next rule
                # * If 'dependency_rules' is empty, the 'max' function will return the value of the 'default' parameter, i.e., 0. We then add 1 to get "1".
                # * If 'dependency_rules' is not empty, it will give us the maximum key value plus one.
                dependency_rules = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['dependency'][dependency_type]
                sequence_num = str(max((int(k) for k in dependency_rules.keys()), default=0) + 1)
                generation_rule, path_rule, query_rule = GeneralTool.generate_dependency_data_generation_and_path_and_query_rule(api)
                test_data = DataBuilder.data_builder(generation_rule)
                obj_name, uri_name = GeneralTool._retrieve_obj_and_action(api)
                file_name = f"{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{sequence_num}.json"
                path = f"./artifacts/TestData/Dependency_TestData/{file_name}"
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
                    "query": query_rule if query_rule is not None else {},
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
                    
            self.ui.comboBox_tc_dependency_type.setCurrentText("Setup")
            self.ui.comboBox_tc_dependency_type.setEnabled(True)
            self.ui.line_tc_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.ui.textbox_tc_dependency_return_variable_name,
                self.ui.line_tc_api_search,
                self.ui.textbox_tc_dependency_return_variable_name,
                self.ui.table_tc_dependency_rule
            ])
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.ui.table_tc_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_rule, level=3)
        
    def btn_tc_add_assertion_rule_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0 or self.ui.table_test_plan_api_list.selectedItems()[0].parent() is None:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()   
         
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, 'r+') as f:
                test_plan = json.load(f)
                # * Generate the sequence number for the next rule
                # * If 'assertion_rules' is empty, the 'max' function will return the value of the 'default' parameter, i.e., 0. We then add 1 to get "1".
                # * If 'assertion_rules' is not empty, it will give us the maximum key value plus one.
                assertion_rules = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['assertion']
                sequence_num = str(max((int(k) for k in assertion_rules.keys()), default=0) + 1)
                new_value = {
                    "source": self.ui.comboBox_tc_assertion_source.currentText(),
                    "field_expression": self.ui.textbox_tc_assertion_rule_field_expression.text(),
                    "filter_expression": self.ui.textbox_tc_assertion_rule_expression.text(),
                    "assertion_method": self.ui.comboBox_tc_assertion_method.currentText(),
                    "expected_value": self.ui.textbox_tc_assertion_rule_expected_value.text(),
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
                self.ui.table_tc_assertion_rule,
                self.ui.comboBox_tc_assertion_source,
                self.ui.comboBox_tc_assertion_method,
                self.ui.textbox_tc_assertion_rule_field_expression,
                self.ui.textbox_tc_assertion_rule_expression,
                self.ui.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.ui.table_tc_assertion_rule.addTopLevelItem(assertion_item)
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
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_assertion_rule, level=3)
        
    def btn_tc_remove_assertion_rule_clicked(self):
        if len(self.ui.table_tc_assertion_rule.selectedItems()) == 0 or self.ui.table_tc_assertion_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            index = self.ui.table_tc_assertion_rule.selectedItems()[0].text(0)
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, "r+") as f:
                test_plan = json.load(f)
                result = test_plan["test_cases"][test_case_id]["test_point"][test_point_id]["assertion"].pop(index)
                f.seek(0)
                json.dump(test_plan, f, indent=4)
                f.truncate()
                logging.info(f"Assertion Rule {result} is removed from {operation_id}.json")

            GeneralTool.clean_ui_content([
                self.ui.table_tc_assertion_rule,
                self.ui.comboBox_tc_assertion_source,
                self.ui.comboBox_tc_assertion_method,
                self.ui.textbox_tc_assertion_rule_field_expression,
                self.ui.textbox_tc_assertion_rule_expression,
                self.ui.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.ui.table_tc_assertion_rule.addTopLevelItem(assertion_item)
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
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_assertion_rule)
       
    def btn_tc_update_assertion_rule_clicked(self):
        if len(self.ui.table_tc_assertion_rule.selectedItems()) == 0 or self.ui.table_tc_assertion_rule.selectedItems()[0].parent() is None:
            return

        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            
            index = self.ui.table_tc_assertion_rule.selectedItems()[0].text(0)
            new_value = {
                "source": self.ui.comboBox_tc_assertion_source.currentText(),
                "field_expression": self.ui.textbox_tc_assertion_rule_field_expression.text(),
                "filter_expression": self.ui.textbox_tc_assertion_rule_expression.text(),
                "assertion_method": self.ui.comboBox_tc_assertion_method.currentText(),
                "expected_value": self.ui.textbox_tc_assertion_rule_expected_value.text(),
            }
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
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
                self.ui.table_tc_assertion_rule,
                self.ui.comboBox_tc_assertion_source,
                self.ui.comboBox_tc_assertion_method,
                self.ui.textbox_tc_assertion_rule_field_expression,
                self.ui.textbox_tc_assertion_rule_expression,
                self.ui.textbox_tc_assertion_rule_expected_value
            ])
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.ui.table_tc_assertion_rule.addTopLevelItem(assertion_item)
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
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_assertion_rule)        
        
    def table_tc_assertion_rule_item_clicked(self, item):
        GeneralTool.clean_ui_content([
            self.ui.comboBox_tc_assertion_source,
            self.ui.textbox_tc_assertion_rule_field_expression,
            self.ui.textbox_tc_assertion_rule_expression,
            self.ui.comboBox_tc_assertion_method,
            self.ui.textbox_tc_assertion_rule_expected_value
        ])
        selected_item = self.ui.table_tc_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.ui.comboBox_tc_assertion_source.setCurrentText(parent_item.text(1))
            self.ui.textbox_tc_assertion_rule_field_expression.setText(selected_item.text(2))
            self.ui.textbox_tc_assertion_rule_expression.setText(selected_item.text(3))
            self.ui.comboBox_tc_assertion_method.setCurrentText(selected_item.text(4))
            self.ui.textbox_tc_assertion_rule_expected_value.setText(selected_item.text(5))

    def btn_tc_remove_query_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
    
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id = test_id.split(".")[0]
            use_case_id = test_id.split(".")[1]
            name = self.ui.textbox_tc_query_name.text()
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.remove_key_in_json(
                    data, 
                    ["test_cases", test_case_id ,"test_point", use_case_id, "query", name]
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', use_case_id, 'query', name]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to remove key `{['test_cases', test_case_id, 'test_point', use_case_id, 'query', name]}`.")
            GeneralTool.clean_ui_content([self.ui.textbox_tc_query_name, self.ui.textbox_tc_query_value, self.ui.table_tc_query])
            root_item = QTreeWidgetItem(["Query Parameter"])
            self.ui.table_tc_query.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["query"], root_item)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_query, level=2)            
    
    def btn_tc_update_query_clicked(self):
        
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id, use_case_id = test_id.split(".")[0], test_id.split(".")[1]
            name = self.ui.textbox_tc_query_name.text()
            new_value = self.ui.textbox_tc_query_value.text()
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
            with open(file_path, "r+") as f:
                data = json.load(f)
                result = GeneralTool.update_value_in_json(
                    data, 
                    ["test_cases", test_case_id ,"test_point", use_case_id, "query", name],
                    new_value
                )
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `{file_path}` to update key `{['test_cases', test_case_id, 'test_point', use_case_id, 'query', name, new_value]}`.")
                else:
                    logging.error(f"Error updating JSON file `{file_path}` to update key `{['test_cases', test_case_id, 'test_point', use_case_id, 'query', name, new_value]}`.") 
            
            GeneralTool.clean_ui_content([self.ui.textbox_tc_query_name, self.ui.textbox_tc_query_value, self.ui.table_tc_query])
            root_item = QTreeWidgetItem(["Query Parameter"])
            self.ui.table_tc_query.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["query"], root_item)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_query, level=2)
        
    def btn_tc_remove_path_clicked(self):
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
    
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id = test_id.split(".")[0]
            use_case_id = test_id.split(".")[1]
            name = self.ui.textbox_tc_path_name.text()
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
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
            GeneralTool.clean_ui_content([self.ui.textbox_tc_path_name, self.ui.textbox_tc_path_value, self.ui.table_tc_path])
            root_item = QTreeWidgetItem(["Path Parameter"])
            self.ui.table_tc_path.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["path"], root_item)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_path, level=2)            
    
    def btn_tc_update_path_clicked(self):
        
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = parent_item.parent().text(0)
            test_id = selected_item.text(1)
            test_case_id, use_case_id = test_id.split(".")[0], test_id.split(".")[1]
            name = self.ui.textbox_tc_path_name.text()
            new_value = self.ui.textbox_tc_path_value.text()
            file_path = f"./artifacts/TestPlan/{operation_id}.json"
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
            
            GeneralTool.clean_ui_content([self.ui.textbox_tc_path_name, self.ui.textbox_tc_path_value, self.ui.table_tc_path])
            root_item = QTreeWidgetItem(["Path Parameter"])
            self.ui.table_tc_path.addTopLevelItem(root_item)
            GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][use_case_id]["path"], root_item)
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_path, level=2)
        
        
    def table_tc_path_item_clicked(self):

        selected_item = self.ui.table_tc_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.ui.textbox_tc_path_name.setText(selected_item.text(0))
            self.ui.textbox_tc_path_value.setText(selected_item.text(1))
            
    def table_tc_query_item_clicked(self):
        
        selected_item = self.ui.table_tc_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None:
            self.ui.textbox_tc_query_name.setText(selected_item.text(0))
            self.ui.textbox_tc_query_value.setText(selected_item.text(1))

    def btn_tc_dependency_generation_rule_remove_clicked(self):
        """ Remove Dependency Generation Rule Field """
        if len(self.ui.table_tc_dependency_generation_rule.selectedItems()) == 0:
            return
        
        # * Retrieve the origin API Operation ID.
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        origin_api_operation_id = test_plan_parent_item.parent().text(0)
        
        # * Retrieve the Dependency Rule Index and Data Generation Rule Field name which should be removed.
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        generation_table_selected_item = self.ui.table_tc_dependency_generation_rule.selectedItems()[0]
        test_case_id = test_plan_selected_item.text(1).split('.')[0]
        test_point_id = test_plan_selected_item.text(1).split('.')[1]
        if generation_table_selected_item.parent() is None or generation_table_selected_item.parent().parent() is not None:
            return
        else:
            generation_rule_field_name = generation_table_selected_item.text(0)
            
        # * Retrieve the Generation Rule List selected items to get the corresponding path
        paths = []
        for item in self.ui.table_tc_dependency_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
        
        # * Update the value in the JSON file
        file_path = f"./artifacts/TestPlan/{origin_api_operation_id}.json"
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
        GeneralTool.remove_table_item_from_ui(self.ui.table_tc_dependency_generation_rule)     
       
    def btn_dependency_generation_rule_remove_clicked(self):
        """ Remove Generation Rule Item """
        
        # * If no API or Generation Rule is selected, return directly.
        if len(self.ui.table_dependency_generation_rule.selectedItems()) == 0:
            return
        
        # * Retrieve the origin API Operation ID.
        api_selected_item = self.ui.table_api_tree.selectedItems()[0]
        origin_api_operation_id = api_selected_item.text(4)
        
        # * Retrieve the Dependency Rule Index and Data Generation Rule Field name which should be removed.
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        generation_table_selected_item = self.ui.table_dependency_generation_rule.selectedItems()[0]
        if generation_table_selected_item.parent() is None or generation_table_selected_item.parent().parent() is not None:
            return
        else:
            generation_rule_field_name = generation_table_selected_item.text(0)
            
        # * Retrieve the Generation Rule List selected items to get the corresponding path
        paths = []
        for item in self.ui.table_dependency_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
                
        # * Update the value in the JSON file
        file_path = f"./artifacts/DependencyRule/{origin_api_operation_id}.json"
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
        GeneralTool.remove_table_item_from_ui(self.ui.table_dependency_generation_rule)
        
    def btn_dependency_constraint_rule_apply_clicked(self):
        src_action = self.ui.comboBox_dependency_constraint_rule_src_action.currentText()
        src_path = self.ui.textbox_dependency_constraint_rule_src.text()
        src_condition = self.ui.comboBox_dependency_constraint_rule_condition.currentText()
        src_expected_value = self.ui.textbox_dependency_constraint_rule_expected_value.text()
        dst_action = self.ui.comboBox_dependency_constraint_rule_dst_action.currentText()
        dst_path = self.ui.textbox_dependency_constraint_rule_dst.text()
        dst_action_type = self.ui.comboBox_dependency_constraint_dst_action_type.currentText()
        dst_value = self.ui.textbox_dependency_constraint_rule_dst_value.text()
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        
        if len(self.ui.table_dependency_rule.selectedItems()) == 0:
            return
        else:
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./artifacts/DependencyRule/{operation_id}.json"
            
        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path,
            dst_action_type, dst_value, dependency_type, dependency_sequence_num, is_general_dependency=True
        )
        
        with open(file_path, "r+") as f:
            data = json.load(f)
        # * Refresh the Dependency Generation Rule Table
        root_item = QTreeWidgetItem(["Data Generation Rule"])
        self.ui.table_dependency_generation_rule.clear()
        self.ui.table_dependency_generation_rule.addTopLevelItem(root_item)
        GeneralTool.parse_request_body(data[dependency_type][dependency_sequence_num]["data_generation_rules"], root_item, editabled=True)
        GeneralTool.expand_and_resize_tree(self.ui.table_dependency_generation_rule, 0)
        # * Clear the constraint rule UI
        GeneralTool.clean_ui_content([
            self.ui.textbox_dependency_constraint_rule_src,
            self.ui.textbox_dependency_constraint_rule_expected_value,
            self.ui.textbox_dependency_constraint_rule_dst,
            self.ui.textbox_dependency_constraint_rule_dst_value,
        ])
        self.ui.checkBox_dependency_constraint_rule_wildcard.setChecked(False)
        self.ui.comboBox_dependency_constraint_rule_dst_action.setCurrentText("Then Remove")
        self.ui.comboBox_dependency_constraint_dst_action_type.setCurrentText("")
        self.ui.comboBox_dependency_constraint_dst_action_type.setEnabled(False)
        self.ui.textbox_dependency_constraint_rule_dst_value.setEnabled(False)
        
    def btn_dependency_constraint_rule_clear_clicked(self):
        """ Clear the Dependency Constraint Rule UI. """
        GeneralTool.clean_ui_content([
            self.ui.textbox_dependency_constraint_rule_src, 
            self.ui.textbox_dependency_constraint_rule_expected_value, 
            self.ui.textbox_dependency_constraint_rule_dst, 
            self.ui.textbox_dependency_constraint_rule_dst_value,
        ])
        self.ui.checkBox_dependency_constraint_rule_wildcard.setChecked(False)
        
    def btn_tc_dependency_constraint_rule_clear_clicked(self):
        """ Clear the Dependency Constraint Rule UI. """
        GeneralTool.clean_ui_content([
            self.ui.textbox_tc_dependency_constraint_rule_src,
            self.ui.textbox_tc_dependency_constraint_rule_expected_value,
            self.ui.textbox_tc_dependency_constraint_rule_dst,
            self.ui.textbox_tc_dependency_constraint_rule_dst_value,
        ])
    
    def btn_tc_dependency_constraint_rule_apply_clicked(self):
        """ Apply the Dependency Constraint Rule to the selected API. """
        src_action = self.ui.comboBox_tc_dependency_constraint_rule_src_action.currentText()
        src_path = self.ui.textbox_tc_dependency_constraint_rule_src.text()
        src_condition = self.ui.comboBox_tc_dependency_constraint_rule_condition.currentText()
        src_expected_value = self.ui.textbox_tc_dependency_constraint_rule_expected_value.text()
        dst_action = self.ui.comboBox_tc_dependency_constraint_rule_dst_action.currentText()
        dst_path = self.ui.textbox_tc_dependency_constraint_rule_dst.text()
        dst_action_type = self.ui.comboBox_tc_dependency_constraint_dst_action_type.currentText()
        dst_value = self.ui.textbox_tc_dependency_constraint_rule_dst_value.text()
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        if len(self.ui.table_test_plan_api_list.selectedItems()) == 0:
            return
        else:
            test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_case_id = test_plan_selected_item.text(1).split(".")[0]
            test_point_id = test_plan_selected_item.text(1).split(".")[1]
    
        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path,
            dst_action_type, dst_value, dependency_type, dependency_sequence_num, True, test_case_id, test_point_id)
        
        with open(f"./artifacts/TestPlan/{operation_id}.json", "r+") as f:
            data = json.load(f)
        # * Refresh the Dependency Generation Rule Table
        root_item = QTreeWidgetItem(["Data Generation Rule"])
        self.ui.table_tc_dependency_generation_rule.clear()
        self.ui.table_tc_dependency_generation_rule.addTopLevelItem(root_item)
        GeneralTool.parse_request_body(data["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["data_generation_rules"], root_item, editabled=True)
        GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_generation_rule, 0)
        # * Clear the constraint rule UI
        GeneralTool.clean_ui_content([
            self.ui.textbox_tc_dependency_constraint_rule_src,
            self.ui.textbox_tc_dependency_constraint_rule_expected_value,
            self.ui.textbox_tc_dependency_constraint_rule_dst,
            self.ui.textbox_tc_dependency_constraint_rule_dst_value,
        ])
        self.ui.checkBox_tc_dependency_constraint_rule_wildcard.setChecked(False)
        self.ui.comboBox_tc_dependency_constraint_rule_dst_action.setCurrentText("Then Remove")
        self.ui.comboBox_tc_dependency_constraint_dst_action_type.setCurrentText("")
        self.ui.comboBox_tc_dependency_constraint_dst_action_type.setEnabled(False)
        self.ui.textbox_tc_dependency_constraint_rule_dst_value.setEnabled(False)
    
    def btn_tc_dependency_generation_rule_build_clicked(self):
        
        if len(self.ui.table_tc_dependency_rule.selectedItems()) == 0:
            return
        
        test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        test_plan_parent_item = test_plan_selected_item.parent()
        operation_id = test_plan_parent_item.parent().text(0)
        test_case_id = test_plan_selected_item.text(1).split(".")[0]
        test_point_id = test_plan_selected_item.text(1).split(".")[1]
        selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
        parent_item = selected_item.parent()
        dependency_type = self.ui.table_tc_dependency_rule.selectedItems()[0].parent().text(0)
        dependency_sequence_num = self.ui.table_tc_dependency_rule.selectedItems()[0].text(0)
        
        # * Retrieve the dependency data generation rule.
        file_path = f"./artifacts/TestPlan/{operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            generation_rule = data["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][dependency_sequence_num]["data_generation_rules"]
            testdata = DataBuilder.data_builder(generation_rule)
            
        # * Render the dependency request body. 
        testdata_path = f"./artifacts/TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{dependency_sequence_num}.json"
        with open(testdata_path, "w+") as f:
            json.dump(testdata, f, indent=4)
        with open(testdata_path, "r+") as f:
            testdata = json.load(f)
        testdata_str = json.dumps(testdata, indent=4)
        self.ui.textbox_tc_dependency_requestbody.setPlainText(testdata_str)
        self.ui.table_tc_dependency_schema_2.setCurrentIndex(1)
        
    def table_dependency_path_item_clicked(self):
        
        if len(self.ui.table_dependency_path.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_dependency_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
        
            name = selected_item.text(0)
            value = selected_item.child(4).text(1)
            self.ui.textbox_path_dependency_name.setText(name)
            self.ui.textbox_path_dependency_value.setText(value)
            
    def table_dependency_query_item_clicked(self):
        
        if len(self.ui.table_dependency_query.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_dependency_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            
            name = selected_item.text(0)
            value = selected_item.child(4).text(1)
            self.ui.textbox_query_dependency_name.setText(name)
            self.ui.textbox_query_dependency_value.setText(value)
            
    def btn_remove_dependency_query_clicked(self):
        
        if len(self.ui.table_dependency_query.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.ui.table_dependency_query.selectedItems()[0]
        
        name = self.ui.textbox_query_dependency_name.text()
        value = self.ui.textbox_query_dependency_value.text()
        
        file_path = f"./artifacts/DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            path = [dependency_type, dependency_sequence_num, "query", name]
            result = GeneralTool.remove_key_in_json(data, path)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{path}`.")
                
        GeneralTool.clean_ui_content([self.ui.textbox_query_dependency_name, self.ui.textbox_query_dependency_value, self.ui.table_dependency_query])
        root_item = QTreeWidgetItem(["Query Parameter"])
        self.ui.table_dependency_query.addTopLevelItem(root_item)
        query_rule = data[dependency_type][dependency_sequence_num]["query"]
        GeneralTool.parse_request_body(query_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_query, level=3)
    
    def btn_update_dependency_query_clicked(self):
        
        if len(self.ui.table_dependency_query.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.ui.table_dependency_query.selectedItems()[0]
        
        name = self.ui.textbox_query_dependency_name.text()
        value = self.ui.textbox_query_dependency_value.text()
        
        file_path = f"./artifacts/DependencyRule/{origin_api_operation_id}.json"
        with open(file_path, "r+") as f:
            data = json.load(f)
            path = [dependency_type, dependency_sequence_num, "query", name, "Value"]
            result = GeneralTool.update_value_in_json(data, path, value)
            if result is not False:
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                logging.info(f"Successfully updating JSON file `{file_path}` to remove key `{path}`.")
            else:
                logging.error(f"Error updating JSON file `{file_path}` to remove key `{path}`.")
                
        GeneralTool.clean_ui_content([self.ui.textbox_query_dependency_name, self.ui.textbox_query_dependency_value, self.ui.table_dependency_query])
        root_item = QTreeWidgetItem(["Query Parameter"])
        self.ui.table_dependency_query.addTopLevelItem(root_item)
        query_rule = data[dependency_type][dependency_sequence_num]["query"]
        GeneralTool.parse_request_body(query_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_query, level=3)
        
    def btn_remove_dependency_path_clicked(self):
        
        if len(self.ui.table_dependency_path.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.ui.table_dependency_path.selectedItems()[0]
        
        name = self.ui.textbox_path_dependency_name.text()
        value = self.ui.textbox_path_dependency_value.text()
        
        file_path = f"./artifacts/DependencyRule/{origin_api_operation_id}.json"
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
                
        GeneralTool.clean_ui_content([self.ui.textbox_path_dependency_name, self.ui.textbox_path_dependency_value, self.ui.table_dependency_path])
        root_item = QTreeWidgetItem(["Path Parameter"])
        self.ui.table_dependency_path.addTopLevelItem(root_item)
        path_rule = data[dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_path, level=2)
    
    def btn_update_dependency_path_clicked(self):
        
        if len(self.ui.table_dependency_path.selectedItems()) == 0:
            return
        
        origin_api_operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        dependency_sequence_num = self.ui.table_dependency_rule.selectedItems()[0].text(0)
        dependency_type = self.ui.table_dependency_rule.selectedItems()[0].parent().text(0)
        selected_item = self.ui.table_dependency_path.selectedItems()[0]
        
        name = self.ui.textbox_path_dependency_name.text()
        value = self.ui.textbox_path_dependency_value.text()
        
        file_path = f"./artifacts/DependencyRule/{origin_api_operation_id}.json"
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
                
        GeneralTool.clean_ui_content([self.ui.textbox_path_dependency_name, self.ui.textbox_path_dependency_value, self.ui.table_dependency_path])
        root_item = QTreeWidgetItem(["Path Parameter"])
        self.ui.table_dependency_path.addTopLevelItem(root_item)
        path_rule = data[dependency_type][dependency_sequence_num]["path"]
        GeneralTool.parse_request_body(path_rule, root_item)
        GeneralTool.expand_and_resize_tree(self.ui.table_path, level=2)
        
    def table_tc_dependency_item_clicked(self):
        
        # * Render the Dependency Action's Data Generation Rule and Path Rule and Schema.
        GeneralTool.clean_ui_content([
            self.ui.table_tc_dependency_generation_rule,
            self.ui.textbox_tc_dependency_requestbody,
            self.ui.table_tc_dependency_path,
            self.ui.table_tc_dependency_query,
            self.ui.textbox_tc_path_dependency_name,
            self.ui.textbox_tc_path_dependency_value,
            self.ui.table_tc_dependency_additional_action,
        ])
        
        selected_item = self.ui.table_tc_dependency_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            # * Render the Dependency Rule Mangement UI for the update action.
            self.ui.comboBox_tc_dependency_type.setCurrentText(parent_item.text(0))
            self.ui.line_tc_api_search.setText(selected_item.child(0).text(1))
            self.ui.textbox_tc_dependency_return_variable_name.setText(selected_item.child(1).text(1))
            self.ui.comboBox_tc_dependency_type.setEnabled(False)
            self.ui.line_tc_api_search.setEnabled(False)
            
            test_plan_selected_item = self.ui.table_test_plan_api_list.selectedItems()[0]
            test_plan_parent_item = test_plan_selected_item.parent()
            operation_id = test_plan_parent_item.parent().text(0)
            test_id = test_plan_selected_item.text(1)
            test_case_id , test_point_id = test_id.split('.')[0], test_id.split('.')[1]
            dependency_type = parent_item.text(0)
            api = selected_item.child(0).text(1)
            index = selected_item.text(0)
            
            with open(f"./artifacts/TestPlan/{operation_id}.json", "r") as f:
                data = json.load(f)["test_cases"][test_case_id]["test_point"][test_point_id]["dependency"][dependency_type][index]
                
            # * Render the Data Generation Rule and Path Rule and Schema.
            if "data_generation_rules" in data and data["data_generation_rules"] != {}:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.ui.table_tc_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["data_generation_rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_generation_rule, level=2)
            else:
                root_item = QTreeWidgetItem(["This API does not have a request body."])
                self.ui.table_dependency_generation_rule.addTopLevelItem(root_item)
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{operation_id}`.")
                
            # * Render the Path Rule
            if "path" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.ui.table_tc_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["path"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_path, level=2)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{operation_id}`.")
                
            # * Render the Query Rule
            if "query" in data:
                root_item = QTreeWidgetItem(["Query Parameter"])
                self.ui.table_tc_dependency_query.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["query"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_query, level=2)
            else:
                logging.info(f"Query Rule is not exist in the dependency rule `{operation_id}`.")
            
            # * Render the additional action rule
            if 'additional_action' in data:
                root_item = QTreeWidgetItem(["Additional Action"])
                self.ui.table_tc_dependency_additional_action.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["additional_action"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_tc_dependency_additional_action, level=2)
            else:
                logging.info(f"Additional Action is not exist in the dependency rule `{operation_id}`.")
                
            testdata_path = f"./artifacts/TestData/Dependency_TestData/{operation_id}_{test_case_id}_{test_point_id}_{dependency_type}_{index}.json"
            try:
                with open(testdata_path, "r+") as f:
                    testdata = json.load(f)
                testdata_str = json.dumps(testdata, indent=4)
                self.ui.textbox_tc_dependency_requestbody.setPlainText(testdata_str)
            except FileNotFoundError:
                logging.info(f"Test Data `{testdata_path}` is not exist.")
                
        else:
            self.ui.comboBox_tc_dependency_type.setEnabled(True)
            self.ui.line_tc_api_search.setEnabled(True)
        
    def table_dependency_rule_item_clicked(self):
        
        # * Render the Dependency Action's Data Generation Rule and Path Rule and Schema.
        GeneralTool.clean_ui_content([
            self.ui.table_dependency_generation_rule,
            self.ui.table_dependency_path,
            self.ui.table_dependency_query,
            self.ui.textbox_path_dependency_name,
            self.ui.textbox_path_dependency_value,
            self.ui.table_dependency_additional_action,
        ])

        selected_item = self.ui.table_dependency_rule.selectedItems()[0]
        parent_item = selected_item.parent()

        if parent_item and parent_item.parent() is None:
            # * Render the Dependency Rule Mangement UI for the update action.
            self.ui.comboBox_dependency_type.setCurrentText(parent_item.text(0))
            self.ui.line_api_search.setText(selected_item.child(0).text(1))
            self.ui.textbox_dependency_return_variable_name.setText(selected_item.child(1).text(1))
            self.ui.comboBox_dependency_type.setEnabled(False)
            self.ui.line_api_search.setEnabled(False)
            
            api_tree_selected_item = self.ui.table_api_tree.selectedItems()[0]
            dependency_type = parent_item.text(0)
            sequence_num = selected_item.text(0)
            origin_api_operation_id = api_tree_selected_item.text(4)
            with open(f"./artifacts/DependencyRule/{origin_api_operation_id}.json", "r") as f:
                data = json.load(f)[dependency_type][sequence_num]
                
            # * Render the Data Generation Rule and Path Rule and Schema.
            if "data_generation_rules" in data and data["data_generation_rules"] != {}:
                root_item = QTreeWidgetItem(["Data Generation Rule"])
                self.ui.table_dependency_generation_rule.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["data_generation_rules"], root_item, editabled=True)
                GeneralTool.expand_and_resize_tree(self.ui.table_dependency_generation_rule, level=2)
            else:
                root_item = QTreeWidgetItem(["This API does not have a request body."])
                self.ui.table_dependency_generation_rule.addTopLevelItem(root_item)
                logging.info(f"Data Generation Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
            
            # * Render the Path Rule
            if "path" in data:
                root_item = QTreeWidgetItem(["Path Parameter"])
                self.ui.table_dependency_path.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["path"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_dependency_path, level=2)
            else:
                logging.info(f"Path Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
                
            # * Render the Query Rule
            if "query" in data:
                root_item = QTreeWidgetItem(["Query Parameter"])
                self.ui.table_dependency_query.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["query"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_dependency_query, level=2)
            else:
                logging.info(f"Query Rule is not exist in the dependency rule `{origin_api_operation_id}`.")
                
            # * Render the additional action rule
            if 'additional_action' in data:
                root_item = QTreeWidgetItem(["Additional Action"])
                self.ui.table_dependency_additional_action.addTopLevelItem(root_item)
                GeneralTool.parse_request_body(data["additional_action"], root_item)
                GeneralTool.expand_and_resize_tree(self.ui.table_dependency_additional_action, level=2)
                
        else:
            self.ui.comboBox_dependency_type.setEnabled(True)
            self.ui.line_api_search.setEnabled(True)
        
    def btn_add_dependency_rule_clicked(self):
        """Add Dependency Rule Item"""
        
        if len(self.ui.table_api_tree.selectedItems()) == 0:
            return
        
        operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
        dependency_type = self.ui.comboBox_dependency_type.currentText()
        api = self.ui.line_api_search.text()
        return_name = self.ui.textbox_dependency_return_variable_name.text()
        if api == "" or return_name == "":
            logging.error(f"API or Return Name is empty.")
            return
        
        file_path = f"./artifacts/DependencyRule/{operation_id}.json"
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
                
        self.ui.comboBox_dependency_type.setCurrentText("Setup")
        GeneralTool.clean_ui_content([self.ui.line_api_search, self.ui.textbox_dependency_return_variable_name])
        GeneralTool.parse_dependency_rule(operation_id, self.ui.table_dependency_rule)
        GeneralTool.expand_and_resize_tree(self.ui.table_dependency_rule, level=3)
        
        # * Generate the Data Generation Rule and Path Rule and Schema.
        self._create_dependency_generation_and_path_and_query_rule(api, operation_id, dependency_type, sequence_num)
        
    def btn_remove_dependency_rule_clicked(self):
        """Remove Dependency Rule Item"""
        
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_dependency_rule.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_dependency_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
            dependency_type = self.ui.comboBox_dependency_type.currentText()
            dependency_name = selected_item.text(0)
            file_path = f"./artifacts/DependencyRule/{operation_id}.json"
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
            
            self.ui.comboBox_dependency_type.setCurrentText("Setup")
            self.ui.comboBox_dependency_type.setEnabled(True)
            self.ui.line_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([self.ui.line_api_search, self.ui.textbox_dependency_return_variable_name])
            GeneralTool.parse_dependency_rule(operation_id, self.ui.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_dependency_rule, level=3)
    
    def btn_update_dependency_rule_clicked(self):
        """Update Dependency Rule Item"""
            
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_dependency_rule.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_dependency_rule.selectedItems()[0]
        selected_item_api_name = selected_item.child(0).text(1)
        parent_item = selected_item.parent()

        if parent_item and parent_item.parent() is None:
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
            dependency_type = self.ui.comboBox_dependency_type.currentText()
            api = self.ui.line_api_search.text()
            if api != selected_item_api_name:
                logging.error(f"API name cannot be changed.")
                return
            return_name = self.ui.textbox_dependency_return_variable_name.text()
            file_path = f"./artifacts/DependencyRule/{operation_id}.json"
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
            
            self.ui.comboBox_dependency_type.setCurrentText("Setup")
            self.ui.comboBox_dependency_type.setEnabled(True)
            self.ui.line_api_search.setEnabled(True)
            GeneralTool.clean_ui_content([
                self.ui.line_api_search,
                self.ui.textbox_dependency_return_variable_name,
                self.ui.table_dependency_path,
                self.ui.table_dependency_generation_rule,
                self.ui.textbox_path_dependency_name,
                self.ui.textbox_path_dependency_value,  
            ])
            GeneralTool.parse_dependency_rule(operation_id, self.ui.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_dependency_rule, level=3)

    def line_api_search_text_changed(self):
        """ When the text in the line_api_search is changed to trigger this event. """
        for api in range(self.ui.list_dependency_available_api_list.count()):
            if self.ui.line_api_search.text() in self.ui.list_dependency_available_api_list.item(api).text():
                self.ui.list_dependency_available_api_list.setCurrentItem(self.ui.list_dependency_available_api_list.item(api))
                break
            
    def line_tc_api_search_text_changed(self):
        for api in range(self.ui.list_tc_dependency_available_api_list.count()):
            if self.ui.line_tc_api_search.text() in self.ui.list_tc_dependency_available_api_list.item(api).text():
                self.ui.list_tc_dependency_available_api_list.setCurrentItem(self.ui.list_tc_dependency_available_api_list.item(api))
                break
        
    def list_dependency_available_api_list_item_clicked(self):
        """ When the item in the list_dependency_available_api_list is clicked. """
        api_name = self.ui.list_dependency_available_api_list.selectedItems()[0].text()
        self.ui.line_api_search.setText(api_name)
        
    def list_tc_dependency_available_api_list_item_clicked(self):
        """ When the item in the list_tc_dependency_available_api_list is clicked. """
        api_name = self.ui.list_tc_dependency_available_api_list.selectedItems()[0].text()
        self.ui.line_tc_api_search.setText(api_name)
    
    def table_path_item_clicked(self):
        selected_item = self.ui.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is None:
            self.ui.textbox_path_name.setText(selected_item.text(0))
            self.ui.textbox_path_value.setText(selected_item.child(4).text(1))
        else:
            return
        
    def table_query_item_clicked(self):
        selected_item = self.ui.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item is not None and parent_item.parent() is None:
            self.ui.textbox_query_name.setText(selected_item.text(0))
            self.ui.textbox_query_value.setText(selected_item.child(4).text(1))
        
    def btn_add_path_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_api_tree.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.ui.textbox_path_name.text(), self.ui.textbox_path_value.text(), self.ui.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./artifacts/PathRule/{operation_id}.json"
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
                    
            GeneralTool.clean_ui_content([self.ui.textbox_path_name, self.ui.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.ui.table_path)
            GeneralTool.expand_and_resize_tree(self.ui.table_path)
        
    def btn_update_path_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_path.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.ui.textbox_path_name.text(), self.ui.textbox_path_value.text(), self.ui.table_api_tree.selectedItems()[0].text(4)      
            file_path = f"./artifacts/PathRule/{operation_id}.json"
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
            
            GeneralTool.clean_ui_content([self.ui.textbox_path_name, self.ui.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.ui.table_path)
            GeneralTool.expand_and_resize_tree(self.ui.table_path)
            
    def btn_update_query_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_query.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name, value, operation_id = self.ui.textbox_query_name.text(), self.ui.textbox_query_value.text(), self.ui.table_api_tree.selectedItems()[0].text(4)      
            file_path = f"./artifacts/QueryRule/{operation_id}.json"
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
            
            GeneralTool.clean_ui_content([self.ui.textbox_query_name, self.ui.textbox_query_value])
            GeneralTool.parse_query_rule(operation_id, self.ui.table_query)
            GeneralTool.expand_and_resize_tree(self.ui.table_query)

    def btn_remove_query_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_query.selectedItems()) == 0:
            return
        
        selected_item = self.ui.table_query.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name = self.ui.textbox_query_name.text()
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4) 
            file_path = f"./artifacts/QueryRule/{operation_id}.json"
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
        
            GeneralTool.clean_ui_content([self.ui.textbox_query_name, self.ui.textbox_query_value])
            GeneralTool.parse_path_rule(operation_id, self.ui.table_query)
            GeneralTool.expand_and_resize_tree(self.ui.table_path)
                
    def btn_remove_path_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0 or len(self.ui.table_path.selectedItems()) == 0:
            return

        selected_item = self.ui.table_path.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is None:
            name = self.ui.textbox_path_name.text()
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4) 
            file_path = f"./artifacts/PathRule/{operation_id}.json"
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
        
            GeneralTool.clean_ui_content([self.ui.textbox_path_name, self.ui.textbox_path_value])
            GeneralTool.parse_path_rule(operation_id, self.ui.table_path)
            GeneralTool.expand_and_resize_tree(self.ui.table_path)
        
    def checkBox_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.ui.textbox_constraint_rule_dst, self.ui.checkBox_constraint_rule_wildcard, self.ui.textbox_constraint_rule_dst)
        
    def checkBox_dependency_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.ui.textbox_dependency_constraint_rule_dst, self.ui.checkBox_dependency_constraint_rule_wildcard, self.ui.textbox_dependency_constraint_rule_dst)

    def checkBox_tc_dependency_constraint_rule_wildcard_changed(self):
        GeneralTool.update_dependency_wildcard(
            self.ui.textbox_tc_dependency_constraint_rule_dst, self.ui.checkBox_tc_dependency_constraint_rule_wildcard, self.ui.textbox_tc_dependency_constraint_rule_dst)
        
    def comboBox_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.ui.comboBox_constraint_rule_src_action, self.ui.comboBox_constraint_rule_condition)
            
    def comboBox_dependency_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.ui.comboBox_dependency_constraint_rule_src_action, self.ui.comboBox_dependency_constraint_rule_condition)
            
    def comboBox_tc_dependency_constraint_rule_src_action_changed(self):
        GeneralTool.update_constraint_actions_src(
            self.ui.comboBox_tc_dependency_constraint_rule_src_action, self.ui.comboBox_tc_dependency_constraint_rule_condition)
            
    def comboBox_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.ui.comboBox_constraint_rule_dst_action,
            self.ui.comboBox_constraint_dst_action_type,
            self.ui.textbox_constraint_rule_dst_value,
            self.ui.checkBox_constraint_rule_wildcard
        )
            
    def comboBox_dependency_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.ui.comboBox_dependency_constraint_rule_dst_action,
            self.ui.comboBox_dependency_constraint_dst_action_type,
            self.ui.textbox_dependency_constraint_rule_dst_value,
            self.ui.checkBox_dependency_constraint_rule_wildcard
        )
            
    def comboBox_tc_dependency_constraint_rule_dst_action_changed(self):
        GeneralTool.update_constraint_actions_dst(
            self.ui.comboBox_tc_dependency_constraint_rule_dst_action,
            self.ui.comboBox_tc_dependency_constraint_dst_action_type,
            self.ui.textbox_tc_dependency_constraint_rule_dst_value,
            self.ui.checkBox_tc_dependency_constraint_rule_wildcard
        )
      
    def btn_constraint_rule_clear_clicked(self):
        """ Clear the Constraint Rule UI. """
        GeneralTool.clean_ui_content([
            self.ui.textbox_constraint_rule_src, 
            self.ui.textbox_constraint_rule_expected_value, 
            self.ui.textbox_constraint_rule_dst, 
            self.ui.textbox_constraint_rule_dst_value,
        ])
        self.ui.checkBox_constraint_rule_wildcard.setChecked(False)

    def btn_constraint_rule_apply_clicked(self):
        src_action = self.ui.comboBox_constraint_rule_src_action.currentText()
        src_path = self.ui.textbox_constraint_rule_src.text()
        src_condition = self.ui.comboBox_constraint_rule_condition.currentText()
        src_expected_value = self.ui.textbox_constraint_rule_expected_value.text()
        dst_action = self.ui.comboBox_constraint_rule_dst_action.currentText()
        dst_path = self.ui.textbox_constraint_rule_dst.text()
        dst_action_type = self.ui.comboBox_constraint_dst_action_type.currentText()
        dst_value = self.ui.textbox_constraint_rule_dst_value.text()
        
        if len(self.ui.table_api_tree.selectedItems()) == 0 or self.ui.table_api_tree.selectedItems()[0].parent() is None:
            return
        else:
            operation_id = self.ui.table_api_tree.selectedItems()[0].text(4)
            file_path = f"./artifacts/GenerationRule/{operation_id}.json"
            if os.path.exists(file_path) is False:
                return

        GeneralTool.apply_constraint_rule(
            operation_id, src_action, src_path, src_condition, src_expected_value, dst_action, dst_path, dst_action_type, dst_value)
        
        # * Refresh the Generation Rule Table
        GeneralTool.refresh_generation_rule_table(self.ui.table_api_tree, self.ui.table_generation_rule, file_path)
        GeneralTool.expand_and_resize_tree(self.ui.table_generation_rule, 0)
        GeneralTool.clean_ui_content([self.ui.textbox_constraint_rule_src, self.ui.textbox_constraint_rule_expected_value,
                                        self.ui.textbox_constraint_rule_dst, self.ui.textbox_constraint_rule_dst_value])
        self.ui.checkBox_constraint_rule_wildcard.setChecked(False)
            
    def table_generation_rule_item_clicked(self):
        """ 
        When the user click the item in the table_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.ui.table_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item,
            self.ui.textbox_constraint_rule_src, 
            self.ui.textbox_constraint_rule_expected_value, 
            self.ui.textbox_constraint_rule_dst,
            self.ui.textbox_constraint_rule_dst_value, 
            self.ui.checkBox_constraint_rule_wildcard,
        )
        GeneralTool.render_data_rule(
            selected_item,
            self.ui.textbox_data_rule_type,
            self.ui.textbox_data_rule_format,
            self.ui.textbox_data_rule_value,
            self.ui.comboBox_data_rule_data_generator,
            self.ui.textbox_data_rule_data_length,
            self.ui.comboBox_data_rule_required,
            self.ui.comboBox_data_rule_nullable,
            self.ui.textbox_data_rule_regex_pattern
        )
                 
    def table_dependency_generation_rule_item_clicked(self):
        """ 
        When the user click the item in the table_dependency_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.ui.table_dependency_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item, 
            self.ui.textbox_dependency_constraint_rule_src, 
            self.ui.textbox_dependency_constraint_rule_expected_value, 
            self.ui.textbox_dependency_constraint_rule_dst,
            self.ui.textbox_dependency_constraint_rule_dst_value, 
            self.ui.checkBox_dependency_constraint_rule_wildcard
        )
        GeneralTool.render_data_rule(
            selected_item,
            self.ui.textbox_dependency_data_rule_type,
            self.ui.textbox_dependency_data_rule_format,
            self.ui.textbox_dependency_data_rule_value,
            self.ui.comboBox_dependency_data_rule_data_generator,
            self.ui.textbox_dependency_data_rule_data_length,
            self.ui.comboBox_dependency_data_rule_required,
            self.ui.comboBox_dependency_data_rule_nullable,
            self.ui.textbox_dependency_data_rule_regex_pattern,
        )        
        
    def table_tc_dependency_generation_rule_item_clicked(self):
        """
        When the user click the item in the table_tc_dependency_generation_rule.
        It will render the constraint rule UI for quick setup the constraint rule.
        """
        selected_item = self.ui.table_tc_dependency_generation_rule.selectedItems()[0]
        GeneralTool.render_constraint_rule(
            selected_item,
            self.ui.textbox_tc_dependency_constraint_rule_src,
            self.ui.textbox_tc_dependency_constraint_rule_expected_value,
            self.ui.textbox_tc_dependency_constraint_rule_dst,
            self.ui.textbox_tc_dependency_constraint_rule_dst_value,
            self.ui.checkBox_tc_dependency_constraint_rule_wildcard,
        )
        GeneralTool.render_data_rule(
            selected_item,
            self.ui.textbox_tc_dependency_data_rule_type,
            self.ui.textbox_tc_dependency_data_rule_format,
            self.ui.textbox_tc_dependency_data_rule_value,
            self.ui.comboBox_tc_dependency_data_rule_data_generator,
            self.ui.textbox_tc_dependency_data_rule_data_length,
            self.ui.comboBox_tc_dependency_data_rule_required,
            self.ui.comboBox_tc_dependency_data_rule_nullable,
            self.ui.textbox_tc_dependency_data_rule_regex_pattern,
        )  

        
    def btn_api_table_add_use_case_clicked(self):
        """ This Add Button is used to duplicate an existing first-level API, and also copy over the Generation Rule, Assertion Rule, and Dependency Request Body. """
        # * To get the selected api item, and copy it.
        if len(self.ui.table_api_tree.selectedItems()) == 0:
            return
        else:
            selected_item = self.ui.table_api_tree.selectedItems()[0]
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
                file_path = f"./artifacts/{folder}/{operation_id}.json"
                if os.path.exists(file_path):
                    new_file_path = f"./artifacts/{folder}/{new_operation_id}.json"
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    with open(new_file_path, "w") as f:
                        json.dump(data, f, indent=4)
                else:
                    continue
            logging.info(f"Create a new use case `{new_operation_id}` from `{operation_id}`.")

    
    def table_assertion_rule_item_clicked(self):
        """ When the assertion rule item is clicked. """
        selected_item = self.ui.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            self.ui.comboBox_assertion_type.setCurrentText(parent_item.text(0))
            self.ui.comboBox_assertion_source.setCurrentText(selected_item.child(0).text(1))
            self.ui.textbox_assertion_rule_field_expression.setText(selected_item.child(1).text(1))
            self.ui.textbox_assertion_rule_expression.setText(selected_item.child(2).text(1))
            self.ui.comboBox_assertion_method.setCurrentText(selected_item.child(3).text(1))
            self.ui.textbox_assertion_rule_expected_value.setText(selected_item.child(4).text(1))
            self.ui.comboBox_assertion_type.setEnabled(False)
        else:
            self.ui.comboBox_assertion_type.setEnabled(True)
    
    def btn_update_assertion_rule_clicked(self):
        """ Update Assertion Rule Item """
        if len(self.ui.table_assertion_rule.selectedItems()) == 0:
            return
        
        test_type = self.ui.comboBox_assertion_type.currentText()
        source = self.ui.comboBox_assertion_source.currentText()
        filter_expression = self.ui.textbox_assertion_rule_expression.text()
        field_expression = self.ui.textbox_assertion_rule_field_expression.text()
        method = self.ui.comboBox_assertion_method.currentText()
        expected_value = self.ui.textbox_assertion_rule_expected_value.text()
                
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.ui.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Retrieve the Rule Sequence Number
        assertion_selected_item = [item.text(0) for item in self.ui.table_assertion_rule.selectedItems()]
        sequence_num = assertion_selected_item[0]

        # * To obtain the selected item's parent item
        selected_item = self.ui.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item and parent_item.parent() is None:
            # * Update the value in the JSON file
            file_path = "./artifacts/AssertionRule/" + operation_id + ".json"
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
            for clean_item in [self.ui.textbox_assertion_rule_expression, self.ui.textbox_assertion_rule_field_expression, self.ui.textbox_assertion_rule_expected_value, self.ui.table_assertion_rule]:
                clean_item.clear()
            GeneralTool.parse_assertion_rule(operation_id, self.ui.table_assertion_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_assertion_rule)
            self.ui.comboBox_assertion_type.setEnabled(True)
        else:
            return

    def btn_remove_assertion_rule_clicked(self):
        """ Remove Assertion Rule Item """
        
        if len(self.ui.table_assertion_rule.selectedItems()) == 0:
            return

        selected_item = self.ui.table_assertion_rule.selectedItems()[0]
        parent_item = selected_item.parent()
        
        if parent_item and parent_item.parent() is None:
            # * Get the JSON Path of the selected item
            path = [parent_item.text(0).lower(), selected_item.text(0)]
            # * Retrieve the API List selected item to get the corresponding operation id
            api_selected_item = [item.text(4) for item in self.ui.table_api_tree.selectedItems()]
            operation_id = api_selected_item[0]
            assertion_file_path = f"./artifacts/AssertionRule/{operation_id}.json"
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
            GeneralTool.remove_table_item_from_ui(self.ui.table_assertion_rule)
            self.ui.comboBox_assertion_type.setEnabled(True)

    def btn_add_assertion_rule_clicked(self):
        if len(self.ui.table_api_tree.selectedItems()) == 0:
            return
        
        test_type = self.ui.comboBox_assertion_type.currentText()
        source = self.ui.comboBox_assertion_source.currentText()
        field_expression = self.ui.textbox_assertion_rule_field_expression.text()
        filter_expression = self.ui.textbox_assertion_rule_expression.text()
        method = self.ui.comboBox_assertion_method.currentText()
        expected_value = self.ui.textbox_assertion_rule_expected_value.text()
        
        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.ui.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Add the value in the JSON file
        file_path = "./artifacts/AssertionRule/" + operation_id + ".json"
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
        for clean_item in [self.ui.textbox_assertion_rule_expression, self.ui.textbox_assertion_rule_field_expression, self.ui.textbox_assertion_rule_expected_value, self.ui.table_assertion_rule]:
            clean_item.clear()
        GeneralTool.parse_assertion_rule(operation_id, self.ui.table_assertion_rule)
        GeneralTool.expand_and_resize_tree(self.ui.table_assertion_rule)
    
    def btn_update_text_body_clicked(self):
        selected_items = self.ui.table_test_plan_api_list.selectedItems()
        parent = None
        if len(selected_items) > 0:
            parent = selected_items[0].parent()
            if parent is not None and parent.parent() is not None:
                test_id = selected_items[0].text(1)
                serial_num = test_id.split(".")[0]
                test_point = test_id.split(".")[1]
                operation_id = parent.parent().text(0)
                new_value = self.ui.text_body.toPlainText()
                testdata_path = f"./artifacts/TestData/{operation_id}_{serial_num}_{test_point}.json"
                
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
                        self.ui.text_body.setPlainText(json.dumps(copy_testdata, indent=4))
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
        api_selected_item = [item.text(4) for item in self.ui.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Update the value in the JSON file
        file_path = "./artifacts/GenerationRule/" + operation_id + ".json"
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
                
    def _create_dependency_generation_and_path_and_query_rule(
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
        generation_rule, path_rule, query_rule = GeneralTool.generate_dependency_data_generation_and_path_and_query_rule(api_name)
        
        if generation_rule != None or generation_rule != {}:
            with open(f"./artifacts/DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "data_generation_rules" , generation_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'data_generation_rules']}`.")
                else:
                    logging.error(f"Error updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'data_generation_rules']}`.")
                
        if path_rule != None:
            with open(f"./artifacts/DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "path", path_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'path']}`.")
                else:
                    logging.error(f"Error updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'path']}`.")    
        
        if query_rule != None:
            with open(f"./artifacts/DependencyRule/{original_operation_id}.json", "r+") as f:
                data = json.load(f)
                result = GeneralTool.add_key_in_json(data, [dependency_type, sequence_num], "query", query_rule)
                if result is not False:
                    f.seek(0)
                    json.dump(data, f , indent=4)
                    f.truncate()
                    logging.info(f"Successfully updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'query']}`.")
                else:
                    logging.error(f"Error updating JSON file `./artifacts/DependencyRule/{original_operation_id}.json` to add key `{[dependency_type, sequence_num, 'query']}`.")
        
    def _create_generation_rule_and_assertion_files(self):
        """ Create Generation Rule and Assertion Files """
        for schema in self.ui.schema_list:
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
                        with open(f"./artifacts/GenerationRule/{operation_id}.json", "w") as f:
                            json.dump(generation_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have requestBody.')
                    
                    # * Create the Assertion Rule File
                    if 'responses' in operation:
                        assertion_rule = GeneralTool.parse_schema_to_assertion_rule(operation['responses'])
                        with open(f"./artifacts/AssertionRule/{operation_id}.json", "w") as f:
                            json.dump(assertion_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have responses.')
                        
                    # * Create the Path Rule File
                    if 'parameters' in operation:
                        path_rule = GeneralTool.parse_schema_to_path_rule(operation['parameters'])
                        with open(f"./artifacts/PathRule/{operation_id}.json", "w") as f:
                            json.dump(path_rule, f, indent=4)
                    else:
                        logging.debug(f'This API "{method} {uri}"  does not have parameters.')
                        
                    # * Create the Query Rule File
                    if 'parameters' in operation:
                        query_rule = GeneralTool.parse_schema_to_query_rule(operation['parameters'])
                        with open(f"./artifacts/QueryRule/{operation_id}.json", "w") as f:
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
        if self.ui.table_api_tree.selectedItems() == [] or self.ui.table_generation_rule.selectedItems() == []:
            return

        # * Retrieve the API List selected item to get the corresponding operation id
        api_selected_item = [item.text(4) for item in self.ui.table_api_tree.selectedItems()]
        operation_id = api_selected_item[0]
        
        # * Retrieve the Generation Rule List selected items to get the corresponding paths
        paths = []
        for item in self.ui.table_generation_rule.selectedItems():
            path = []
            while item.parent() is not None:
                path.insert(0, item.text(0))
                item = item.parent()
            # * If toplevel item is selected, return directly.
            if path == []: return
            paths.append(path)
                
        # * Update the value in the JSON file
        file_path = "./artifacts/GenerationRule/" + operation_id + ".json"
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
        GeneralTool.remove_table_item_from_ui(self.ui.table_generation_rule)
        
    def btn_api_table_remove_clicked(self):
        """ Remove API Table Item """
        selected_items = self.ui.table_api_tree.selectedItems()
        for item in selected_items:
            if item.parent() is None:
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule", "AdditionalAction", "QueryRule"]
                for folder in teardown_folder:  
                    for child_file in glob.glob(f"./artifacts/{folder}/{item.text(0)}*.json"):
                        os.remove(child_file)
                self.ui.table_api_tree.takeTopLevelItem(self.ui.table_api_tree.indexOfTopLevelItem(item))
            else:
                file_name = item.text(4)
                teardown_folder = ["GenerationRule", "AssertionRule", "PathRule", "DependencyRule", "AdditionalAction", "QueryRule"]
                for folder in teardown_folder:
                    file_path = f"./artifacts/{folder}/" + file_name + ".json"
                    if os.path.exists(file_path):
                        os.remove(file_path)
                item.parent().takeChild(item.parent().indexOfChild(item))
                # * Clear the table
                teardown_table = [self.ui.table_schema, self.ui.table_generation_rule, self.ui.table_assertion_rule,]
                for table in teardown_table: table.clear()

    def generate_test_plan(self):
        """ Generate Test Plan """
        
        # * Check if the object mapping file is imported.
        if not os.path.exists("config/obj_mapping.json"):
            logging.error(f"Object Mapping File not found.")
            error_message = f"The Object Mapping File is not imported."
            detailed_message = f"Please import the Object Mapping File first."
            GeneralTool.show_error_dialog(error_message, detailed_message)
            return
        
        # * Generate TCG Config
        GeneralTool.generate_tcg_config(self.ui.group_test_strategy.findChildren(QCheckBox))
        with open(f"config/tcg_config.json", "r") as f:
            tcg_config = json.load(f)
            
        # * Generate Test Plan
        GeneralTool.teardown_folder_files(["./artifacts/TestPlan", "./artifacts/TestData", "./artifacts/TestData/Dependency_TestData"])  
        serial_number = 1
        test_count = self.ui.spinbox_test_case_count.value()
        for i in range(self.ui.table_api_tree.topLevelItemCount()):
            schema_item = self.ui.table_api_tree.topLevelItem(i)
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
                                self.ui.tabTCG.setCurrentIndex(1)
        
        # * Render Test Plan to Table
        GeneralTool.clean_ui_content([
            self.ui.table_test_plan_api_list,
            self.ui.table_tc_assertion_rule,
            self.ui.table_tc_dependency_rule,
            self.ui.table_tc_dependency_path,
            self.ui.table_tc_dependency_generation_rule,
            self.ui.textbox_tc_dependency_requestbody,
            self.ui.table_tc_path,
            self.ui.text_body,
        ])
        self.ui.table_test_plan_api_list.clear()
        for test_plan in glob.glob("./artifacts/TestPlan/*.json"):
            with open(test_plan, "r") as f:
                test_plan = json.load(f)
            file_name = test_plan['test_info']['operationId']
            toplevel_length = self.ui.table_test_plan_api_list.topLevelItemCount()
            self.ui.table_test_plan_api_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
            for index, test_case in test_plan['test_cases'].items():
                testcase_child = QtWidgets.QTreeWidgetItem(["", str(index), test_case['test_strategy'], test_case['test_type']])
                self.ui.table_test_plan_api_list.topLevelItem(toplevel_length).addChild(testcase_child)
                for tp_index, test_point in test_case['test_point'].items():
                    tp_index = str(index) + "." + str(tp_index)
                    testcase_child.addChild(QtWidgets.QTreeWidgetItem(["", tp_index, "", "", test_point['parameter']['name']]))
                    
    def import_object_mapping_file(self):
        """ Import Object Mapping File """
        file_filter = "Object Mapping File (*.json)"
        response = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self.ui.tab, caption="Open Object Mapping File", directory=os.getcwd(), filter=file_filter)

        try:
            for file_path in response[0]:
                file_name = os.path.basename(file_path)
                if not os.path.exists("./config/"):
                    os.mkdir("./config/")
                shutil.copy(file_path, f"./config/obj_mapping.json")
                logging.info(f"Import Object Mapping File `{file_name}`.")
        except shutil.SameFileError as e:
            logging.warning(f"Import Object Mapping File `{file_name}` is the same as the existing one.")

    def import_openapi_doc(self):
        """ Import OpenAPI Doc """
        file_filter = "OpenAPI Doc (*.yaml *.yml *.json)"
        response = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self.ui.tab, caption="Open OpenAPI Doc", directory=os.getcwd(), filter=file_filter)
        
        # * Clean Environment
        GeneralTool.teardown_folder_files([
            "./artifacts/GenerationRule", 
            "./artifacts/AssertionRule", 
            "./artifacts/PathRule", 
            "./artifacts/DependencyRule", 
            "./artifacts/AdditionalAction", 
            "./artifacts/QueryRule",
            "./schemas",
            ])
        GeneralTool.clean_ui_content([
            self.ui.table_api_tree, 
            self.ui.table_schema,
            self.ui.table_path,
            self.ui.table_query,
            self.ui.table_generation_rule, 
            self.ui.table_assertion_rule, 
            self.ui.list_dependency_available_api_list,
            self.ui.list_tc_dependency_available_api_list,
        ])
        
        try:
            for file_path in response[0]:
                file_name = os.path.basename(file_path)
                if not os.path.exists("./schemas/"):
                    os.mkdir("./schemas/")
                shutil.copy(file_path, f"./schemas/{file_name}")
                logging.info(f"Import OpenAPI Doc `{file_name}`.")
        except shutil.SameFileError as e:
            logging.warning(f"Import OpenAPI Doc `{file_name}` is the same as the existing one.")
        
        self.ui.schema_list = response[0]
        index = 1
        for schema in self.ui.schema_list:
            file_path = schema
            file_name = os.path.basename(file_path).split(".")[0]
            api_doc = GeneralTool.load_schema_file(file_path)
            index = self._render_api_tree(api_doc, index, file_name)
            # * If the index is None, it means the API Doc is not in the correct format, return directly.
            if index == None:
                self.ui.table_api_tree.clear()
                return
        self._create_generation_rule_and_assertion_files()
        GeneralTool.expand_and_resize_tree(self.ui.table_api_tree)
        
        # * Update Search Completion List
        all_api_list = []
        for i in range(self.ui.list_dependency_available_api_list.count()):
            all_api_list.append(self.ui.list_dependency_available_api_list.item(i).text())
        model = QStringListModel()
        model.setStringList(all_api_list)
        self.ui.search_completer.setModel(model)
        
        all_tc_api_list = []
        for i in range(self.ui.list_tc_dependency_available_api_list.count()):
            all_tc_api_list.append(self.ui.list_tc_dependency_available_api_list.item(i).text())
        tc_model = QStringListModel()
        tc_model.setStringList(all_tc_api_list)
        self.ui.tc_search_completer.setModel(tc_model)     
                     
    def _render_api_tree(self, api_doc, index, file_name):
        """ Render API Tree """
        toplevel_length = self.ui.table_api_tree.topLevelItemCount()
        self.ui.table_api_tree.addTopLevelItem(QtWidgets.QTreeWidgetItem([file_name]))
        try:
            for uri, path_item in api_doc['paths'].items():
                for method, operation in path_item.items():
                    self.ui.table_api_tree.topLevelItem(toplevel_length).addChild(
                        QtWidgets.QTreeWidgetItem(["", str(index), uri, method.upper(), operation['operationId']])
                    )
                    # * Render the Available API List
                    self.ui.list_dependency_available_api_list.addItem(f"{method.upper()} {uri}")
                    self.ui.list_tc_dependency_available_api_list.addItem(f"{method.upper()} {uri}")
                    index += 1
        except KeyError as e:
            logging.error(f"Error parsing API Doc `{file_name}`.")
            error_message = f"Error parsing API Doc `{file_name}`. Please check the format."
            detailed_message = "Cannot find the key `{}` in the API Doc.".format(e.args[0])
            GeneralTool.show_error_dialog(error_message, detailed_message)
            return None
        return index
    
    def test_plan_api_list_item_clicked(self, item, column):
        """When the test plan api list item is clicked."""
        
        # * Clear the table
        GeneralTool.clean_ui_content([
            self.ui.table_tc_dependency_rule, self.ui.table_tc_assertion_rule, self.ui.text_body, self.ui.textbox_tc_dependency_requestbody, self.ui.table_tc_dependency_path,
            self.ui.table_tc_path, self.ui.textbox_tc_path_name, self.ui.textbox_tc_path_value, self.ui.table_tc_dependency_rule, self.ui.table_tc_dependency_generation_rule,
            self.ui.comboBox_tc_dependency_type, self.ui.line_tc_api_search, self.ui.textbox_tc_dependency_return_variable_name, self.ui.textbox_tc_description,
            self.ui.textbox_tc_request_name, self.ui.textbox_tc_response_name, self.ui.table_tc_additional_action, self.ui.table_tc_dependency_additional_action,
            self.ui.table_tc_query, self.ui.table_tc_dependency_query
        ])
        self.ui.comboBox_tc_dependency_type.setEnabled(True)
        self.ui.line_tc_api_search.setEnabled(True)
        
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
            with open(f"./artifacts/TestPlan/{test_plan_name}.json", "r") as f:
                test_plan = json.load(f)
            test_case_id = test_id.split(".")[0]
            test_point_id = test_id.split(".")[1]
            
            # * Render the Description and Request/Response Name
            description = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['description']
            request_name = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['request_name']
            response_name = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['parameter']['response_name']
            self.ui.textbox_tc_description.setText(description)
            self.ui.textbox_tc_request_name.setText(request_name)
            self.ui.textbox_tc_response_name.setText(response_name)
            
            # * Render the Test Case Dependency Rule.
            GeneralTool.render_dependency_rule(test_plan, test_case_id, test_point_id, self.ui.table_tc_dependency_rule)
            
            # * Render the Path Rule.
            path_item = QTreeWidgetItem(["Path Parameters"])
            self.ui.table_tc_path.addTopLevelItem(path_item)
            path_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['path']
            for key, value in path_rule.items():
                path_item.addChild(QTreeWidgetItem([key, value]))
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_path)
            
            # * Render the Query Rule.
            query_item = QTreeWidgetItem(["Query Parameters"])
            self.ui.table_tc_query.addTopLevelItem(query_item)
            query_rule = test_plan['test_cases'][test_case_id]['test_point'][test_point_id]['query']
            for key, value in query_rule.items():
                query_item.addChild(QTreeWidgetItem([key, value]))
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_query)
            
            # * Render the Assertion Rule.
            assertion_item = QTreeWidgetItem(["Assertion Rules"])
            self.ui.table_tc_assertion_rule.addTopLevelItem(assertion_item)
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
            GeneralTool.expand_and_resize_tree(self.ui.table_tc_assertion_rule, level=3)
                    
            # * Render the request body in text box.
            serial_num = test_id.split(".")[0]
            test_point = test_id.split(".")[1]
            try:
                with open(f"./artifacts/TestData/{test_plan_name}_{serial_num}_{test_point}.json") as file:
                    testdata = json.load(file)
                testdata_str = json.dumps(testdata, indent=4)
                self.ui.text_body.setPlainText(testdata_str)
            except FileNotFoundError:
                logging.info(f"Test data file `./artifacts/TestData/{test_plan_name}_{serial_num}_{test_point}.json` does not exist.")
                
            # * Render Additional Action
            GeneralTool.parse_tc_additional_action_rule(test_plan_name, self.ui.table_tc_additional_action, test_case_id, test_point_id)

    def api_tree_item_clicked(self, item, column):
        """When the api tree item is clicked."""
        # * Clear the table
        GeneralTool.clean_ui_content([
            self.ui.table_schema,
            self.ui.table_generation_rule, 
            self.ui.table_assertion_rule, 
            self.ui.table_path,
            self.ui.table_query,
            self.ui.table_dependency_rule,
            self.ui.table_dependency_path,
            self.ui.table_dependency_generation_rule,
            self.ui.line_api_search,
            self.ui.textbox_dependency_return_variable_name,
            self.ui.textbox_data_rule_type,
            self.ui.textbox_data_rule_format,
            self.ui.textbox_data_rule_value,
            self.ui.comboBox_data_rule_data_generator,
            self.ui.textbox_data_rule_data_length,
            self.ui.comboBox_data_rule_required,
            self.ui.comboBox_data_rule_nullable,
            self.ui.table_additional_action,
            self.ui.textbox_data_rule_regex_pattern,
            self.ui.table_dependency_additional_action,
        ])
        self.ui.comboBox_dependency_type.setEnabled(True)
        self.ui.line_api_search.setEnabled(True)
        
        # * If the column is top level, return
        if column == 0:
            return
        
        # * If the use case item is clicked.
        selected_item = self.ui.table_api_tree.selectedItems()[0]
        parent_item = selected_item.parent()
        if parent_item is not None and parent_item.parent() is not None:
            operation_id = selected_item.text(4)
            
            # * Render the Generation Rule from the file.
            # * Some API does not have requestBody, so the generation rule file does not exist.
            # * Ex : GET, DELETE, etc.
            GeneralTool.parse_generation_rule(operation_id, self.ui.table_generation_rule)
            
            # * Render the Assertion Rule from the file.
            GeneralTool.parse_assertion_rule(operation_id, self.ui.table_assertion_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_assertion_rule, level=3)
            
            # * Render the Path Rule from the file.
            GeneralTool.parse_path_rule(operation_id, self.ui.table_path)
            GeneralTool.expand_and_resize_tree(self.ui.table_path, level=3)
            
            # * Render the Query Rule from the file.
            GeneralTool.parse_query_rule(operation_id, self.ui.table_query)
            GeneralTool.expand_and_resize_tree(self.ui.table_query, level=3)
            
            # * Render the Dependency Rule from the file.
            GeneralTool.parse_dependency_rule(operation_id, self.ui.table_dependency_rule)
            GeneralTool.expand_and_resize_tree(self.ui.table_dependency_rule, level=3)
            
            # * Render the Additional Action from the file.
            GeneralTool.parse_additional_action_rule(operation_id, self.ui.table_additional_action)
            GeneralTool.expand_and_resize_tree(self.ui.table_additional_action, level=3)
            
            return
            
        table_path, table_method = item.text(2), item.text(3)
        logging.debug(f"Table Path: {table_path}, Table Method: {table_method}, Table Column: {column}")
        
        for schema in self.ui.schema_list:
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
                            self.ui.table_schema.addTopLevelItem(root_item)
                            GeneralTool.parse_request_body(request_body_schema, root_item, editabled=True)
                            
                            root_item_2 = QTreeWidgetItem(["Data Generation Rule"])
                            self.ui.table_generation_rule.addTopLevelItem(root_item_2)
                            with open(f"./artifacts/GenerationRule/{operation_id}.json", "r") as f:
                                generation_rule = json.load(f)
                            GeneralTool.parse_request_body(generation_rule, root_item_2, editabled=True)
                        else:
                            logging.info(f"This API {uri} does not have requestBody.")
                            
                        if 'responses' in operation:
                            root_item = QTreeWidgetItem(["Response Body"])
                            self.ui.table_schema.addTopLevelItem(root_item)
                            for status_code, response in operation['responses'].items():
                                if len(status_code) == 3 or status_code == 'default':
                                    # * WARNING: Only support the first content type now.
                                    if operation['responses'][status_code]['content'] == {}:
                                        continue
                                    first_content_type = next(iter(operation['responses'][status_code]['content']))
                                    response_body_schema = response['content'][first_content_type]['schema']
                                    response_body_schema = GeneralTool().retrive_ref_schema(api_doc, response_body_schema)
                                    sub_root_item = QTreeWidgetItem([status_code])
                                    root_item.addChild(sub_root_item)
                                    GeneralTool.parse_request_body(response_body_schema, sub_root_item, editabled=False)
                                else:
                                    logging.warning(f"API {uri} has a wrong status code {status_code}.")
                                    
                        # * Render the assertion rule from the file.
                        GeneralTool.parse_assertion_rule(operation_id, self.ui.table_assertion_rule)
                        GeneralTool.expand_and_resize_tree(self.ui.table_generation_rule, level=2)
                        GeneralTool.expand_and_resize_tree(self.ui.table_assertion_rule, level=3)
                        GeneralTool.expand_and_resize_tree(self.ui.table_schema, level=2)
                        
                        # * Render the Path Rule from the file.
                        GeneralTool.parse_path_rule(operation_id, self.ui.table_path)
                        GeneralTool.expand_and_resize_tree(self.ui.table_path, level=3)
                        
                        # * Render the Query Rule from the file.
                        GeneralTool.parse_query_rule(operation_id, self.ui.table_query)
                        GeneralTool.expand_and_resize_tree(self.ui.table_query, level=3)
                        
                        # * Render the Dependency Rule from the file.
                        GeneralTool.parse_dependency_rule(operation_id, self.ui.table_dependency_rule)
                        GeneralTool.expand_and_resize_tree(self.ui.table_dependency_rule, level=3)
                        
                        # * Render the Additional Action from the file.
                        GeneralTool.parse_additional_action_rule(operation_id, self.ui.table_additional_action)
                        GeneralTool.expand_and_resize_tree(self.ui.table_additional_action, level=3)

if __name__ == '__main__':                        
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.showMaximized()
    window.show()
    app.exec()
