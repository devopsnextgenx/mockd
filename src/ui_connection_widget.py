from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF, QRectF, Qt
from typing import Optional

# NOTE: To ensure delete key works, NodeGraphScene must import ConnectionWidget from ui_connection_widget.py
# In your gui.py, at the top, add:
# from src.ui_connection_widget import ConnectionWidget
#
# This ensures isinstance(item, ConnectionWidget) works in keyPressEvent.

class ConnectionWidget(QGraphicsItem):
    """Visual representation of a connection between ports"""
    def __init__(self, source_port, target_port=None):
        super().__init__()
        self.source_port = source_port
        self.target_port = target_port
        self.temp_end_point = None
        self.setZValue(-1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)  # Enable hover events
        self._hovered = False
        if source_port:
            source_port.connections.append(self)
        if target_port:
            target_port.connections.append(self)

    def boundingRect(self) -> QRectF:
        if self.source_port and (self.target_port or self.temp_end_point):
            source_pos = self.source_port.scenePos()
            if self.target_port:
                target_pos = self.target_port.scenePos()
            else:
                target_pos = self.temp_end_point
            return QRectF(
                min(source_pos.x(), target_pos.x()) - 10,
                min(source_pos.y(), target_pos.y()) - 10,
                abs(target_pos.x() - source_pos.x()) + 20,
                abs(target_pos.y() - source_pos.y()) + 20
            )
        return QRectF()

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update()
        # Do not call super().hoverEnterEvent(event) to avoid clearing hover state

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update()
        # Do not call super().hoverLeaveEvent(event) to avoid clearing hover state

    def shape(self):
        # Return a thicker path for easier selection/hover
        if self.source_port and (self.target_port or self.temp_end_point):
            from PySide6.QtGui import QPainterPathStroker
            source_pos = self.source_port.scenePos()
            if self.target_port:
                target_pos = self.target_port.scenePos()
            else:
                target_pos = self.temp_end_point
            path = QPainterPath()
            path.moveTo(source_pos)
            dx = target_pos.x() - source_pos.x()
            control1 = QPointF(source_pos.x() + dx * 0.5, source_pos.y())
            control2 = QPointF(target_pos.x() - dx * 0.5, target_pos.y())
            path.cubicTo(control1, control2, target_pos)
            stroker = QPainterPathStroker()
            stroker.setWidth(12)  # Make the clickable/hoverable area wider
            return stroker.createStroke(path)
        return super().shape()

    def paint(self, painter: QPainter, option, widget):
        if self.source_port and (self.target_port or self.temp_end_point):
            source_pos = self.source_port.scenePos()
            if self.target_port:
                target_pos = self.target_port.scenePos()
            else:
                target_pos = self.temp_end_point
            path = QPainterPath()
            path.moveTo(source_pos)
            dx = target_pos.x() - source_pos.x()
            control1 = QPointF(source_pos.x() + dx * 0.5, source_pos.y())
            control2 = QPointF(target_pos.x() - dx * 0.5, target_pos.y())
            path.cubicTo(control1, control2, target_pos)
            # Highlight on hover or selection
            if self.isSelected():
                pen = QPen(QColor(255, 255, 100), 4)
            elif self._hovered:
                pen = QPen(QColor(100, 255, 255), 4, Qt.DashLine)
            else:
                pen = QPen(QColor(200, 200, 200), 2)
            painter.setPen(pen)
            painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
            self._dragging = True
            self._drag_start_pos = event.scenePos()
            super().mousePressEvent(event)  # Let base class handle selection/hover
        elif event.button() == Qt.RightButton:
            # Right-click to select and delete connection safely
            self.setSelected(False)
            self.clearFocus()
            scene = self.scene()
            if hasattr(scene, 'delete_connection'):
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: scene.delete_connection(self))
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            scene = self.scene()
            if scene and hasattr(scene, 'start_connection'):
                scene.delete_connection(self)
                scene.start_connection(self.source_port)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_dragging'):
            self._dragging = False
        super().mouseReleaseEvent(event)  # Let base class handle selection/hover

    def set_temp_end_point(self, point: QPointF):
        self.temp_end_point = point
        self.update()

    def complete_connection(self, target_port):
        self.target_port = target_port
        target_port.connections.append(self)
        self.temp_end_point = None
        self.update()

    def get_connection_id(self) -> Optional[str]:
        if not self.source_port or not self.target_port:
            return None
        scene = self.scene()
        if not hasattr(scene, 'pipeline'):
            return None
        source_node_id = self.source_port.node_widget.process_node.id
        target_node_id = self.target_port.node_widget.process_node.id
        for conn_id, conn in scene.pipeline.connections.items():
            if (conn.source_node_id == source_node_id and \
                conn.source_port == self.source_port.name and
                conn.target_node_id == target_node_id and \
                conn.target_port == self.target_port.name):
                return conn_id
        return None

    def contains(self, point):
        # Use the custom shape for hit testing
        return self.shape().contains(point)
