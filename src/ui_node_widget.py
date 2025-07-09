from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget, QLineEdit, QGraphicsItem
from PySide6.QtGui import QBrush, QColor, QPen, QFont
from PySide6.QtCore import Qt, QObject
from typing import Dict
from .ui_node_port import NodePort
from .ui_connection_widget import ConnectionWidget

class NodeWidget(QObject, QGraphicsRectItem):
    """Visual representation of a process node"""
    def __init__(self, process_node, parent=None):
        QObject.__init__(self)
        QGraphicsRectItem.__init__(self, parent)
        self.process_node = process_node
        # Connect process_node's data_changed signal to update_node if it exists
        if hasattr(self.process_node, 'data_changed'):
            self.process_node.data_changed.connect(self.update_node)
        self.input_ports: Dict[str, NodePort] = {}
        self.output_ports: Dict[str, NodePort] = {}
        self.setRect(0, 0, 150, 100)
        self.setBrush(QBrush(QColor(80, 80, 80)))
        self.setPen(QPen(QColor(200, 200, 200), 2))
        self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable | QGraphicsRectItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)  # Enable hover events
        self._default_pen = QPen(QColor(200, 200, 200), 2)
        self._hover_pen = QPen(QColor(100, 255, 255), 4, Qt.DashLine)
        self.setPen(self._default_pen)
        self.title = QGraphicsTextItem(process_node.name, self)
        self.title.setPos(10, 5)
        self.title.setDefaultTextColor(QColor(255, 255, 255))
        font = QFont()
        font.setBold(True)
        self.title.setFont(font)
        self.create_ports()
        self.setPos(process_node.position[0], process_node.position[1])
        self.properties_labels = {}
        self.editing = False
        self.show_properties_on_card()

    def create_ports(self):
        y_offset = 30
        for i, (name, port) in enumerate(self.process_node.input_ports.items()):
            port_widget = NodePort(name, True, self, self)
            port_widget.setPos(-6, y_offset + i * 20)
            self.input_ports[name] = port_widget
            label = QGraphicsTextItem(name, self)
            label.setPos(15, y_offset + i * 20 - 8)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Arial", 8))
        for i, (name, port) in enumerate(self.process_node.output_ports.items()):
            port_widget = NodePort(name, False, self, self)
            port_widget.setPos(156, y_offset + i * 20)
            self.output_ports[name] = port_widget
            label = QGraphicsTextItem(name, self)
            label.setPos(125, y_offset + i * 20 - 8)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Arial", 8))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.process_node.position = (self.x(), self.y())
            for port in self.input_ports.values():
                port.update_position()
            for port in self.output_ports.values():
                port.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.context_menu_event(event)
        super().mousePressEvent(event)

    def context_menu_event(self, event):
        # Implement context menu for the node
        pass

    def show_properties_on_card(self):
        # Remove old property labels and editors
        for label in getattr(self, 'properties_labels', {}).values():
            if isinstance(label, QGraphicsTextItem) or isinstance(label, QGraphicsProxyWidget):
                label.setParentItem(None)
        self.properties_labels = {}
        y_offset = 55
        # Show all input ports as label/value pairs
        if hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for i, (port_name, port) in enumerate(self.process_node.input_ports.items()):
                label = QGraphicsTextItem(f"{port_name}: ", self)
                label.setPos(10, y_offset + i * 22)
                label.setDefaultTextColor(QColor(220, 220, 220))
                label.setFont(QFont("Arial", 8))
                value_label = QGraphicsTextItem(str(port.value), self)
                value_label.setPos(70, y_offset + i * 22)
                value_label.setDefaultTextColor(QColor(255, 255, 180))
                value_label.setFont(QFont("Arial", 8))
                self.properties_labels[port_name] = (label, value_label)
        self.adjust_card_size_for_properties()

    def start_editing(self):
        if self.editing:
            return
        self.editing = True
        # Remove old property labels
        for label_pair in self.properties_labels.values():
            for label in label_pair:
                label.setParentItem(None)
        self.properties_labels = {}
        self.edit_proxies = {}
        y_offset = 55
        if hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for i, (port_name, port) in enumerate(self.process_node.input_ports.items()):
                label = QGraphicsTextItem(f"{port_name}: ", self)
                label.setPos(10, y_offset + i * 22)
                label.setDefaultTextColor(QColor(220, 220, 220))
                label.setFont(QFont("Arial", 8))
                editor = QLineEdit(str(port.value))
                proxy = QGraphicsProxyWidget(self)
                proxy.setWidget(editor)
                proxy.setPos(70, y_offset + i * 22 - 2)
                proxy.setMinimumWidth(60)
                editor.installEventFilter(self)
                editor.editingFinished.connect(lambda port_name=port_name, proxy=proxy: self.update_property_with_proxy(proxy, port_name))
                self.properties_labels[port_name] = (label, proxy)
                self.edit_proxies[port_name] = editor
        self.adjust_card_size_for_properties()
        # Focus first editor
        if hasattr(self, 'edit_proxies') and self.edit_proxies:
            first_editor = next(iter(self.edit_proxies.values()))
            first_editor.setFocus()

    def finish_editing(self):
        if not self.editing:
            return
        # Remove all QGraphicsProxyWidget editors
        for prop, (label, proxy) in self.properties_labels.items():
            if isinstance(proxy, QGraphicsProxyWidget):
                proxy.setWidget(None)
                proxy.setParentItem(None)
        self.editing = False
        self.show_properties_on_card()

    def update_property_with_proxy(self, proxy_widget, property_name):
        if not self.editing:
            return
        editor = proxy_widget.widget()
        if editor:
            self.update_property(property_name, editor.text())
        self.finish_editing()

    def adjust_card_size_for_properties(self):
        # Adjust the card size to fit all properties
        num_props = len(getattr(self.process_node, 'inputs', {}))
        min_height = 100
        prop_height = 22 * num_props + 55
        height = max(min_height, prop_height)
        self.setRect(0, 0, 150, height)

    def eventFilter(self, source, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.FocusOut:
            # Only finish editing if focus is not moving to another editor in this card
            next_focus = source.focusWidget()
            if next_focus in getattr(self, 'edit_proxies', {}).values():
                return False  # Don't finish editing if focus is moving to another editor
            # Find which property this editor is for
            for prop, editor in getattr(self, 'edit_proxies', {}).items():
                if source is editor:
                    self.update_property(prop, editor.text())
                    self.finish_editing()
                    break
            return True  # Always finish editing and revert to label/value
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.finish_editing()
            # Explicitly clear focus from all editors
            for editor in getattr(self, 'edit_proxies', {}).values():
                editor.clearFocus()
            return True
        return super().eventFilter(source, event)

    def update_property(self, property_name, value):
        # Update the process_node input port value and refresh
        if hasattr(self.process_node, 'set_input_value'):
            self.process_node.set_input_value(property_name, value)
        # If DataNode, also update output
        if hasattr(self.process_node, 'output_ports') and property_name in getattr(self.process_node, 'output_ports', {}):
            self.process_node.set_output_value(property_name, value)
        self.refresh()

    def refresh(self):
        if self.editing:
            self.start_editing()
        else:
            self.show_properties_on_card()

    def set_process_node(self, process_node):
        self.process_node = process_node
        self.title.setPlainText(process_node.name)
        self.setPos(process_node.position[0], process_node.position[1])
        self.refresh()

    def deselect(self):
        # Implement deselect logic
        pass

    def update_node(self):
        self.refresh()

    def mouseDoubleClickEvent(self, event):
        self.start_editing()
        event.accept()

    def keyPressEvent(self, event):
        # Prevent Delete key from deleting the widget while editing
        if self.editing and event.key() == Qt.Key_Delete:
            # Propagate to focused child (e.g., QLineEdit)
            focus_item = self.scene().focusItem()
            if focus_item and focus_item is not self:
                # Send event to the focused child
                focus_item.keyPressEvent(event)
                return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.finish_editing()
        super().focusOutEvent(event)

    def hoverEnterEvent(self, event):
        self.setPen(self._hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(self._default_pen)
        super().hoverLeaveEvent(event)
