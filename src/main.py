import os
import sys
import json
import asyncio
import argparse
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from agent import create_supervisor_agent
from agent.state import MyAgentState

# Load environment variables
load_dotenv()


def format_message_for_display(message):
    """Format message for display in terminal"""
    if isinstance(message, HumanMessage):
        return f"Human: {message.content}"
    elif isinstance(message, AIMessage):
        return f"AI: {message.content}"
    elif isinstance(message, ToolMessage):
        content = message.content
        # Try to parse and prettify JSON
        try:
            data = json.loads(content)
            content = json.dumps(data, indent=2)
            return f"Tool ({message.name}):\n{content}"
        except:
            # Not JSON or invalid JSON
            return f"Tool ({message.name}): {content[:150]}..."
    return str(message)


async def cleanup_resources():
    """Cleanup any resources before exiting"""
    # Add any cleanup code here if needed
    pass


async def run_conversation(initial_message: str = None):
    """Run an interactive conversation with the agent"""
    try:
        # Create agent
        agent = create_supervisor_agent()
        
        # Create initial state
        state = MyAgentState()
        
        # Start conversation loop
        print("\n=== KMA Student Assistant ===")
        print("Type 'exit', 'quit', or press Ctrl+C to end the conversation.\n")
        
        if initial_message:
            print(f"Human: {initial_message}")
            state.add_message(HumanMessage(content=initial_message))
            current_state = agent.invoke(state)
        else:
            current_state = state
        
        while True:
            # Check if we need human input
            if current_state.awaiting_human_input:
                print(f"\nAgent: {current_state.human_input_prompt}")
                user_input = input("> ")
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                # Process human input
                human_message = HumanMessage(content=user_input)
                current_state.add_message(human_message)
                current_state.set_human_input_received()
                
            else:
                # Run agent
                current_state = agent.invoke(current_state)
                
                # Print new messages (only the last one should be from the AI)
                for message in current_state.messages[-1:]:
                    print(f"\n{format_message_for_display(message)}")
                
                if not current_state.awaiting_human_input:
                    # Get next user message
                    user_input = input("\nHuman: ")
                    
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    
                    # Add to state
                    current_state.add_message(HumanMessage(content=user_input))
        
        print("\nConversation ended.")
        
    except KeyboardInterrupt:
        print("\nConversation ended by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        await cleanup_resources()


async def run_single_query(query: str):
    """Run a single query through the agent and exit"""
    try:
        # Create agent
        agent = create_supervisor_agent()
        
        # Create initial state
        state = MyAgentState()
        
        # Add query
        state.add_message(HumanMessage(content=query))
        
        # Run agent
        result = agent.invoke(state)
        
        # If we need human input, request it
        while result.awaiting_human_input:
            print(f"\nAgent: {result.human_input_prompt}")
            user_input = input("> ")
            
            # Process human input
            human_message = HumanMessage(content=user_input)
            result.add_message(human_message)
            result.set_human_input_received()
            
            # Continue
            result = agent.invoke(result)
        
        # Print all messages
        for message in result.messages:
            print(f"\n{format_message_for_display(message)}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        await cleanup_resources()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="KMA Student Assistant")
    parser.add_argument(
        "--query", "-q", type=str, help="Run a single query and exit"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.query:
        await run_single_query(args.query)
    else:
        await run_conversation()


if __name__ == "__main__":
    asyncio.run(main()) 