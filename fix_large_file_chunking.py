#!/usr/bin/env python3
"""
Fix chunking cho file giáo trình quá lớn
Chia file 617KB thành nhiều chunks nhỏ hơn
"""
import sys
import os
sys.path.append('src')
from rag.table_aware_chunking import load_documents_from_folder
from langchain_text_splitters import RecursiveCharacterTextSplitter

def fix_large_file_chunking():
    """Fix chunking cho file giáo trình"""
    
    # Load documents hiện tại
    documents = load_documents_from_folder('data', chunk_size=800, chunk_overlap=200)
    
    # Tìm document from giáo trình
    target_file = 'Giao trinh _ Phần mềm mã nguồn mở.md'
    large_docs = [doc for doc in documents if target_file in doc.metadata.get('source', '')]
    
    if not large_docs:
        print(f"❌ Không tìm thấy {target_file}")
        return
        
    large_doc = large_docs[0]
    print(f"📊 Document gốc: {len(large_doc.page_content)} chars")
    
    # Force split thành chunks nhỏ hơn, bỏ qua table preservation
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Chunks lớn hơn
        chunk_overlap=300,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=True
    )
    
    # Split content
    chunks = text_splitter.split_text(large_doc.page_content)
    print(f"📊 Sau khi split: {len(chunks)} chunks")
    
    # Kiểm tra chunks
    for i, chunk in enumerate(chunks[:5]):
        print(f"  Chunk {i}: {len(chunk)} chars - {chunk[:100]}...")
    
    # Tạo documents mới
    new_docs = []
    for i, chunk in enumerate(chunks):
        metadata = large_doc.metadata.copy()
        metadata['chunk_index'] = i
        metadata['total_chunks'] = len(chunks)
        metadata['forced_split'] = True  # Mark as forced split
        
        from langchain_core.documents import Document
        new_doc = Document(
            page_content=chunk,
            metadata=metadata
        )
        new_docs.append(new_doc)
    
    # Replace large doc with new docs
    other_docs = [doc for doc in documents if target_file not in doc.metadata.get('source', '')]
    all_docs = other_docs + new_docs
    
    print(f"📊 Tổng documents sau fix: {len(all_docs)}")
    return all_docs

if __name__ == "__main__":
    fix_large_file_chunking()