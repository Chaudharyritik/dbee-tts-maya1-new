#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment...${NC}"

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit 1
fi

PROJECT_DIR=$(pwd)
echo -e "${GREEN}Project directory: $PROJECT_DIR${NC}"

# 1. Install System Dependencies
echo -e "${GREEN}Installing system dependencies...${NC}"
apt-get update
apt-get install -y nginx python3-venv python3-pip nodejs

# 2. Setup Backend
echo -e "${GREEN}Setting up Backend...${NC}"
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing backend requirements..."
pip install -r requirements.txt
deactivate

# 3. Setup Frontend
echo -e "${GREEN}Setting up Frontend...${NC}"
cd "$PROJECT_DIR/frontend"
echo "Installing frontend dependencies..."
npm install --legacy-peer-deps
echo "Building frontend..."
npm run build

# 4. Configure Systemd Service
echo -e "${GREEN}Configuring Systemd Service...${NC}"
cd "$PROJECT_DIR"
cp dbee-tts-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable dbee-tts-backend
systemctl restart dbee-tts-backend

# 5. Configure Nginx
echo -e "${GREEN}Configuring Nginx...${NC}"
cp nginx.conf /etc/nginx/sites-available/tts.dbee.live
ln -sf /etc/nginx/sites-available/tts.dbee.live /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default if exists
nginx -t
systemctl reload nginx

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}Backend status: systemctl status dbee-tts-backend${NC}"
echo -e "${GREEN}Nginx status: systemctl status nginx${NC}"
