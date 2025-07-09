#!/usr/bin/env python3
"""
Test script for MockNode functionality
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nodes import MockNode

def test_mock_node():
    print("Testing MockNode functionality...")
    
    # Test different data types
    test_cases = [
        {"data_type": "text", "size": 5, "min_length": 10, "max_length": 50},
        {"data_type": "first_name", "size": 3},
        {"data_type": "email", "size": 4},
        {"data_type": "integer", "size": 5, "min_length": 1, "max_length": 100},
        {"data_type": "float", "size": 3, "min_length": 0, "max_length": 10},
        {"data_type": "phone", "size": 2},
        {"data_type": "address", "size": 2},
        {"data_type": "url", "size": 3},
        {"data_type": "boolean", "size": 5},
        {"data_type": "uuid", "size": 2},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['data_type']} ---")
        
        # Create MockNode with test parameters
        node = MockNode(**test_case)
        
        # Process the node
        success = node.process()
        
        if success:
            # Get the generated data
            mock_data = node.get_output_value("mock_data")
            print(f"✓ Generated {len(mock_data)} items of type '{test_case['data_type']}'")
            print(f"Sample data: {mock_data[:3]}")  # Show first 3 items
            
            # Validate size
            expected_size = test_case.get('size', 10)
            if len(mock_data) == expected_size:
                print(f"✓ Size validation passed: {len(mock_data)} items")
            else:
                print(f"✗ Size validation failed: expected {expected_size}, got {len(mock_data)}")
                
            # Validate length constraints for text data
            if test_case['data_type'] in ['text', 'word'] and 'min_length' in test_case:
                min_len = test_case['min_length']
                max_len = test_case.get('max_length')
                for item in mock_data:
                    if isinstance(item, str):
                        if len(item) < min_len:
                            print(f"✗ Length validation failed: '{item}' is shorter than {min_len}")
                        elif max_len and len(item) > max_len:
                            print(f"✗ Length validation failed: '{item}' is longer than {max_len}")
                print(f"✓ Length constraints validated")
                        
        else:
            print(f"✗ Node processing failed for {test_case['data_type']}")

def test_node_chaining():
    print("\n\n=== Testing Node Chaining ===")
    
    # Import additional nodes for chaining test
    from nodes import PrintNode
    
    # Create MockNode for integers
    mock_node = MockNode("integer", size=10, min_length=1, max_length=50)
    
    # Create PrintNode to display results
    print_node = PrintNode()
    
    # Process mock node
    print("1. Generating mock integers...")
    success = mock_node.process()
    
    if success:
        mock_data = mock_node.get_output_value("mock_data")
        print(f"✓ Generated: {mock_data}")
        
        # Chain to print node
        print_node.set_input_value("data", mock_data)
        print("2. Chaining to PrintNode...")
        print_success = print_node.process()
        
        if print_success:
            print("✓ Node chaining successful!")
        else:
            print("✗ Node chaining failed!")
    else:
        print("✗ Mock node processing failed!")

if __name__ == "__main__":
    try:
        test_mock_node()
        test_node_chaining()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
