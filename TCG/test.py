from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor,  QPainter, QPainterPath
import requests
import sys
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPen, QPainterPath
from PyQt6.QtWidgets import QGraphicsPathItem

class Arrow(QGraphicsPathItem):
    def __init__(self, start_item, end_item):
        super().__init__()

        self.start_item = start_item
        self.end_item = end_item
        self.start_item.add_arrow(self)
        self.end_item.add_arrow(self)

        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPathItem.ItemIsFocusable, True)

        self.update_position()

    def update_position(self):
        start_pos = self.mapFromItem(self.start_item, self.start_item.width / 2, self.start_item.height / 2)
        end_pos = self.mapFromItem(self.end_item, self.end_item.width / 2, self.end_item.height / 2)

        line = QLineF(start_pos, end_pos)
        path = QPainterPath()
        path.moveTo(line.p1())
        path.lineTo(line.p2())

        self.setPath(path)

    def mousePressEvent(self, event):
        self.setSelected(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.update_position()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.start_item.remove_arrow(self)
            self.end_item.remove_arrow(self)
            self.scene().removeItem(self)
            self.deleteLater()
        else:
            super().keyPressEvent(event)

class ApiNode(QGraphicsRectItem):
    def __init__(self, name):
        super().__init__(QRectF(0, 0, 100, 50))

        self.name = name
        self.arrows = []
        self.setBrush(QBrush(QColor("gray")))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.text = QGraphicsTextItem(name)
        self.text.setParentItem(self)
        self.text.setPos(10, 10)

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        painter.setBrush(self.brush())
        painter.drawPath(path)

    def add_arrow(self, arrow):
        self.arrows.append(arrow)

    def remove_arrow(self, arrow):
        if arrow in self.arrows:
            self.arrows.remove(arrow)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for arrow in self.arrows:
                arrow.update_position()
        return super().itemChange(change, value)

class ApiFlowApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self.start_button = QPushButton('Add START Node')
        self.start_button.clicked.connect(self.add_start_node)
        layout.addWidget(self.start_button)

        self.get_button = QPushButton('Add GET Node')
        self.get_button.clicked.connect(self.add_get_node)
        layout.addWidget(self.get_button)

        self.post_button = QPushButton('Add POST Node')
        self.post_button.clicked.connect(self.add_post_node)
        layout.addWidget(self.post_button)

        layout.addWidget(self.view)

        self.setLayout(layout)

    def add_start_node(self):
        node = ApiNode("START")
        self.scene.addItem(node)

    def add_get_node(self):
        node = ApiNode("GET")
        self.scene.addItem(node)

    def add_post_node(self):
        node = ApiNode("POST")
        self.scene.addItem(node)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print(event.pos())
            self.start_node = self.get_node_at(event.pos())
            print("GET1")
            print(self.start_node)
            if self.start_node:
                
                self.line = QGraphicsLineItem(QLineF(self.start_node.scenePos(), event.pos()))
                self.scene.addItem(self.line)

            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_node and not self.line is None:
            new_line = QLineF(self.start_node.scenePos(), event.pos())
            self.line.setLine(new_line)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.start_node:
            end_node = self.get_node_at(event.pos())
            if end_node and end_node != self.start_node:
                arrow = Arrow(self.start_node, end_node)
                self.scene.addItem(arrow)
            self.scene.removeItem(self.line)
            self.start_node = None
            self.line = None

        super().mouseReleaseEvent(event)

    def get_node_at(self, pos):
        items = self.scene.items(QPointF(pos))
        for item in items:
            if isinstance(item, ApiNode):
                return item
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ApiFlowApp()
    ex.show()
    sys.exit(app.exec())
