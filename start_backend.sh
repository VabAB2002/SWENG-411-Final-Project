#!/bin/bash
# Quick start script for backend server

echo "🚀 Starting Penn State Course Recommendation Backend..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Navigate to backend
cd backend

# Start Flask server
echo "✓ Starting Flask server on http://localhost:5001"
echo ""
python3 app.py

