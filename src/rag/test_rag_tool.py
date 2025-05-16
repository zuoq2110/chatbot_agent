#!/usr/bin/env python
"""
Test script for the KMA RAG Tool.

This script tests the functionality of the RAG (Retrieval Augmented Generation) tool
used for retrieving information about KMA regulations.
"""

import asyncio
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from langchain_core.documents import Document

from tool import get_chat_agent, search_kma_regulations, create_rag_tool
from rag_graph import KMAChatAgent


class TestRAGTool(unittest.TestCase):
    """Test cases for the RAG Tool functionality."""

    def setUp(self):
        """Set up test environment."""
        # Make sure there's a regulation.txt file for the retriever
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = os.path.join(self.project_root, "data")
        self.vector_db_path = os.path.join(self.project_root, "vector_db")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Create a sample regulation file if it doesn't exist
        self.regulation_file = os.path.join(self.data_dir, "regulation.txt")
        if not os.path.exists(self.regulation_file):
            with open(self.regulation_file, "w", encoding="utf-8") as f:
                f.write("This is a sample KMA regulation for testing.\n")
                f.write("Students must maintain a GPA of at least 2.0 to graduate.\n")
                f.write("All students must complete at least 120 credits to graduate.\n")
    
    @patch('tool.KMAChatAgent')
    def test_get_chat_agent(self, mock_agent):
        """Test that get_chat_agent returns a singleton instance."""
        # Reset singleton for testing
        import tool
        tool._chat_agent = None
        
        # Call get_chat_agent twice
        agent1 = get_chat_agent()
        agent2 = get_chat_agent()
        
        # Verify the agent is created only once
        mock_agent.assert_called_once()
        
        # Verify we get the same instance both times
        self.assertEqual(agent1, agent2)
    
    @patch('tool.get_chat_agent')
    async def test_search_kma_regulations(self, mock_get_agent):
        """Test the search_kma_regulations function."""
        # Create mock agent and retriever
        mock_agent = MagicMock()
        mock_agent.chat.return_value = "Students must maintain a GPA of at least 2.0 to graduate."
        
        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = [
            Document(page_content="Students must maintain a GPA of at least 2.0 to graduate."),
            Document(page_content="All students must complete at least 120 credits to graduate.")
        ]
        mock_agent.retriever = mock_retriever
        
        # Set up get_chat_agent to return our mock
        mock_get_agent.return_value = mock_agent
        
        # Call the function
        result = await search_kma_regulations("What is the minimum GPA required to graduate?")
        
        # Verify the result
        result_data = json.loads(result)
        
        # Check if the function called the agent's chat method
        mock_agent.chat.assert_called_once_with("What is the minimum GPA required to graduate?")
        
        # Check that result contains expected fields
        self.assertIn("answer", result_data)
        self.assertIn("sources", result_data)
        self.assertIn("message", result_data)
        
        # Check answer content
        self.assertEqual(result_data["answer"], "Students must maintain a GPA of at least 2.0 to graduate.")
        
        # Check sources
        self.assertEqual(len(result_data["sources"]), 2)
        self.assertTrue(any("GPA of at least 2.0" in source for source in result_data["sources"]))
    
    @patch('tool.get_chat_agent')
    async def test_search_kma_regulations_error_handling(self, mock_get_agent):
        """Test error handling in search_kma_regulations."""
        # Set up agent to raise an exception
        mock_agent = MagicMock()
        mock_agent.chat.side_effect = Exception("Test exception")
        mock_get_agent.return_value = mock_agent
        
        # Call the function
        result = await search_kma_regulations("What is the minimum GPA?")
        
        # Verify the result
        result_data = json.loads(result)
        
        # Check that we got an error message
        self.assertEqual(result_data["answer"], "")
        self.assertEqual(result_data["sources"], [])
        self.assertIn("Error searching KMA regulations", result_data["message"])
        self.assertIn("Test exception", result_data["message"])
    
    def test_create_rag_tool(self):
        """Test create_rag_tool returns the search_kma_regulations function."""
        with patch('tool.get_chat_agent'):
            tool_fn = create_rag_tool()
            self.assertEqual(tool_fn, search_kma_regulations)


async def run_async_tests():
    """Run the async test methods."""
    # Create an instance of the test class
    test_case = TestRAGTool()
    
    # Set up the test environment
    test_case.setUp()
    
    # Run async tests
    await test_case.test_search_kma_regulations()
    await test_case.test_search_kma_regulations_error_handling()
    
    print("All async tests passed!")


def run_sync_tests():
    """Run the synchronous test methods."""
    # Run only synchronous tests using unittest
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add only the synchronous test methods
    sync_test_names = [
        'test_get_chat_agent',
        'test_create_rag_tool'
    ]
    
    for test_name in sync_test_names:
        suite.addTest(TestRAGTool(test_name))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    print("Testing KMA RAG Tool...")
    
    # Run synchronous tests
    run_sync_tests()
    
    # Run asynchronous tests
    asyncio.run(run_async_tests())
    
    print("All tests completed!") 