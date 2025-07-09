"""
Core data structures for the node graph system
"""
from abc import ABC, abstractmethod, ABCMeta
from typing import Any, Dict, List, Optional, Callable
import uuid
from PySide6.QtCore import QObject, Signal
import json


class MetaQObjectABC(type(QObject), ABCMeta):
    pass


class NodePort:
    """Represents an input or output port on a node"""
    
    def __init__(self, name: str, data_type: type, is_input: bool, value: Any = None, connected_to: Optional['NodePort'] = None):
        self.name = name
        self.data_type = data_type
        self.is_input = is_input
        self.value = value
        self.connected_to = connected_to
    
    def connect(self, other_port: 'NodePort') -> bool:
        """Connect this port to another port"""
        if self.is_input == other_port.is_input:
            return False  # Can't connect input to input or output to output
        
        if self.is_input:
            self.connected_to = other_port
            other_port.connected_to = self
        else:
            other_port.connected_to = self
            self.connected_to = other_port
        return True
    
    def disconnect(self):
        """Disconnect this port"""
        if self.connected_to:
            self.connected_to.connected_to = None
            self.connected_to = None


class ProcessNode(QObject, ABC, metaclass=MetaQObjectABC):
    """Abstract base class for all process nodes"""
    data_changed = Signal()
    def __init__(self, name: str):
        QObject.__init__(self)
        self.id = str(uuid.uuid4())
        self.name = name
        self.input_ports: Dict[str, NodePort] = {}
        self.output_ports: Dict[str, NodePort] = {}
        self.position = (0, 0)
        self.metadata: Dict[str, Any] = {}
        self.properties: Dict[str, Any] = {}  # Ensure all nodes have a 'properties' attribute
    
    def add_input_port(self, name: str, data_type: type = Any):
        """Add an input port to the node"""
        self.input_ports[name] = NodePort(name, data_type, is_input=True)
    
    def add_output_port(self, name: str, data_type: type = Any):
        """Add an output port to the node"""
        self.output_ports[name] = NodePort(name, data_type, is_input=False)
    
    def get_input_value(self, port_name: str) -> Any:
        """Get the value from an input port"""
        port = self.input_ports.get(port_name)
        port_value = None
        if port and port.connected_to:
            port_value = port.connected_to.value
        else:
            port_value = port.value if port else None

        # if port_value is int return it as int, if float return as float, just return string
        if isinstance(port_value, str):
            try:
                if port_value.isdigit():
                    return int(port_value)
                else:
                    return float(port_value)
            except ValueError:
                # check if port_value is a list valid list or object accordingly return as list or object else return as string
                if port_value.startswith("[") and port_value.endswith("]"):
                    try:
                        return eval(port_value)
                    except (SyntaxError, NameError):
                        return port_value
                return port_value
        return port_value
    
    def set_input_value(self, port_name: str, value: Any):
        """Set the value of an input port"""
        port = self.input_ports.get(port_name)
        if port:
            port.value = value
    
    def get_input_port(self, port_name: str) -> Optional[NodePort]:
        """Get an input port by name"""
        return self.input_ports.get(port_name)
    
    def get_output_port(self, port_name: str) -> Optional[NodePort]:
        """Get an output port by name"""
        return self.output_ports.get(port_name)
    
    def get_output_value(self, port_name: str) -> Any:
        """Get the value from an output port"""
        port = self.output_ports.get(port_name)
        return port.value if port else None
    
    def set_output_value(self, port_name: str, value: Any):
        """Set the value of an output port"""
        port = self.output_ports.get(port_name)
        if port:
            port.value = value
    
    @abstractmethod
    def process(self) -> bool:
        """Execute the node's processing logic"""
        pass
    
    def can_execute(self) -> bool:
        """Check if the node has all required inputs"""
        for port in self.input_ports.values():
            if port.connected_to is None and port.value is None:
                return False
        return True

class TrueNode(ProcessNode):
    """A node that always returns True"""
    
    def __init__(self, name: str = "TrueNode"):
        super().__init__(name)
        self.add_output_port("output", bool)
        self.output = True
        self.set_output_value("output", self.output)
    
    def process(self) -> bool:
        # Simply set the output to True
        self.set_output_value("output", self.output)
        return True
    
