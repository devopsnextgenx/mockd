# Node Graph Pipeline Editor

A powerful GUI application for creating and managing data processing pipelines using visual node-based programming. Built with PySide6 (Qt) for a professional, modern interface.

## Features

### Visual Node Editor
- **Drag & Drop Interface**: Intuitive node-based visual programming
- **Real-time Connections**: Connect nodes with visual cables
- **Node Palette**: Organized library of available processing nodes
- **Property Panel**: Edit node parameters and settings
- **Zoom & Pan**: Navigate large pipelines easily

### Built-in Node Types
- **Data Nodes**: Static data sources and inputs
- **Math Nodes**: Basic arithmetic operations (add, subtract, multiply, divide, power, modulo)
- **Transform Nodes**: Data transformations (square, sqrt, abs, log, normalize)
- **Filter Nodes**: Data filtering (positive, negative, even, odd)
- **Aggregate Nodes**: Statistical operations (sum, mean, min, max, count, std, median)
- **Utility Nodes**: Join, split, and print operations

### Pipeline Management
- **Execution Engine**: Automatic topological sorting and execution
- **Validation**: Cycle detection and dependency checking
- **Save/Load**: JSON-based pipeline persistence
- **Auto-save**: Automatic backup functionality

### Programmatic API
- **Core Classes**: `ProcessNode`, `DataNode`, `Pipeline`
- **Custom Nodes**: Easy creation of custom processing nodes
- **Programmatic Control**: Build and execute pipelines in code

## Why PySide6/Qt Over CustomTkinter?

For this node graph editor, **PySide6 (Qt) is the superior choice** because:

1. **Advanced Graphics Framework**: 
   - `QGraphicsView` and `QGraphicsScene` are specifically designed for complex 2D graphics
   - Built-in support for transformations, animations, and complex visual elements
   - Optimized rendering for large numbers of graphical objects

2. **Professional GUI Components**:
   - Modern, native-looking interface across all platforms
   - Rich set of widgets with advanced features
   - Better theming and styling capabilities

3. **Drag & Drop Excellence**:
   - Sophisticated drag-and-drop framework built-in
   - Easy handling of custom drag operations
   - Visual feedback during drag operations

4. **Performance**:
   - Hardware-accelerated rendering when available
   - Efficient handling of complex visual scenes
   - Better memory management for graphics

5. **Extensibility**:
   - Large ecosystem of Qt-based tools and libraries
   - Professional development practices and patterns
   - Better support for complex applications

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mockd
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Quick Start

### Using the GUI

1. **Launch the Application**:
   ```bash
   python main.py
   ```

2. **Add Nodes**:
   - Double-click items in the Node Palette (left panel)
   - Nodes will appear in the center canvas

3. **Connect Nodes**:
   - Click and drag from output ports (right side, orange) to input ports (left side, blue)
   - Connections are drawn as curved lines

4. **Set Data**:
   - Select a Data node and use the Properties panel (right side) to set values
   - For example, set a list like `[1, 2, 3, 4, 5]`

5. **Execute Pipeline**:
   - Press F5 or use Pipeline → Execute Pipeline
   - View results in the execution dialog

### Programmatic Usage

```python
from src.core import Pipeline, DataNode
from src.nodes import create_node, MathNode

# Create a pipeline
pipeline = Pipeline("My Pipeline")

# Create nodes
data_node = DataNode("Input", [1, 2, 3, 4, 5])
transform_node = create_node("transform_square")
sum_node = create_node("aggregate_sum")

# Add to pipeline
data_id = pipeline.add_node(data_node)
transform_id = pipeline.add_node(transform_node)
sum_id = pipeline.add_node(sum_node)

# Connect nodes
pipeline.connect_nodes(data_id, "output", transform_id, "data")
pipeline.connect_nodes(transform_id, "transformed_data", sum_id, "data")

# Execute
results = pipeline.execute()
print(results)
```

## Creating Custom Nodes

```python
from src.core import ProcessNode

class CustomMathNode(ProcessNode):
    def __init__(self):
        super().__init__("Custom Math")
        self.add_input_port("x", float)
        self.add_input_port("y", float)
        self.add_output_port("result", float)
    
    def process(self) -> bool:
        x = self.get_input_value("x")
        y = self.get_input_value("y")
        
        if x is not None and y is not None:
            # Custom operation: (x^2 + y^2)^0.5
            result = (x**2 + y**2)**0.5
            self.set_output_value("result", result)
            return True
        return False
```

## Example Pipelines

Check the `examples/` directory for:
- **Basic Pipeline**: Simple data transformation
- **Complex Pipeline**: Multi-branch processing with joins and splits
- **Math Operations**: Demonstration of all math nodes
- **Custom Nodes**: How to create and use custom processing nodes

## Architecture

### Core Components

- **`src/core.py`**: Core data structures (`ProcessNode`, `Pipeline`, `NodePort`)
- **`src/nodes.py`**: Built-in node implementations
- **`src/gui.py`**: Qt-based GUI components
- **`src/main_app.py`**: Main application window and logic

### Key Design Patterns

- **Abstract Base Classes**: `ProcessNode` for consistent node interface
- **Observer Pattern**: Qt signals for GUI updates
- **Command Pattern**: For undo/redo functionality (future)
- **Factory Pattern**: Node creation and registration

## File Format

Pipelines are saved in JSON format:

```json
{
  "name": "My Pipeline",
  "nodes": [
    {
      "id": "node-uuid",
      "type": "data",
      "name": "Input Data",
      "position": [100, 100],
      "data": [1, 2, 3, 4, 5]
    }
  ],
  "connections": [
    {
      "id": "connection-uuid",
      "source_node": "source-node-uuid",
      "source_port": "output",
      "target_node": "target-node-uuid",
      "target_port": "input"
    }
  ]
}
```

## Keyboard Shortcuts

- **Ctrl+N**: New pipeline
- **Ctrl+O**: Open pipeline
- **Ctrl+S**: Save pipeline
- **Ctrl+Shift+S**: Save As
- **F5**: Execute pipeline
- **Delete**: Delete selected nodes
- **Mouse Wheel**: Zoom in/out
- **Middle Mouse**: Pan view

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom nodes or improvements
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Future Enhancements

- **Undo/Redo System**: Command pattern implementation
- **Node Groups**: Collapse related nodes into groups
- **Subgraphs**: Reusable pipeline components
- **Python Code Export**: Generate Python scripts from pipelines
- **Plugin System**: Dynamic loading of custom node libraries
- **Performance Profiling**: Execution timing and optimization
- **Remote Execution**: Distribute pipeline execution across machines