#!/bin/bash

# Single script to launch Python Backend & React Frontend simultaneously (using Yarn)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================================"
echo "  🚀 Starting Daily Brief (Python Backend + React UI)  "
echo "========================================================"

# Function to handle shutdown on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Shutting down backend & frontend servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Start Python Backend API (Port 8090)
echo "🐍 Launching Python Backend API on http://localhost:8090..."
python3 main.py --port 8090 &
BACKEND_PID=$!

# Wait 1 second for backend to initialize
sleep 1

# 2. Check if frontend node_modules exists, if not install via Yarn
if [ ! -d "$PROJECT_DIR/frontend/node_modules" ]; then
    echo "📦 Installing React frontend dependencies via Yarn..."
    (cd "$PROJECT_DIR/frontend" && yarn install)
fi

# 3. Start React Frontend Dev Server via Yarn (Port 3000)
echo "⚛️  Launching React Frontend on http://localhost:3000..."
(cd "$PROJECT_DIR/frontend" && yarn dev) &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are live!"
echo "   - Python Backend: http://localhost:8090"
echo "   - React Frontend (Yarn): http://localhost:3000"
echo "   (Press Ctrl+C to stop both servers)"
echo "========================================================"

# Keep script running to monitor children
wait
