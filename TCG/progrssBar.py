from PyQt6.QtWidgets import QMainWindow, QApplication, QProgressBar, QPushButton
import time
from PyQt6.QtCore import QThread, pyqtSignal

class LongTask(QThread):
    progress = pyqtSignal(int)

    def run(self):
        for i in range(101):
            time.sleep(0.1)
            self.progress.emit(i)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 50, 200, 25)

        self.button = QPushButton('Start', self)
        self.button.move(50, 80)
        self.button.clicked.connect(self.startLongTask)

    def startLongTask(self):
        self.longTask = LongTask()
        self.longTask.progress.connect(self.onProgress)
        self.longTask.start()

    def onProgress(self, i):
        self.progressBar.setValue(i)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
