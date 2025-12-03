#!/usr/bin/env python3
"""
Simple Department Graph Builder
Xây dựng graph riêng cho từng phòng ban - version đơn giản
"""
import sys
import os
import time
from pathlib import Path

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("=" * 80)
print("🏢 SIMPLE DEPARTMENT GRAPH BUILDER")
print("=" * 80)

# Tạo mock documents từ data folder để test
def create_mock_documents():
    """Tạo mock documents để test department classification"""
    from langchain_core.documents import Document
    
    # Scan data folder
    data_folder = os.path.join(project_root, "data")
    documents = []
    
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]  # First 1000 chars only
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': file_path,
                            'filename': file,
                            'size': len(content)
                        }
                    )
                    documents.append(doc)
                    print(f"   📄 Loaded: {file}")
                except Exception as e:
                    print(f"   ⚠️  Error loading {file}: {e}")
    
    return documents

# Load documents
print(f"📁 Scanning data folder: {os.path.join(project_root, 'data')}")
documents = create_mock_documents()
print(f"✅ Loaded {len(documents)} documents")

# Test department classification
from graph_rag.department_graph_manager import DepartmentGraphManager

dept_manager = DepartmentGraphManager(os.path.join(project_root, "test_department_graphs"))

print("\n📊 Analyzing document distribution by department...")
dept_counts = {}
for doc in documents:
    source_path = doc.metadata.get('source', '')
    dept = dept_manager.detect_department_from_path(source_path)
    dept_counts[dept] = dept_counts.get(dept, 0) + 1

print("   Documents by department:")
for dept, count in sorted(dept_counts.items()):
    print(f"   📁 {dept}: {count} documents")

# Mock graph building (without actual GraphBuilder which needs LLM)
print("\n🔨 Mock department graph building...")

class MockDocumentGraph:
    """Mock DocumentGraph for testing"""
    def __init__(self, **kwargs):
        import networkx as nx
        self.graph = nx.Graph()
        
    def build_graph(self, documents):
        # Add mock nodes
        for i, doc in enumerate(documents):
            self.graph.add_node(i, document=doc, content=doc.page_content[:200])
        # Add some mock edges
        for i in range(len(documents) - 1):
            if i < len(documents) - 1:
                self.graph.add_edge(i, i + 1, weight=0.5, edge_type='structural')
        return self.graph
    
    def save_graph(self, filepath):
        import pickle
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'graph': self.graph,
                'doc_embeddings': {},  # Mock empty embeddings
                'semantic_threshold': 0.5
            }, f)
        print(f"   💾 Mock graph saved: {filepath}")

# Mock department-specific graph building
dept_documents = {}
for doc in documents:
    source_path = doc.metadata.get('source', '')
    dept = dept_manager.detect_department_from_path(source_path)
    if dept not in dept_documents:
        dept_documents[dept] = []
    dept_documents[dept].append(doc)

# Build mock graphs for each department
output_dir = os.path.join(project_root, "test_department_graphs")
os.makedirs(output_dir, exist_ok=True)

for dept, docs in dept_documents.items():
    if len(docs) == 0:
        continue
        
    print(f"   🔨 Building mock graph for {dept}: {len(docs)} documents")
    
    # Create mock graph
    graph_builder = MockDocumentGraph()
    graph = graph_builder.build_graph(docs)
    
    # Save to department-specific folder
    dept_dir = os.path.join(output_dir, dept)
    os.makedirs(dept_dir, exist_ok=True)
    graph_path = os.path.join(dept_dir, "graph.pkl")
    graph_builder.save_graph(graph_path)
    
    print(f"   ✅ {dept}: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

print("\n🧪 Testing department manager with mock graphs...")

# Test with mock graphs
class MockDepartmentGraphManager(DepartmentGraphManager):
    """Mock version that doesn't need embeddings"""
    
    def load_department_graphs(self):
        import pickle
        import os
        
        if not os.path.exists(self.base_output_dir):
            return False
        
        loaded_count = 0
        for dept_name in os.listdir(self.base_output_dir):
            dept_dir = os.path.join(self.base_output_dir, dept_name)
            if not os.path.isdir(dept_dir):
                continue
                
            graph_path = os.path.join(dept_dir, "graph.pkl")
            if not os.path.exists(graph_path):
                continue
            
            try:
                # Load graph
                with open(graph_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Mock retriever 
                class MockRetriever:
                    def __init__(self, graph, dept_name):
                        self.graph = graph
                        self.dept_name = dept_name
                    
                    def query(self, query, k=4):
                        # Return mock documents
                        docs = []
                        for node_id in list(self.graph.nodes())[:k]:
                            doc = self.graph.nodes[node_id].get('document')
                            if doc:
                                doc.metadata['query_department'] = self.dept_name
                                docs.append(doc)
                        return docs
                
                self.department_retrievers[dept_name] = MockRetriever(data['graph'], dept_name)
                
                loaded_count += 1
                print(f"   ✅ Loaded mock graph for {dept_name}")
                
            except Exception as e:
                print(f"   ❌ Failed to load {dept_name}: {e}")
        
        return loaded_count > 0

# Test mock manager
test_manager = MockDepartmentGraphManager(output_dir)
success = test_manager.load_department_graphs()

if success:
    print("✅ Mock graphs loaded successfully!")
    
    # Test queries
    test_queries = [
        "Quy định về điểm TOEIC",
        "Chương trình đào tạo",
        "Nghiên cứu khoa học"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test query: '{query}'")
        depts = test_manager.detect_department_from_query(query, top_k=2)
        print(f"   🎯 Detected departments: {depts}")
        
        for dept in depts:
            if dept in test_manager.department_retrievers:
                retriever = test_manager.department_retrievers[dept]
                results = retriever.query(query, k=2)
                print(f"   📁 {dept}: {len(results)} mock results")

print("\n" + "=" * 80)
print("✅ MOCK DEPARTMENT GRAPH TEST COMPLETE!")
print("=" * 80)
print(f"Mock graphs created in: {output_dir}")
print("Next step: Install LLM dependencies and run real build_department_graphs.py")