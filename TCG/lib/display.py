import time

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QMessageBox, QProgressBar
from PyQt6.QtCore import QBasicTimer, QThread, pyqtSignal

class CustomForm(QWidget):
    def __init__(self, parent=None):
        super(CustomForm, self).__init__(parent)
        self.layout = QFormLayout(self)

    def clear_form(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_form(self, action, fields):
        self.clear_form()
        for field in fields:
            label = QLabel(field)
            edit = None
            if action == "API Parser":
                edit = QComboBox()
                if field == "Return Type":
                    edit.addItems(["list", "string", "set"])
                elif field == "${Response Name}":
                    edit = QLineEdit()
                    edit.setPlaceholderText("The name of the response variable to store the result")
                else:
                    edit = QLineEdit()
            elif action == "Config Analyzer":
                edit = QComboBox()
                if field == "Action":
                    edit.addItems(["", "config_compare", "string_match"])
                elif field == "Verbose":
                    edit.addItems(["", "true", "false"])
                elif field == "${Response Name}":
                    edit = QLineEdit()
                    edit.setPlaceholderText("The name of the response variable to store the result")
                else:
                    edit = QLineEdit()
            elif action == "Data Analyzer":
                edit = QComboBox()
                if field == "Return Type":
                    edit.addItems(["list", "string", "set"])
                elif field == "Result Type":
                    edit.addItems(["", "count_interval", "number_count", "success_rate"])
                elif field == "Verbose":
                    edit.addItems(["", "true", "false"])
                elif field == "${Response Name}":
                    edit = QLineEdit()
                    edit.setPlaceholderText("The name of the response variable to store the result")
                else:
                    edit = QLineEdit()
            elif action == "Get ID From Name":
                edit = QLineEdit()
                if field == "Objects":
                    edit.setPlaceholderText("e.g. agent, monitor, tenant")
                elif field == "Sender Instance":
                    edit.setPlaceholderText("e.g. FHE_U1_T1, FHE_U4_T2")
                elif field == "${Response Name}":
                    edit = QLineEdit()
                    edit.setPlaceholderText("The name of the responce variable to store the result")
                else:
                    edit = QLineEdit()
            else:
                edit = QLineEdit()
            if edit:
                self.layout.addRow(label, edit)

    def get_values(self, action):
        values = {"Action Name": action}
        for i in range(0, self.layout.count(), 2):
            label = self.layout.itemAt(i).widget().text()
            edit = self.layout.itemAt(i).widget().nextInFocusChain()
            if isinstance(edit, QLineEdit):
                values[label] = edit.text()
            elif isinstance(edit, QComboBox):
                values[label] = edit.currentText()
        return values
    
class UiRender:
    
    @classmethod
    def update_progress(cls, progress_obj, value):
        """ Update specified progress bar object with given value."""
                
        progress_obj.setValue(value)
        
    @classmethod
    def finish_progress(cls, progress_obj, msg):
        """ When the progress is finished, show the message."""
        QMessageBox.information(progress_obj, "Complete", msg)
        progress_obj.setValue(0)

class DataProcessor(QThread):
    progress = pyqtSignal(int)
    
    def run(self):
        for i in range(16, 101):
            time.sleep(0.05)
            self.progress.emit(i)
            