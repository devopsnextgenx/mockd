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
        
        # Set up inputs and outputs
        self.input_names = definition.get("inputs", [])
        self.output_names = definition.get("outputs", [])
        
        # Store the logic code
        self.logic_code = definition.get("logic", "")
        
        # Initialize properties if not already done by parent
        if not hasattr(self, 'properties'):
            self.properties = {}
        
        # Compile the logic for execution
        self._compile_logic()
    
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
                "execute": lambda self, inputs: {output: None for output in self.output_names}
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
                return {output: None for output in self.output_names}
                
        except Exception as e:
            print(f"Error executing custom node {self.name}: {e}")
            return {output: None for output in self.output_names}
    
    def update_definition(self, new_definition: Dict[str, Any]):
        """Update the node definition"""
        self.definition = new_definition
        self.name = new_definition.get("name", self.name)
        self.input_names = new_definition.get("inputs", [])
        self.output_names = new_definition.get("outputs", [])
        self.logic_code = new_definition.get("logic", "")
        self._compile_logic()
    
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