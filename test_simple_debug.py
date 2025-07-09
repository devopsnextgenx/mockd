#!/usr/bin/env python3
"""
Simple test to debug pipeline data flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nodes import MockNode, PrintNode
from src.core import Pipeline

def test_simple_pipeline():
    """Test a very simple pipeline"""
    
    print("=== Simple Pipeline Debug Test ===\n")
    
    # Create a simple pipeline with just MockNode -> PrintNode
    pipeline = Pipeline("Simple Test")
    
    # Create nodes
    mock_node = MockNode("first_name", size=3)
    print_node = PrintNode()
    
    print(f"Mock node ID: {mock_node.id}")
    print(f"Print node ID: {print_node.id}")
    
    # Add nodes to pipeline
    pipeline.add_node(mock_node)
    pipeline.add_node(print_node)
    
    print(f"Pipeline nodes: {list(pipeline.nodes.keys())}")
    
    # Connect nodes
    connection_id = pipeline.connect_nodes(mock_node.id, "mock_data", print_node.id, "data")
    print(f"Connection ID: {connection_id}")
    print(f"Pipeline connections: {list(pipeline.connections.keys())}")
    
    # Test MockNode processing first
    print("\n--- Testing MockNode alone ---")
    mock_success = mock_node.process()
    print(f"MockNode process success: {mock_success}")
    mock_data = mock_node.get_output_value("mock_data")
    print(f"MockNode output: {mock_data}")
    
    # Test PrintNode with manual input
    print("\n--- Testing PrintNode with manual input ---")
    print_node.set_input_value("data", ["Test", "Data", "Manual"])
    print_success = print_node.process()
    print(f"PrintNode process success: {print_success}")
    
    # Now test the full pipeline
    print("\n--- Testing Full Pipeline ---")
    
    # Reset the mock node
    mock_node2 = MockNode("first_name", size=3)
    print_node2 = PrintNode()
    
    pipeline2 = Pipeline("Simple Test 2")
    pipeline2.add_node(mock_node2)
    pipeline2.add_node(print_node2)
    pipeline2.connect_nodes(mock_node2.id, "mock_data", print_node2.id, "data")
    
    # Execute pipeline
    results = pipeline2.execute()
    print(f"Pipeline results: {results}")
    
    # Check individual node outputs
    for node_id, result in results.items():
        node = pipeline2.nodes[node_id]
        print(f"Node {node.name} ({node_id}): success={result['success']}")
        print(f"  Outputs: {result['outputs']}")

if __name__ == "__main__":
    test_simple_pipeline()
