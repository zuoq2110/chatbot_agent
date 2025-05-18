#!/bin/bash

# KMA Chat Agent Runner Script
# This script runs the KMA Chat Agent backend and/or Streamlit frontend

# Default ports
BACKEND_PORT=8000
STREAMLIT_PORT=8501

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print KMA Chat Agent header
print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "             KMA CHAT AGENT RUNNER                "
    echo "=================================================="
    echo -e "${NC}"
}

# Print help information
print_help() {
    echo -e "${GREEN}Usage:${NC}"
    echo "  ./run.sh [options]"
    echo ""
    echo -e "${GREEN}Options:${NC}"
    echo "  --help                 Show this help message"
    echo "  --backend              Run only the backend API"
    echo "  --frontend             Run only the Streamlit frontend"
    echo "  --all                  Run both backend and frontend (default)"
    echo "  --backend-port PORT    Set backend port (default: 8000)"
    echo "  --frontend-port PORT   Set frontend port (default: 8501)"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./run.sh --all"
    echo "  ./run.sh --backend --backend-port 9000"
    echo "  ./run.sh --frontend --frontend-port 8502"
}

# Run backend API
run_backend() {
    echo -e "${BLUE}Starting Backend API on port ${BACKEND_PORT}...${NC}"
    python -m src.backend.main start --port ${BACKEND_PORT} &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend API running with PID: ${BACKEND_PID}${NC}"
    echo -e "${GREEN}Backend API URL: http://localhost:${BACKEND_PORT}${NC}"
    echo -e "${GREEN}API Documentation: http://localhost:${BACKEND_PORT}/docs${NC}"
}

# Run Streamlit frontend
run_frontend() {
    echo -e "${BLUE}Starting Streamlit frontend on port ${STREAMLIT_PORT}...${NC}"
    streamlit run src/frontend/app.py --server.port=${STREAMLIT_PORT} &
    FRONTEND_PID=$!
    echo -e "${GREEN}Streamlit frontend running with PID: ${FRONTEND_PID}${NC}"
    echo -e "${GREEN}Streamlit URL: http://localhost:${STREAMLIT_PORT}${NC}"
}

# Handle graceful shutdown
graceful_shutdown() {
    echo -e "${YELLOW}Shutting down KMA Chat Agent...${NC}"
    if [ ! -z "${BACKEND_PID}" ]; then
        echo -e "${YELLOW}Stopping Backend API (PID: ${BACKEND_PID})${NC}"
        kill ${BACKEND_PID} 2>/dev/null
    fi
    if [ ! -z "${FRONTEND_PID}" ]; then
        echo -e "${YELLOW}Stopping Streamlit frontend (PID: ${FRONTEND_PID})${NC}"
        kill ${FRONTEND_PID} 2>/dev/null
    fi
    echo -e "${GREEN}KMA Chat Agent stopped successfully${NC}"
    exit 0
}

# Setup signal handler for graceful shutdown
trap graceful_shutdown SIGINT SIGTERM

# Default to running all components
RUN_BACKEND=true
RUN_FRONTEND=true

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            print_header
            print_help
            exit 0
            ;;
        --backend)
            RUN_BACKEND=true
            RUN_FRONTEND=false
            shift
            ;;
        --frontend)
            RUN_BACKEND=false
            RUN_FRONTEND=true
            shift
            ;;
        --all)
            RUN_BACKEND=true
            RUN_FRONTEND=true
            shift
            ;;
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            STREAMLIT_PORT="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

# Print header
print_header

# Run the requested components
if [ "$RUN_BACKEND" = true ]; then
    run_backend
fi

if [ "$RUN_FRONTEND" = true ]; then
    run_frontend
fi

# Keep the script running
echo -e "${BLUE}KMA Chat Agent is running. Press Ctrl+C to stop.${NC}"
wait 