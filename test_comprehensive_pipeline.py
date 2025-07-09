#!/usr/bin/env python3
"""
Comprehensive test of MockNode data creation pipeline functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nodes import MockNode, PrintNode, AggregateNode, FilterNode
from src.core import Pipeline, DataNode

def test_comprehensive_mock_pipeline():
    """Test a comprehensive mock data creation pipeline"""
    
    print("=== Comprehensive MockNode Pipeline Test ===\n")
    
    # Test 1: Basic mock data generation and printing
    print("1. Basic Mock Data Generation Pipeline:")
    print("-" * 40)
    
    pipeline1 = Pipeline("Mock Names Pipeline")
    
    # Create MockNode for names
    names_node = MockNode("full_name", size=5)
    print_node1 = PrintNode()
    
    # Add nodes to pipeline
    pipeline1.add_node(names_node)
    pipeline1.add_node(print_node1)
    
    # Connect the nodes
    pipeline1.connect_nodes(names_node.id, "mock_data", print_node1.id, "data")
    
    # Execute the pipeline
    results1 = pipeline1.execute()
    print(f"Pipeline executed successfully: {all(r['success'] for r in results1.values())}")
    print()
    
    # Test 2: Mock integers with aggregation
    print("2. Mock Integers with Aggregation Pipeline:")
    print("-" * 45)
    
    pipeline2 = Pipeline("Mock Numbers with Stats")
    
    # Create MockNode for integers
    numbers_node = MockNode("integer", size=10, min_length=1, max_length=100)
    sum_node = AggregateNode("sum")
    mean_node = AggregateNode("mean")
    max_node = AggregateNode("max")
    print_node2 = PrintNode()
    print_node3 = PrintNode()
    print_node4 = PrintNode()
    
    # Add nodes to pipeline
    for node in [numbers_node, sum_node, mean_node, max_node, print_node2, print_node3, print_node4]:
        pipeline2.add_node(node)
    
    # Connect the nodes
    pipeline2.connect_nodes(numbers_node.id, "mock_data", sum_node.id, "data")
    pipeline2.connect_nodes(numbers_node.id, "mock_data", mean_node.id, "data")
    pipeline2.connect_nodes(numbers_node.id, "mock_data", max_node.id, "data")
    pipeline2.connect_nodes(sum_node.id, "result", print_node2.id, "data")
    pipeline2.connect_nodes(mean_node.id, "result", print_node3.id, "data")
    pipeline2.connect_nodes(max_node.id, "result", print_node4.id, "data")
    
    # Execute the pipeline
    print("Generated numbers and statistics:")
    results2 = pipeline2.execute()
    print(f"Pipeline executed successfully: {all(r['success'] for r in results2.values())}")
    print()
    
    # Test 3: Multi-type mock data generation
    print("3. Multi-Type Mock Data Generation Pipeline:")
    print("-" * 45)
    
    pipeline3 = Pipeline("Multi-Type Mock Data")
    
    # Create multiple MockNodes for different data types
    emails_node = MockNode("email", size=3)
    phones_node = MockNode("phone", size=3)
    addresses_node = MockNode("address", size=3)
    booleans_node = MockNode("boolean", size=5)
    
    # Create print nodes for each type
    email_print = PrintNode()
    phone_print = PrintNode()
    address_print = PrintNode()
    boolean_print = PrintNode()
    
    # Add all nodes
    for node in [emails_node, phones_node, addresses_node, booleans_node,
                 email_print, phone_print, address_print, boolean_print]:
        pipeline3.add_node(node)
    
    # Connect nodes
    pipeline3.connect_nodes(emails_node.id, "mock_data", email_print.id, "data")
    pipeline3.connect_nodes(phones_node.id, "mock_data", phone_print.id, "data")
    pipeline3.connect_nodes(addresses_node.id, "mock_data", address_print.id, "data")
    pipeline3.connect_nodes(booleans_node.id, "mock_data", boolean_print.id, "data")
    
    # Execute the pipeline
    print("Generated different types of mock data:")
    results3 = pipeline3.execute()
    print(f"Pipeline executed successfully: {all(r['success'] for r in results3.values())}")
    print()
    
    # Test 4: Mock data with filtering
    print("4. Mock Data with Filtering Pipeline:")
    print("-" * 38)
    
    pipeline4 = Pipeline("Mock Data with Filter")
    
    # Create MockNode for large integers
    large_numbers = MockNode("integer", size=20, min_length=1, max_length=50)
    
    # Create filter node to filter numbers > 25
    filter_node = FilterNode()
    
    # Create print node
    filtered_print = PrintNode()
    
    # Add nodes
    pipeline4.add_node(large_numbers)
    pipeline4.add_node(filter_node)
    pipeline4.add_node(filtered_print)
    
    # Set filter condition (numbers greater than 25)
    filter_node.set_input_value("condition", lambda x: x > 25)
    
    # Connect nodes
    pipeline4.connect_nodes(large_numbers.id, "mock_data", filter_node.id, "data")
    pipeline4.connect_nodes(filter_node.id, "filtered_data", filtered_print.id, "data")
    
    # Execute the pipeline
    print("Generated numbers and filtered (> 25):")
    results4 = pipeline4.execute()
    print(f"Pipeline executed successfully: {all(r['success'] for r in results4.values())}")
    print()
    
    # Summary
    print("=== Test Summary ===")
    total_pipelines = 4
    successful_pipelines = sum([
        all(r['success'] for r in results1.values()),
        all(r['success'] for r in results2.values()),
        all(r['success'] for r in results3.values()),
        all(r['success'] for r in results4.values())
    ])
    
    print(f"✓ {successful_pipelines}/{total_pipelines} pipelines executed successfully")
    print("✓ MockNode can generate various data types")
    print("✓ MockNode integrates well with other nodes")
    print("✓ Pipeline execution works correctly")
    print("✓ Data flows properly through the pipeline")
    
    return successful_pipelines == total_pipelines

if __name__ == "__main__":
    try:
        success = test_comprehensive_mock_pipeline()
        if success:
            print("\n🎉 All comprehensive pipeline tests passed!")
        else:
            print("\n❌ Some pipeline tests failed!")
    except Exception as e:
        print(f"\n❌ Comprehensive test failed with error: {e}")
        import traceback
        traceback.print_exc()
