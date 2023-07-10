from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox

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
            print(fields)
            print(field)
            label = QLabel(field)
            edit = None
            if action == "Parser - API Parser":
                edit = QComboBox()
                if field == "Return Type":
                    edit.addItems(["String", "List", "Dict"])
                else:
                    edit = QLineEdit()
            elif action == "Analyzer - Config Analyzer":
                edit = QComboBox()
                if field == "Action":
                    edit.addItems(["Config Compare", "String Match"])
                elif field == "Verbose":
                    edit.addItems(["True", "False"])
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
    