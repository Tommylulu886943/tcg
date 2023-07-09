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

    def load_form(self, fields):
        self.clear_form()
        for field in fields:
            label = QLabel(field)
            edit = QLineEdit()
            self.layout.addRow(label, edit)

    def get_values(self, action):
        values = {"Action Name": action}
        for i in range(0, self.layout.count(), 2):
            label = self.layout.itemAt(i).widget().text()
            edit = self.layout.itemAt(i).widget().nextInFocusChain()
            values[label] = edit.text()
        return values

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.specialActions = {
            "特殊處理1": ["Variable Name", "Paser Name", "Response", "Field", "Return Type"],
            "特殊處理2": ["Variable Name", "Remove IP"]
        }

        self.combo = QComboBox()
        self.combo.addItems(self.specialActions.keys())
        self.layout.addWidget(self.combo)

        self.form = CustomForm()
        self.layout.addWidget(self.form)

        self.combo.currentTextChanged.connect(self.load_form)

        self.button = QPushButton("新增特殊處理")
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.add_special_action)
        self.load_form()

    def load_form(self):
        current_action = self.combo.currentText()
        fields = self.specialActions[current_action]
        self.form.load_form(fields)
            
    def add_special_action(self):
        values = self.form.get_values(self.combo.currentText())
        print(values)
        # do something with values

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
