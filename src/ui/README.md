# KMA Agent Streamlit Demo

This is a Streamlit-based demo for the KMA Agent. It provides a user-friendly interface to interact with the agent.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install streamlit
```

Or if you're using Poetry:

```bash
poetry add streamlit
```

## Running the Streamlit Demo

To run the Streamlit demo, execute:

```bash
streamlit run src/ui/streamlit_app.py
```

This will start a local web server and automatically open your browser to the demo page.

## Troubleshooting

If you encounter issues with the agent responses, check the following:

1. Make sure you have all the required dependencies installed, including `nest-asyncio`:

   ```bash
   poetry add nest-asyncio
   ```

2. Ensure that the agent's environment variables are properly set up.

3. Enable debug mode in the Streamlit UI to see processing times and detailed logs.

4. If you get the error "I couldn't generate a response. Please try a different query.", it means the agent wasn't able to generate a proper response. This could be due to:
   - The agent's tools returning errors
   - Issues with the query itself
   - Problems with the agent's implementation

## Features

- Chat interface to interact with the KMA Agent
- Session history to keep track of conversations
- Clear chat functionality
- Examples of questions to ask

## Note

This Streamlit demo operates independently from the API. You don't need to start the API server to use this demo.
