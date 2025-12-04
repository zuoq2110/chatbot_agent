#!/usr/bin/env python3
"""
Kiểm tra chi tiết graph data chứa những gì
"""

import pickle
import networkx as nx

def inspect_graph_data():
    print("🔍 Kiểm tra chi tiết graph data")
    print("="*60)
    
    # Load graph
    with open('document_graph/graph.pkl', 'rb') as f:
        graph_data = pickle.load(f)
    
    print(f"📊 Graph data type: {type(graph_data)}")
    print(f"📋 Keys in graph_data: {list(graph_data.keys())}")
    
    # Inspect each key
    for key, value in graph_data.items():
        print(f"\n🔑 Key: '{key}'")
        print(f"   Type: {type(value)}")
        
        if key == 'graph':
            graph = value
            print(f"   Nodes: {graph.number_of_nodes()}")
            print(f"   Edges: {graph.number_of_edges()}")
            
            # Check node attributes
            sample_nodes = list(graph.nodes(data=True))[:3]
            print(f"   Sample node attributes:")
            for node_id, node_data in sample_nodes:
                print(f"      Node {node_id}: {list(node_data.keys())}")
                
        elif key == 'doc_embeddings':
            print(f"   Length: {len(value) if hasattr(value, '__len__') else 'N/A'}")
            if hasattr(value, 'keys'):
                print(f"   Keys: {list(value.keys())[:5]}...")
                
        elif key == 'semantic_threshold':
            print(f"   Value: {value}")
            
        else:
            if hasattr(value, '__len__'):
                print(f"   Length: {len(value)}")
            if hasattr(value, 'keys'):
                print(f"   Keys: {list(value.keys())[:5]}...")
            else:
                print(f"   Value: {str(value)[:100]}...")

    # Check if communities exist in nodes
    graph = graph_data['graph']
    community_nodes = {}
    
    print(f"\n🏘️ Community analysis:")
    for node_id, node_data in graph.nodes(data=True):
        comm_id = node_data.get('community')
        if comm_id is not None:
            if comm_id not in community_nodes:
                community_nodes[comm_id] = []
            community_nodes[comm_id].append(node_id)
    
    if community_nodes:
        print(f"   ✅ Found {len(community_nodes)} communities in nodes")
        for comm_id, nodes in sorted(community_nodes.items())[:5]:
            print(f"      Community {comm_id}: {len(nodes)} nodes")
    else:
        print(f"   ❌ No community attributes found in nodes")
    
    # Check for partitioner-related data
    partitioner_keys = [k for k in graph_data.keys() if 'community' in k.lower() or 'partition' in k.lower() or 'summary' in k.lower()]
    
    print(f"\n📊 Partitioner-related keys:")
    if partitioner_keys:
        for key in partitioner_keys:
            print(f"   ✅ Found: {key}")
    else:
        print(f"   ❌ No partitioner data found in graph_data")
    
    # Check for any saved partitioner state
    print(f"\n🔍 Looking for saved partitioner state...")
    potential_keys = ['partitioner', 'subgraphs', 'communities', 'community_summaries', 'community_centroids']
    
    for key in potential_keys:
        if key in graph_data:
            value = graph_data[key]
            print(f"   ✅ Found {key}: {type(value)}")
            if hasattr(value, '__len__'):
                print(f"      Length: {len(value)}")
        else:
            print(f"   ❌ Missing: {key}")

if __name__ == "__main__":
    inspect_graph_data()