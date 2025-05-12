#!/usr/bin/env python3
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

from retriever import create_hybrid_retriever
from graph import KMAChatAgent

# Load environment variables
load_dotenv()


def main():
    """Main function to run the chat application"""
    print("Initializing KMA Chat Assistant...")
    try:
        # Get the current directory and project root
        current_dir = Path(__file__).parent.absolute()
        project_root = current_dir.parent.parent.parent
        
        # Paths for vector database and data
        vector_db_path = os.path.join(current_dir, "vector_db")
        data_path = os.path.join(project_root, "data", "regulation.txt")
        
        # Create hybrid retriever
        hybrid_retriever, _ = create_hybrid_retriever(
            vector_db_path=vector_db_path,
            data_path=data_path
        )
        
        # Initialize chat agent
        chat_agent = KMAChatAgent(hybrid_retriever)
        
        print("\nKMA Chat Assistant is ready! Type 'quit' to exit.")
        print("Ask me anything about KMA!\n")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                # Check if user wants to quit
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye! Have a great day!")
                    break

                # Skip empty inputs
                if not user_input:
                    continue

                # Get AI response
                print("\nAssistant: ", end="")
                response = chat_agent.chat(user_input)
                print(response)

            except UnicodeDecodeError as e:
                print(f"\nError with text encoding: {e}")
                print("Please try again with different text.")
            except Exception as e:
                print("\nError during conversation:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print("\nDetailed error traceback:")
                traceback.print_exc()
                print("\nYou can continue chatting or type 'quit' to exit.")

    except Exception as e:
        print("\nFatal error during initialization:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        print("\nPlease check your environment setup and try again.")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print("\nUnexpected error:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nDetailed error traceback:")
        traceback.print_exc()
        sys.exit(1) 