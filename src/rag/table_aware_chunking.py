"""
Table-Aware Chunking for GraphRAG
Enhanced chunking that preserves markdown tables and Vietnamese legal structure
Copied from graph_routed_rag for GraphRAG integration
"""

import re
import glob
import os
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def is_legal_document(content: str) -> bool:
    """Check if content is a Vietnamese legal/regulation document"""
    legal_patterns = [
        r'Điều \d+\.',
        r'Khoản \d+\.',
        r'QUY ĐỊNH|QUY CHẾ|QUYẾT ĐỊNH',
        r'Ban hành|Căn cứ'
    ]
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in legal_patterns)


def detect_markdown_tables(text: str) -> List[Dict[str, Any]]:
    """
    Detect markdown tables in text and return their positions
    
    Returns:
        List of dicts with 'start', 'end', 'content', 'header_lines' for each table
    """
    tables = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if line contains table separator (|---|---| or | --- | --- |)
        if '|' in line and re.search(r'\|[\s-]+\|', line):
            # Found potential table separator
            # Look back for header (previous line with |)
            if i > 0 and '|' in lines[i-1]:
                # Found table! Collect all table rows
                table_start = i - 1
                table_end = i + 1
                
                # Collect following rows that are part of table
                while table_end < len(lines) and '|' in lines[table_end]:
                    table_end += 1
                
                # Look for context before table (up to 2 lines)
                context_start = max(0, table_start - 2)
                header_lines = []
                for j in range(context_start, table_start):
                    line_text = lines[j].strip()
                    # Include lines that describe the table (Bảng X, Table X, etc.)
                    if line_text and ('bảng' in line_text.lower() or 'table' in line_text.lower() or line_text.startswith('#')):
                        header_lines.append(line_text)
                
                # Extract table content with context
                table_content_lines = header_lines + lines[table_start:table_end]
                table_content = '\n'.join(table_content_lines)
                
                tables.append({
                    'start': context_start if header_lines else table_start,
                    'end': table_end,
                    'content': table_content,
                    'header_lines': len(header_lines)
                })
                
                # Skip past this table
                i = table_end
                continue
        
        i += 1
    
    return tables


