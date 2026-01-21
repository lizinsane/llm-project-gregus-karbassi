#!/bin/bash

# Swiss History RAG - Setup Script
# This script sets up the complete environment for the project

echo "🇨🇭 Swiss History RAG - Setup Script"
echo "======================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
python3 -c "from src.utils import ensure_directories; ensure_directories()"

# Test configuration
echo ""
echo "🧪 Testing configuration..."
python3 src/utils.py

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Place your PDF in data/raw/ directory"
echo "3. Run: python src/ingestion/pdf_processor.py (Phase 2)"
echo "4. Run: streamlit run src/web/app.py (Phase 4)"
echo ""
echo "To activate the environment later, run:"
echo "  source venv/bin/activate"
echo ""
