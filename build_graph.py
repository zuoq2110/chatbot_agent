#!/usr/bin/env python3
"""
Build and save document graph for Graph-Routed RAG in chatbot_agent
Uses load_documents_from_folder from table_aware_chunking with enhanced chunking
"""
import sys
import os
import time

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from rag.table_aware_chunking import load_documents_from_folder
from graph_rag.graph_builder import DocumentGraph

print("=" * 80)
print("BUILDING DOCUMENT GRAPH WITH TABLE-AWARE CHUNKING")
print("=" * 80)

# Path configurations
data_folder = os.path.join(project_root, "data")
output_folder = os.path.join(project_root, "document_graph")

# Load documents using enhanced table-aware chunking from retriever.py
print(f"\n📁 Loading documents from: {data_folder}")
print("   Using enhanced chunking from graph_routed_rag approach:")
print("   - Auto-detection of markdown tables (|...| format)")
print("   - Table preservation (keeps complete tables intact)")
print("   - Vietnamese legal document structure awareness (Điều/Khoản)")
print("   - Semantic boundaries instead of hard character limits")
print()

start_time = time.time()
documents = load_documents_from_folder(
    data_folder=data_folder,
    chunk_size=800,      # Keep original size for more granular chunks
    chunk_overlap=200    # Standard overlap
)
load_time = time.time() - start_time

print(f"\n✅ Loaded {len(documents)} document chunks in {load_time:.2f}s")

# Count special chunks for diagnostics
table_chunks = sum(1 for doc in documents if doc.metadata.get('contains_table', False))
if table_chunks > 0:
    print(f"   📊 {table_chunks} chunks contain markdown tables (preserved intact)")
    print(f"   📝 {len(documents) - table_chunks} regular text chunks")

# Build graph with optimal settings for table-heavy documents
print("\n📊 Building document graph...")
print("   Settings:")
print("   - semantic_threshold=0.7 (balanced for precision)")
print("   - max_edges=5 (optimal connections per node)")
print()

start_time = time.time()
graph_builder = DocumentGraph(
    semantic_threshold=0.7,
    max_semantic_edges_per_node=5
)
graph = graph_builder.build_graph(documents)
graph_build_time = time.time() - start_time

print(f"✅ Graph built in {graph_build_time:.2f}s")
print(f"   📈 Nodes: {graph.number_of_nodes()}")
print(f"   📈 Edges: {graph.number_of_edges()}")
if graph.number_of_nodes() > 0:
    avg_degree = 2 * graph.number_of_edges() / graph.number_of_nodes()
    print(f"   📈 Average degree: {avg_degree:.2f} edges/node")

# Save graph
print(f"\n💾 Saving graph to: {output_folder}")
os.makedirs(output_folder, exist_ok=True)
graph_path = os.path.join(output_folder, "graph.pkl")
graph_builder.save_graph(graph_path)

print("\n" + "=" * 80)
print("✅ GRAPH BUILD COMPLETE!")
print("=" * 80)
print(f"\nTotal time: {load_time + graph_build_time:.2f}s")
print(f"Graph saved: {graph_path}")

# Quick verification
print("\n🔍 Verifying saved graph...")
test_builder = DocumentGraph()
test_builder.load_graph(graph_path)
print(f"✅ Verification successful!")
print(f"   Loaded graph: {test_builder.graph.number_of_nodes()} nodes, {test_builder.graph.number_of_edges()} edges")


