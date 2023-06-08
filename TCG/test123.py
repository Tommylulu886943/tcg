import sys
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QCompleter, QGroupBox, QLabel

class APIViewer(QWidget):
    def __init__(self, apis):
        super().__init__()
        self.apis = apis

        # 創建一個垂直佈局來容納控制項
        layout = QVBoxLayout()

        # 創建一個搜索框
        self.search_bar = QLineEdit()
        layout.addWidget(self.search_bar)

        # 創建一個列表來顯示 APIs
        self.api_list = QListWidget()
        layout.addWidget(self.api_list)

        # 創建一個 completer 並與搜索框關聯
        self.completer = QCompleter()
        self.search_bar.setCompleter(self.completer)

        # 將佈局應用到窗口
        self.setLayout(layout)

        # 初始化 API 列表和 completer
        self.update_api_list()
        self.update_completer()

    def update_api_list(self):
        # 清除當前列表
        self.api_list.clear()

        # 創建一個新的列表項目並將其添加到列表中
        for category, apis in self.apis.items():
            item = QListWidgetItem(category)
            self.api_list.addItem(item)

            # 在每個類別下面添加 API 項目
            for api in apis:
                item = QListWidgetItem("  " + api)
                self.api_list.addItem(item)

    def update_completer(self):
        # 從 API 列表中提取所有的 API
        all_apis = [api for apis in self.apis.values() for api in apis]

        # 創建一個模型並將其設置為 completer 的模型
        model = QStringListModel()
        model.setStringList(all_apis)
        self.completer.setModel(model)


# 假設這是我們的 APIs，分類後的結果
apis = {
    "Users": ["GET /api/v1/users", "DELETE /api/v1/posts"],
    "Tenant": ["POST /api/v1/tenants/new", "GET /api/v1/tenants/new"],
    # 等等...
}

app = QApplication(sys.argv)

viewer = APIViewer(apis)
viewer.show()

sys.exit(app.exec())
