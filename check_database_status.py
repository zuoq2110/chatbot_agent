#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check if vector database needs rebuilding
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_database_status():
    print("🔍 Checking vector database status...")
    
    # Check if vector database exists
    vector_db_path = os.path.join(os.path.dirname(__file__), "vector_db")
    
    if not os.path.exists(vector_db_path):
        print("❌ Vector database not found - needs to be created")
        return False
    
    # Check data folders and their contents
    data_path = os.path.join(os.path.dirname(__file__), "data")
    
    print("📁 Checking data folders:")
    for item in os.listdir(data_path):
        item_path = os.path.join(data_path, item)
        if os.path.isdir(item_path):
            files = []
            for root, dirs, filenames in os.walk(item_path):
                files.extend([f for f in filenames if f.endswith(('.txt', '.pdf', '.docx'))])
            
            if files:
                print(f"   ✅ {item}: {len(files)} files")
            else:
                print(f"   ⚪ {item}: empty")
        elif item.endswith(('.txt', '.pdf', '.docx')):
            print(f"   ✅ {item}: root file")
    
    # Check vector database modification time
    try:
        db_time = os.path.getmtime(os.path.join(vector_db_path, "index.faiss"))
        print(f"\n📊 Database last modified: {db_time}")
        
        # Check if any data files are newer
        newest_data_time = 0
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(('.txt', '.pdf', '.docx')):
                    file_time = os.path.getmtime(os.path.join(root, file))
                    newest_data_time = max(newest_data_time, file_time)
        
        if newest_data_time > db_time:
            print("⚠️  Data files newer than database - rebuild recommended")
            return False
        else:
            print("✅ Database is up to date")
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_database_status()