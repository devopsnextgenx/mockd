"""
Dialog for creating custom nodes
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QLabel, QPushButton, QTextEdit, QListWidget, 
                              QListWidgetItem, QMessageBox, QFormLayout,
                              QGroupBox, QScrollArea, QWidget)
from PySide6.QtCore import Qt, Signal
from typing import Dict, List
import json

class CustomNodeDialog(QDialog):
    """Dialog for creating custom nodes"""
    
    node_created = Signal(str, dict)  # node_name, node_definition
    
    def __init__(self, parent=None, existing_definition=None):
        super().__init__(parent)
        self.existing_definition = existing_definition
        self.setup_ui()
        if existing_definition:
            self.load_definition(existing_definition)
    
    def setup_ui(self):
        self.setWindowTitle("Custom Node Creator")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Node name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Node Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter custom node name")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Main content in scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Input ports section
        inputs_group = QGroupBox("Input Ports")
        inputs_layout = QVBoxLayout(inputs_group)
        
        self.inputs_list = QListWidget()
        self.inputs_list.setMaximumHeight(100)
        inputs_layout.addWidget(self.inputs_list)
        
        input_controls = QHBoxLayout()
        self.input_name_edit = QLineEdit()
        self.input_name_edit.setPlaceholderText("Input port name")
        input_controls.addWidget(self.input_name_edit)
        
        add_input_btn = QPushButton("Add Input")
        add_input_btn.clicked.connect(self.add_input_port)
        input_controls.addWidget(add_input_btn)
        
        remove_input_btn = QPushButton("Remove Selected")
        remove_input_btn.clicked.connect(self.remove_input_port)
        input_controls.addWidget(remove_input_btn)
        
        inputs_layout.addLayout(input_controls)
        scroll_layout.addWidget(inputs_group)
        
        # Output ports section
        outputs_group = QGroupBox("Output Ports")
        outputs_layout = QVBoxLayout(outputs_group)
        
        self.outputs_list = QListWidget()
        self.outputs_list.setMaximumHeight(100)
        outputs_layout.addWidget(self.outputs_list)
        
        output_controls = QHBoxLayout()
        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("Output port name")
        output_controls.addWidget(self.output_name_edit)
        
        add_output_btn = QPushButton("Add Output")
        add_output_btn.clicked.connect(self.add_output_port)
        output_controls.addWidget(add_output_btn)
        
        remove_output_btn = QPushButton("Remove Selected")
        remove_output_btn.clicked.connect(self.remove_output_port)
        output_controls.addWidget(remove_output_btn)
        
        outputs_layout.addLayout(output_controls)
        scroll_layout.addWidget(outputs_group)
        
        # Logic section
        logic_group = QGroupBox("Node Logic (Python Code)")
        logic_layout = QVBoxLayout(logic_group)
        
        logic_help = QLabel("""
Write Python code for your node logic. Available variables:
- inputs: dict containing input port values (e.g., inputs['data'])
- self: reference to the node instance
- self.properties: dict for storing node properties

Return a dict with output port names as keys:
return {'output': result, 'status': 'success'}
        """)
        logic_help.setStyleSheet("color: #666; font-size: 11px;")
        logic_layout.addWidget(logic_help)
        
        self.logic_edit = QTextEdit()
        self.logic_edit.setPlaceholderText("def execute(self, inputs):\n    # Your logic here\n    return {'output': inputs.get('input', None)}")
        self.logic_edit.setMinimumHeight(200)
        logic_layout.addWidget(self.logic_edit)
        
        scroll_layout.addWidget(logic_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Logic")
        test_btn.clicked.connect(self.test_logic)
        button_layout.addWidget(test_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Node")
        save_btn.clicked.connect(self.save_node)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def add_input_port(self):
        """Add an input port"""
        name = self.input_name_edit.text().strip()
        if name and name not in [self.inputs_list.item(i).text() for i in range(self.inputs_list.count())]:
            self.inputs_list.addItem(name)
            self.input_name_edit.clear()
    
    def remove_input_port(self):
        """Remove selected input port"""
        current = self.inputs_list.currentRow()
        if current >= 0:
            self.inputs_list.takeItem(current)
    
    def add_output_port(self):
        """Add an output port"""
        name = self.output_name_edit.text().strip()
        if name and name not in [self.outputs_list.item(i).text() for i in range(self.outputs_list.count())]:
            self.outputs_list.addItem(name)
            self.output_name_edit.clear()
    
    def remove_output_port(self):
        """Remove selected output port"""
        current = self.outputs_list.currentRow()
        if current >= 0:
            self.outputs_list.takeItem(current)
    
    def test_logic(self):
        """Test the node logic"""
        try:
            logic_code = self.logic_edit.toPlainText()
            if not logic_code.strip():
                QMessageBox.warning(self, "Warning", "Please enter some logic code to test.")
                return
            
            # Create a test environment
            test_inputs = {}
            for i in range(self.inputs_list.count()):
                port_name = self.inputs_list.item(i).text()
                test_inputs[port_name] = f"test_value_{i}"
            
            # Execute the logic
            exec_globals = {"inputs": test_inputs}
            exec(logic_code, exec_globals)
            
            if "execute" in exec_globals:
                # Test with mock node
                class MockNode:
                    def __init__(self):
                        self.properties = {}
                
                mock_node = MockNode()
                result = exec_globals["execute"](mock_node, test_inputs)
                
                QMessageBox.information(self, "Test Result", 
                                      f"Logic executed successfully!\nResult: {result}")
            else:
                QMessageBox.warning(self, "Test Warning", 
                                  "No 'execute' function found in the logic code.")
        
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Logic test failed:\n{str(e)}")
    
    def save_node(self):
        """Save the custom node"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a node name.")
            return
        
        inputs = [self.inputs_list.item(i).text() for i in range(self.inputs_list.count())]
        outputs = [self.outputs_list.item(i).text() for i in range(self.outputs_list.count())]
        logic = self.logic_edit.toPlainText()
        
        if not logic.strip():
            QMessageBox.warning(self, "Warning", "Please enter node logic.")
            return
        
        definition = {
            "name": name,
            "inputs": inputs,
            "outputs": outputs,
            "logic": logic
        }
        
        self.node_created.emit(name, definition)
        self.accept()
    
    def load_definition(self, definition):
        """Load an existing node definition"""
        self.name_edit.setText(definition.get("name", ""))
        
        for input_name in definition.get("inputs", []):
            self.inputs_list.addItem(input_name)
        
        for output_name in definition.get("outputs", []):
            self.outputs_list.addItem(output_name)
        
        self.logic_edit.setPlainText(definition.get("logic", ""))