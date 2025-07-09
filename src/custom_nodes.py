"""
Custom node implementation
"""
from src.core import ProcessNode
from typing import Dict, Any, List
import json
import os

class CustomNode(ProcessNode):
    """A user-defined custom node"""
    
    def __init__(self, definition: Dict[str, Any]):
        # Extract name from definition and pass to parent
        node_name = definition.get("name", "Custom Node")
        super().__init__(node_name)
        
        self.definition = definition
        self.is_custom_node = True
        
        # Set node type
        self.node_type = "custom"
        
        # Set up inputs and outputs using ProcessNode methods
        self._setup_ports(definition)

        # Store the logic code
        self.logic_code = definition.get("logic", "")
        
        # Initialize properties if not already done by parent
        if not hasattr(self, 'properties'):
            self.properties = {}
        
        # Compile the logic for execution
        self._compile_logic()
    
    def _setup_ports(self, definition: Dict[str, Any]):
        """Set up input and output ports using ProcessNode methods"""
        # Add input ports
        input_ports = definition.get("input_ports", [])
        for port_def in input_ports:
            if isinstance(port_def, str):
                # Simple string port name
                self.add_input_port(port_def)
            elif isinstance(port_def, dict):
                # Dictionary with port details
                port_name = port_def.get("name", "input")
                data_type = port_def.get("data_type", "any")
                self.add_input_port(port_name, data_type)
            else:
                print(f"Warning: Invalid input port definition: {port_def}")
    
        # Add output ports
        output_ports = definition.get("output_ports", [])
        for port_def in output_ports:
            if isinstance(port_def, str):
                # Simple string port name
                self.add_output_port(port_def)
            elif isinstance(port_def, dict):
                # Dictionary with port details
                port_name = port_def.get("name", "output")
                data_type = port_def.get("data_type", "any")
                self.add_output_port(port_name, data_type)
            else:
                print(f"Warning: Invalid output port definition: {port_def}")
    
    def _compile_logic(self):
        """Compile the custom logic code"""
        try:
            self.compiled_globals = {}
            exec(self.logic_code, self.compiled_globals)
            
            if "execute" not in self.compiled_globals:
                raise ValueError("Custom node logic must define an 'execute' function")
                
        except Exception as e:
            print(f"Failed to compile custom node logic: {e}")
            # Fallback to a simple pass-through
            self.compiled_globals = {
                "execute": lambda self, inputs: {output: None for output in self.get_output_port_names()}
            }
    
    def execute(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the custom node logic"""
        if inputs is None:
            inputs = {}
        
        try:
            # Execute the custom logic
            if "execute" in self.compiled_globals:
                result = self.compiled_globals["execute"](self, inputs)
                
                # Ensure result is a dictionary
                if not isinstance(result, dict):
                    result = {"output": result}
                
                return result
            else:
                # Fallback
                return {output: None for output in self.get_output_port_names()}
                
        except Exception as e:
            print(f"Error executing custom node {self.name}: {e}")
            return {output: None for output in self.get_output_port_names()}
    
    def process(self) -> bool:
        """Process method required by ProcessNode - invokes the custom execute function"""
        try:
            # Get input values from connected ports
            inputs = {}
            for port_name in self.get_input_port_names():
                try:
                    input_value = self.get_input_value(port_name)
                    if input_value is not None:
                        inputs[port_name] = input_value
                except (AttributeError, KeyError):
                    # Port may not have a value or connection
                    inputs[port_name] = None
            
            # Execute the custom logic with input values
            outputs = self.execute(inputs)
            
            if outputs is None:
                return False
            
            # Set output port values using set_output_value
            for port_name, value in outputs.items():
                try:
                    if port_name in self.get_output_port_names():
                        self.set_output_value(port_name, value)
                except (AttributeError, KeyError):
                    # Output port may not exist
                    print(f"Warning: Output port '{port_name}' not found")
            
            return True
            
        except Exception as e:
            print(f"Error processing custom node {self.name}: {e}")
            return False
    
    def update_definition(self, new_definition: Dict[str, Any]):
        """Update the node definition"""
        self.definition = new_definition
        self.name = new_definition.get("name", self.name)
        
        # Clear existing ports
        self.clear_input_ports()
        self.clear_output_ports()
        
        # Set up new ports
        self._setup_ports(new_definition)
        
        self.logic_code = new_definition.get("logic", "")
        self._compile_logic()
    
    def get_input_port_names(self) -> List[str]:
        """Get list of input port names"""
        try:
            # Try different possible attribute names
            if hasattr(self, 'inputs'):
                return list(self.inputs.keys())
            elif hasattr(self, 'input_ports'):
                return list(self.input_ports.keys())
            else:
                # Fallback: extract from definition
                input_ports = self.definition.get("input_ports", [])
                names = []
                for port_def in input_ports:
                    if isinstance(port_def, str):
                        names.append(port_def)
                    elif isinstance(port_def, dict):
                        names.append(port_def.get("name", "input"))
                return names
        except Exception:
            return []
    
    def get_output_port_names(self) -> List[str]:
        """Get list of output port names"""
        try:
            # Try different possible attribute names
            if hasattr(self, 'outputs'):
                return list(self.outputs.keys())
            elif hasattr(self, 'output_ports'):
                return list(self.output_ports.keys())
            else:
                # Fallback: extract from definition
                output_ports = self.definition.get("output_ports", [])
                names = []
                for port_def in output_ports:
                    if isinstance(port_def, str):
                        names.append(port_def)
                    elif isinstance(port_def, dict):
                        names.append(port_def.get("name", "output"))
                return names
        except Exception:
            return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the custom node"""
        base_dict = super().to_dict()
        base_dict.update({
            "definition": self.definition,
            "is_custom_node": True
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Deserialize a custom node"""
        definition = data.get("definition", {})
        node = cls(definition)
        
        # Restore base properties
        if "id" in data:
            node.id = data["id"]
        if "position" in data:
            node.position = data["position"]
        if "properties" in data:
            node.properties.update(data["properties"])
        
        return node


class CustomNodeManager:
    """Manager for saving/loading custom node definitions"""
    
    def __init__(self, custom_nodes_file: str = "custom_nodes.json"):
        self.custom_nodes_file = custom_nodes_file
        self.custom_definitions = self.load_custom_nodes()
    
    def save_custom_node(self, name: str, definition: Dict[str, Any]):
        """Save a custom node definition"""
        self.custom_definitions[name] = definition
        self._save_to_file()
        print(f"Saved custom node '{name}' to {self.custom_nodes_file}")
    
    def load_custom_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Load custom node definitions from file"""
        if os.path.exists(self.custom_nodes_file):
            try:
                with open(self.custom_nodes_file, 'r') as f:
                    data = json.load(f)
                    # Handle both list and dict formats
                    if isinstance(data, list):
                        # Convert list format to dict format
                        result = {}
                        for item in data:
                            if isinstance(item, dict) and 'name' in item:
                                result[item['name']] = item
                        return result
                    elif isinstance(data, dict):
                        return data
                    else:
                        print(f"Invalid format in {self.custom_nodes_file}")
                        return {}
            except Exception as e:
                print(f"Failed to load custom nodes: {e}")
        return {}
    
    def _save_to_file(self):
        """Save custom definitions to file"""
        try:
            with open(self.custom_nodes_file, 'w') as f:
                json.dump(self.custom_definitions, f, indent=2)
        except Exception as e:
            print(f"Failed to save custom nodes: {e}")
    
    def get_custom_node_types(self) -> List[str]:
        """Get list of available custom node types"""
        return list(self.custom_definitions.keys())
    
    def create_custom_node(self, node_type: str) -> CustomNode:
        """Create a custom node instance"""
        # Handle custom node type prefix
        if node_type.startswith("custom_"):
            node_type = node_type[7:]  # Remove "custom_" prefix
        
        if node_type in self.custom_definitions:
            return CustomNode(self.custom_definitions[node_type])
        else:
            raise ValueError(f"Unknown custom node type: {node_type}")

# Global instance
custom_node_manager = CustomNodeManager()