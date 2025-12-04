#!/usr/bin/env python3
"""
Tìm node chứa đoạn OpenOffice.org và xem community summary
"""

import pickle
import networkx as nx

def find_openoffice_node():
    print("🔍 Tìm node chứa đoạn OpenOffice.org")
    print("="*60)
    
    # Load graph
    with open('document_graph/graph.pkl', 'rb') as f:
        graph_data = pickle.load(f)
    
    graph = graph_data['graph']
    print(f"📊 Graph có {graph.number_of_nodes()} nodes")
    
    # Search text
    search_text = "OpenOffice.org"
    search_text_2 = "StarOffice"
    
    # Find nodes containing the text
    matching_nodes = []
    
    for node_id in graph.nodes():
        content = graph.nodes[node_id].get('content', '')
        
        if search_text in content and search_text_2 in content:
            matching_nodes.append(node_id)
            print(f"\n📄 Found Node {node_id}")
            print(f"   Content preview: {content[:200]}...")
            
            # Get community info
            community_id = graph.nodes[node_id].get('community', 'N/A')
            print(f"   Community: {community_id}")
            
    if not matching_nodes:
        print("❌ Không tìm thấy node chứa OpenOffice.org")
        return
    
    # Get community summary for the first matching node
    target_node = matching_nodes[0]
    community_id = graph.nodes[target_node].get('community')
    
    print(f"\n🏘️ Community {community_id} Summary:")
    print("="*60)
    
    # Load partitioner to get community summary
    from src.graph_rag.subgraph_partitioner import SubgraphPartitioner
    
    partitioner = SubgraphPartitioner(graph)
    
    # Reconstruct communities from nodes
    communities = {}
    for node_id, node_data in graph.nodes(data=True):
        comm_id = node_data.get('community', 0)
        if comm_id not in communities:
            communities[comm_id] = set()
        communities[comm_id].add(node_id)
    
    partitioner.subgraphs = communities
    
    # Check if we have saved community summaries
    if hasattr(graph_data, 'community_summaries'):
        summaries = graph_data.get('community_summaries', {})
        if community_id in summaries:
            print(f"📋 Summary: {summaries[community_id]}")
        else:
            print("❌ Không có summary được lưu trong graph")
    else:
        print("❌ Không có community summaries trong graph data")
    
    # Show community stats
    community_nodes = communities.get(community_id, set())
    print(f"\n📊 Community {community_id} Stats:")
    print(f"   Nodes: {len(community_nodes)}")
    print(f"   Target node: {target_node}")
    
    # Show other nodes in same community
    print(f"\n📋 Các nodes khác trong Community {community_id}:")
    for i, node_id in enumerate(sorted(list(community_nodes))[:10], 1):
        content = graph.nodes[node_id].get('content', '')
        content_preview = content[:80].replace('\n', ' ')
        
        if node_id == target_node:
            print(f"   🎯 {i:2d}. Node {node_id} (OPENOFFICE!) - {content_preview}...")
        else:
            print(f"      {i:2d}. Node {node_id} - {content_preview}...")

if __name__ == "__main__":
    find_openoffice_node()