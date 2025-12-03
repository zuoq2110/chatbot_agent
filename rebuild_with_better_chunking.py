"""
Force rebuild graph with better chunking for the large textbook file
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

def force_chunk_large_file(content, chunk_size=1500, chunk_overlap=300):
    """
    Force chunk large file by splitting on major section headers
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Use aggressive splitting for very large files
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[
            "\n\n## ",  # Major sections 
            "\n\n### ", # Sub sections
            "\n\n#### ", # Sub-sub sections
            "\n\n", # Paragraphs
            "\n", # Lines
            ". ", # Sentences
            " ", # Words
            ""
        ],
        keep_separator=True
    )
    
    chunks = text_splitter.split_text(content)
    return chunks

def rebuild_with_better_chunking():
    """Rebuild graph with forced chunking for large textbook"""
    
    print("=" * 80)
    print("REBUILDING GRAPH WITH BETTER CHUNKING")
    print("=" * 80)
    
    # Data folder
    data_folder = os.path.join(project_root, "data")
    
    # Load documents but override chunking for large file
    documents = []
    
    import glob
    from langchain_core.documents import Document
    
    # Find all text files
    txt_files = []
    for pattern in ["*.txt", "*.md", "*.markdown"]:
        txt_files.extend(glob.glob(os.path.join(data_folder, "**", pattern), recursive=True))
    
    print(f"Found {len(txt_files)} text files")
    
    target_file = "Giao trinh _ Phần mềm mã nguồn mở.md"
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Special handling for the large textbook file
            if filename == target_file:
                print(f"  📚 SPECIAL CHUNKING for {filename} ({len(content):,} chars)")
                chunks = force_chunk_large_file(content, chunk_size=1500, chunk_overlap=300)
                print(f"  ✅ Created {len(chunks)} chunks from large file")
            else:
                # Use normal chunking for other files  
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=800,
                    chunk_overlap=200,
                    length_function=len
                )
                chunks = text_splitter.split_text(content)
            
            # Create Document objects
            for i, chunk in enumerate(chunks):
                # Simple metadata
                metadata = {
                    'source': filename,
                    'file_path': file_path,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                
                doc = Document(
                    page_content=chunk,
                    metadata=metadata
                )
                documents.append(doc)
                
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
            continue
    
    print(f"\\n✅ Loaded {len(documents)} document chunks")
    
    # Build graph
    print("\\n📊 Building document graph...")
    start_time = time.time()
    
    builder = DocumentGraph(semantic_threshold=0.7, max_semantic_edges_per_node=5)
    graph = builder.build_graph(documents)
    
    build_time = time.time() - start_time
    print(f"✅ Graph built in {build_time:.2f}s")
    print(f"   Nodes: {graph.number_of_nodes()}")
    print(f"   Edges: {graph.number_of_edges()}")
    
    # Save graph
    output_folder = os.path.join(project_root, "document_graph")
    os.makedirs(output_folder, exist_ok=True)
    
    graph_path = os.path.join(output_folder, "graph.pkl")
    builder.save_graph(graph_path)
    
    print(f"\\n💾 Graph saved to: {graph_path}")
    
    # Verify target file is now properly chunked
    print(f"\\n🔍 Verifying {target_file} chunking...")
    target_docs = [doc for doc in documents if target_file in doc.metadata['source']]
    print(f"Target file now has {len(target_docs)} chunks!")
    
    if len(target_docs) > 0:
        print(f"  Sample chunk sizes: {[len(doc.page_content) for doc in target_docs[:5]]}")

if __name__ == "__main__":
    rebuild_with_better_chunking()