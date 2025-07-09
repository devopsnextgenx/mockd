#!/usr/bin/env python3
"""
Example usage of MockNode for generating mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nodes import MockNode, PrintNode, AggregateNode
from src.core import Pipeline

def demo_mock_data():
    """Demonstrate MockNode usage with different data types"""
    
    print("=== Mock Data Generation Demo ===\n")
    
    # Example 1: Generate mock names
    print("1. Generating mock names:")
    mock_names = MockNode("full_name", size=5)
    print_node = PrintNode()
    
    # Create a simple pipeline
    pipeline = Pipeline()
    pipeline.add_node(mock_names)
    pipeline.add_node(print_node)
    
    # Connect nodes
    pipeline.add_connection(mock_names.get_output_port("mock_data"), 
                          print_node.get_input_port("data"))
    
    # Execute
    pipeline.execute()
    print()
    
    # Example 2: Generate mock emails with aggregation
    print("2. Generating mock emails and counting them:")
    mock_emails = MockNode("email", size=8)
    count_node = AggregateNode("count")
    print_count = PrintNode()
    
    # Create pipeline
    pipeline2 = Pipeline()
    pipeline2.add_node(mock_emails)
    pipeline2.add_node(count_node)
    pipeline2.add_node(print_count)
    
    # Connect nodes
    pipeline2.add_connection(mock_emails.get_output_port("mock_data"), 
                           count_node.get_input_port("data"))
    pipeline2.add_connection(count_node.get_output_port("result"), 
                           print_count.get_input_port("data"))
    
    # Execute
    pipeline2.execute()
    print()
    
    # Example 3: Generate integers with specific range
    print("3. Generating integers between 10 and 100:")
    mock_ints = MockNode("integer", size=10, min_length=10, max_length=100)
    print_ints = PrintNode()
    
    # Create pipeline
    pipeline3 = Pipeline()
    pipeline3.add_node(mock_ints)
    pipeline3.add_node(print_ints)
    
    # Connect nodes
    pipeline3.add_connection(mock_ints.get_output_port("mock_data"), 
                           print_ints.get_input_port("data"))
    
    # Execute
    pipeline3.execute()
    print()
    
    # Example 4: Generate text with length constraints
    print("4. Generating text with length constraints:")
    mock_text = MockNode("text", size=3, min_length=20, max_length=50)
    print_text = PrintNode()
    
    # Create pipeline
    pipeline4 = Pipeline()
    pipeline4.add_node(mock_text)
    pipeline4.add_node(print_text)
    
    # Connect nodes
    pipeline4.add_connection(mock_text.get_output_port("mock_data"), 
                           print_text.get_input_port("data"))
    
    # Execute
    pipeline4.execute()
    print()
    
    print("=== Available Mock Data Types ===")
    data_types = [
        "text", "word", "sentence", "first_name", "last_name", "full_name",
        "email", "phone", "age", "integer", "float", "date", "datetime",
        "address", "city", "country", "zipcode", "url", "username", 
        "password", "uuid", "boolean", "programming_language", "database", "os"
    ]
    
    for i, dtype in enumerate(data_types, 1):
        print(f"{i:2d}. {dtype}")


if __name__ == "__main__":
    demo_mock_data()
