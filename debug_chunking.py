"""
Quick test to check why the large file isn't chunked properly
"""
import os

def simple_test_chunking():
    file_path = 'data/Giao trinh _ Phần mềm mã nguồn mở.md'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content):,} characters")
    print(f"Lines: {content.count(chr(10)):,}")
    
    # Check if it has tables (which would make it 1 giant chunk)
    has_tables = '|' in content and '-' in content
    print(f"Has markdown tables: {has_tables}")
    
    if has_tables:
        # Find table pattern
        import re
        table_patterns = content.count('|')
        table_separators = len(re.findall(r'\|[\s-]+\|', content))
        print(f"Pipe symbols: {table_patterns}")
        print(f"Table separators (|---|): {table_separators}")
        
        if table_separators > 0:
            print("This file is being treated as ONE GIANT TABLE")
            print("That's why it's not chunked!")
    
    return has_tables

if __name__ == "__main__":
    simple_test_chunking()