from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtCore import Qt
from typing import List

class NodePort(QGraphicsEllipseItem):
    """Visual representation of a node port"""
    def __init__(self, name: str, is_input: bool, node_widget, parent=None):
        super().__init__(-6, -6, 12, 12, parent)
        self.name = name
        self.is_input = is_input
        self.node_widget = node_widget
        self.connections: List = []
        # Styling
        if is_input:
            self.setBrush(QBrush(QColor(100, 150, 255)))
        else:
            self.setBrush(QBrush(QColor(255, 150, 100)))
        self.setPen(QPen(QColor(50, 50, 50), 2))
        self.setAcceptHoverEvents(True)
        self.setToolTip(self.name)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor(255, 255, 100)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.is_input:
            self.setBrush(QBrush(QColor(100, 150, 255)))
        else:
            self.setBrush(QBrush(QColor(255, 150, 100)))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if hasattr(scene, 'start_connection'):
                scene.start_connection(self)
        super().mousePressEvent(event)

    def update_position(self):
        # Stub for compatibility; implement logic if needed
        pass
