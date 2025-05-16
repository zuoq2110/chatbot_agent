# KMA Chat Agent

A LangGraph-based agent system for Academy of Cryptography Techniques (KMA) students, designed to answer questions about regulations, student information, and academic scores.

## Features

- Simple API for querying the agent
- Interactive Streamlit UI for demonstrations
- Tools for KMA regulations search, student information, and score calculations
- No authentication or chat history (stateless)

## Setup

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:

```
# Required for LLM
OPENAI_API_KEY=your-openai-api-key

# MongoDB connection (if needed)
MONGODB_URL=your-mongodb-url
MONGODB_DB_NAME=kma_chat
```

## Usage

The system provides two separate interfaces:

### FastAPI Server

Run the FastAPI server:

```bash
python src/main.py --api
```

This will start the API server at http://localhost:8000

API Endpoints:

- GET `/` - Basic health check and info
- POST `/query` - Submit a query to the agent
  - Request body: `{"query": "your question here"}`
  - Response: `{"response": "agent's answer", "processing_time_ms": 123.45}`

Example curl request:

```bash
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "What are the graduation requirements for KMA?"}'
```

### Streamlit UI

Run the Streamlit UI:

```bash
python src/main.py --ui
```

This will start the Streamlit app, usually at http://localhost:8501

The UI provides:

- A chat-like interface for interacting with the agent
- Example queries to get started
- Debug mode toggle to see processing times and details

### Testing

Test the agent directly without starting the server or UI:

```bash
python src/main.py --test "What are the graduation requirements for KMA?"
```

## Components

- `src/agent/supervisor_agent.py` - The core LangGraph agent implementation
- `src/api/agent_api.py` - FastAPI server implementation
- `src/ui/streamlit_app.py` - Streamlit UI implementation
- `src/main.py` - Command-line interface for running the components

## Development

Both the API and Streamlit app can be run independently. The code is structured to ensure each component can run without the other.

To modify the agent behavior, edit the `src/agent/supervisor_agent.py` file.
