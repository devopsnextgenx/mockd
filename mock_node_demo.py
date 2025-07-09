#!/usr/bin/env python3
"""
MockNode Demonstration Script
This script shows how the MockNode would work once Mimesis is properly installed.
"""

def demo_mock_node_usage():
    """
    Demonstrates how to use the MockNode for generating mock data
    """
    print("=== MockNode Usage Demonstration ===\n")
    
    print("The MockNode supports the following data types:")
    data_types = [
        "text", "word", "sentence", "first_name", "last_name", "full_name",
        "email", "phone", "age", "integer", "float", "date", "datetime",
        "address", "city", "country", "zipcode", "url", "username", 
        "password", "uuid", "boolean", "programming_language", "database", "os"
    ]
    
    for i, dtype in enumerate(data_types, 1):
        print(f"{i:2d}. {dtype}")
    
    print("\n=== Example Usage ===")
    
    examples = [
        {
            "description": "Generate 5 email addresses",
            "code": 'mock_node = MockNode("email", size=5)',
            "expected": "['john@example.com', 'jane@company.org', ...]"
        },
        {
            "description": "Generate 10 integers between 1 and 100",
            "code": 'mock_node = MockNode("integer", size=10, min_length=1, max_length=100)',
            "expected": "[45, 23, 89, 67, 12, ...]"
        },
        {
            "description": "Generate 3 text strings with length 10-50 characters",
            "code": 'mock_node = MockNode("text", size=3, min_length=10, max_length=50)',
            "expected": "['Lorem ipsum dolor...', 'Consectetur adipiscing...', ...]"
        },
        {
            "description": "Generate 5 phone numbers",
            "code": 'mock_node = MockNode("phone", size=5)',
            "expected": "['+1-555-123-4567', '+1-555-987-6543', ...]"
        },
        {
            "description": "Generate 4 full names",
            "code": 'mock_node = MockNode("full_name", size=4)',
            "expected": "['John Smith', 'Jane Doe', 'Bob Johnson', ...]"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}")
        print(f"   Code: {example['code']}")
        print(f"   Expected: {example['expected']}")
    
    print("\n=== Pipeline Usage ===")
    print("""
# Create a data generation pipeline
mock_node = MockNode("integer", size=100, min_length=1, max_length=1000)
filter_node = FilterNode()  # Filter positive numbers
aggregate_node = AggregateNode("mean")  # Calculate average

# Connect nodes
success = mock_node.process()
if success:
    data = mock_node.get_output_value("mock_data")
    filter_node.set_input_value("data", data)
    filter_node.set_input_value("condition", "positive")
    
    if filter_node.process():
        filtered_data = filter_node.get_output_value("filtered_data")
        aggregate_node.set_input_value("data", filtered_data)
        
        if aggregate_node.process():
            result = aggregate_node.get_output_value("result")
            print(f"Average of generated numbers: {result}")
    """)

def show_mock_node_features():
    """
    Shows the key features of the MockNode
    """
    print("\n=== MockNode Key Features ===")
    
    features = [
        "✓ Configurable data types (25+ supported types)",
        "✓ Adjustable data size (number of items to generate)",
        "✓ Length constraints (min_length, max_length for applicable types)",
        "✓ Input ports for dynamic configuration",
        "✓ Pipeline-ready with input/output ports",
        "✓ Error handling and validation",
        "✓ Compatible with existing processing nodes",
        "✓ Extensible for new data types"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n=== Node Configuration ===")
    print("""
Input Ports:
- size (int): Override default number of items to generate
- min_length (int): Minimum length/value for applicable data types
- max_length (int): Maximum length/value for applicable data types

Output Ports:
- mock_data (List): Generated mock data items

Constructor Parameters:
- data_type (str): Type of data to generate (default: "text")
- size (int): Number of items to generate (default: 10)
- min_length (int): Minimum constraint (optional)
- max_length (int): Maximum constraint (optional)
    """)

if __name__ == "__main__":
    demo_mock_node_usage()
    show_mock_node_features()
    
    print("\n" + "="*60)
    print("Note: To use the MockNode, ensure Mimesis is installed:")
    print("pip install mimesis")
    print("="*60)
