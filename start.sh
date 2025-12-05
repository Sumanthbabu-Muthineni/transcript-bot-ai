#!/bin/bash

# Quick start script for YouTube RAG application

echo "=========================================="
echo "  YouTube RAG Application - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found!"
    echo "Please create it from backend/.env.example and add your API keys"
    echo ""
    echo "  cp backend/.env.example backend/.env"
    echo "  nano backend/.env"
    echo ""
    exit 1
fi

# Start backend server in background
echo "🚀 Starting backend server on http://localhost:5000..."
cd backend/local_dev
python3 local_server.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 2

# Start frontend server in background
echo "🌐 Starting frontend server on http://localhost:8000..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application is running!"
echo ""
echo "📱 Open your browser and go to:"
echo "   http://localhost:8000"
echo ""
echo "📝 To stop the servers, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🎬 Paste a YouTube URL and start chatting with videos!"
echo "=========================================="

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
