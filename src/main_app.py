"""
Main application window for the Node Graph Editor
"""
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                              QWidget, QPushButton, QSplitter, QMenuBar, QMenu, 
                              QToolBar, QStatusBar, QFileDialog, QMessageBox,
                              QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
                              QTextEdit, QLabel)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QKeySequence
import json
import sys
import os

from src.core import Pipeline, DataNode
from src.gui import NodeGraphScene, NodeGraphView, NodePalette, PropertyPanel
from src.nodes import create_node


class NodeGraphEditor(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.pipeline = Pipeline("My Pipeline")
        self.current_file = None
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds
    
    def setup_ui(self):
        """Setup the main UI layout"""
        self.setWindowTitle("Node Graph Pipeline Editor")
        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Node palette
        self.node_palette = NodePalette()
        self.node_palette.setMaximumWidth(250)
        splitter.addWidget(self.node_palette)

        # Center - Node graph view
        self.scene = NodeGraphScene(self.pipeline)
        self.view = NodeGraphView(self.scene)
        splitter.addWidget(self.view)

        # Right panel - Execution results (replaces property panel)
        self.execution_results = QTextEdit()
        self.execution_results.setReadOnly(True)
        self.execution_results.setMaximumWidth(350)
        self.execution_results.setMinimumWidth(250)
        self.execution_results.setStyleSheet("background: #222; color: #fff; font-family: monospace;")
        splitter.addWidget(self.execution_results)

        # Set splitter proportions
        splitter.setSizes([250, 700, 300])

        main_layout.addWidget(splitter)
    
    def setup_menus(self):
        """Setup application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_pipeline)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_pipeline)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_pipeline)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_pipeline_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        delete_action = QAction("Delete Selected", self)
        delete_action.setShortcut(Qt.Key_Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(self.clear_pipeline)
        edit_menu.addAction(clear_action)
        
        # Pipeline menu
        pipeline_menu = menubar.addMenu("Pipeline")
        
        execute_action = QAction("Execute Pipeline", self)
        execute_action.setShortcut(Qt.Key_F5)
        execute_action.triggered.connect(self.execute_pipeline)
        pipeline_menu.addAction(execute_action)
        
        validate_action = QAction("Validate Pipeline", self)
        validate_action.triggered.connect(self.validate_pipeline)
        pipeline_menu.addAction(validate_action)
    
    def setup_toolbar(self):
        """Setup application toolbar"""
        toolbar = self.addToolBar("Main")
        
        # Add common actions to toolbar
        toolbar.addAction("New", self.new_pipeline)
        toolbar.addAction("Open", self.open_pipeline)
        toolbar.addAction("Save", self.save_pipeline)
        toolbar.addSeparator()
        toolbar.addAction("Execute", self.execute_pipeline)
        toolbar.addAction("Validate", self.validate_pipeline)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def setup_connections(self):
        """Setup signal connections"""
        # Node palette connections
        self.node_palette.node_requested.connect(self.add_node)
        
        # Scene connections
        self.scene.node_added.connect(self.on_node_added)
        self.scene.connection_created.connect(self.on_connection_created)
        
        # Selection changes
        self.scene.selectionChanged.connect(self.on_selection_changed)
    
    def add_node(self, node_type: str, position: tuple):
        """Add a new node to the scene"""
        try:
            # Get click position in scene coordinates
            scene_pos = self.view.mapToScene(self.view.viewport().rect().center())
            actual_position = (scene_pos.x(), scene_pos.y())
            
            node_id = self.scene.add_node(node_type, actual_position)
            if node_id:
                self.status_bar.showMessage(f"Added {node_type} node")
                return node_id
        except Exception as e:
            self.status_bar.showMessage(f"Failed to add node: {e}")
            return None
    
    def on_node_added(self, node_id: str):
        """Handle node added to scene"""
        self.status_bar.showMessage(f"Node {node_id[:8]} added")
    
    def on_connection_created(self, source_node: str, source_port: str, 
                            target_node: str, target_port: str):
        """Handle connection created"""
        self.status_bar.showMessage(f"Connected {source_port} -> {target_port}")
    
    def on_selection_changed(self):
        """Handle selection changes"""
        # Do not show node properties in the right panel; all editing is on the card itself
        pass
    
    def delete_selected(self):
        """Delete selected nodes"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if hasattr(item, 'process_node'):
                node_id = item.process_node.id
                self.scene.remove_node(node_id)
                self.status_bar.showMessage(f"Deleted node {node_id[:8]}")
    
    def new_pipeline(self):
        """Create a new pipeline"""
        if self.confirm_unsaved_changes():
            self.pipeline = Pipeline("New Pipeline")
            self.scene.pipeline = self.pipeline
            self.scene.clear()
            self.scene.node_widgets.clear()
            self.scene.connection_widgets.clear()
            self.current_file = None
            self.status_bar.showMessage("New pipeline created")
    
    def open_pipeline(self):
        """Open a pipeline from file"""
        if not self.confirm_unsaved_changes():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Pipeline", "", "Pipeline Files (*.json)"
        )
        
        if file_path:
            try:
                self.load_pipeline(file_path)
                self.current_file = file_path
                self.status_bar.showMessage(f"Opened {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")
    
    def save_pipeline(self):
        """Save the current pipeline"""
        if self.current_file:
            try:
                self.save_pipeline_to_file(self.current_file)
                self.status_bar.showMessage(f"Saved {os.path.basename(self.current_file)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            self.save_pipeline_as()
    
    def save_pipeline_as(self):
        """Save the pipeline with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Pipeline", "", "Pipeline Files (*.json)"
        )
        
        if file_path:
            try:
                self.save_pipeline_to_file(file_path)
                self.current_file = file_path
                self.status_bar.showMessage(f"Saved as {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    
    def execute_pipeline(self):
        """Execute the current pipeline and show results in right panel"""
        try:
            self.status_bar.showMessage("Executing pipeline...")
            results = self.pipeline.execute()
            node_id_name_map = {nid: node.name for nid, node in self.pipeline.nodes.items()}
            formatted = self.format_execution_results(results, node_id_name_map)
            self.execution_results.setPlainText(formatted)
            self.status_bar.showMessage("Pipeline execution completed")
        except Exception as e:
            self.execution_results.setPlainText(f"Pipeline execution failed: {e}")
            self.status_bar.showMessage("Pipeline execution failed")

    def format_execution_results(self, results: dict, node_id_name_map: dict) -> str:
        formatted = []
        for node_id, result in results.items():
            node_name = node_id_name_map.get(node_id, "<unknown>")
            formatted.append(f"Node {node_id[:8]} ({node_name}):")
            formatted.append(f"  Success: {result['success']}")
            formatted.append(f"  Outputs: {result['outputs']}")
            formatted.append("")
        return "\n".join(formatted)
    
    def validate_pipeline(self):
        """Validate the current pipeline"""
        try:
            # Check for cycles, missing connections, etc.
            execution_order = self.pipeline.get_execution_order()
            
            if len(execution_order) == len(self.pipeline.nodes):
                QMessageBox.information(self, "Validation", "Pipeline is valid!")
                self.status_bar.showMessage("Pipeline validation passed")
            else:
                QMessageBox.warning(self, "Validation", 
                                  "Pipeline has issues (cycles or missing connections)")
                self.status_bar.showMessage("Pipeline validation failed")
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", f"Validation failed: {e}")
    
    def clear_pipeline(self):
        """Clear the entire pipeline"""
        if self.confirm_unsaved_changes():
            self.scene.clear()
            self.pipeline = Pipeline("Empty Pipeline")
            self.scene.pipeline = self.pipeline
            self.scene.node_widgets.clear()
            self.scene.connection_widgets.clear()
            self.status_bar.showMessage("Pipeline cleared")
    
    def auto_save(self):
        """Auto-save the current pipeline"""
        if self.current_file:
            try:
                self.save_pipeline_to_file(self.current_file)
                self.status_bar.showMessage("Auto-saved", 2000)
            except Exception:
                pass  # Silent fail for auto-save
    
    def confirm_unsaved_changes(self) -> bool:
        """Confirm if user wants to discard unsaved changes"""
        # For simplicity, always return True
        # In a real app, you'd check if there are unsaved changes
        return True
    
    def load_pipeline(self, file_path: str):
        """Load pipeline from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear current pipeline
        self.scene.clear()
        self.pipeline = Pipeline(data.get('name', 'Loaded Pipeline'))
        self.scene.pipeline = self.pipeline
        self.scene.node_widgets.clear()
        self.scene.connection_widgets.clear()
        
        # Load nodes
        nodes_data = data.get('nodes', [])
        node_id_mapping = {}  # Map old IDs to new IDs
        
        for node_data in nodes_data:
            node_type = node_data.get('type', 'data')
            position = tuple(node_data.get('position', [0, 0]))
            
            new_node_id = self.scene.add_node(node_type, position)
            if new_node_id:
                old_id = node_data.get('id')
                node_id_mapping[old_id] = new_node_id
                
                # Set node properties
                node = self.pipeline.nodes[new_node_id]
                if hasattr(node, 'set_data') and 'data' in node_data:
                    node.set_data(node_data['data'])
        
        # Load connections
        connections_data = data.get('connections', [])
        for conn_data in connections_data:
            old_source_id = conn_data.get('source_node')
            old_target_id = conn_data.get('target_node')
            
            if old_source_id in node_id_mapping and old_target_id in node_id_mapping:
                new_source_id = node_id_mapping[old_source_id]
                new_target_id = node_id_mapping[old_target_id]
                
                self.pipeline.connect_nodes(
                    new_source_id, conn_data.get('source_port', ''),
                    new_target_id, conn_data.get('target_port', '')
                )
    
    def save_pipeline_to_file(self, file_path: str):
        """Save pipeline to JSON file"""
        # Prepare data structure
        data = {
            'name': self.pipeline.name,
            'nodes': [],
            'connections': []
        }
        
        # Save nodes
        for node_id, node in self.pipeline.nodes.items():
            node_data = {
                'id': node_id,
                'type': type(node).__name__.lower().replace('node', ''),
                'name': node.name,
                'position': list(node.position)
            }
            
            # Save special properties
            if hasattr(node, 'data'):
                node_data['data'] = node.data
            
            data['nodes'].append(node_data)
        
        # Save connections
        for conn_id, conn in self.pipeline.connections.items():
            conn_data = {
                'id': conn_id,
                'source_node': conn.source_node_id,
                'source_port': conn.source_port,
                'target_node': conn.target_node_id,
                'target_port': conn.target_port
            }
            data['connections'].append(conn_data)
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.confirm_unsaved_changes():
            event.accept()
        else:
            event.ignore()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Node Graph Pipeline Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DevOpsNextGen")
    
    # Create and show main window
    window = NodeGraphEditor()
    window.show()
    
    # Create some example nodes
    data_node_id = window.add_node("array", (100, 100))
    if data_node_id:
        # Set some example data
        data_node = window.pipeline.nodes[data_node_id]
        if hasattr(data_node, 'set_data'):
            data_node.set_data([1, 2, 3, 4, 5])
    
    # window.add_node("transform_square", (300, 100))
    # window.add_node("aggregate_sum", (500, 100))
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
