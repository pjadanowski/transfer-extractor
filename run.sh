#!/bin/bash
#
# Simple wrapper script to run the get-transfer application
#

# Activate the virtual environment and run the main script
cd "$(dirname "$0")"
./.venv/bin/python main.py "$@"