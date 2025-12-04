#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (use sudo)"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# Suppress needrestart prompts if installed
if [ -f /etc/needrestart/needrestart.conf ]; then
    sed -i "s/#\$nrconf{restart} = 'i';/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
fi

echo "Updating package list..."
apt-get update

echo "Installing FFmpeg and eSpeak..."
apt-get install -y ffmpeg espeak-ng

echo "Ensuring Node.js 20 is installed..."

# Remove conflicting packages from old Node.js installation
echo "Removing conflicting packages..."
apt-get remove -y libnode-dev libnode72 nodejs-doc nodejs npm
apt-get autoremove -y
apt-get --fix-broken install -y

# Always run setup to ensure correct version (Node 20+)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
echo "Node.js 20 installed/updated successfully."

echo "System dependencies installed."
