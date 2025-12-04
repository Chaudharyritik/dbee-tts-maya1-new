#!/bin/bash

# Start Backend
echo "Starting Backend..."
cd backend
# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
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
