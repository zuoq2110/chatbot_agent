#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug chunking to see how PHÒNG THIẾT BỊ - QUẢN TRỊ sections are split
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.retriever import read_file_with_metadata, smart_text_chunking
from rag.metadata_config import get_metadata_config

def debug_chunking():
    print("🔍 Debugging chunking for PHÒNG THIẾT BỊ - QUẢN TRỊ sections...")
    
    # Read the specific file
    file_path = "data/phongkhaothi/02. Hoạt động đảm bảo chất lượng giáo dục tại HVKTMM.txt"
    
    # Read file content and metadata
    content, metadata = read_file_with_metadata(file_path, "data")
    
    print(f"📄 File: {file_path}")
    print(f"📊 Content length: {len(content)} characters")
    print()
    
    # Get chunk settings
    config = get_metadata_config()
    chunk_settings = config.get_chunk_settings()
    
    print(f"⚙️  Chunk settings:")
    print(f"   Chunk size: {chunk_settings['chunk_size']}")
    print(f"   Overlap: {chunk_settings['chunk_overlap']}")
    print()
    
    # Create chunks
    chunks = smart_text_chunking(content, metadata, chunk_settings)
    
    print(f"📋 Total chunks created: {len(chunks)}")
    print()
    
    # Find chunks containing PHÒNG THIẾT BỊ sections
    relevant_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        if ("phòng thiết bị" in chunk_lower and "quản trị" in chunk_lower) or \
           ("xi." in chunk_lower and "phòng thiết bị" in chunk_lower):
            relevant_chunks.append((i, chunk))
    
    print(f"🎯 Found {len(relevant_chunks)} relevant chunks:")
    print()
    
    for i, (chunk_idx, chunk) in enumerate(relevant_chunks):
        print(f"{'='*80}")
        print(f"📄 Chunk #{chunk_idx + 1} (Index: {chunk_idx})")
        print(f"📏 Length: {len(chunk)} chars")
        print(f"{'='*80}")
        
        # Show first and last lines to understand chunk boundaries
        lines = chunk.split('\n')
        print("🔝 First 10 lines:")
        for line_num, line in enumerate(lines[:10], 1):
            if line.strip():
                print(f"   {line_num:2}: {line}")
        
        if len(lines) > 20:
            print("   ... (middle content omitted) ...")
            print("🔚 Last 10 lines:")
            for line_num, line in enumerate(lines[-10:], len(lines)-9):
                if line.strip():
                    print(f"   {line_num:2}: {line}")
        
        # Check for specific sections
        sections_found = []
        if "1. văn bản quy định" in chunk.lower():
            sections_found.append("1. Văn bản quy định")
        if "2. đảm bảo cơ sở" in chunk.lower():
            sections_found.append("2. Đảm bảo cơ sở vật chất")
        if "3. quân y" in chunk.lower():
            sections_found.append("3. Quân y")
        
        print(f"📋 Sections found: {', '.join(sections_found) if sections_found else 'None'}")
        print()
    
    # Look for "3. Quân y" specifically in all chunks
    quan_y_chunks = []
    for i, chunk in enumerate(chunks):
        if "quân y" in chunk.lower():
            quan_y_chunks.append((i, chunk))
    
    print(f"🔍 Chunks containing 'Quân y': {len(quan_y_chunks)}")
    for i, (chunk_idx, chunk) in enumerate(quan_y_chunks):
        print(f"   Chunk #{chunk_idx + 1}: Found 'Quân y'")
        # Show context around Quân y
        lines = chunk.split('\n')
        for line_num, line in enumerate(lines):
            if "quân y" in line.lower():
                start = max(0, line_num - 2)
                end = min(len(lines), line_num + 3)
                print(f"      Context (lines {start+1}-{end}):")
                for ctx_line_num in range(start, end):
                    marker = ">>> " if ctx_line_num == line_num else "    "
                    print(f"      {marker}{lines[ctx_line_num]}")
                break

if __name__ == "__main__":
    debug_chunking()