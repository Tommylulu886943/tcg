from PyQt6.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton
from PyQt6.QtCore import Qt, QBasicTimer


class ProgressBarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("進度條應用")
        self.setGeometry(300, 300, 300, 150)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 40, 240, 30)

        self.start_button = QPushButton("開始", self)
        self.start_button.setGeometry(110, 90, 80, 30)
        self.start_button.clicked.connect(self.start_progress)

        self.timer = QBasicTimer()
        self.progress_value = 0
        self.max_value = 100

    def start_progress(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.start_button.setText("開始")
        else:
            self.progress_value = 0
            self.progress_bar.setValue(self.progress_value)
            self.timer.start(100, self)
            self.start_button.setEnabled(False)
            self.start_button.setText("停止")


app = QApplication([])
window = ProgressBarApp()
window.show()
app.exec()
