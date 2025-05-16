# KMA Chat Supervisor Agent

This module implements a multi-agent system using LangGraph to help KMA (Academy of Cryptography Techniques) students with their questions about regulations, scores, and other academic information.

## Architecture

The system follows a Supervisor Agent pattern with the following components:

### Main Components

1. **Supervisor Agent**: The central ReAct agent that orchestrates the workflow

   - Decides which tools or agents to use based on the question
   - Handles human-in-the-loop interaction when needed

2. **Tools**:
   - **RAG Tool**: Retrieves information from KMA regulations
   - **Student Info Tool**: Gets student information (name, class)
   - **Score Tool**: Retrieves student scores with filtering options
   - **Calculator Tool**: Calculates average scores and statistics

### State Management

The agent uses a shared state (`MyAgentState`) to keep track of:

- Conversation history
- Student information
- Score data
- Human-in-the-loop status
- Current task and tool being used

### LangGraph Implementation

The Supervisor Agent is implemented as a LangGraph with the following nodes:

1. **Agent Node**: Processes messages and decides next actions
2. **Tools Node**: Executes tools based on agent decisions
3. **Human Input Node**: Handles human-in-the-loop interaction

The graph's edges define the workflow:

```
Agent → Tools → Agent
Agent → Human Input → Agent
Agent → END
```

### Human-in-the-Loop

The system implements human-in-the-loop interaction to:

- Request student information when needed
- Ask for clarification on queries
- Handle ambiguous requests

## Usage

### Basic Usage

```python
from agent.supervisor_agent import run_agent

async def example():
    question = "What are the graduation requirements for KMA?"
    result = await run_agent(question)
    print(result.get_last_message().content)
```

### With Known Student Code

```python
async def example_with_student():
    question = "What were my scores last semester?"
    student_code = "CT050123"
    result = await run_agent(question, student_code)
    print(result.get_last_message().content)
```

### Interactive Demo

Run the demo script for an interactive session:

```bash
python -m src.agent.demo
```

## Development

### Adding New Tools

To add a new tool to the supervisor agent:

1. Create a new tool function with the appropriate LangChain tool decorator
2. Add the tool to the `tools` list in `create_supervisor_agent`
3. Update the system prompt to include information about the new tool
4. Add handling for the tool in the `tools_executor` function

### Extending the State

If you need to store additional information in the agent state:

1. Update the `MyAgentState` class in `agent/state.py`
2. Add helper methods as needed for managing the new state properties

## Debugging

- Set environment variables in `.env` file
- Check logs and tool outputs in the console
- Run the agent with test cases to verify behavior

## Future Improvements

- Add authentication and authorization
- Implement memory for longer conversations
- Add more specialized agents for complex tasks
- Improve error handling and recovery
