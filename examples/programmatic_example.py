"""
Example script demonstrating programmatic use of the node graph system
"""
from src.core import Pipeline, DataNode
from src.nodes import create_node, MathNode, TransformNode, AggregateNode


def create_simple_pipeline():
    """Create a simple data processing pipeline programmatically"""
    
    # Create a new pipeline
    pipeline = Pipeline("Example Pipeline")
    
    # Create nodes
    data_node = DataNode("Input Data", [1, 2, 3, 4, 5])
    transform_node = TransformNode("square")
    aggregate_node = AggregateNode("sum")
    print_node = create_node("print")
    
    # Add nodes to pipeline
    data_id = pipeline.add_node(data_node)
    transform_id = pipeline.add_node(transform_node)
    aggregate_id = pipeline.add_node(aggregate_node)
    print_id = pipeline.add_node(print_node)
    
    # Connect nodes
    pipeline.connect_nodes(data_id, "output", transform_id, "data")
    pipeline.connect_nodes(transform_id, "transformed_data", aggregate_id, "data")
    pipeline.connect_nodes(aggregate_id, "result", print_id, "data")
    
    return pipeline


def create_complex_pipeline():
    """Create a more complex pipeline with branching"""
    
    pipeline = Pipeline("Complex Pipeline")
    
    # Create data nodes
    data1 = DataNode("Data 1", [1, 2, 3, 4, 5])
    data2 = DataNode("Data 2", [6, 7, 8, 9, 10])
    
    # Create processing nodes
    join_node = create_node("join")
    split_node = create_node("split")
    filter_node = create_node("filter")
    math_node = MathNode("multiply")
    
    # Create aggregation nodes
    sum_node = AggregateNode("sum")
    mean_node = AggregateNode("mean")
    
    # Create output nodes
    print1 = create_node("print")
    print2 = create_node("print")
    
    # Add all nodes
    data1_id = pipeline.add_node(data1)
    data2_id = pipeline.add_node(data2)
    join_id = pipeline.add_node(join_node)
    split_id = pipeline.add_node(split_node)
    filter_id = pipeline.add_node(filter_node)
    math_id = pipeline.add_node(math_node)
    sum_id = pipeline.add_node(sum_node)
    mean_id = pipeline.add_node(mean_node)
    print1_id = pipeline.add_node(print1)
    print2_id = pipeline.add_node(print2)
    
    # Connect the pipeline
    # Join the two data sources
    pipeline.connect_nodes(data1_id, "output", join_id, "data1")
    pipeline.connect_nodes(data2_id, "output", join_id, "data2")
    
    # Split the joined data
    split_index_node = DataNode("Split Index", 5)  # Split at index 5
    split_index_id = pipeline.add_node(split_index_node)
    
    pipeline.connect_nodes(join_id, "joined_data", split_id, "data")
    pipeline.connect_nodes(split_index_id, "output", split_id, "split_index")
    
    # Process each branch differently
    pipeline.connect_nodes(split_id, "data1", sum_id, "data")
    pipeline.connect_nodes(split_id, "data2", filter_id, "data")
    
    # Set filter condition for positive numbers
    filter_node.input_ports["condition"].value = "positive"
    
    # Process filtered data
    pipeline.connect_nodes(filter_id, "filtered_data", mean_id, "data")
    
    # Output results
    pipeline.connect_nodes(sum_id, "result", print1_id, "data")
    pipeline.connect_nodes(mean_id, "result", print2_id, "data")
    
    return pipeline


def demonstrate_math_operations():
    """Demonstrate various math operations"""
    
    pipeline = Pipeline("Math Demo")
    
    # Create input data
    num1 = DataNode("Number 1", 10)
    num2 = DataNode("Number 2", 3)
    
    # Create math operations
    add_node = MathNode("add")
    subtract_node = MathNode("subtract")
    multiply_node = MathNode("multiply")
    divide_node = MathNode("divide")
    power_node = MathNode("power")
    
    # Create output nodes
    print_add = create_node("print")
    print_sub = create_node("print")
    print_mul = create_node("print")
    print_div = create_node("print")
    print_pow = create_node("print")
    
    # Add nodes
    num1_id = pipeline.add_node(num1)
    num2_id = pipeline.add_node(num2)
    add_id = pipeline.add_node(add_node)
    sub_id = pipeline.add_node(subtract_node)
    mul_id = pipeline.add_node(multiply_node)
    div_id = pipeline.add_node(divide_node)
    pow_id = pipeline.add_node(power_node)
    
    print_add_id = pipeline.add_node(print_add)
    print_sub_id = pipeline.add_node(print_sub)
    print_mul_id = pipeline.add_node(print_mul)
    print_div_id = pipeline.add_node(print_div)
    print_pow_id = pipeline.add_node(print_pow)
    
    # Connect all operations
    operations = [
        (add_id, print_add_id),
        (sub_id, print_sub_id),
        (mul_id, print_mul_id),
        (div_id, print_div_id),
        (pow_id, print_pow_id)
    ]
    
    for op_id, print_id in operations:
        pipeline.connect_nodes(num1_id, "output", op_id, "a")
        pipeline.connect_nodes(num2_id, "output", op_id, "b")
        pipeline.connect_nodes(op_id, "result", print_id, "data")
    
    return pipeline


def main():
    """Run all examples"""
    
    print("=== Simple Pipeline Example ===")
    simple_pipeline = create_simple_pipeline()
    simple_results = simple_pipeline.execute()
    print(f"Execution results: {simple_results}")
    print()
    
    print("=== Complex Pipeline Example ===")
    complex_pipeline = create_complex_pipeline()
    complex_results = complex_pipeline.execute()
    print(f"Execution results: {complex_results}")
    print()
    
    print("=== Math Operations Example ===")
    math_pipeline = demonstrate_math_operations()
    math_results = math_pipeline.execute()
    print(f"Execution results: {math_results}")
    print()
    
    print("=== Pipeline Analysis ===")
    print(f"Simple pipeline execution order: {simple_pipeline.get_execution_order()}")
    print(f"Complex pipeline execution order: {complex_pipeline.get_execution_order()}")
    print(f"Math pipeline execution order: {math_pipeline.get_execution_order()}")


if __name__ == "__main__":
    main()
