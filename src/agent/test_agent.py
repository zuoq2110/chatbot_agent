#!/usr/bin/env python
"""
Test script for the KMA Supervisor Agent.
This script tests the agent's ability to understand queries, use tools, and 
handle human-in-the-loop interactions.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from agent import create_supervisor_agent
from state import MyAgentState

# Load environment variables
load_dotenv()


async def test_agent_initialization():
    """Test agent initialization"""
    try:
        agent = create_supervisor_agent()
        print("✅ Agent initialization successful")
        return agent
    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        return None


async def test_agent_response(agent, query: str):
    """Test the agent's response to a query"""
    print(f"\nTesting query: '{query}'")
    
    # Create initial state
    state = MyAgentState()
    
    # Add query as message
    state.add_message(HumanMessage(content=query))
    
    try:
        # Run agent
        result = await agent(state)
        
        # Check for human input request
        if result.awaiting_human_input:
            print(f"✅ Agent requesting human input: {result.human_input_prompt}")
            return result, True
            
        # Check for tool usage
        tool_messages = [m for m in result.messages if isinstance(m, ToolMessage)]
        if tool_messages:
            print(f"✅ Agent used {len(tool_messages)} tools")
            for msg in tool_messages:
                print(f"   Tool: {msg.name}")
            
        # Check for AI response
        ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
        if ai_messages and ai_messages[-1].content:
            print("✅ Agent provided a response")
            content = ai_messages[-1].content
            print(f"   Response: {content[:100]}..." if len(content) > 100 else f"   Response: {content}")
        else:
            print("❌ Agent didn't provide a response")
            
        return result, False
    except Exception as e:
        print(f"❌ Agent processing failed: {str(e)}")
        return None, False


async def test_human_in_loop(agent, state: MyAgentState, human_input: str):
    """Test providing human input to the agent"""
    print(f"\nProviding human input: '{human_input}'")
    
    # Add human input
    state.add_message(HumanMessage(content=human_input))
    state.set_human_input_received()
    
    try:
        # Continue agent execution
        result = await agent(state)
        
        # Check for AI response
        ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
        if ai_messages and ai_messages[-1].content:
            print("✅ Agent provided a response after human input")
            content = ai_messages[-1].content
            print(f"   Response: {content[:100]}..." if len(content) > 100 else f"   Response: {content}")
        else:
            print("❌ Agent didn't provide a response after human input")
            
        return result
    except Exception as e:
        print(f"❌ Agent processing with human input failed: {str(e)}")
        return None


async def run_tests():
    """Run all agent tests"""
    print("\n===== Testing Agent Initialization =====")
    agent = await test_agent_initialization()
    if not agent:
        print("Cannot continue tests without agent")
        return
    
    print("\n===== Testing Simple Query =====")
    await test_agent_response(agent, "Hello, can you help me?")
    
    print("\n===== Testing Regulation Query =====")
    await test_agent_response(agent, "What are the graduation requirements at KMA?")
    
    print("\n===== Testing Score Query (Requires Student Code) =====")
    result, needs_input = await test_agent_response(agent, "What are my scores for the first semester?")
    
    if needs_input and result:
        print("\n===== Testing Human-in-Loop =====")
        await test_human_in_loop(agent, result, "CT123")  # Replace with a valid student code
    
    print("\n===== Testing Query with Semester Format =====")
    await test_agent_response(agent, "What are my scores for the semester ki1_2023_2024?")


if __name__ == "__main__":
    print("Starting KMA Agent Tests...")
    asyncio.run(run_tests())
    print("\nTests completed!") 