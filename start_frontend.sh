#!/bin/bash
# Quick start script for frontend development server

echo "🚀 Starting Penn State Course Recommendation Frontend (Next.js)..."
echo ""

# Navigate to Next.js frontend
cd frontend-nextjs

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start Next.js dev server
echo "✓ Starting Next.js development server..."
echo "📱 Frontend will be available at http://localhost:3000"
echo ""
npm run dev

