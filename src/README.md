# KMA Agent Demos

This directory contains two implementations for interacting with the KMA Agent:

1. **API**: A FastAPI-based API for programmatic interaction
2. **Streamlit UI**: A user-friendly web interface for demonstration

## API

The API provides a simple endpoint to interact with the KMA Agent. It's designed for programmatic access and integration with other systems.

### Running the API

```bash
uvicorn src.api.agent_api:app --reload
```

For more details, see the [API README](api/README.md).

## Streamlit UI

The Streamlit UI provides a user-friendly interface to demonstrate the KMA Agent. It's designed for human interaction and exploration.

### Running the Streamlit UI

```bash
streamlit run src/ui/streamlit_app.py
```

For more details, see the [Streamlit UI README](ui/README.md).

## Usage

You can run either the API or the Streamlit UI separately, depending on your needs. They don't depend on each other and can be used independently.

### Dependencies

Both implementations require the KMA Agent to be properly set up and configured. Make sure you have the necessary environment variables set up (check the `.env` file requirements in the agent documentation).

## Development

To add new features or modify the existing implementations:

1. For API changes, modify `src/api/agent_api.py`
2. For Streamlit UI changes, modify `src/ui/streamlit_app.py`

## Running Tests

While there are no specific tests for these implementations yet, you can test them manually by:

1. Running the API and using the Swagger UI at `http://localhost:8000/docs`
2. Running the Streamlit UI and interacting with it in your browser
