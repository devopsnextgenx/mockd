"""
Built-in process nodes for common data operations
"""
import pandas as pd
import numpy as np
from typing import Any, List, Dict
from src.core import TrueNode, ProcessNode, ArrayDataNode, DataNode, TrueNode, FalseNode, JsonDefinedNode, load_custom_node_definitions

from mimesis import Generic, Person, Text, Numeric, Datetime, Address, Internet, Development


class MathNode(ProcessNode):
    """Performs basic mathematical operations"""
    
    def __init__(self, operation: str = "add"):
        super().__init__(f"Math ({operation})")
        self.operation = operation
        self.add_input_port("a", (int, float))
        self.add_input_port("b", (int, float))
        self.add_output_port("result", (int, float))
    
    def process(self) -> bool:
        try:
            a = self.get_input_value("a")
            b = self.get_input_value("b")
            
            if a is None or b is None:
                return False
            
            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else 0,
                "power": lambda x, y: x ** y,
                "modulo": lambda x, y: x % y if y != 0 else 0
            }
            
            if self.operation in operations:
                result = operations[self.operation](a, b)
                self.set_output_value("result", result)
                return True
            
            return False
        except Exception:
            return False


class FilterNode(ProcessNode):
    """Filters data based on conditions"""
    
    def __init__(self):
        super().__init__("Filter")
        self.add_input_port("data", List)
        self.add_input_port("condition", Any)  # Can be string or callable
        self.add_output_port("filtered_data", List)
    
    def process(self) -> bool:
        try:
            data = self.get_input_value("data")
            condition = self.get_input_value("condition")
            
            if data is None:
                return False
            
            if condition is None:
                self.set_output_value("filtered_data", data)
                return True
            
            # Support callable conditions (lambda functions)
            if callable(condition):
                filtered = [x for x in data if condition(x)]
            # Simple filtering logic - can be extended
            elif condition == "positive":
                filtered = [x for x in data if isinstance(x, (int, float)) and x > 0]
            elif condition == "negative":
                filtered = [x for x in data if isinstance(x, (int, float)) and x < 0]
            elif condition == "even":
                filtered = [x for x in data if isinstance(x, int) and x % 2 == 0]
            elif condition == "odd":
                filtered = [x for x in data if isinstance(x, int) and x % 2 == 1]
            else:
                filtered = data
            
            self.set_output_value("filtered_data", filtered)
            return True
        except Exception:
            return False


class TransformNode(ProcessNode):
    """Transforms data using various operations"""
    
    def __init__(self, transform_type: str = "none"):
        super().__init__(f"Transform ({transform_type})")
        self.transform_type = transform_type
        self.add_input_port("data", List)
        self.add_output_port("transformed_data", List)
        self.properties = {"transform_type": transform_type}  # Add properties for TransformNode
    
    def process(self) -> bool:
        try:
            data = self.get_input_value("data")
            
            if data is None:
                return False
            
            if self.transform_type == "square":
                transformed = [x**2 if isinstance(x, (int, float)) else x for x in data]
            elif self.transform_type == "sqrt":
                transformed = [x**0.5 if isinstance(x, (int, float)) and x >= 0 else x for x in data]
            elif self.transform_type == "abs":
                transformed = [abs(x) if isinstance(x, (int, float)) else x for x in data]
            elif self.transform_type == "log":
                transformed = [np.log(x) if isinstance(x, (int, float)) and x > 0 else x for x in data]
            elif self.transform_type == "normalize":
                numeric_data = [x for x in data if isinstance(x, (int, float))]
                if numeric_data:
                    min_val, max_val = min(numeric_data), max(numeric_data)
                    range_val = max_val - min_val if max_val != min_val else 1
                    transformed = [(x - min_val) / range_val if isinstance(x, (int, float)) else x for x in data]
                else:
                    transformed = data
            else:
                transformed = data
            
            self.set_output_value("transformed_data", transformed)
            return True
        except Exception:
            return False


