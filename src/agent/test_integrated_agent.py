#!/usr/bin/env python
"""
Test script for the Integrated KMA Agent System.

This script tests the supervisor agent's ability to use the RAG tool
and integrate with other tools to answer complex queries.
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from agent import create_supervisor_agent
from state import MyAgentState


class MockTool:
    """Mock class for tools used in testing."""
    
    @staticmethod
    async def mock_rag_search(*args, **kwargs):
        """Mock implementation of search_kma_regulations."""
        return json.dumps({
            "answer": "Students must maintain a GPA of at least 2.0 to graduate.",
            "sources": [
                "Graduation requirements state that students must maintain a GPA of at least 2.0.",
                "Students below 2.0 GPA will be placed on academic probation."
            ],
            "message": "KMA regulation information retrieved successfully"
        })
    
    @staticmethod
    async def mock_student_info(*args, **kwargs):
        """Mock implementation of get_student_info."""
        return json.dumps({
            "student": {
                "student_code": "CT123",
                "student_name": "Nguyen Van A",
                "student_class": "K16-ATTT"
            },
            "message": "Found student information for CT123"
        })
    
    @staticmethod
    async def mock_student_scores(*args, **kwargs):
        """Mock implementation of get_student_scores."""
        return json.dumps({
            "scores": [
                {
                    "score_first": 8.5,
                    "score_second": 8.0,
                    "score_final": 9.0,
                    "score_over_rall": 8.5,
                    "semester": "ki1-2023-2024",
                    "student_code": "CT123",
                    "subject_id": 1,
                    "subject": {
                        "subject_id": 1,
                        "subject_name": "Cryptography",
                        "subject_credits": 3
                    },
                    "student": {
                        "student_code": "CT123",
                        "student_name": "Nguyen Van A",
                        "student_class": "K16-ATTT"
                    }
                }
            ],
            "message": "Found 1 scores for student CT123"
        })
    
    @staticmethod
    def mock_calculate_scores(*args, **kwargs):
        """Mock implementation of calculate_average_scores."""
        return json.dumps({
            "overall_average": {
                "score_first": 8.5,
                "score_second": 8.0,
                "score_final": 9.0,
                "score_over_rall": 8.5
            },
            "semester_averages": {
                "ki1-2023-2024": {
                    "score_first": 8.5,
                    "score_second": 8.0,
                    "score_final": 9.0,
                    "score_over_rall": 8.5
                }
            },
            "total_subjects": 1,
            "message": "Calculated averages for 1 subjects across 1 semesters"
        })


async def test_agent_with_rag_query():
    """Test the supervisor agent with a regulation query that uses RAG."""
    print("\n===== Testing Agent with RAG Query =====")
    
    # Create agent with patched tools
    with patch('agent.create_score_tool') as mock_score_tool, \
         patch('agent.create_student_info_tool') as mock_student_tool, \
         patch('agent.create_score_calculator') as mock_calculator, \
         patch('agent.create_rag_tool') as mock_rag_tool:
         
        # Set up mock tools
        mock_score = MagicMock()
        mock_score.get_student_scores = MockTool.mock_student_scores
        mock_score_tool.return_value = mock_score
        
        mock_student = MagicMock()
        mock_student.get_student_info = MockTool.mock_student_info
        mock_student_tool.return_value = mock_student
        
        mock_calc = MagicMock()
        mock_calc.calculate_average_scores = MockTool.mock_calculate_scores
        mock_calculator.return_value = mock_calc
        
        mock_rag = MagicMock()
        mock_rag.search_kma_regulations = MockTool.mock_rag_search
        mock_rag_tool.return_value = mock_rag
        
        # Create agent
        agent = create_supervisor_agent()
        
        # Create state with a regulation query
        state = MyAgentState()
        state.add_message(HumanMessage(content="What is the minimum GPA to graduate from KMA?"))
        
        # Run agent
        result = await agent(state)
        
        # Check results
        tool_messages = [m for m in result.messages if isinstance(m, ToolMessage)]
        ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
        
        # Verify RAG tool was used
        rag_used = any(m.name == "search_kma_regulations" for m in tool_messages)
        print(f"RAG tool used: {'✅' if rag_used else '❌'}")
        
        if tool_messages:
            print(f"Number of tool calls: {len(tool_messages)}")
            for i, msg in enumerate(tool_messages):
                print(f"  Tool {i+1}: {msg.name}")
        
        # Check if we got an AI response
        if ai_messages:
            print("AI response received: ✅")
            # Check if the response mentions the GPA requirement
            contains_gpa = "2.0" in ai_messages[-1].content
            print(f"Response mentions 2.0 GPA: {'✅' if contains_gpa else '❌'}")
        else:
            print("AI response received: ❌")
        
        # Check if the RAG results were stored
        if result.rag_results:
            print("RAG results stored in state: ✅")
            print(f"Number of RAG results: {len(result.rag_results)}")
        else:
            print("RAG results stored in state: ❌")
        
        return result


async def test_agent_with_combined_query():
    """Test the supervisor agent with a query that needs both RAG and score tools."""
    print("\n===== Testing Agent with Combined Query =====")
    
    # Create agent with patched tools
    with patch('agent.create_score_tool') as mock_score_tool, \
         patch('agent.create_student_info_tool') as mock_student_tool, \
         patch('agent.create_score_calculator') as mock_calculator, \
         patch('agent.create_rag_tool') as mock_rag_tool:
         
        # Set up mock tools
        mock_score = MagicMock()
        mock_score.get_student_scores = MockTool.mock_student_scores
        mock_score_tool.return_value = mock_score
        
        mock_student = MagicMock()
        mock_student.get_student_info = MockTool.mock_student_info
        mock_student_tool.return_value = mock_student
        
        mock_calc = MagicMock()
        mock_calc.calculate_average_scores = MockTool.mock_calculate_scores
        mock_calculator.return_value = mock_calc
        
        mock_rag = MagicMock()
        mock_rag.search_kma_regulations = MockTool.mock_rag_search
        mock_rag_tool.return_value = mock_rag
        
        # Create agent
        agent = create_supervisor_agent()
        
        # Create initial state with student code
        state = MyAgentState()
        state.student_code = "CT123"
        
        # Add a complex query that needs both regulation and score information
        state.add_message(HumanMessage(
            content="Am I meeting the graduation requirements based on my GPA?"
        ))
        
        # Run agent
        result = await agent(state)
        
        # Track tools used
        tool_counts = {}
        for m in result.messages:
            if isinstance(m, ToolMessage):
                if m.name in tool_counts:
                    tool_counts[m.name] += 1
                else:
                    tool_counts[m.name] = 1
        
        print("Tools used:")
        for tool, count in tool_counts.items():
            print(f"  {tool}: {count} time(s)")
        
        # Check if both RAG and score tools were used
        rag_used = "search_kma_regulations" in tool_counts
        scores_used = "get_student_scores" in tool_counts or "calculate_average_scores" in tool_counts
        
        print(f"RAG tool used: {'✅' if rag_used else '❌'}")
        print(f"Score tools used: {'✅' if scores_used else '❌'}")
        
        # Check if we got an AI response
        ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
        if ai_messages:
            print("AI response received: ✅")
            response = ai_messages[-1].content.lower()
            contains_gpa = "gpa" in response or "average" in response
            contains_requirement = "requirement" in response or "graduate" in response
            
            print(f"Response mentions GPA/average: {'✅' if contains_gpa else '❌'}")
            print(f"Response mentions requirements: {'✅' if contains_requirement else '❌'}")
        else:
            print("AI response received: ❌")
        
        return result


async def run_tests():
    """Run all agent tests."""
    print("\n===== Starting Integrated Agent Tests =====")
    
    # Test with regulation query
    rag_result = await test_agent_with_rag_query()
    
    # Test with combined query
    combined_result = await test_agent_with_combined_query()
    
    print("\n===== All Tests Completed =====")


if __name__ == "__main__":
    asyncio.run(run_tests()) 