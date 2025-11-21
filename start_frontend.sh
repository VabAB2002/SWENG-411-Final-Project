#!/bin/bash
# Quick start script for frontend development server

echo "🚀 Starting Penn State Course Recommendation Frontend..."
echo ""

# Navigate to frontend
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start Vite dev server
echo "✓ Starting Vite development server..."
echo ""
npm run dev

