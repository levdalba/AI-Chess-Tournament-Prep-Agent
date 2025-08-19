#!/bin/bash
# Development setup script

echo "🚀 Setting up AI Chess Tournament Prep Agent for development..."

# Check if .env exists, if not create it from template
if [ ! -f .env ]; then
    echo "📄 Creating .env from template..."
    cp .env.template .env
    echo "✅ .env created! Please edit it with your configuration."
else
    echo "✅ .env already exists"
fi

# Check if Stockfish is available
if command -v stockfish &> /dev/null; then
    STOCKFISH_PATH=$(which stockfish)
    echo "♟️  Stockfish found at: $STOCKFISH_PATH"
else
    echo "⚠️  Stockfish not found. Please install:"
    echo "   macOS: brew install stockfish"
    echo "   Ubuntu: sudo apt install stockfish"
fi

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if python -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
    echo "✅ Backend dependencies installed"
else
    echo "📦 Installing backend dependencies..."
    cd backend && pip install -r requirements.txt
fi

if python -c "import chess, aiohttp, beautifulsoup4" 2>/dev/null; then
    echo "✅ Data analysis dependencies installed"
else
    echo "📦 Installing data analysis dependencies..."
    cd data && pip install -r requirements.txt
fi

# Check Node.js dependencies
echo "📦 Checking Node.js dependencies..."
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install
fi

echo "🎉 Setup complete! You can now run:"
echo "   Backend:  cd backend && python main.py"
echo "   Frontend: cd frontend && npm run dev"
echo "   Visit:    http://localhost:5173"
