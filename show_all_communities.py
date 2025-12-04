#!/usr/bin/env python3
"""
Hiển thị tóm tắt đầy đủ của tất cả communities trong graph
"""

import pickle
import networkx as nx
from collections import Counter

def load_graph_data():
    """Load saved graph data"""
    with open('document_graph/graph.pkl', 'rb') as f:
        return pickle.load(f)

def analyze_community_content(graph, community_members):
    """Phân tích nội dung chi tiết của từng community"""
    community_analysis = {}
    
    for comm_id, member_nodes in community_members.items():
        print(f"\n🏘️ COMMUNITY {comm_id}")
        print("="*60)
        print(f"📊 Số lượng nodes: {len(member_nodes)}")
        
        # Thống kê metadata
        categories = Counter()
        departments = Counter()
        contains_tables = 0
        total_content_length = 0
        
        # Sample nội dung
        sample_contents = []
        
        for node_id in list(member_nodes)[:10]:  # Lấy 10 nodes đầu làm mẫu
            if node_id in graph.nodes:
                node_data = graph.nodes[node_id]
                metadata = node_data.get('metadata', {})
                content = node_data.get('content', '')
                
                # Thống kê
                category = metadata.get('category', 'unknown')
                categories[category] += 1
                
                # Trích xuất department từ category
                if 'phongdaotao' in category:
                    departments['phongdaotao'] += 1
                elif 'phongkhaothi' in category:
                    departments['phongkhaothi'] += 1
                elif 'viennghiencuuvahoptacphattrien' in category:
                    departments['viennghiencuuvahoptacphattrien'] += 1
                elif 'thongtinhvktmm' in category:
                    departments['thongtinhvktmm'] += 1
                else:
                    departments['other'] += 1
                
                if metadata.get('contains_table', False):
                    contains_tables += 1
                
                total_content_length += len(content)
                
                # Lấy sample content (100 ký tự đầu)
                if len(sample_contents) < 5 and len(content) > 50:
                    sample_contents.append(content[:150] + "...")
        
        # Hiển thị thống kê
        print(f"📂 Categories phổ biến:")
        for cat, count in categories.most_common(5):
            print(f"   • {cat}: {count} nodes")
        
        print(f"🏢 Departments:")
        for dept, count in departments.most_common():
            print(f"   • {dept}: {count} nodes")
        
        print(f"📋 Chứa bảng: {contains_tables} nodes")
        print(f"📝 Độ dài nội dung trung bình: {total_content_length // len(member_nodes) if member_nodes else 0} ký tự")
        
        print(f"📖 Sample nội dung:")
        for i, content in enumerate(sample_contents):
            print(f"   {i+1}. {content}")
        
        community_analysis[comm_id] = {
            'size': len(member_nodes),
            'categories': dict(categories),
            'departments': dict(departments),
            'tables': contains_tables,
            'avg_content_length': total_content_length // len(member_nodes) if member_nodes else 0
        }
    
    return community_analysis

def show_community_summaries():
    """Hiển thị tóm tắt chi tiết của tất cả communities"""
    print("🔍 TÓM TẮT ĐẦY ĐỦ TẤT CẢ COMMUNITIES")
    print("="*80)
    
    # Load data
    graph_data = load_graph_data()
    graph = graph_data['graph']
    community_summaries = graph_data.get('community_summaries', {})
    community_members = graph_data.get('community_members', {})
    community_centroids = graph_data.get('community_centroids', {})
    
    print(f"📊 Tổng quan:")
    print(f"   • Số lượng communities: {len(community_summaries)}")
    print(f"   • Tổng nodes: {graph.number_of_nodes()}")
    print(f"   • Tổng edges: {graph.number_of_edges()}")
    
    # Hiển thị tóm tắt LLM-generated
    print(f"\n📝 TÓM TẮT LLM-GENERATED CHO TỪNG COMMUNITY:")
    print("="*80)
    
    for comm_id in sorted(community_summaries.keys()):
        summary = community_summaries[comm_id]
        size = len(community_members.get(comm_id, []))
        
        print(f"\n🏘️ COMMUNITY {comm_id} ({size} nodes)")
        print("-" * 50)
        print(f"📋 Tóm tắt:")
        print(f"{summary}")
        print("-" * 50)
    
    # Phân tích chi tiết nội dung
    print(f"\n🔬 PHÂN TÍCH CHI TIẾT NỘI DUNG:")
    print("="*80)
    
    community_analysis = analyze_community_content(graph, community_members)
    
    # Tổng kết
    print(f"\n📊 TỔNG KẾT:")
    print("="*60)
    
    total_nodes = sum(data['size'] for data in community_analysis.values())
    total_tables = sum(data['tables'] for data in community_analysis.values())
    
    print(f"🎯 Phân bố theo department:")
    all_departments = Counter()
    for data in community_analysis.values():
        for dept, count in data['departments'].items():
            all_departments[dept] += count
    
    for dept, count in all_departments.most_common():
        percentage = (count / total_nodes) * 100 if total_nodes > 0 else 0
        print(f"   • {dept}: {count} nodes ({percentage:.1f}%)")
    
    print(f"📋 Tổng số nodes chứa bảng: {total_tables}")
    print(f"📈 Communities theo kích thước:")
    
    sorted_communities = sorted(community_analysis.items(), key=lambda x: x[1]['size'], reverse=True)
    for comm_id, data in sorted_communities:
        print(f"   • Community {comm_id}: {data['size']} nodes")

def show_community_connections():
    """Hiển thị kết nối giữa các communities"""
    print(f"\n🔗 KẾT NỐI GIỮA CÁC COMMUNITIES:")
    print("="*60)
    
    graph_data = load_graph_data()
    graph = graph_data['graph']
    community_members = graph_data.get('community_members', {})
    
    # Đếm edges giữa communities
    inter_community_edges = Counter()
    intra_community_edges = Counter()
    
    for edge in graph.edges():
        node1, node2 = edge
        comm1 = graph.nodes[node1].get('community')
        comm2 = graph.nodes[node2].get('community')
        
        if comm1 is not None and comm2 is not None:
            if comm1 == comm2:
                intra_community_edges[comm1] += 1
            else:
                # Sắp xếp để tránh trùng lặp (comm1, comm2) và (comm2, comm1)
                comm_pair = tuple(sorted([comm1, comm2]))
                inter_community_edges[comm_pair] += 1
    
    print(f"🔗 Kết nối giữa communities (top 10):")
    for (comm1, comm2), count in inter_community_edges.most_common(10):
        print(f"   • Community {comm1} ↔ Community {comm2}: {count} edges")
    
    print(f"\n🔄 Kết nối nội bộ communities:")
    for comm_id, count in sorted(intra_community_edges.items()):
        print(f"   • Community {comm_id}: {count} internal edges")

if __name__ == "__main__":
    show_community_summaries()
    show_community_connections()
    print("\n✅ Hoàn thành hiển thị tóm tắt tất cả communities!")