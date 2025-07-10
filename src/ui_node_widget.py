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
        
        # Remove old QGraphicsTextItem title
        # self.title = QGraphicsTextItem(process_node.name, self)
        # self.title.setPos(10, 5)
        # self.title.setDefaultTextColor(QColor(255, 255, 255))
        # font = QFont()
        # font.setBold(True)
        # self.title.setFont(font)

        # Header height
        self.header_height = 28

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
        """Paint the node widget with a header/titlebar"""
        # Draw header/titlebar
        header_rect = QRectF(0, 0, self.node_width, self.header_height)
        painter.save()
        painter.setBrush(QColor(40, 40, 40))  # dark gray
        painter.setPen(Qt.NoPen)
        painter.drawRect(header_rect)

        # Draw title in red
        title = getattr(self.process_node, "name", "Node")
        node_id = getattr(self.process_node, "node_id", self.process_node.id.split('-')[0])
        title_text = f"{title} [{node_id}]"
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(220, 40, 40))  # red
        painter.drawText(header_rect.adjusted(10, 0, -10, 0), Qt.AlignVCenter | Qt.AlignLeft, title_text)
        painter.restore()

        # Draw the rest of the node (body)
        body_rect = QRectF(0, self.header_height, self.node_width, self.node_height - self.header_height)
        painter.save()
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRect(body_rect)
        painter.restore()

        # Draw border around the whole node
        painter.save()
        painter.setPen(self.pen())
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(0, 0, self.node_width, self.node_height))
        painter.restore()

    def create_ports(self):
        """Create input and output ports"""
        y_offset = self.header_height + 2  # move ports below header
        
        # Get input ports using input_names property
        input_names = getattr(self.process_node, 'input_names', [])
        input_ports = {}
        
        # Build input_ports dict from input_names
        if input_names:
            for name in input_names:
                # Try to get the actual port object if it exists
                if hasattr(self.process_node, 'input_ports') and name in self.process_node.input_ports:
                    input_ports[name] = self.process_node.input_ports[name]
                else:
                    # Create a placeholder port object if needed
                    input_ports[name] = type('Port', (), {'name': name, 'value': '', 'default_value': ''})()
        else:
            # Fallback to existing input_ports if input_names not available
            input_ports = getattr(self.process_node, 'input_ports', {})
        
        # Get output ports
        output_ports = getattr(self.process_node, 'output_ports', {})
        
        if not input_ports and not output_ports:
            print(f"Warning: Node {getattr(self.process_node, 'name', 'Unknown')} has no ports or properties")
            return
            
        # Create input ports
        for i, (name, port) in enumerate(input_ports.items()):
            port_widget = NodePort(name, True, self, self)
            port_widget.setPos(-6, y_offset + i * 20)
            self.input_ports[name] = port_widget

            # Create label for input port
            label = QGraphicsTextItem(name, self)
            label.setPos(15, y_offset + i * 20 - 8)
            label.setDefaultTextColor(QColor(200, 200, 200))
            label.setFont(QFont("Arial", 8))

        # Create output ports
        for i, (name, port) in enumerate(output_ports.items()):
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
            if isinstance(label, tuple):
                for item in label:
                    if isinstance(item, (QGraphicsTextItem, QGraphicsProxyWidget)):
                        if hasattr(item, 'setParentItem'):
                            item.setParentItem(None)
            elif isinstance(label, (QGraphicsTextItem, QGraphicsProxyWidget)):
                if hasattr(label, 'setParentItem'):
                    label.setParentItem(None)
        self.properties_labels = {}
        
        y_offset = self.header_height + 25  # move properties below header
        
        # Get properties to display using input_names
        properties_to_show = {}
        
        # Try input_names first
        input_names = getattr(self.process_node, 'input_names', [])
        if input_names:
            for port_name in input_names:
                value = ''
                # Try to get value from input_ports if it exists
                if hasattr(self.process_node, 'input_ports') and port_name in self.process_node.input_ports:
                    port = self.process_node.input_ports[port_name]
                    value = getattr(port, 'value', getattr(port, 'default_value', ''))
                # Try to get value from inputs
                elif hasattr(self.process_node, 'inputs') and port_name in self.process_node.inputs:
                    prop = self.process_node.inputs[port_name]
                    value = getattr(prop, 'value', getattr(prop, 'default_value', ''))
                # Try direct attribute access
                elif hasattr(self.process_node, port_name):
                    attr_value = getattr(self.process_node, port_name)
                    if not callable(attr_value):
                        value = str(attr_value)
                
                properties_to_show[port_name] = value
        # Fallback to existing logic if input_names not available
        elif hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for port_name, port in self.process_node.input_ports.items():
                value = getattr(port, 'value', getattr(port, 'default_value', ''))
                properties_to_show[port_name] = value
        # Try inputs
        elif hasattr(self.process_node, 'inputs') and self.process_node.inputs:
            for prop_name, prop in self.process_node.inputs.items():
                value = getattr(prop, 'value', getattr(prop, 'default_value', ''))
                properties_to_show[prop_name] = value
        # Try properties directly
        elif hasattr(self.process_node, 'properties') and self.process_node.properties:
            for prop_name, prop in self.process_node.properties.items():
                if isinstance(prop, dict):
                    value = prop.get('value', prop.get('default_value', ''))
                else:
                    value = getattr(prop, 'value', getattr(prop, 'default_value', str(prop)))
                properties_to_show[prop_name] = value
        # Fallback: try to get any attributes that look like properties
        else:
            for attr_name in dir(self.process_node):
                if not attr_name.startswith('_') and attr_name not in ['name', 'position', 'input_ports', 'output_ports']:
                    attr_value = getattr(self.process_node, attr_name)
                    if not callable(attr_value):
                        properties_to_show[attr_name] = str(attr_value)
        
        # Display properties
        for i, (prop_name, value) in enumerate(properties_to_show.items()):
            # Property name label
            label = QGraphicsTextItem(f"{prop_name}: ", self)
            label.setPos(10, y_offset + i * 22)
            label.setDefaultTextColor(QColor(220, 220, 220))
            label.setFont(QFont("Arial", 8))
            
            # Property value label
            value_text = str(value)
            value_label = QGraphicsTextItem(value_text, self)
            value_label.setPos(70, y_offset + i * 22)
            value_label.setDefaultTextColor(QColor(255, 255, 180))
            value_label.setFont(QFont("Arial", 8))
            
            self.properties_labels[prop_name] = (label, value_label)
        
        self.adjust_card_size_for_properties()

    def start_editing(self):
        """Start editing mode for properties"""
        if self.editing:
            return
        self.editing = True
        
        # Remove old property labels
        for label_pair in self.properties_labels.values():
            if isinstance(label_pair, tuple):
                for label in label_pair:
                    if hasattr(label, 'setParentItem'):
                        label.setParentItem(None)
            else:
                if hasattr(label_pair, 'setParentItem'):
                    label_pair.setParentItem(None)
        
        self.properties_labels = {}
        self.edit_proxies = {}
        y_offset = self.header_height + 25  # move editors below header
        
        # Get editable properties
        editable_properties = {}
        
        if hasattr(self.process_node, 'input_ports') and self.process_node.input_ports:
            for port_name, port in self.process_node.input_ports.items():
                value = getattr(port, 'value', getattr(port, 'default_value', ''))
                editable_properties[port_name] = value
        elif hasattr(self.process_node, 'inputs') and self.process_node.inputs:
            for prop_name, prop in self.process_node.inputs.items():
                value = getattr(prop, 'value', getattr(prop, 'default_value', ''))
                editable_properties[prop_name] = value
        elif hasattr(self.process_node, 'properties') and self.process_node.properties:
            for prop_name, prop in self.process_node.properties.items():
                if isinstance(prop, dict):
                    value = prop.get('value', prop.get('default_value', ''))
                else:
                    value = getattr(prop, 'value', getattr(prop, 'default_value', str(prop)))
                editable_properties[prop_name] = value
        
        for i, (prop_name, value) in enumerate(editable_properties.items()):
            # Property name label
            label = QGraphicsTextItem(f"{prop_name}: ", self)
            label.setPos(10, y_offset + i * 22)
            label.setDefaultTextColor(QColor(220, 220, 220))
            label.setFont(QFont("Arial", 8))
            
            # Property value editor
            current_value = str(value)
            editor = QLineEdit(current_value)
            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(editor)
            proxy.setPos(70, y_offset + i * 22 - 2)
            
            # Connect editor signals
            editor.editingFinished.connect(
                lambda prop_name=prop_name, proxy=proxy: self.update_property_with_proxy(proxy, prop_name)
            )
            
            self.properties_labels[prop_name] = (label, proxy)
            self.edit_proxies[prop_name] = editor
        
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
        # Try different methods to update the property
        updated = False
        
        # Try input_ports
        if hasattr(self.process_node, 'set_input_value'):
            try:
                self.process_node.set_input_value(property_name, value)
                updated = True
            except:
                pass
        elif hasattr(self.process_node, 'input_ports') and property_name in self.process_node.input_ports:
            if hasattr(self.process_node.input_ports[property_name], 'value'):
                self.process_node.input_ports[property_name].value = value
                updated = True
        
        # Try inputs
        elif hasattr(self.process_node, 'inputs') and property_name in self.process_node.inputs:
            if hasattr(self.process_node.inputs[property_name], 'value'):
                self.process_node.inputs[property_name].value = value
                updated = True
        
        # Try properties
        elif hasattr(self.process_node, 'properties') and property_name in self.process_node.properties:
            prop = self.process_node.properties[property_name]
            if isinstance(prop, dict):
                prop['value'] = value
                updated = True
            elif hasattr(prop, 'value'):
                prop.value = value
                updated = True
        
        # Try direct attribute setting as fallback
        if not updated:
            try:
                setattr(self.process_node, property_name, value)
                updated = True
            except:
                pass
        
        if updated:
            # Try to notify the process node of the change
            if hasattr(self.process_node, 'data_changed'):
                self.process_node.data_changed.emit()
        
        self.refresh()

    def adjust_card_size_for_properties(self):
        """Adjust card size to fit properties"""
        num_props = 0
        
        # Count properties from various sources
        if hasattr(self.process_node, 'input_ports'):
            num_props = len(self.process_node.input_ports)
        elif hasattr(self.process_node, 'inputs'):
            num_props = len(self.process_node.inputs)
        elif hasattr(self.process_node, 'properties'):
            num_props = len(self.process_node.properties)
        
        min_height = 100
        prop_height = 22 * num_props + self.header_height + 25
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
