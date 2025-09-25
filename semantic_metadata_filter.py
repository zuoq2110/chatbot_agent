#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improved metadata filtering using semantic similarity instead of keyword matching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from typing import Dict, Any, List
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticMetadataFilter:
    def __init__(self):
        # Load a multilingual sentence transformer
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        except:
            # Fallback to basic model if the above is not available
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Define department descriptions in Vietnamese (more semantic than keywords)
        self.department_descriptions = {
            "phongdaotao": "phòng đào tạo, quản lý chương trình học, sinh viên, học viên, tuyển sinh, đào tạo đại học thạc sĩ tiến sĩ",
            "phongkhaothi": "phòng khảo thí, thi cử, đánh giá, kiểm tra, đảm bảo chất lượng giáo dục, hội đồng khảo thí",
            "vanphong": "văn phòng, hành chính, thủ tục, giấy tờ, công văn, quản lý chung, tổ chức sự kiện",
            "khoa": "khoa chuyên môn, ngành học, chương trình đào tạo, giảng dạy, môn học, an toàn thông tin, công nghệ thông tin, bộ môn",
            "phongkhcn": "khoa học công nghệ, nghiên cứu khoa học, đề tài nghiên cứu, công bố khoa học, hội thảo",
            "phongtccb": "tổ chức cán bộ, nhân sự, tuyển dụng, đánh giá cán bộ, bổ nhiệm, khen thưởng kỷ luật",
            "thongtinhvktmm": "thông tin chung học viện, giới thiệu, lịch sử, tổ chức, cơ cấu, nhiệm vụ chung",
            "viennghiencuu": "viện nghiên cứu, hợp tác quốc tế, phát triển, dự án hợp tác, nghiên cứu ứng dụng"
        }
        
        # Pre-compute embeddings for department descriptions
        self.dept_embeddings = {}
        for dept, desc in self.department_descriptions.items():
            self.dept_embeddings[dept] = self.model.encode([desc])[0]
    
    def analyze_query_semantic(self, query: str, similarity_threshold: float = 0.3) -> Dict[str, Any]:
        """
        Analyze query using semantic similarity instead of keyword matching
        
        Args:
            query: The user query
            similarity_threshold: Minimum similarity score to consider a match
            
        Returns:
            Dictionary with metadata filters or empty dict if no clear match
        """
        # Encode the query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities with all departments
        similarities = {}
        for dept, dept_embedding in self.dept_embeddings.items():
            similarity = np.dot(query_embedding, dept_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(dept_embedding)
            )
            similarities[dept] = similarity
        
        # Find the best match
        best_dept = max(similarities.keys(), key=lambda k: similarities[k])
        best_score = similarities[best_dept]
        
        print(f"🔍 Semantic analysis for query: '{query}'")
        print(f"📊 Department similarities:")
        for dept, score in sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]:
            from rag.metadata_config import get_metadata_config
            config = get_metadata_config()
            dept_vn = config.config['folder_mappings'].get(dept, {}).get('department_vn', dept)
            print(f"   {dept_vn}: {score:.3f}")
        
        # Only return filter if similarity is above threshold
        if best_score >= similarity_threshold:
            print(f"✅ Selected department: {best_dept} (score: {best_score:.3f})")
            return {"department": best_dept}
        else:
            print(f"⚠️  No clear department match (best: {best_score:.3f} < {similarity_threshold})")
            return {}

# Test the semantic filter
def test_semantic_filter():
    print("🧪 Testing Semantic Metadata Filter...")
    
    filter_engine = SemanticMetadataFilter()
    
    test_queries = [
        "KHỐI LƯỢNG KIẾN THỨC TOÀN KHÓA ngành an toàn thông tin",
        "ĐỐI TƯỢNG TUYỂN SINH ngành an toàn thông tin", 
        "quy định về thi cử và khảo thí",
        "hồ sơ tuyển sinh đại học",
        "nghiên cứu khoa học và đề tài",
        "thông tin về học viện",
        "quản lý nhân sự và cán bộ"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        result = filter_engine.analyze_query_semantic(query)
        print(f"🎯 Result: {result}")

if __name__ == "__main__":
    test_semantic_filter()