#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (use sudo)"
  exit 1
fi

echo "Updating package list..."
apt-get update

echo "Installing FFmpeg and eSpeak..."
apt-get install -y ffmpeg espeak-ng

echo "Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
    echo "Node.js installed successfully."
else
    echo "Node.js is already installed."
fi

echo "System dependencies installed."
