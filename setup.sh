#!/bin/bash
# Initial setup script for Penn State Course Recommendation System

echo "================================================"
echo "Penn State Course Recommendation System Setup"
echo "================================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

# Check Node version
echo "🔍 Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   Found Node $NODE_VERSION"
else
    echo "   ❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Setup Python virtual environment
echo ""
echo "📦 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

# Activate and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
echo "   ✓ Python dependencies installed"

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "   ✓ Frontend dependencies installed"
else
    echo "   ✓ Frontend dependencies already installed"
fi
cd ..

# Create .gitkeep for uploads if needed
mkdir -p backend/uploads

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Start backend:  ./start_backend.sh"
echo "  2. Start frontend: ./start_frontend.sh"
echo "  3. Open http://localhost:5173 in your browser"
echo ""
echo "For more information, see README.md"

