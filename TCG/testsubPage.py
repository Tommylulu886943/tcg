import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel

class SubWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("子視窗")
        
        layout = QVBoxLayout()
        label = QLabel("這是子視窗")
        layout.addWidget(label)
        
        confirm_button = QPushButton("確認")
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主視窗")

        button = QPushButton("彈出視窗")
        button.clicked.connect(self.open_subwindow)
        self.setCentralWidget(button)

    def open_subwindow(self):
        subwindow = SubWindow()
        if subwindow.exec() == QDialog.Accepted:
            print("按下了確認按鈕")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
