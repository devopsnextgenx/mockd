"""
GUI components for the node graph editor using PySide6
"""
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QApplication,
                              QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                              QPushButton, QListWidget, QSplitter, QMenuBar,
                              QMenu, QToolBar, QStatusBar, QGraphicsProxyWidget,
                              QLineEdit, QLabel, QFrame, QTreeWidget, QTreeWidgetItem,
                              QMessageBox, QFileDialog, QDialog)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QTimer, QObject, QEvent
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QAction, QPainterPath
from typing import Dict, List, Optional, Tuple
import json

from src.core import ProcessNode, DataNode, Pipeline
from src.nodes import NODE_TYPES, create_node, get_all_node_types
from .ui_node_port import NodePort
from .ui_connection_widget import ConnectionWidget
from .ui_node_widget import NodeWidget

# Only import if the file exists, otherwise we'll create it
try:
    from .custom_node_dialog import CustomNodeDialog
except ImportError:
    CustomNodeDialog = None


class NodeGraphScene(QGraphicsScene):
    """Scene for managing the node graph"""
    
    node_added = Signal(str)  # Signal emitted when a node is added
    connection_created = Signal(str, str, str, str)  # source_node, source_port, target_node, target_port
    
    def __init__(self, pipeline: Pipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.node_widgets: Dict[str, NodeWidget] = {}
        self.connection_widgets: Dict[str, ConnectionWidget] = {}
        
        # Connection creation state
        self.creating_connection = False
        self.temp_connection = None
        
        # Scene styling
        self.setBackgroundBrush(QBrush(QColor(40, 40, 40)))
    
    def add_node(self, node_type: str, position: Tuple[float, float] = (0, 0)) -> str:
        """Add a new node to the scene"""
        try:
            if node_type == "custom":
                return self.add_custom_node(position)
            elif node_type.startswith("custom_"):
                # Handle existing custom node types
                from .custom_nodes import custom_node_manager
                custom_node = custom_node_manager.create_custom_node(node_type)
                custom_node.position = position
                
                # Add to pipeline
                node_id = self.pipeline.add_node(custom_node)
                
                # Create visual representation
                node_widget = NodeWidget(custom_node)
                node_widget.setPos(position[0], position[1])
                self.addItem(node_widget)
                self.node_widgets[node_id] = node_widget
                
                self.node_added.emit(node_id)
                return node_id
            else:
                process_node = create_node(node_type)
                
                if process_node is None:
                    print(f"ERROR: create_node returned None for type: {node_type}")
                    return ""
                
                process_node.position = position
                
                # Add to pipeline
                node_id = self.pipeline.add_node(process_node)
                
                # Create visual representation
                node_widget = NodeWidget(process_node)
                
                # Debug the widget before positioning
                
                # Force the widget to calculate its size
                node_widget.prepareGeometryChange()
                
                # Set position and add to scene  
                node_widget.setPos(position[0], position[1])
                
                self.addItem(node_widget)
                
                # Store reference
                self.node_widgets[node_id] = node_widget
                
                # Make sure the widget is visible and has proper size
                node_widget.setVisible(True)
                node_widget.show()
                
                # Force geometry update
                node_widget.update()
                
                # Debug the widget after adding to scene
                widget_rect = node_widget.boundingRect()
                
                # If the widget has zero size, there's a problem with NodeWidget
                if widget_rect.width() == 0 or widget_rect.height() == 0:
                    print("ERROR: NodeWidget has zero size! Check ui_node_widget.py implementation")
                    # Set a minimum fallback size for debugging
                    fallback_rect = QRectF(0, 0, 120, 80)
                    widget_rect = fallback_rect
                
                # Update scene rect to include the widget
                widget_scene_rect = QRectF(
                    position[0], position[1], 
                    widget_rect.width(), widget_rect.height()
                )
                
                current_scene_rect = self.sceneRect()
                new_scene_rect = current_scene_rect.united(widget_scene_rect)
                
                # Ensure minimum scene size
                min_width = max(new_scene_rect.width(), 2000)
                min_height = max(new_scene_rect.height(), 2000)
                
                # Ensure the widget is within the scene bounds
                if new_scene_rect.width() < 2000 or new_scene_rect.height() < 2000:
                    center_x = position[0]
                    center_y = position[1]
                    new_scene_rect = QRectF(
                        center_x - min_width/2, center_y - min_height/2,
                        min_width, min_height
                    )
                
                self.setSceneRect(new_scene_rect)
                
                # Force scene update
                self.update()
                
                # Center the view on the new node
                if self.views():
                    view = self.views()[0]
                    view.centerOn(node_widget)
                
                # Emit signal
                self.node_added.emit(node_id)
                
                # Print final debug info
                return node_id
        except Exception as e:
            print(f"Failed to create node: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def remove_node(self, node_id: str):
        """Remove a node from the scene"""
        if node_id in self.node_widgets:
            node_widget = self.node_widgets[node_id]
            
            # Remove all connections
            connections_to_remove = []
            for port in list(node_widget.input_ports.values()) + list(node_widget.output_ports.values()):
                for connection in port.connections[:]:
                    connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                self.removeItem(connection)
            
            # Remove from scene and pipeline
            self.removeItem(node_widget)
            del self.node_widgets[node_id]
            self.pipeline.remove_node(node_id)
    
    def start_connection(self, source_port: NodePort):
        """Start creating a connection from a port"""
        if source_port.is_input:
            return  # Can only start connections from output ports
        
        self.creating_connection = True
        self.temp_connection = ConnectionWidget(source_port)
        self.addItem(self.temp_connection)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for connection creation"""
        if self.creating_connection and self.temp_connection:
            self.temp_connection.set_temp_end_point(event.scenePos())
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if self.creating_connection and event.button() == Qt.LeftButton:
            # Check if we clicked on an input port
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            if isinstance(item, NodePort) and item.is_input:
                # Complete the connection
                source_port = self.temp_connection.source_port
                target_port = item
                
                # Validate connection
                if source_port.node_widget != target_port.node_widget:
                    self.temp_connection.complete_connection(target_port)
                    
                    # Create connection in pipeline
                    source_node_id = source_port.node_widget.process_node.id
                    target_node_id = target_port.node_widget.process_node.id
                    
                    connection_id = self.pipeline.connect_nodes(
                        source_node_id, source_port.name,
                        target_node_id, target_port.name
                    )
                    
                    if connection_id:
                        self.connection_widgets[connection_id] = self.temp_connection
                        self.connection_created.emit(
                            source_node_id, source_port.name,
                            target_node_id, target_port.name
                        )
                    else:
                        self.removeItem(self.temp_connection)
                else:
                    self.removeItem(self.temp_connection)
            else:
                # Cancel connection
                self.removeItem(self.temp_connection)
            
            self.creating_connection = False
            self.temp_connection = None
        
        super().mousePressEvent(event)
    
    def delete_connection(self, connection_widget: ConnectionWidget):
        """Delete a connection"""
        if not connection_widget.source_port or not connection_widget.target_port:
            return
        connection_id = connection_widget.get_connection_id()
        if connection_id:
            self.pipeline.remove_connection(connection_id)
            if connection_id in self.connection_widgets:
                del self.connection_widgets[connection_id]
        # Remove from ports' connection lists
        if connection_widget in connection_widget.source_port.connections:
            connection_widget.source_port.connections.remove(connection_widget)
        if connection_widget in connection_widget.target_port.connections:
            connection_widget.target_port.connections.remove(connection_widget)
        
        # Ensure the connection widget releases the mouse before deletion
        connection_widget.ungrabMouse()
        
        self.removeItem(connection_widget)

    def keyPressEvent(self, event):
        """Handle delete key for selected items (connections/nodes)"""
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, ConnectionWidget):
                    print(f"Deleting connection: {item.get_connection_id()}")
                    self.delete_connection(item)
                elif isinstance(item, NodeWidget):
                    for node_id, node_widget in self.node_widgets.items():
                        if node_widget == item:
                            self.remove_node(node_id)
                            break
            return  # Prevent base class from interfering with deletion
        super().keyPressEvent(event)
    
    def add_custom_node(self, position: Tuple[float, float] = (0, 0)) -> str:
        """Add a new custom node to the scene"""
        if CustomNodeDialog is None:
            QMessageBox.warning(None, "Error", "Custom node dialog not available. Please create custom_node_dialog.py first.")
            return ""
            
        dialog = CustomNodeDialog(self.parent())
        dialog.node_created.connect(self.on_custom_node_created)
        
        if dialog.exec() == QDialog.Accepted:
            # The node will be created via the signal
            pass
        
        return ""
    
    def on_custom_node_created(self, node_name: str, definition: dict):
        """Handle custom node creation"""
        try:
            # Save the custom node definition
            from .custom_nodes import custom_node_manager
            custom_node_manager.save_custom_node(node_name, definition)
            
            # Create a custom node instance
            from .custom_nodes import CustomNode
            custom_node = CustomNode(definition)
            custom_node.position = (100, 100)
            
            # Add to pipeline
            node_id = self.pipeline.add_node(custom_node)
            
            # Create visual representation
            node_widget = NodeWidget(custom_node)
            node_widget.setPos(100, 100)
            self.addItem(node_widget)
            self.node_widgets[node_id] = node_widget
            
            self.node_added.emit(node_id)
            
            # Refresh the node palette to show the new custom node
            if hasattr(self.parent(), 'refresh_node_palette'):
                self.parent().refresh_node_palette()
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create custom node: {e}")
            import traceback
            traceback.print_exc()


class NodeGraphView(QGraphicsView):
    """View for the node graph scene with pan and zoom"""
    
    def __init__(self, scene: NodeGraphScene, parent=None):
        super().__init__(scene, parent)
        
        # View settings
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Enable wheel zoom
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Set initial scene rect to ensure visibility
        self.setSceneRect(-1000, -1000, 2000, 2000)
    
    def center_on_point(self, point: QPointF):
        """Center the view on a specific point"""
        self.centerOn(point)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        # Set zoom factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        # Scale the view
        self.scale(zoom_factor, zoom_factor)


class NodePalette(QWidget):
    """Widget for selecting and adding nodes"""
    
    node_requested = Signal(str, tuple)  # node_type, position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Node Palette")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)
        
        # Custom node button
        create_custom_btn = QPushButton("Create Custom Node")
        create_custom_btn.clicked.connect(self.create_custom_node)
        create_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(create_custom_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_palette)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(refresh_btn)
        
        # Node categories
        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderHidden(True)
        
        self.populate_node_tree()
        
        self.node_tree.expandAll()
        self.node_tree.itemDoubleClicked.connect(self.on_node_double_clicked)
        
        layout.addWidget(self.node_tree)
    
    def populate_node_tree(self):
        """Populate the node tree with all available nodes"""
        self.node_tree.clear()
        
        # Populate with available node types
        categories = {
            "Data": ["data", "array", "true", "false"],
            "Math": {
                "math": ["math_add", "math_subtract", "math_multiply", "math_divide"],
                "Transform": ["transform_square", "transform_sqrt", "transform_abs", "transform_normalize"],
                "Aggregate": ["aggregate_sum", "aggregate_mean", "aggregate_min", "aggregate_max"],
            },
            "Utility": {
                "Filter": ["filter", "join", "split", "print"],
            },
            "Mock Data": {
                "Basic": [
                    "mock", "mock_text", "mock_word", "mock_sentence"
                ],
                "Personal": [
                    "mock_first_names", "mock_last_names", "mock_full_names", 
                    "mock_emails", "mock_phones", "mock_ages"
                ],
                "Numbers": [
                    "mock_integers", "mock_floats", "mock_booleans"
                ],
                "Dates": [
                    "mock_dates", "mock_datetimes"
                ],
                "Address": [
                    "mock_addresses", "mock_cities", "mock_countries", "mock_zipcodes"
                ],
                "Internet": [
                    "mock_urls", "mock_usernames", "mock_passwords"
                ],
                "Tech": [
                    "mock_uuids", "mock_programming_languages", "mock_databases", "mock_operating_systems"
                ]
            }
        }
        
        for category, nodes in categories.items():
            category_item = QTreeWidgetItem([category])
            
            # Handle nested categories (like Mock Data)
            if isinstance(nodes, dict):
                for subcategory, subnodes in nodes.items():
                    subcategory_item = QTreeWidgetItem([subcategory])
                    for node_type in subnodes:
                        # Create better display names for mock data nodes
                        if node_type.startswith("mock_"):
                            display_name = node_type.replace("mock_", "").replace("_", " ").title()
                            if node_type == "mock":
                                display_name = "Mock Data (Generic)"
                            else:
                                display_name = f"Mock {display_name}"
                        else:
                            display_name = node_type.replace("_", " ").title()
                        
                        node_item = QTreeWidgetItem([display_name])
                        node_item.setData(0, Qt.UserRole, node_type)
                        subcategory_item.addChild(node_item)
                    category_item.addChild(subcategory_item)
            else:
                # Handle flat categories
                for node_type in nodes:
                    # Create better display names for mock data nodes
                    if node_type.startswith("mock_"):
                        display_name = node_type.replace("mock_", "").replace("_", " ").title()
                        if node_type == "mock":
                            display_name = "Mock Data (Generic)"
                        else:
                            display_name = f"Mock {display_name}"
                    else:
                        display_name = node_type.replace("_", " ").title()
                    
                    node_item = QTreeWidgetItem([display_name])
                    node_item.setData(0, Qt.UserRole, node_type)
                    category_item.addChild(node_item)
            
            self.node_tree.addTopLevelItem(category_item)
        
        # Add Custom Nodes category
        self.add_custom_nodes_category()
    
    def add_custom_nodes_category(self):
        """Add custom nodes to the palette"""
        try:
            from .custom_nodes import custom_node_manager
            custom_node_types = custom_node_manager.get_custom_node_types()
            
            if custom_node_types:
                custom_category_item = QTreeWidgetItem(["Custom Nodes"])
                for node_name in custom_node_types:
                    display_name = node_name
                    node_item = QTreeWidgetItem([display_name])
                    node_item.setData(0, Qt.UserRole, f"custom_{node_name}")
                    custom_category_item.addChild(node_item)
                self.node_tree.addTopLevelItem(custom_category_item)
        except Exception as e:
            print(f"Error loading custom nodes: {e}")
    
    def refresh_palette(self):
        """Refresh the node palette"""
        self.populate_node_tree()
        self.node_tree.expandAll()
    
    def on_node_double_clicked(self, item, column):
        """Handle double-click on node type"""
        node_type = item.data(0, Qt.UserRole)
        if node_type:
            # Emit signal to create node at the center of the view
            self.node_requested.emit(node_type, (0, 0))

    def create_custom_node(self):
        """Create a new custom node"""
        self.node_requested.emit("custom", (0, 0))


class PropertyPanel(QWidget):
    """Panel for editing node properties"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)
        
        # Properties area (will be populated dynamically)
        self.properties_frame = QFrame()
        layout.addWidget(self.properties_frame)
        
        layout.addStretch()
    
    def set_node(self, node_widget: NodeWidget):
        """Set the current node for property editing"""
        self.current_node = node_widget
        self.update_properties()
    
    def update_properties(self):
        """Update the properties display"""
        # Clear existing properties
        if self.properties_frame.layout():
            layout = self.properties_frame.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout(self.properties_frame)
        
        if self.current_node:
            node = self.current_node.process_node
            
            # Node name
            name_label = QLabel("Name:")
            name_edit = QLineEdit(node.name)
            layout.addWidget(name_label)
            layout.addWidget(name_edit)
            
            # Node type
            type_label = QLabel(f"Type: {type(node).__name__}")
            layout.addWidget(type_label)
            
            # Custom node editing
            if hasattr(node, 'definition') and hasattr(node, 'is_custom_node'):
                edit_custom_btn = QPushButton("Edit Custom Node")
                edit_custom_btn.clicked.connect(self.edit_custom_node)
                layout.addWidget(edit_custom_btn)
            
            # Special properties for DataNode
            if isinstance(node, DataNode):
                data_label = QLabel("Data:")
                data_edit = QLineEdit(str(node.data) if node.data is not None else "")
                layout.addWidget(data_label)
                layout.addWidget(data_edit)
                
                def update_data():
                    try:
                        # Try to evaluate as Python expression
                        data = eval(data_edit.text()) if data_edit.text() else None
                        node.set_data(data)
                    except:
                        # If evaluation fails, store as string
                        node.set_data(data_edit.text())
                
                data_edit.textChanged.connect(update_data)
            else:
                # Generic properties for other node types
                for prop_name, prop_value in node.properties.items():
                    label = QLabel(f"{prop_name.capitalize()}:")
                    value_edit = QLineEdit(str(prop_value))
                    layout.addWidget(label)
                    layout.addWidget(value_edit)
        
        # Update the layout
        self.properties_frame.setLayout(layout)
    
    def edit_custom_node(self):
        """Edit the current custom node"""
        if CustomNodeDialog is None:
            QMessageBox.warning(self, "Error", "Custom node dialog not available.")
            return
            
        if self.current_node and hasattr(self.current_node.process_node, 'definition'):
            node = self.current_node.process_node
            dialog = CustomNodeDialog(self, node.definition)
            dialog.node_created.connect(lambda name, definition: self.update_custom_node(node, definition))
            dialog.exec()
    
    def update_custom_node(self, node, definition):
        """Update a custom node with new definition"""
        node.update_definition(definition)
        self.update_properties()
        
        # Update the visual representation
        if hasattr(self.current_node, 'update_from_definition'):
            self.current_node.update_from_definition()


class Pipeline:
    # ...existing code...
    def execute(self):
        """Execute the pipeline and return results."""
        results = {}
        for node_id, node in self.nodes.items():
            try:
                result = node.execute()
                results[node_id] = {
                    "name": node.name,
                    "result": result
                }
            except Exception as e:
                results[node_id] = {
                    "name": node.name,
                    "error": str(e)
                }
        return results
    # ...existing code...

class ProcessNode:
    # ...existing code...
    def __init__(self):
        self.properties = {}  # Ensure all nodes have a 'properties' attribute
    # ...existing code...

class AggregateNode(ProcessNode):
    def __init__(self):
        super().__init__()
        # Initialize specific properties for AggregateNode
        self.properties = {"operation": "sum"}

class TransformNode(ProcessNode):
    def __init__(self):
        super().__init__()
        # Initialize specific properties for TransformNode
        self.properties = {"transform_type": "square"}

class NodeEditEventFilter(QObject):
    def __init__(self, finish_callback):
        super().__init__()
        self.finish_callback = finish_callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.finish_callback()
                return True  # Stop further processing
        elif event.type() == QEvent.FocusOut:
            # Only finish editing if the QLineEdit is not being destroyed
            if obj.isVisible():
                self.finish_callback()
            return False  # Let the event propagate
        return False
