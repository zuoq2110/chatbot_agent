#!/usr/bin/env python3
"""
Test script for querying about grade calculation
"""

from src.graph_rag.department_graph_manager import DepartmentGraphManager

def test_grade_calculation_query():
    print('=== TESTING: Cách tính điểm học phần ===')
    print()

    # Initialize manager
    manager = DepartmentGraphManager()

    # Test query about grading calculation
    query = 'cách tính điểm học phần'
    user_metadata = {}

    print(f'Query: "{query}"')
    print(f'User metadata: {user_metadata}')
    print()

    try:
        # Test smart query
        results, decision = manager.query_smart(query, user_metadata, k=5)
        
        print(f'Department decision: {decision.chosen_department} (confidence: {decision.confidence:.2f})')
        print(f'Found {len(results)} results')
        print('=' * 60)
        
        for i, result in enumerate(results, 1):
            print(f'Result {i}:')
            print(f'  Content ({len(result)} chars):')
            print(f'  {result[:300]}...')
            print('-' * 50)
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grade_calculation_query()