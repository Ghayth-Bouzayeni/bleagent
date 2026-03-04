#!/bin/bash
# Setup script for BLE Agent Backend

set -e

echo "🚀 Setting up BLE Agent Backend..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo ""
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your DATABASE_URL before running the app!"
    echo "   nano .env"
else
    echo ""
    echo "✅ .env file exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Supabase DATABASE_URL:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Open the API docs:"
echo "   http://localhost:8000/docs"
echo ""
