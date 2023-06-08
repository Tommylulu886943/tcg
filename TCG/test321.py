from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()  # 創建一個 QVBoxLayout 佈局

# 添加兩個按鈕到佈局中
layout.addWidget(QPushButton('Button 1'))
layout.addWidget(QPushButton('Button 2'))

window.setLayout(layout)  # 設置視窗的佈局
window.show()

app.exec()