class AggregateNode(ProcessNode):
    """Aggregates data using various statistical operations"""
    
    def __init__(self, operation: str = "sum"):
        super().__init__(f"Aggregate ({operation})")
        self.operation = operation
        self.add_input_port("data", List)
        self.add_output_port("result", (int, float))
        self.properties = {"operation": operation}  # Add properties for AggregateNode
    
    def process(self) -> bool:
        try:
            data = self.get_input_value("data")
            
            if data is None:
                return False
            
            # Filter numeric data
            numeric_data = [x for x in data if isinstance(x, (int, float))]
            
            if not numeric_data:
                return False
            
            operations = {
                "sum": sum,
                "mean": lambda x: sum(x) / len(x),
                "min": min,
                "max": max,
                "count": len,
                "std": lambda x: np.std(x),
                "median": lambda x: np.median(x)
            }
            
            if self.operation in operations:
                result = operations[self.operation](numeric_data)
                self.set_output_value("result", result)
                return True
            
            return False
        except Exception:
            return False


class JoinNode(ProcessNode):
    """Joins multiple data streams"""
    
    def __init__(self):
        super().__init__("Join")
        self.add_input_port("data1", List)
        self.add_input_port("data2", List)
        self.add_output_port("joined_data", List)
    
    def process(self) -> bool:
        try:
            data1 = self.get_input_value("data1") or []
            data2 = self.get_input_value("data2") or []
            
            joined = list(data1) + list(data2)
            self.set_output_value("joined_data", joined)
            return True
        except Exception:
            return False


class SplitNode(ProcessNode):
    """Splits data into multiple streams"""
    
    def __init__(self):
        super().__init__("Split")
        self.add_input_port("data", List)
        self.add_input_port("split_index", int)
        self.add_output_port("data1", List)
        self.add_output_port("data2", List)
    
    def process(self) -> bool:
        try:
            data = self.get_input_value("data")
            split_index = self.get_input_value("split_index") or len(data) // 2
            
            if data is None:
                return False
            
            data1 = data[:split_index]
            data2 = data[split_index:]
            
            self.set_output_value("data1", data1)
            self.set_output_value("data2", data2)
            return True
        except Exception:
            return False


class PrintNode(ProcessNode):
    """Prints data to console (useful for debugging)"""
    
    def __init__(self):
        super().__init__("Print")
        self.add_input_port("data", Any)
        self.add_output_port("data", Any)  # Pass-through
    
    def process(self) -> bool:
        try:
            data = self.get_input_value("data")
            print(f"[{self.name} - {self.id.split('-')[0]}] {data}")
            self.set_output_value("data", data)
            return True
        except Exception:
            return False


