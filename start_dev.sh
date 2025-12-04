#!/bin/bash

# Start Backend
echo "Starting Backend..."
cd backend
# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
# Always install/upgrade dependencies to ensure we have the correct versions
pip install --upgrade -r requirements.txt

# Optional: Set MODEL_PATH if you have a local copy
# export MODEL_PATH="/home/dbee-tts-coqui/..." 

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend..."
if command -v npm &> /dev/null; then
    cd ../frontend
    npm install # Ensure frontend deps are installed
    npm run dev &
    FRONTEND_PID=$!
else
    echo "WARNING: 'npm' not found. Frontend will not start."
    echo "Please install Node.js and npm to run the frontend."
    FRONTEND_PID=""
fi

echo "App running. Backend: http://localhost:8000"
if [ -n "$FRONTEND_PID" ]; then
    echo "Frontend: http://localhost:5173"
fi
echo "Press CTRL+C to stop."

if [ -n "$FRONTEND_PID" ]; then
    wait $BACKEND_PID $FRONTEND_PID
else
    wait $BACKEND_PID
fi
