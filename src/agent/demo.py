#!/usr/bin/env python
"""
Demo script for the KMA Supervisor Agent.

This script demonstrates the agent's ability to understand queries, use tools, and
handle human-in-the-loop interactions with a simple interactive loop.
"""

import asyncio
import os
from dotenv import load_dotenv
from typing import List

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent import create_supervisor_agent
from state import MyAgentState

# Load environment variables
load_dotenv()


async def print_message(message, prefix=None):
    """Print a message with optional prefix"""
    if prefix:
        print(f"{prefix}: {message}")
    else:
        print(message)


async def format_tool_message(message: ToolMessage):
    """Format a tool message for display"""
    content = message.content
    if len(content) > 100:
        content = f"{content[:100]}..."
    return f"[Tool: {message.name}] {content}"


async def print_agent_state(state: MyAgentState):
    """Print relevant information from the agent state"""
    if state.student_code:
        print(f"\nStudent: {state.student_name or 'Unknown'} ({state.student_code})")
        print(f"Class: {state.student_class or 'Unknown'}")
    
    if state.scores:
        print(f"\nRetrieved {len(state.scores)} scores")
    
    if state.average_scores and "overall_average" in state.average_scores:
        overall = state.average_scores["overall_average"]
        print(f"\nOverall Averages:")
        print(f"  First: {overall.get('score_first', 'N/A')}")
        print(f"  Second: {overall.get('score_second', 'N/A')}")
        print(f"  Final: {overall.get('score_final', 'N/A')}")
        print(f"  Overall: {overall.get('score_over_rall', 'N/A')}")
    
    # Display RAG results
    if state.rag_results:
        print(f"\nRetrieved {len(state.rag_results)} regulation search results")
        # Show the latest RAG result sources
        if state.rag_results[-1].get("sources"):
            print("\nSources used:")
            for i, source in enumerate(state.rag_results[-1]["sources"][:2]):  # Show first 2 sources
                short_source = source[:100] + "..." if len(source) > 100 else source
                print(f"  Source {i+1}: {short_source}")


async def interactive_demo():
    """Run an interactive demo of the KMA Agent"""
    print("=== KMA Agent Interactive Demo ===")
    print("Type 'exit' to quit the demo")
    
    # Create agent
    print("\nInitializing agent...")
    agent = create_supervisor_agent()
    
    # Create state
    state = MyAgentState()
    
    # Interactive loop
    while True:
        print("\n" + "-" * 50)
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting demo...")
            break
        
        # Add user message to state
        state.add_message(HumanMessage(content=user_input))
        
        # Run agent
        try:
            result = await agent(state)
            state = result  # Update state with results
            
            # Check if we need human input
            if result.awaiting_human_input:
                await print_message(f"\n[Agent needs input]: {result.human_input_prompt}")
                human_input = input("Your response: ")
                
                # Add human input
                state.add_message(HumanMessage(content=human_input))
                state.set_human_input_received()
                
                # Continue execution
                result = await agent(state)
                state = result  # Update state again
            
            # Print AI response
            ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                await print_message(last_ai_message.content, "Agent")
            
            # Print tool usage
            tool_messages = [m for m in result.messages if isinstance(m, ToolMessage)]
            if tool_messages:
                print("\nTools used:")
                for message in tool_messages[-3:]:  # Show last 3 tool messages
                    formatted = await format_tool_message(message)
                    print(f"  {formatted}")
            
            # Print state information
            await print_agent_state(state)
            
        except Exception as e:
            print(f"\nError: {str(e)}")


async def demo_queries():
    """Run a demo with predefined queries"""
    print("=== KMA Agent Demo with Predefined Queries ===")
    
    # Create agent
    print("\nInitializing agent...")
    agent = create_supervisor_agent()
    
    # Define queries to demonstrate
    queries = [
        "Hello, can you help me?",
        "What are the graduation requirements at KMA?",
        "What are my scores for the first semester?",
        "What's my GPA?",
        "How many credits do I need to graduate?"
    ]
    
    # Process each query
    for query in queries:
        print("\n" + "-" * 50)
        print(f"Query: {query}")
        
        # Create new state for each query
        state = MyAgentState()
        state.add_message(HumanMessage(content=query))
        
        # Run agent
        try:
            result = await agent(state)
            
            # Check if we need human input
            if result.awaiting_human_input:
                print(f"\n[Agent needs input]: {result.human_input_prompt}")
                
                # For demo purposes, we'll provide a fake student code
                human_input = "CT123"
                print(f"Providing: {human_input}")
                
                # Add human input
                result.add_message(HumanMessage(content=human_input))
                result.set_human_input_received()
                
                # Continue execution
                result = await agent(result)
            
            # Print AI response
            ai_messages = [m for m in result.messages if isinstance(m, AIMessage)]
            if ai_messages:
                last_ai_message = ai_messages[-1]
                print(f"\nAgent: {last_ai_message.content}")
            
            # Print tool usage
            tool_messages = [m for m in result.messages if isinstance(m, ToolMessage)]
            if tool_messages:
                print("\nTools used:")
                for message in tool_messages:
                    formatted = await format_tool_message(message)
                    print(f"  {formatted}")
            
            # Print state information
            await print_agent_state(result)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        # Pause between queries
        await asyncio.sleep(1)


if __name__ == "__main__":
    print("Starting KMA Agent Demo...")
    print("1. Interactive demo")
    print("2. Predefined queries demo")
    choice = input("Select a demo (1 or 2): ")
    
    if choice == "1":
        asyncio.run(interactive_demo())
    else:
        asyncio.run(demo_queries())
    
    print("\nDemo completed!") 