class MockNode(ProcessNode):
    """Generates mock data using Mimesis library"""
    
    def __init__(self, data_type: str = "text", size: int = 10, min_length: int = None, max_length: int = None):
        super().__init__(f"Mock ({data_type})")
        self.data_type = data_type
        self.size = size
        self.min_length = min_length
        self.max_length = max_length
        
        # Add configuration input ports
        self.add_input_port("size", int)  # Override default size
        self.add_input_port("min_length", int)  # Override default min_length
        self.add_input_port("max_length", int)  # Override default max_length
        
        # Output port for generated data
        self.add_output_port("mock_data", List)
        
        # Add properties for display/editing on card
        self.properties = {
            "data_type": data_type,
            "size": size,
            "min_length": min_length if min_length is not None else '',
            "max_length": max_length if max_length is not None else ''
        }
    
    def process(self) -> bool:
        try:
            # Import Mimesis here to avoid import issues
            from mimesis import Generic, Person, Text, Numeric, Datetime, Address, Internet, Development
            
            # Get configuration from inputs or use defaults
            size = self.get_input_value("size") or self.size
            min_length = self.get_input_value("min_length") or self.min_length
            max_length = self.get_input_value("max_length") or self.max_length
            
            # Initialize Mimesis providers
            generic = Generic()
            person = Person()
            text = Text()
            numeric = Numeric()
            datetime_provider = Datetime()
            address = Address()
            internet = Internet()
            dev = Development()
            
            mock_data = []
            
            for _ in range(size):
                if self.data_type == "text":
                    if min_length and max_length:
                        data = text.text(quantity=1)[0][:max_length]
                        while len(data) < min_length:
                            data += " " + text.word()
                        data = data[:max_length]
                    else:
                        data = text.text(quantity=1)[0]
                    mock_data.append(data)
                
                elif self.data_type == "word":
                    data = text.word()
                    if min_length and len(data) < min_length:
                        data = text.words(quantity=2, separator=" ")
                    if max_length and len(data) > max_length:
                        data = data[:max_length]
                    mock_data.append(data)
                
                elif self.data_type == "sentence":
                    data = text.sentence()
                    if max_length and len(data) > max_length:
                        data = data[:max_length]
                    mock_data.append(data)
                
                elif self.data_type == "first_name":
                    mock_data.append(person.first_name())
                
                elif self.data_type == "last_name":
                    mock_data.append(person.last_name())
                
                elif self.data_type == "full_name":
                    mock_data.append(person.full_name())
                
                elif self.data_type == "email":
                    mock_data.append(person.email())
                
                elif self.data_type == "phone":
                    mock_data.append(person.phone_number())
                
                elif self.data_type == "age":
                    min_val = min_length or 18
                    max_val = max_length or 80
                    mock_data.append(numeric.integer_number(start=min_val, end=max_val))
                
                elif self.data_type == "integer":
                    min_val = min_length or 1
                    max_val = max_length or 100
                    mock_data.append(numeric.integer_number(start=min_val, end=max_val))
                
                elif self.data_type == "float":
                    min_val = min_length or 0.0
                    max_val = max_length or 100.0
                    mock_data.append(round(numeric.float_number(start=min_val, end=max_val), 2))
                
                elif self.data_type == "date":
                    mock_data.append(datetime_provider.date().isoformat())
                
                elif self.data_type == "datetime":
                    mock_data.append(datetime_provider.datetime().isoformat())
                
                elif self.data_type == "address":
                    mock_data.append(address.address())
                
                elif self.data_type == "city":
                    mock_data.append(address.city())
                
                elif self.data_type == "country":
                    mock_data.append(address.country())
                
                elif self.data_type == "zipcode":
                    mock_data.append(address.zip_code())
                
                elif self.data_type == "url":
                    mock_data.append(internet.url())
                
                elif self.data_type == "username":
                    mock_data.append(internet.username())
                
                elif self.data_type == "password":
                    length = max_length or 12
                    mock_data.append(internet.password(length=length))
                
                elif self.data_type == "uuid":
                    import uuid
                    mock_data.append(str(uuid.uuid4()))
                
                elif self.data_type == "boolean":
                    import random
                    mock_data.append(random.choice([True, False]))
                
                elif self.data_type == "programming_language":
                    mock_data.append(dev.programming_language())
                
                elif self.data_type == "database":
                    mock_data.append(dev.database())
                
                elif self.data_type == "os":
                    mock_data.append(dev.os())
                
                else:
                    # Default to generic text
                    mock_data.append(text.word())
            
            self.set_output_value("mock_data", mock_data)
            return True
            
        except ImportError:
            print("Mimesis library not available. Please install it with: pip install mimesis")
            return False
        except Exception as e:
            print(f"Error generating mock data: {e}")
            return False
    
    def can_execute(self) -> bool:
        """MockNode can always execute as it has default values for all inputs"""
        return True

class ForEachNode(ProcessNode):
    """
    Loops over an array input, triggers 'iterate' output for each item,
    and triggers 'exit' output after the loop (optional).
    """
    def __init__(self, name: str = "forEach"):
        super().__init__(name)
        self.add_input_port("items", list)
        self.add_output_port("iterate", Any)  # Used to trigger downstream node for each item
        self.add_output_port("exit", Any)     # Used to trigger downstream node after loop
        self.properties = {}

    def process(self, index) -> any:
        items = self.get_input_value("items")
        if not isinstance(items, list):
            self.set_output_value("iterate", None)
            self.set_output_value("exit", None)
            return {"continueLoop": False, "exit": False}

        # For pipeline execution: set 'iterate' to a generator of items
        # Downstream node should expect to receive 'item' as input for each iteration
        self.set_output_value("iterate", items[index] if index < len(items) else None)
        self.set_output_value("exit", True)  # Just a signal; downstream can use or ignore
        continueLoop = index < len(items) - 1  # Continue if there are more items to process
        exitLoop = not continueLoop  # Exit if no more items to process
        return {"continueLoop": continueLoop, "exit": exitLoop}

