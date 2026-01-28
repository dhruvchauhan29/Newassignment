#!/bin/bash
# Startup script for the AI Product-to-Code System

echo "🚀 Starting AI Product-to-Code Multi-Agent System"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    exit 1
fi

# Run migrations (if database is configured)
echo "🗄️  Running database migrations..."
alembic upgrade head 2>/dev/null || echo "⚠️  Skipping migrations (database not configured)"

# Start the application
echo ""
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
