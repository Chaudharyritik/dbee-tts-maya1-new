#!/bin/bash

# Start Backend
echo "Starting Backend..."
cd backend
# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Aggressively fix transformers version
echo "Ensuring clean transformers installation..."
pip uninstall -y transformers
pip install --upgrade -r requirements.txt

# Verify installation
echo "Verifying transformers version..."
python3 -c "import transformers; print(f'Transformers version: {transformers.__version__}')"

# Optional: Set MODEL_PATH if you have a local copy
# export MODEL_PATH="/home/dbee-tts-coqui/..." 

uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend..."

# Try to load user environment
source ~/.bashrc 2>/dev/null
source ~/.profile 2>/dev/null
source ~/.nvm/nvm.sh 2>/dev/null

echo "Debug: PATH=$PATH"
echo "Debug: npm location=$(which npm)"

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
