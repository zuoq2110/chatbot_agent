# KMA AI Agent

This module implements a multi-agent system for KMA (Academy of Cryptography Techniques) students to get information about regulations, student details, and scores.

## Architecture

The system uses a LangGraph-based ReAct agent as the Supervisor Agent, which coordinates multiple tools and sub-agents:

1. **Supervisor Agent**: Main ReAct agent that orchestrates other tools and agents, using LangGraph for workflow management
2. **RAG Tool**: Retrieval Augmented Generation for accessing KMA regulations
3. **Student Info Tool**: Tool for retrieving student information from the database
4. **Score Tool**: Tool for retrieving and processing student scores
5. **Calculator Tool**: Tool for calculating average scores

The system also implements human-in-the-loop functionality for collecting information from users when needed (like student code).

## Components

### State Management

The `MyAgentState` class in `state.py` tracks:

- Conversation history (messages)
- Student information (student code, name, class)
- Scores and calculated averages
- Human-in-the-loop state

### Agent Workflow

The agent workflow in `agent.py` defines a StateGraph with the following nodes:

- `chatbot`: Processes user messages and decides on next actions
- `tool_executor`: Executes appropriate tools based on the user's query
- `request_student_code`: Requests student code from the user when needed
- `handle_human_input`: Processes human input when received
- `process_tool_results`: Updates the state with tool results

### Tools

The agent integrates the following tools:

- `get_student_scores`: Get student scores with filtering options
- `get_student_info`: Get student information
- `calculate_average_scores`: Calculate average scores
- `search_kma_regulations`: Search for information in KMA regulations

## Usage

To use the KMA Agent in your application:

```python
from agent import create_supervisor_agent
from state import MyAgentState
from langchain_core.messages import HumanMessage

# Create agent
agent = create_supervisor_agent()

# Create initial state
state = MyAgentState()

# Add user query
state.add_message(HumanMessage(content="What are my scores for the first semester?"))

# Run agent
result = await agent(state)

# Check if we need human input
if result.awaiting_human_input:
    print(f"Need input: {result.human_input_prompt}")
    human_input = input("> ")

    # Process human input
    result.add_message(HumanMessage(content=human_input))
    result.set_human_input_received()

    # Continue execution
    result = await agent(result)

# Process final response
print(f"Agent response: {result.messages[-1].content}")
```

## Testing

The `test_agent.py` script provides a way to test the agent's functionality, including:

- Agent initialization
- Simple queries
- Regulation queries
- Score queries (with human-in-the-loop for student code)
- Queries with specific semester formats

Run the test script with:

```bash
python src/agent/test_agent.py
```

## Configuration

The agent uses tools from the `score` package and the `rag` package. Make sure both are properly configured:

1. For the score package, ensure the PostgreSQL database is set up (see `src/score/README.md`)
2. For the RAG component, ensure the vector database is created and regulation data is available

Environment variables should be set in a `.env` file:

- `POSTGRES_URI`: URI for the PostgreSQL database
- `OPENAI_API_KEY`: API key for OpenAI (if using OpenAI models)
