#!/bin/bash
# Convenient script to run the AI agent

# Activate virtual environment
source .venv/bin/activate

# Run the agent
python3 cli_entrypoint.py "$@"
