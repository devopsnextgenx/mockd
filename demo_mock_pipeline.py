#!/usr/bin/env python3
"""
Demo script showing how to create and use mock data nodes programmatically
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core import Pipeline
from src.nodes import create_node

def demo_mock_data_pipeline():
    """Demonstrate creating a pipeline with mock data nodes"""
    print("Mock Data Pipeline Demo")
    print("=" * 50)
    
    # Create a pipeline
    pipeline = Pipeline("Mock Data Demo")
    
    # Create mock data nodes
    names_node = create_node("mock_full_names")
    emails_node = create_node("mock_emails") 
    ages_node = create_node("mock_ages")
    
    # Create utility nodes
    print_names = create_node("print")
    print_emails = create_node("print")
    print_ages = create_node("print")
    
    # Add nodes to pipeline
    names_id = pipeline.add_node(names_node)
    emails_id = pipeline.add_node(emails_node)
    ages_id = pipeline.add_node(ages_node)
    print_names_id = pipeline.add_node(print_names)
    print_emails_id = pipeline.add_node(print_emails)
    print_ages_id = pipeline.add_node(print_ages)
    
    # Connect mock data to print nodes
    pipeline.connect_nodes(names_id, "mock_data", print_names_id, "data")
    pipeline.connect_nodes(emails_id, "mock_data", print_emails_id, "data")
    pipeline.connect_nodes(ages_id, "mock_data", print_ages_id, "data")
    
    print(f"Created pipeline with {len(pipeline.nodes)} nodes")
    print("\nExecuting pipeline...")
    
    # Execute the pipeline
    results = pipeline.execute()
    
    print(f"\nExecution completed. Success rate: {sum(1 for r in results.values() if r['success'])}/{len(results)}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")

if __name__ == "__main__":
    demo_mock_data_pipeline()
