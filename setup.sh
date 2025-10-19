#!/bin/bash
# Setup script for macOS/Linux

echo "===================================="
echo "  Equity Research Generator Setup  "
echo "  Platform: macOS/Linux            "
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "❌ Error: Python 3.10+ required"
    exit 1
fi
echo "✅ Python version OK"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Install dependencies (placeholder - will be created during Phase 1)
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found - will be created during Phase 1"
fi
echo ""

# Check Ollama installation
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    ollama_version=$(ollama --version 2>&1)
    echo "   Version: $ollama_version"
    
    # Check if llama3 is available
    if ollama list | grep -q "llama3"; then
        echo "✅ llama3 model is already pulled"
    else
        echo "Pulling llama3 model (this may take a few minutes)..."
        ollama pull llama3
        echo "✅ llama3 model pulled"
    fi
else
    echo "⚠️  Ollama is not installed"
    echo ""
    echo "To install Ollama:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "Or using Homebrew:"
    echo "  brew install ollama"
fi
echo ""

echo "===================================="
echo "✅ Setup Complete!"
echo "===================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To start Ollama (if not running):"
echo "  ollama serve"
echo ""
echo "To run the application (after Phase 1):"
echo "  streamlit run ui/app.py"
echo ""

