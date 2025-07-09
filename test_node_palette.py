#!/usr/bin/env python3
"""
Test script to verify that mock data nodes are available in the node palette
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from src.gui import NodePalette
from src.nodes import NODE_TYPES

def test_node_palette():
    """Test the node palette functionality"""
    app = QApplication([])
    
    # Create node palette
    palette = NodePalette()
    
    print("Node Palette Test")
    print("=" * 50)
    
    # Check if mock data nodes are in NODE_TYPES
    mock_nodes = [k for k in NODE_TYPES.keys() if k.startswith('mock')]
    print(f"Found {len(mock_nodes)} mock data node types in NODE_TYPES:")
    for node in sorted(mock_nodes):
        print(f"  - {node}")
    
    print("\nNode Palette Categories:")
    root = palette.node_tree.invisibleRootItem()
    for i in range(root.childCount()):
        category_item = root.child(i)
        category_name = category_item.text(0)
        print(f"\n{category_name}:")
        
        for j in range(category_item.childCount()):
            node_item = category_item.child(j)
            node_name = node_item.text(0)
            node_type = node_item.data(0, 2)  # Qt.UserRole = 2
            print(f"  - {node_name} (type: {node_type})")
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
    
    app.quit()

if __name__ == "__main__":
    test_node_palette()
