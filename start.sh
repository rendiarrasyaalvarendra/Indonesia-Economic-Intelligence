#!/bin/bash
# Indonesia Economic Intelligence — Quick Start Script (macOS/Linux)

echo "====================================================="
echo " Indonesia Economic Intelligence Platform"
echo " Quick Start Script"
echo "====================================================="
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found."
    echo "Install from https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env and add your OPENAI_API_KEY."
    echo ""
fi

echo ""
echo "Starting Indonesia Economic Intelligence..."
echo "Open http://localhost:8000 in your browser"
echo "Press Ctrl+C to stop"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
