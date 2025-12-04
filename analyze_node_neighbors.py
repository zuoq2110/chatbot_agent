#!/usr/bin/env python3
"""
Analyze neighbors of node 799 to understand why adjacent documents weren't retrieved
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pickle
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_graph():
    """Load the pre-built graph"""
    graph_file = Path("document_graph/graph.pkl")
    if not graph_file.exists():
        raise FileNotFoundError("Graph file not found!")
    
    with open(graph_file, 'rb') as f:
        data = pickle.load(f)
    
    return data['graph'], data['node_to_doc']

def analyze_node_neighbors(graph, node_to_doc, target_node=799):
    """Analyze neighbors of target node"""
    print(f"\n{'='*80}")
    print(f"🔍 ANALYZING NODE {target_node} AND ITS NEIGHBORS")
    print(f"{'='*80}")
    
    # Get target node info
    if target_node not in graph:
        print(f"❌ Node {target_node} not found in graph!")
        return
        
    target_doc = node_to_doc[target_node]
    print(f"📄 TARGET NODE {target_node}:")
    print(f"   Source: {target_doc.get('source', 'Unknown')}")
    print(f"   Chunk: {target_doc.get('chunk_index', 'Unknown')}/{target_doc.get('total_chunks', 'Unknown')}")
    print(f"   Content preview: {target_doc.get('content', '')[:100]}...")
    
    # Get all neighbors
    neighbors = list(graph.neighbors(target_node))
    print(f"\n🔗 DIRECT NEIGHBORS: {len(neighbors)} nodes")
    
    # Group neighbors by source file and chunk index
    file_neighbors = {}
    for neighbor in neighbors:
        neighbor_doc = node_to_doc[neighbor]
        source = neighbor_doc.get('source', 'Unknown')
        chunk_idx = neighbor_doc.get('chunk_index', -1)
        
        if source not in file_neighbors:
            file_neighbors[source] = []
        file_neighbors[source].append((neighbor, chunk_idx, neighbor_doc))
    
    # Analyze same-file neighbors
    target_source = target_doc.get('source', 'Unknown')
    target_chunk = target_doc.get('chunk_index', -1)
    
    print(f"\n📋 SAME FILE NEIGHBORS (from {target_source}):")
    if target_source in file_neighbors:
        same_file_neighbors = sorted(file_neighbors[target_source], key=lambda x: x[1])
        for neighbor, chunk_idx, neighbor_doc in same_file_neighbors:
            distance = abs(chunk_idx - target_chunk)
            print(f"   Node {neighbor}: chunk {chunk_idx} (distance: {distance})")
            print(f"      Content: {neighbor_doc.get('content', '')[:80]}...")
            
        # Check for missing adjacent chunks
        print(f"\n🔍 CHECKING ADJACENT CHUNKS:")
        print(f"   Target chunk: {target_chunk}")
        
        # Check previous chunk
        prev_chunk = target_chunk - 1
        prev_node = None
        for neighbor, chunk_idx, _ in same_file_neighbors:
            if chunk_idx == prev_chunk:
                prev_node = neighbor
                break
        
        if prev_node:
            print(f"   ✅ Previous chunk {prev_chunk}: Node {prev_node} (connected)")
        else:
            print(f"   ❌ Previous chunk {prev_chunk}: NOT CONNECTED")
            
        # Check next chunk  
        next_chunk = target_chunk + 1
        next_node = None
        for neighbor, chunk_idx, _ in same_file_neighbors:
            if chunk_idx == next_chunk:
                next_node = neighbor
                break
                
        if next_node:
            print(f"   ✅ Next chunk {next_chunk}: Node {next_node} (connected)")
        else:
            print(f"   ❌ Next chunk {next_chunk}: NOT CONNECTED")
    else:
        print(f"   ❌ No same-file neighbors found!")
    
    # Show other file neighbors
    print(f"\n📚 OTHER FILE NEIGHBORS:")
    for source, neighbors_list in file_neighbors.items():
        if source != target_source:
            print(f"   From {source}: {len(neighbors_list)} neighbors")
            for neighbor, chunk_idx, neighbor_doc in neighbors_list[:3]:  # Show first 3
                print(f"      Node {neighbor}: chunk {chunk_idx}")
    
    return neighbors

def find_adjacent_chunks_in_graph(graph, node_to_doc, target_node=799):
    """Find if adjacent chunks exist in graph at all"""
    print(f"\n{'='*80}")
    print(f"🔍 SEARCHING FOR ADJACENT CHUNKS IN ENTIRE GRAPH")
    print(f"{'='*80}")
    
    target_doc = node_to_doc[target_node]
    target_source = target_doc.get('source', 'Unknown')
    target_chunk = target_doc.get('chunk_index', -1)
    
    print(f"Target: {target_source}, chunk {target_chunk}")
    
    # Find all nodes from same file
    same_file_nodes = []
    for node, doc in node_to_doc.items():
        if doc.get('source') == target_source:
            chunk_idx = doc.get('chunk_index', -1)
            same_file_nodes.append((node, chunk_idx, doc))
    
    # Sort by chunk index
    same_file_nodes.sort(key=lambda x: x[1])
    
    print(f"\n📄 ALL CHUNKS FROM {target_source}:")
    for node, chunk_idx, doc in same_file_nodes:
        distance = abs(chunk_idx - target_chunk)
        marker = "🎯" if node == target_node else "📄"
        print(f"   {marker} Node {node}: chunk {chunk_idx} (distance: {distance})")
        
        # Show adjacent chunks specifically
        if abs(distance) <= 2 and distance != 0:
            print(f"      Content: {doc.get('content', '')[:100]}...")
    
    # Check connectivity of adjacent chunks
    print(f"\n🔗 ADJACENCY ANALYSIS:")
    target_index = None
    for i, (node, chunk_idx, _) in enumerate(same_file_nodes):
        if node == target_node:
            target_index = i
            break
    
    if target_index is not None:
        # Check previous chunk
        if target_index > 0:
            prev_node, prev_chunk, _ = same_file_nodes[target_index - 1]
            connected = graph.has_edge(target_node, prev_node)
            print(f"   Previous chunk {prev_chunk} (Node {prev_node}): {'✅ CONNECTED' if connected else '❌ NOT CONNECTED'}")
        
        # Check next chunk
        if target_index < len(same_file_nodes) - 1:
            next_node, next_chunk, _ = same_file_nodes[target_index + 1]
            connected = graph.has_edge(target_node, next_node)
            print(f"   Next chunk {next_chunk} (Node {next_node}): {'✅ CONNECTED' if connected else '❌ NOT CONNECTED'}")

def main():
    """Main analysis function"""
    try:
        # Load graph
        print("📊 Loading graph...")
        graph, node_to_doc = load_graph()
        print(f"✅ Graph loaded: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        # Analyze target node
        neighbors = analyze_node_neighbors(graph, node_to_doc, 799)
        
        # Search for adjacent chunks
        find_adjacent_chunks_in_graph(graph, node_to_doc, 799)
        
        print(f"\n{'='*80}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()