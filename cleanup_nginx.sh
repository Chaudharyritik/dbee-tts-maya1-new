#!/bin/bash
set -e

echo "Cleaning up duplicate Nginx configurations..."

# Remove conflicting symlinks
rm -f /etc/nginx/sites-enabled/dbee-tts
rm -f /etc/nginx/sites-enabled/tts-dbee-live

# Ensure our correct config is linked
ln -sf /etc/nginx/sites-available/tts.dbee.live /etc/nginx/sites-enabled/

# Test and reload
nginx -t
systemctl reload nginx

echo "Cleanup complete! Nginx reloaded."
echo "Your External IP is:"
curl -s ifconfig.me
echo ""
