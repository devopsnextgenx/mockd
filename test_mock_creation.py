#!/usr/bin/env python3
"""
Test script to verify that mock data nodes can be created and executed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.nodes import create_node, NODE_TYPES

def test_mock_node_creation():
    """Test creating and executing mock data nodes"""
    print("Mock Data Node Creation Test")
    print("=" * 50)
    
    # Test a few representative mock nodes
    test_nodes = [
        "mock",
        "mock_text", 
        "mock_full_names",
        "mock_emails",
        "mock_integers",
        "mock_dates",
        "mock_addresses"
    ]
    
    for node_type in test_nodes:
        print(f"\nTesting {node_type}:")
        try:
            # Create the node
            node = create_node(node_type)
            print(f"  ✓ Created: {node.name}")
            
            # Test if it can execute
            can_execute = node.can_execute()
            print(f"  ✓ Can execute: {can_execute}")
            
            # Try to process it
            if can_execute:
                success = node.process()
                print(f"  ✓ Process success: {success}")
                
                # Get the output
                if success and "mock_data" in node.output_ports:
                    output = node.get_output_value("mock_data")
                    if output:
                        print(f"  ✓ Generated {len(output)} items")
                        print(f"  ✓ Sample: {output[0] if output else 'None'}")
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_mock_node_creation()