class FalseNode(ProcessNode):
    """A node that always returns False"""
    
    def __init__(self, name: str = "FalseNode"):
        super().__init__(name)
        self.add_output_port("output", bool)
        self.output = False
        self.set_output_value("output", self.output)
    
    def process(self) -> bool:
        # Simply set the output to False
        self.set_output_value("output", self.output)
        return True

class DataNode(ProcessNode):
    """A node that holds static data"""
    
    def __init__(self, name: str, input: Any = None):
        super().__init__(name)
        self.input = input
        self.output = self.input
        self.add_input_port("input", type(input) if input else Any)  # Add input port
        self.add_output_port("output", type(input) if input else Any)
        self.properties = {"data": input}  # Add properties for DataNode
    
    def process(self) -> bool:
        # If input is connected or set, use it as data
        input_val = self.get_input_value("input")
        self.input = input_val if input_val is not None else self.input
        # input can be empty, int, float array of int or float or string handle them properly to create such output
        typed_input = []
        if ',' in str(self.input):
            try:
                for x in str(self.input).split(','):
                    if x.strip().isdigit():
                        typed_input.append(int(x.strip()))
                    elif x.strip().replace('.', '', 1).isdigit():
                        typed_input.append(float(x.strip()))
                    else:
                        typed_input.append(x.strip())
            except ValueError:
                self.input = [self.input]
        if input_val is not None:
            self.output = typed_input if isinstance(typed_input, list) else input_val
        self.set_output_value("output", self.output)
        return True

    def set_data(self, data: Any):
        self.input = data
        self.set_input_value("input", data)  # Keep input in sync
        self.output_ports["output"].data_type = type(data)
        self.set_output_value("output", data)  # Keep output in sync
        self.properties["data"] = data
        self.data_changed.emit()

class ArrayDataNode(DataNode):
    """A node that holds an array of data"""
    
    def __init__(self, name: str, input: List[Any] = None):
        super().__init__(name, input if input is not None else [])
        self.add_input_port("input", List[Any])
        self.add_output_port("output", List[Any])
        self.properties = {"data": input}  # Add properties for ArrayDataNode
    
    def process(self) -> bool:
        # If input is connected or set, use it as data
        input_val = self.get_input_value("input")
        self.input = input_val if input_val is not None else self.input
        self.output = self.input  # Output is the same as input for ArrayDataNode
        self.set_output_value("output", self.output)
        return True
    
    def set_data(self, data):
        return super().set_data(data)


class Connection:
    """Represents a connection between two ports"""
    
    def __init__(self, id: str = None, source_node_id: str = "", source_port: str = "", target_node_id: str = "", target_port: str = ""):
        self.id = id or str(uuid.uuid4())
        self.source_node_id = source_node_id
        self.source_port = source_port
        self.target_node_id = target_node_id
        self.target_port = target_port


