# KMA Agent API

This is a FastAPI-based API for the KMA Agent. It provides a simple endpoint to interact with the agent.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install fastapi uvicorn
```

Or if you're using Poetry:

```bash
poetry add fastapi uvicorn
```

## Running the API

To run the API server, execute:

```bash
uvicorn src.api.agent_api:app --reload
```

This will start the API server at `http://localhost:8000`.

## API Endpoints

- `GET /`: Simple health check endpoint
- `POST /query`: Main endpoint to interact with the agent
  - Request body: `{"query": "your question here"}`
  - Response body: `{"response": "agent's response"}`

## Testing the API

You can test the API using curl:

```bash
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"query": "What are the graduation requirements for KMA?"}'
```

Or using the Swagger UI at `http://localhost:8000/docs`.

## Note

This API operates independently from the Streamlit demo. You don't need to start the Streamlit server to use this API.
