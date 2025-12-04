"""
Test CVS retrieval specifically with new graph
"""

import sys
sys.path.append('.')

from src.graph_rag.graph_retriever import GraphRoutedRetriever
from src.graph_rag.subgraph_partitioner import SubgraphPartitioner
import logging

logging.basicConfig(level=logging.INFO)

def test_cvs_retrieval():
    print('🔍 Testing CVS query with new graph...')
    
    # Load graph and create retriever like in test_graph_rag_with_llm.py
    from src.graph_rag.graph_builder import DocumentGraph
    
    # Load the graph 
    graph_builder = DocumentGraph()
    graph_builder.load_graph('document_graph/graph.pkl')
    print(f'Graph loaded: {len(graph_builder.graph.nodes)} nodes, {len(graph_builder.graph.edges)} edges')
    
    # Check if graph already has communities
    partitioner = None
    if hasattr(graph_builder, 'community_summaries') and graph_builder.community_summaries:
        print(f'✅ Graph already has communities, skipping partitioning')
        print(f'   Found {len(graph_builder.community_summaries)} existing communities')
        partitioner = SubgraphPartitioner(graph_builder.graph)
        # Set the loaded metadata
        partitioner.community_summaries = graph_builder.community_summaries
        partitioner.community_centroids = graph_builder.community_centroids
        partitioner.community_members = graph_builder.community_members
    else:
        print('🔍 Creating partitioner...')
        partitioner = SubgraphPartitioner(graph_builder.graph)
        partitioner.partition_graph()
    
    # Create retriever
    retriever = GraphRoutedRetriever(
        graph=graph_builder.graph, 
        partitioner=partitioner,
        k=15
    )
    
    # Test CVS query
    query = 'Hệ thống phiên bản đồng thời là gì'
    print(f'Query: {query}')
    
    docs = retriever._get_relevant_documents(query)
    
    print(f'\nRetrieved {len(docs)} documents:')
    
    found_389 = False
    for i, doc in enumerate(docs):
        node_id = doc.metadata.get('node_id', '?')
        score = doc.metadata.get('relevance_score', 0)
        print(f'  {i+1}. Node {node_id} - Score: {score:.3f}')
        
        content_preview = doc.page_content[:150].replace('\n', ' ')
        print(f'     Content: {content_preview}...')
        
        # Check if this is Node 389 (our target CVS node)
        if node_id == 389:
            found_389 = True
            print('     ✅ FOUND Node 389 (CVS content)!')
            print(f'     Full content: {doc.page_content}')
    
    print('\n' + '='*50)
    print('💡 Node 389 status:', 'FOUND' if found_389 else 'NOT FOUND')
    
    if not found_389:
        print('❌ Node 389 still not retrieved. Let me check all nodes containing CVS...')
        
        # Check all CVS-related nodes in the graph
        cvs_nodes = []
        for node_id, data in graph_builder.graph.nodes(data=True):
            content = data.get('content', '')
            if 'CVS' in content or 'phiên bản đồng thời' in content.lower():
                cvs_nodes.append((node_id, content[:200]))
        
        print(f'Found {len(cvs_nodes)} nodes containing CVS or "phiên bản đồng thời":')
        for node_id, content in cvs_nodes:
            print(f'  Node {node_id}: {content}...')

if __name__ == '__main__':
    test_cvs_retrieval()