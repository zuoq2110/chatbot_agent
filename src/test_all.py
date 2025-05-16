#!/usr/bin/env python
"""
Main test script for the KMA Chat Agent.
This script runs all the individual component tests.
"""

import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def run_score_tests():
    """Run tests for the score component"""
    try:
        print("\n" + "="*50)
        print("Running Score Component Tests")
        print("="*50)
        
        # Import and run score tests
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "score"))
        from score.test_score_tool import run_tests as run_score_tests
        
        await run_score_tests()
        return True
    except Exception as e:
        print(f"Error running score tests: {str(e)}")
        return False


async def run_rag_tests():
    """Run tests for the RAG component"""
    try:
        print("\n" + "="*50)
        print("Running RAG Component Tests")
        print("="*50)
        
        # Import and run RAG tests
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "rag"))
        from rag.test_rag_tool import run_tests as run_rag_tests
        
        await run_rag_tests()
        return True
    except Exception as e:
        print(f"Error running RAG tests: {str(e)}")
        return False


async def run_agent_tests():
    """Run tests for the agent component"""
    try:
        print("\n" + "="*50)
        print("Running Agent Component Tests")
        print("="*50)
        
        # Import and run agent tests
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agent"))
        from agent.test_agent import run_tests as run_agent_tests
        
        await run_agent_tests()
        return True
    except Exception as e:
        print(f"Error running agent tests: {str(e)}")
        return False


async def run_all_tests():
    """Run all component tests"""
    print("="*50)
    print("KMA Chat Agent Test Suite")
    print("="*50)
    print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run component tests
    score_success = await run_score_tests()
    rag_success = await run_rag_tests()
    agent_success = await run_agent_tests()
    
    # Print summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Score Component: {'✅ Passed' if score_success else '❌ Failed'}")
    print(f"RAG Component: {'✅ Passed' if rag_success else '❌ Failed'}")
    print(f"Agent Component: {'✅ Passed' if agent_success else '❌ Failed'}")
    
    # Overall result
    if score_success and rag_success and agent_success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. See details above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests()) 