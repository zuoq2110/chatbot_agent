#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug why smart_retrieve is not detecting PHÒNG THIẾT BỊ - QUẢN TRỊ properly
"""

import sys
import os
import re
from unidecode import unidecode
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_smart_detect():
    print("🔍 Testing smart detection logic...")
    
    # Test queries
    queries = [
        "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ",
        "PHÒNG THIẾT BỊ - QUẢN TRỊ làm gì",
        "phòng thiết bị quản trị",
        "PHÒNG THIẾT BỊ",
        "phòng thiết bị"
    ]
    
    print("Testing detection patterns:")
    print()
    
    for query in queries:
        print(f"📝 Query: '{query}'")
        
        # Test original detection
        query_lower = query.lower()
        contains_phong_thiet_bi = "phòng thiết bị" in query_lower
        print(f"   Original detection: {contains_phong_thiet_bi}")
        
        # Test normalized detection
        query_normalized = unidecode(query.lower())
        contains_normalized = "phong thiet bi" in query_normalized
        print(f"   Normalized detection: {contains_normalized}")
        
        # Test combined logic (what should be used)
        smart_detected = contains_phong_thiet_bi or contains_normalized
        print(f"   ✅ Smart detection: {smart_detected}")
        print()

def check_current_retriever_code():
    print("🔍 Checking current retriever code...")
    
    # Read current retriever code
    retriever_path = os.path.join("src", "rag", "retriever.py")
    if os.path.exists(retriever_path):
        with open(retriever_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find smart_retrieve function
        if "def smart_retrieve(" in content:
            print("✅ smart_retrieve function exists")
            
            # Check detection logic
            if '"phòng thiết bị"' in content and '"phong thiet bi"' in content:
                print("✅ Both accented and normalized detection patterns found")
            else:
                print("❌ Missing detection patterns")
                
            # Find the detection block
            detection_start = content.find("def smart_retrieve(")
            if detection_start != -1:
                detection_end = content.find("def ", detection_start + 1)
                if detection_end == -1:
                    detection_end = len(content)
                    
                function_code = content[detection_start:detection_end]
                print("\n📋 Current smart_retrieve detection logic:")
                
                # Extract detection lines
                lines = function_code.split('\n')
                for i, line in enumerate(lines):
                    if 'phòng thiết bị' in line or 'phong thiet bi' in line:
                        print(f"   Line {i+1}: {line.strip()}")
        else:
            print("❌ smart_retrieve function not found!")
    else:
        print("❌ retriever.py not found!")

if __name__ == "__main__":
    test_smart_detect()
    print("-" * 50)
    check_current_retriever_code()