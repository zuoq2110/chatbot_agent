#!/usr/bin/env python3
"""
Script to run the KMA Chat Agent backend.
"""

import os
import sys

# Add the project root to Python path to enable absolute imports
sys.path.insert(0, os.path.abspath("."))

# Import the cli function from the backend module
from src.backend.main import cli

if __name__ == "__main__":
    # Run the CLI which starts the backend server
    cli() 