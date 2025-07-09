from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget, QLineEdit, QGraphicsItem, QGraphicsWidget, QPushButton
from PySide6.QtGui import QBrush, QColor, QPen, QFont, QPainter
from PySide6.QtCore import Qt, QObject, QRectF
from typing import Dict
from .ui_node_port import NodePort
from .ui_connection_widget import ConnectionWidget

class NodeWidget(QGraphicsRectItem):
    """Visual representation of a process node"""
    def __init__(self, process_node, parent=None):
        super().__init__(parent)
        self.process_node = process_node
        
        # Connect process_node's data_changed signal to update_node if it exists
        if hasattr(self.process_node, 'data_changed'):
            self.process_node.data_changed.connect(self.update_node)
            
        self.input_ports: Dict[str, NodePort] = {}
        self.output_ports: Dict[str, NodePort] = {}
        
        # Set initial size - this is crucial!
        self.node_width = 150
        self.node_height = 100
        self.setRect(0, 0, self.node_width, self.node_height)
        
        # Set appearance
        self.setBrush(QBrush(QColor(80, 80, 80)))
        self.setPen(QPen(QColor(200, 200, 200), 2))
        
        # Set flags for interaction
        self.setFlags(
            QGraphicsRectItem.ItemIsMovable | 
            QGraphicsRectItem.ItemIsSelectable | 
            QGraphicsRectItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        
        # Hover effects
        self._default_pen = QPen(QColor(200, 200, 200), 2)
        self._hover_pen = QPen(QColor(100, 255, 255), 4, Qt.DashLine)
        self.setPen(self._default_pen)
        
        # Create title
        self.title = QGraphicsTextItem(process_node.name, self)
        self.title.setPos(10, 5)
        self.title.setDefaultTextColor(QColor(255, 255, 255))
        font = QFont()
        font.setBold(True)
        self.title.setFont(font)
        
        # Initialize properties
        self.properties_labels = {}
        self.editing = False
        
        # Create ports and setup UI
        self.create_ports()
        self.show_properties_on_card()
        
        # Set initial position
        if hasattr(process_node, 'position'):
            self.setPos(process_node.position[0], process_node.position[1])

    def boundingRect(self):
        """Return the bounding rectangle of the widget"""
        return QRectF(0, 0, self.node_width, self.node_height)

    def paint(self, painter, option, widget):
        """Paint the node widget"""
        # Let the parent QGraphicsRectItem handle the painting
        super().paint(painter, option, widget)

    def create_ports(self):
        """Create input and output ports"""
        if not hasattr(self.process_node, 'input_ports') or not hasattr(self.process_node, 'output_ports'):
            print(f"Warning: ProcessNode {self.process_node.name} missing input_ports or output_ports")
            return
            
        y_offset = 30
        
        # Create input ports
        for i, (name, port) in enumerate(self.process_node.input_ports.items()):
            port_widget = NodePort(name, True, self, self)
            port_widget.setPos(-6, y_offset + i * 20)
            self.input_ports[name] = port_widget
            
            # Create label for input port
            label = QGraphicsTextItem(name, self)
            label.setPos(15, y_offset + i * 20 - 8)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Arial", 8))
        
        # Create output ports
        for i, (name, port) in enumerate(self.process_node.output_ports.items()):
            port_widget = NodePort(name, False, self, self)
            port_widget.setPos(self.node_width + 6, y_offset + i * 20)
            self.output_ports[name] = port_widget
            
            # Create label for output port
            label = QGraphicsTextItem(name, self)
            label.setPos(self.node_width - 35, y_offset + i * 20 - 8)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Arial", 8))

    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update process node position
            if hasattr(self.process_node, 'position'):
                self.process_node.position = (self.x(), self.y())
            
            # Update port positions
            for port in self.input_ports.values():
                if hasattr(port, 'update_position'):
                    port.update_position()
            for port in self.output_ports.values():
                if hasattr(port, 'update_position'):
                    port.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.RightButton:
            self.context_menu_event(event)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to start editing"""
        self.start_editing()
        event.accept()

    def context_menu_event(self, event):
        """Handle context menu - to be implemented"""
        pass

    def show_properties_on_card(self):
        """Display node properties on the card"""
        # Remove old property labels
        for label in getattr(self, 'properties_labels', {}).values():
            if isinstance(label, (QGraphicsTextItem, QGraphicsProxyWidget)):
                if hasattr(label, 'setParentItem'):
                    label.setParentItem(None)
        self.properties_labels = {}
        
        y_offset = 55
        
        # Show input ports as label/value pairs
        if hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for i, (port_name, port) in enumerate(self.process_node.input_ports.items()):
                # Property name label
                label = QGraphicsTextItem(f"{port_name}: ", self)
                label.setPos(10, y_offset + i * 22)
                label.setDefaultTextColor(QColor(220, 220, 220))
                label.setFont(QFont("Arial", 8))
                
                # Property value label
                value_text = str(getattr(port, 'value', ''))
                value_label = QGraphicsTextItem(value_text, self)
                value_label.setPos(70, y_offset + i * 22)
                value_label.setDefaultTextColor(QColor(255, 255, 180))
                value_label.setFont(QFont("Arial", 8))
                
                self.properties_labels[port_name] = (label, value_label)
        
        self.adjust_card_size_for_properties()

    def start_editing(self):
        """Start editing mode for properties"""
        if self.editing:
            return
        self.editing = True
        
        # Remove old property labels
        for label_pair in self.properties_labels.values():
            for label in label_pair:
                if hasattr(label, 'setParentItem'):
                    label.setParentItem(None)
        
        self.properties_labels = {}
        self.edit_proxies = {}
        y_offset = 55
        
        if hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for i, (port_name, port) in enumerate(self.process_node.input_ports.items()):
                # Property name label
                label = QGraphicsTextItem(f"{port_name}: ", self)
                label.setPos(10, y_offset + i * 22)
                label.setDefaultTextColor(QColor(220, 220, 220))
                label.setFont(QFont("Arial", 8))
                
                # Property value editor
                current_value = str(getattr(port, 'value', ''))
                editor = QLineEdit(current_value)
                proxy = QGraphicsProxyWidget(self)
                proxy.setWidget(editor)
                proxy.setPos(70, y_offset + i * 22 - 2)
                
                # Connect editor signals
                editor.editingFinished.connect(
                    lambda port_name=port_name, proxy=proxy: self.update_property_with_proxy(proxy, port_name)
                )
                
                self.properties_labels[port_name] = (label, proxy)
                self.edit_proxies[port_name] = editor
        
        self.adjust_card_size_for_properties()

    def finish_editing(self):
        """Finish editing mode"""
        if not self.editing:
            return
        
        # Remove proxy widgets
        for prop, (label, proxy) in self.properties_labels.items():
            if isinstance(proxy, QGraphicsProxyWidget):
                proxy.setWidget(None)
                proxy.setParentItem(None)
        
        self.editing = False
        self.show_properties_on_card()

    def update_property_with_proxy(self, proxy_widget, property_name):
        """Update property value from proxy widget"""
        if not self.editing:
            return
        
        editor = proxy_widget.widget()
        if editor:
            self.update_property(property_name, editor.text())
        self.finish_editing()

    def update_property(self, property_name, value):
        """Update a property value"""
        if hasattr(self.process_node, 'set_input_value'):
            self.process_node.set_input_value(property_name, value)
        
        # Also update output if it's a DataNode
        if hasattr(self.process_node, 'output_ports') and property_name in getattr(self.process_node, 'output_ports', {}):
            if hasattr(self.process_node, 'set_output_value'):
                self.process_node.set_output_value(property_name, value)
        
        self.refresh()

    def adjust_card_size_for_properties(self):
        """Adjust card size to fit properties"""
        if not hasattr(self.process_node, 'input_ports'):
            return
            
        num_props = len(self.process_node.input_ports)
        min_height = 100
        prop_height = 22 * num_props + 55
        new_height = max(min_height, prop_height)
        
        # Update node dimensions
        self.node_height = new_height
        self.setRect(0, 0, self.node_width, self.node_height)

    def refresh(self):
        """Refresh the widget display"""
        if self.editing:
            self.start_editing()
        else:
            self.show_properties_on_card()

    def update_node(self):
        """Update node display when data changes"""
        self.refresh()

    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self.setPen(self._hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        self.setPen(self._default_pen)
        super().hoverLeaveEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out"""
        self.finish_editing()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.finish_editing()
            return
        super().keyPressEvent(event)
