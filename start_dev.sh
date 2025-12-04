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
pip install -r requirements.txt

# Optional: Set MODEL_PATH if you have a local copy
# export MODEL_PATH="/home/dbee-tts-coqui/..." 

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "App running. Backend: http://localhost:8000, Frontend: http://localhost:5173"
echo "Press CTRL+C to stop."

wait $BACKEND_PID $FRONTEND_PID
