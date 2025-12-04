#!/bin/bash

echo "Configuring UFW Firewall..."
if command -v ufw > /dev/null; then
    sudo ufw allow 5173/tcp
    sudo ufw allow 8000/tcp
    sudo ufw reload
    echo "✅ Allowed ports 5173 and 8000 on UFW."
    sudo ufw status
else
    echo "⚠️ UFW not found. Skipping OS firewall configuration."
fi

echo ""
echo "IMPORTANT: GCP / Cloud Firewall"
echo "If you are running on Google Cloud, AWS, or Azure, you MUST also open port 5173 in your cloud console."
echo "For GCP:"
echo "1. Go to VPC Network > Firewall."
echo "2. Create a rule named 'allow-maya1'."
echo "3. Targets: All instances in the network."
echo "4. Source IPv4 ranges: 0.0.0.0/0"
echo "5. Protocols and ports: tcp:5173, tcp:8000"
echo ""
echo "Alternatively, use localtunnel to expose the port without firewall changes:"
echo "npm install -g localtunnel"
echo "lt --port 5173"
