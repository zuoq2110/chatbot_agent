#!/usr/bin/env python3
"""
Check graph structure and analyze node 799 neighbors
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pickle
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def inspect_graph_structure():
    """Inspect the structure of the saved graph"""
    graph_file = Path("document_graph/graph.pkl")
    if not graph_file.exists():
        raise FileNotFoundError("Graph file not found!")
    
    with open(graph_file, 'rb') as f:
        data = pickle.load(f)
    
    print("🔍 Graph file structure:")
    print(f"   Keys: {list(data.keys())}")
    
    for key, value in data.items():
        print(f"   {key}: {type(value)}")
        if hasattr(value, '__len__'):
            try:
                print(f"      Length: {len(value)}")
            except:
                pass
    
    return data

def analyze_node_799(data):
    """Analyze node 799 specifically"""
    graph = data['graph']
    
    print(f"\n{'='*80}")
    print(f"🔍 ANALYZING NODE 799")
    print(f"{'='*80}")
    
    if 799 not in graph:
        print("❌ Node 799 not found in graph!")
        return
    
    # Get node data
    node_data = graph.nodes[799]
    print(f"📄 NODE 799 DATA:")
    for key, value in node_data.items():
        if key == 'content':
            print(f"   {key}: {str(value)[:100]}...")
        else:
            print(f"   {key}: {value}")
    
    # Get neighbors
    neighbors = list(graph.neighbors(799))
    print(f"\n🔗 DIRECT NEIGHBORS: {len(neighbors)} nodes")
    
    # Group neighbors by source and chunk
    same_file_neighbors = []
    other_neighbors = []
    
    target_source = node_data.get('source', node_data.get('filename', 'Unknown'))
    target_chunk = node_data.get('chunk_index', -1)
    
    print(f"Target file: {target_source}, chunk: {target_chunk}")
    
    for neighbor in neighbors[:10]:  # Show first 10 neighbors
        neighbor_data = graph.nodes[neighbor]
        neighbor_source = neighbor_data.get('source', neighbor_data.get('filename', 'Unknown'))
        neighbor_chunk = neighbor_data.get('chunk_index', -1)
        
        if neighbor_source == target_source:
            same_file_neighbors.append((neighbor, neighbor_chunk, neighbor_data))
        else:
            other_neighbors.append((neighbor, neighbor_chunk, neighbor_data))
    
    # Show same file neighbors
    print(f"\n📋 SAME FILE NEIGHBORS:")
    if same_file_neighbors:
        same_file_neighbors.sort(key=lambda x: x[1])
        for neighbor, chunk_idx, neighbor_data in same_file_neighbors:
            distance = abs(chunk_idx - target_chunk)
            print(f"   Node {neighbor}: chunk {chunk_idx} (distance: {distance})")
            content = neighbor_data.get('content', '')[:80]
            print(f"      Content: {content}...")
    else:
        print("   ❌ No same-file neighbors found!")
    
    # Check for missing adjacent chunks
    print(f"\n🔍 CHECKING FOR ADJACENT CHUNKS IN GRAPH:")
    
    # Find all nodes from same file
    all_same_file = []
    for node in graph.nodes():
        node_data_iter = graph.nodes[node]
        source = node_data_iter.get('source', node_data_iter.get('filename', 'Unknown'))
        if source == target_source:
            chunk_idx = node_data_iter.get('chunk_index', -1)
            all_same_file.append((node, chunk_idx, node_data_iter))
    
    all_same_file.sort(key=lambda x: x[1])
    
    print(f"   Total chunks from {target_source}: {len(all_same_file)}")
    
    # Find adjacent chunks
    target_index = None
    for i, (node, chunk_idx, _) in enumerate(all_same_file):
        if node == 799:
            target_index = i
            break
    
    if target_index is not None:
        # Show context around target
        start_idx = max(0, target_index - 3)
        end_idx = min(len(all_same_file), target_index + 4)
        
        print(f"   Context around chunk {target_chunk}:")
        for i in range(start_idx, end_idx):
            node, chunk_idx, node_data_context = all_same_file[i]
            marker = "🎯" if node == 799 else "📄"
            connected = "✅" if node in neighbors or node == 799 else "❌"
            print(f"      {marker} Node {node}: chunk {chunk_idx} {connected}")
            
            # Check specific adjacency
            if abs(chunk_idx - target_chunk) == 1:
                connected_to_target = graph.has_edge(799, node)
                print(f"         Adjacent to target: {'✅ CONNECTED' if connected_to_target else '❌ NOT CONNECTED'}")

def main():
    """Main analysis function"""
    try:
        # Inspect graph structure
        data = inspect_graph_structure()
        
        # Analyze node 799
        analyze_node_799(data)
        
        print(f"\n{'='*80}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()