# Node factory for easy node creation
NODE_TYPES = {
    "true": lambda: TrueNode("True"),
    "false": lambda: FalseNode("False"),
    "data": lambda: DataNode("data"),
    "array": lambda: ArrayDataNode("array"),
    "forEach": lambda: ForEachNode("forEach"),
    "math_add": lambda: MathNode("add"),
    "math_subtract": lambda: MathNode("subtract"),
    "math_multiply": lambda: MathNode("multiply"),
    "math_divide": lambda: MathNode("divide"),
    "filter": lambda: FilterNode(),
    "transform_square": lambda: TransformNode("square"),
    "transform_sqrt": lambda: TransformNode("sqrt"),
    "transform_abs": lambda: TransformNode("abs"),
    "transform_normalize": lambda: TransformNode("normalize"),
    "aggregate_sum": lambda: AggregateNode("sum"),
    "aggregate_mean": lambda: AggregateNode("mean"),
    "aggregate_min": lambda: AggregateNode("min"),
    "aggregate_max": lambda: AggregateNode("max"),
    "join": lambda: JoinNode(),
    "split": lambda: SplitNode(),
    "print": lambda: PrintNode(),
    # Mock data generators - Basic
    "mock": lambda: MockNode(),
    "mock_text": lambda: MockNode("text", 10),
    "mock_word": lambda: MockNode("word", 10),
    "mock_sentence": lambda: MockNode("sentence", 10),
    # Mock data generators - Personal
    "mock_first_names": lambda: MockNode("first_name", 10),
    "mock_last_names": lambda: MockNode("last_name", 10),
    "mock_full_names": lambda: MockNode("full_name", 10),
    "mock_emails": lambda: MockNode("email", 10),
    "mock_phones": lambda: MockNode("phone", 10),
    "mock_ages": lambda: MockNode("age", 10),
    # Mock data generators - Numbers
    "mock_integers": lambda: MockNode("integer", 10),
    "mock_floats": lambda: MockNode("float", 10),
    "mock_booleans": lambda: MockNode("boolean", 10),
    # Mock data generators - Dates
    "mock_dates": lambda: MockNode("date", 10),
    "mock_datetimes": lambda: MockNode("datetime", 10),
    # Mock data generators - Address
    "mock_addresses": lambda: MockNode("address", 10),
    "mock_cities": lambda: MockNode("city", 10),
    "mock_countries": lambda: MockNode("country", 10),
    "mock_zipcodes": lambda: MockNode("zipcode", 10),
    # Mock data generators - Internet
    "mock_urls": lambda: MockNode("url", 10),
    "mock_usernames": lambda: MockNode("username", 10),
    "mock_passwords": lambda: MockNode("password", 10),
    # Mock data generators - Tech
    "mock_uuids": lambda: MockNode("uuid", 10),
    "mock_programming_languages": lambda: MockNode("programming_language", 10),
    "mock_databases": lambda: MockNode("database", 10),
    "mock_operating_systems": lambda: MockNode("os", 10),
}


CUSTOM_NODE_DEFINITIONS = []
CUSTOM_NODE_TYPES = {}

def register_custom_nodes(json_path="custom_nodes.json"):
    global CUSTOM_NODE_DEFINITIONS, CUSTOM_NODE_TYPES
    try:
        loaded_data = load_custom_node_definitions(json_path)
        
        # Handle both formats: list of definitions or dict of definitions
        if isinstance(loaded_data, dict):
            # Convert dict format to list format
            CUSTOM_NODE_DEFINITIONS = []
            for node_name, node_def in loaded_data.items():
                # Ensure the definition has a name field
                if isinstance(node_def, dict):
                    node_def["name"] = node_def.get("name", node_name)
                    CUSTOM_NODE_DEFINITIONS.append(node_def)
        else:
            # Already in list format
            CUSTOM_NODE_DEFINITIONS = loaded_data
            
        print(f"Loading {len(CUSTOM_NODE_DEFINITIONS)} custom node definitions from {json_path}")
        
        for defn in CUSTOM_NODE_DEFINITIONS:
            if isinstance(defn, dict):
                node_type = defn.get("name", "CustomNode")
                CUSTOM_NODE_TYPES[node_type] = lambda d=defn: JsonDefinedNode(d)
            
        print(f"Loaded {len(CUSTOM_NODE_DEFINITIONS)} custom node definitions")
    except Exception as e:
        print(f"Could not load custom nodes: {e}")

# Call this at startup or when refreshing node palette
register_custom_nodes()

# Merge built-in and custom node types
def get_all_node_types():
    all_types = dict(NODE_TYPES)
    all_types.update(CUSTOM_NODE_TYPES)
    return all_types

def create_node(node_type: str) -> ProcessNode:
    """Factory function to create nodes by type"""
    all_types = get_all_node_types()
    if node_type in all_types:
        return all_types[node_type]()
    else:
        raise ValueError(f"Unknown node type: {node_type}")
