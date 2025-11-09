#!/bin/bash
echo "Starting Backend Server..."
cd "$(dirname "$0")"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