class Pipeline:
    """Manages a collection of nodes and their connections"""
    
    def __init__(self, name: str = "Pipeline"):
        self.name = name
        self.nodes: Dict[str, ProcessNode] = {}
        self.connections: Dict[str, Connection] = {}
    
    def add_node(self, node: ProcessNode) -> str:
        """Add a node to the pipeline"""
        self.nodes[node.id] = node
        return node.id
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the pipeline"""
        if node_id in self.nodes:
            # Remove all connections involving this node
            connections_to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.source_node_id == node_id or conn.target_node_id == node_id:
                    connections_to_remove.append(conn_id)
            
            for conn_id in connections_to_remove:
                self.remove_connection(conn_id)
            
            del self.nodes[node_id]
            return True
        return False
    
    def connect_nodes(self, source_node_id: str, source_port: str, 
                     target_node_id: str, target_port: str) -> Optional[str]:
        """Connect two nodes"""
        source_node = self.nodes.get(source_node_id)
        target_node = self.nodes.get(target_node_id)
        
        if not source_node or not target_node:
            return None
        
        source_port_obj = source_node.output_ports.get(source_port)
        target_port_obj = target_node.input_ports.get(target_port)
        
        if not source_port_obj or not target_port_obj:
            return None
        
        if source_port_obj.connect(target_port_obj):
            connection = Connection(
                source_node_id=source_node_id,
                source_port=source_port,
                target_node_id=target_node_id,
                target_port=target_port
            )
            self.connections[connection.id] = connection
            return connection.id
        
        return None
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection"""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        source_node = self.nodes.get(connection.source_node_id)
        target_node = self.nodes.get(connection.target_node_id)
        
        if source_node and target_node:
            source_port = source_node.output_ports.get(connection.source_port)
            target_port = target_node.input_ports.get(connection.target_port)
            
            if source_port:
                source_port.disconnect()
            if target_port:
                target_port.disconnect()
        
        del self.connections[connection_id]
        return True
    
    def execute(self) -> Dict[str, Any]:
        """Execute the pipeline by running nodes in topological order"""
        # Simple execution order based on dependencies
        executed = set()
        results = {}
        
        def can_execute_node(node: ProcessNode) -> bool:
            return node.can_execute() and node.id not in executed
        
        # Keep executing until no more nodes can be executed
        while len(executed) < len(self.nodes):
            executed_this_round = False
            
            for node_id, node in self.nodes.items():
                if can_execute_node(node):
                    success = node.process()
                    executed.add(node_id)
                    results[node_id] = {
                        'success': success,
                        'outputs': {name: port.value for name, port in node.output_ports.items()}
                    }
                    executed_this_round = True
            
            if not executed_this_round:
                # Circular dependency or missing inputs
                break
        
        return results
    
    def get_execution_order(self) -> List[str]:
        """Get the topological order of nodes for execution"""
        # Simplified topological sort
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # Calculate in-degrees
        for connection in self.connections.values():
            in_degree[connection.target_node_id] += 1
        
        # Start with nodes that have no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees of dependent nodes
            for connection in self.connections.values():
                if connection.source_node_id == current:
                    in_degree[connection.target_node_id] -= 1
                    if in_degree[connection.target_node_id] == 0:
                        queue.append(connection.target_node_id)
        
        return result
    
    def add_connection(self, source_port: NodePort, target_port: NodePort) -> Optional[str]:
        """Add a connection between two ports"""
        # Find the nodes that own these ports
        source_node_id = None
        target_node_id = None
        source_port_name = source_port.name
        target_port_name = target_port.name
        
        for node_id, node in self.nodes.items():
            if source_port_name in node.output_ports and node.output_ports[source_port_name] == source_port:
                source_node_id = node_id
            if target_port_name in node.input_ports and node.input_ports[target_port_name] == target_port:
                target_node_id = node_id
        
        if source_node_id and target_node_id:
            return self.connect_nodes(source_node_id, source_port_name, target_node_id, target_port_name)
        
        return None

class JsonDefinedNode(ProcessNode):
    """
    Node defined by a JSON schema.
    JSON example:
    {
        "name": "MultiplyByN",
        "inputs": [
            {"name": "value", "type": "float"},
            {"name": "factor", "type": "float"}
        ],
        "outputs": [
            {"name": "result", "type": "float"}
        ],
        "logic": "result = value * factor"
    }
    """
    def __init__(self, definition: dict):
        super().__init__(definition.get("name", "CustomNode"))
        self.definition = definition
        # Add input ports
        for inp in definition.get("inputs", []):
            self.add_input_port(inp["name"], eval(inp.get("type", "Any")))
        # Add output ports
        for outp in definition.get("outputs", []):
            self.add_output_port(outp["name"], eval(outp.get("type", "Any")))
        self.logic = definition.get("logic", "")
        self.properties = definition.get("properties", {})

    def process(self) -> bool:
        # Prepare local variables for logic execution
        local_vars = {}
        for inp in self.input_ports:
            local_vars[inp] = self.get_input_value(inp)
        try:
            # Evaluate logic (should assign output variables)
            exec(self.logic, {}, local_vars)
            # Set outputs
            for outp in self.output_ports:
                self.set_output_value(outp, local_vars.get(outp))
            return True
        except Exception as e:
            print(f"Error in JsonDefinedNode '{self.name}': {e}")
            return False

# Utility functions for loading/saving custom node definitions
def load_custom_node_definitions(json_path: str) -> list:
    with open(json_path, "r") as f:
        return json.load(f)

def save_custom_node_definitions(json_path: str, definitions: list):
    with open(json_path, "w") as f:
        json.dump(definitions, f, indent=2)