def split_text_with_table_preservation(text: str, chunk_size: int = 800, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into chunks while keeping markdown tables intact
    
    Strategy:
    1. Detect all markdown tables
    2. Split text around tables (tables become their own chunks)
    3. Split non-table text normally
    """
    # Detect tables
    tables = detect_markdown_tables(text)
    
    if not tables:
        # No tables found, use standard splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=False
        )
        return text_splitter.split_text(text)
    
    # Split text into segments: [text_before_table1, table1, text_between_tables, table2, ...]
    lines = text.split('\n')
    chunks = []
    last_end = 0
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=False
    )
    
    for table in tables:
        # Text before table
        if last_end < table['start']:
            text_before = '\n'.join(lines[last_end:table['start']])
            if text_before.strip():
                # Split normally
                chunks.extend(text_splitter.split_text(text_before))
        
        # Table itself (keep intact as one chunk)
        table_chunk = table['content']
        if len(table_chunk) > chunk_size * 2:
            # Table is very large, add warning but still keep it intact
            print(f"⚠️  Warning: Large table detected ({len(table_chunk)} chars). Keeping intact despite chunk_size={chunk_size}.")
        chunks.append(table_chunk)
        
        last_end = table['end']
    
    # Text after last table
    if last_end < len(lines):
        text_after = '\n'.join(lines[last_end:])
        if text_after.strip():
            chunks.extend(text_splitter.split_text(text_after))
    
    return chunks


def split_by_vietnamese_structure(content: str, chunk_settings: Dict[str, Any]) -> List[str]:
    """
    Split Vietnamese legal documents by structural units (Điều, Chương, Mục)
    Keeps complete logical units together within size limits.
    """
    max_chunk_size = chunk_settings.get('max_chunk_size', 1500)
    min_chunk_size = chunk_settings.get('min_chunk_size', 500)
    overlap_size = chunk_settings.get('overlap_size', 300)
    
    # Extract all Điều sections using split
    dieu_pattern = r'(##?\s*Điều\s+\d+\.?\s*[^\n]+)'
    parts = re.split(dieu_pattern, content)
    
    if len(parts) <= 1:
        return [content]
    
    # Reconstruct Điều sections
    dieu_sections = []
    for i in range(1, len(parts), 2):
        if i < len(parts):
            header = parts[i]
            content_part = parts[i+1] if i+1 < len(parts) else ""
            full_dieu = header + content_part
            dieu_sections.append(full_dieu.strip())
    
    if not dieu_sections:
        return [content]
    
    chunks = []
    current_chunk = ""
    
    for dieu_text in dieu_sections:
        if not dieu_text:
            continue
        
        # If this Điều can fit in current chunk, add it
        if len(current_chunk + "\n\n" + dieu_text) <= max_chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + dieu_text
            else:
                current_chunk = dieu_text
        else:
            # Save current chunk if it has content
            if current_chunk.strip() and len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk)
            
            # Check if this Điều alone is too large
            if len(dieu_text) > max_chunk_size:
                # Split large Điều by khoản
                sub_chunks = split_large_dieu_by_khoan(dieu_text, max_chunk_size, min_chunk_size)
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = dieu_text
    
    # Add remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk)
    
    # Add overlap
    if len(chunks) > 1:
        chunks = add_overlap_to_chunks(chunks, overlap_size)
    
    return chunks if chunks else [content]


def split_large_dieu_by_khoan(dieu_text: str, max_size: int, min_size: int) -> List[str]:
    """Split a large Điều section by khoản (clauses)"""
    khoan_pattern = r'(?:^|\n)(\d+\.(?:\s|$))'
    khoan_splits = re.split(khoan_pattern, dieu_text, flags=re.MULTILINE)
    
    if len(khoan_splits) <= 1:
        return [dieu_text]
    
    chunks = []
    current_chunk = khoan_splits[0]
    
    for i in range(1, len(khoan_splits), 2):
        if i + 1 < len(khoan_splits):
            khoan_marker = khoan_splits[i]
            khoan_content = khoan_splits[i + 1]
            khoan_full = khoan_marker + khoan_content
            
            if len(current_chunk + khoan_full) <= max_size:
                current_chunk += khoan_full
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk)
                current_chunk = khoan_full
    
    if current_chunk.strip():
        chunks.append(current_chunk)
    
    return chunks


def add_overlap_to_chunks(chunks: List[str], overlap_size: int) -> List[str]:
    """Add overlap from previous chunk to each subsequent chunk"""
    if len(chunks) <= 1:
        return chunks
    
    overlapped_chunks = [chunks[0]]
    
    for i in range(1, len(chunks)):
        prev_chunk = chunks[i-1]
        curr_chunk = chunks[i]
        
        # Get last overlap_size chars from previous chunk
        overlap = get_last_n_chars(prev_chunk, overlap_size)
        
        # Prepend overlap to current chunk
        overlapped_chunk = overlap + "\n\n" + curr_chunk
        overlapped_chunks.append(overlapped_chunk)
    
    return overlapped_chunks


def get_last_n_chars(text: str, n: int) -> str:
    """Get last n characters, preferring complete sentences"""
    if len(text) <= n:
        return text
    
    last_part = text[-n:]
    
    # Find first sentence boundary in the overlap region
    sentence_breaks = [m.start() for m in re.finditer(r'[.!?]\s+', last_part)]
    if sentence_breaks:
        return last_part[sentence_breaks[0]+2:]
    
    return last_part


def ensure_chunk_overlap(chunks: List[str], target_overlap: int) -> List[str]:
    """Ensure chunks have actual overlap by post-processing"""
    if len(chunks) <= 1:
        return chunks
    
    enhanced_chunks = []
    
    for i, chunk in enumerate(chunks):
        if i == 0:
            enhanced_chunks.append(chunk)
        else:
            prev_chunk = chunks[i-1]
            overlap_text = prev_chunk[-target_overlap:] if len(prev_chunk) > target_overlap else prev_chunk
            
            if len(overlap_text) == target_overlap:
                last_space = overlap_text.rfind(' ')
                if last_space > target_overlap // 2:
                    overlap_text = overlap_text[last_space+1:]
            
            enhanced_chunk = overlap_text + "\n" + chunk
            enhanced_chunks.append(enhanced_chunk)
    
    return enhanced_chunks


def enhanced_text_chunking(content: str, chunk_settings: Dict[str, Any]) -> List[str]:
    """
    Structure-aware chunking that respects Vietnamese document structure
    - Keeps complete Điều (articles) together when possible
    - Preserves khoản (clauses) and điểm (points) hierarchy
    - Uses semantic boundaries instead of hard character limits
    """
    # Try structure-aware chunking first for Vietnamese legal documents
    if is_legal_document(content):
        chunks = split_by_vietnamese_structure(content, chunk_settings)
        if chunks:
            return chunks
    
    # Fallback to enhanced recursive chunking
    separators = [
        "\n\n\n",
        "\n\n",
        "\n",
        ". ",
        ".",
        "; ",
        ", ",
        " ",
        "",
    ]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_settings.get('chunk_size', 1200),
        chunk_overlap=max(300, chunk_settings.get('chunk_overlap', 300)),
        length_function=len,
        separators=separators,
        keep_separator=True,
        is_separator_regex=False
    )
    
    chunks = text_splitter.split_text(content)
    
    # Post-process to ensure overlap
    if len(chunks) > 1:
        chunks = ensure_chunk_overlap(chunks, chunk_settings.get('chunk_overlap', 300))
    
    return chunks


def load_documents_from_folder(data_folder: str, chunk_size: int = 800, chunk_overlap: int = 200) -> List[Document]:
    """
    Load all .txt/.md documents from a folder recursively with enhanced chunking
    - Structure-aware chunking for Vietnamese legal documents (Điều/khoản)
    - Markdown table preservation
    - Standard recursive chunking for other documents
    
    Args:
        data_folder: Path to folder containing documents
        chunk_size: Size of text chunks (default 800)
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of Document objects with metadata
    """
    # Import here to avoid circular dependency
    import sys
    import os
    
    # Add parent directory to path if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from rag.metadata_config import get_metadata_config
    from rag.retriever import extract_metadata_from_path
    
    documents = []
    
    chunk_settings = {
        'chunk_size': chunk_size,
        'chunk_overlap': chunk_overlap,
        'max_chunk_size': 1500,
        'min_chunk_size': 500,
        'overlap_size': 300
    }
    
    # Find all text files
    txt_files = []
    for pattern in ["*.txt", "*.md", "*.markdown"]:
        txt_files.extend(glob.glob(os.path.join(data_folder, "**", pattern), recursive=True))
    
    print(f"Found {len(txt_files)} text files in {data_folder}")
    
    for file_path in txt_files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            metadata = extract_metadata_from_path(file_path, data_folder)
            metadata['source'] = os.path.basename(file_path)
            
            # Use enhanced chunking
            chunks = enhanced_text_chunking(content, chunk_settings)
            
            # Log chunking type
            is_markdown = file_path.endswith('.md') or file_path.endswith('.markdown')
            if is_markdown and '|' in content:
                print(f"📊 Table-aware chunking: {os.path.basename(file_path)} -> {len(chunks)} chunks")
            elif is_legal_document(content):
                print(f"📜 Vietnamese legal chunking: {os.path.basename(file_path)} -> {len(chunks)} chunks")
            
            # Create Document objects
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                
                # Mark if chunk contains table
                if '|' in chunk and re.search(r'\|[\s-]+\|', chunk):
                    chunk_metadata['contains_table'] = True
                
                doc = Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                )
                documents.append(doc)
        
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    print(f"Loaded {len(documents)} document chunks")
    return documents
