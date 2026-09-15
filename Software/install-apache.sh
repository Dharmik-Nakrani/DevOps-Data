#!/usr/bin/env bash

set -e

echo "======================================"
echo "        Install Apache Web Server"
echo "======================================"

echo
echo "Updating package lists..."
sudo apt-get update

echo
echo "Installing Apache2..."
sudo apt-get install -y apache2

echo
echo "Starting Apache..."
sudo systemctl start apache2

echo
echo "Enabling Apache to start automatically on boot..."
sudo systemctl enable apache2

echo
echo "Checking Apache service status..."

if systemctl is-active --quiet apache2; then
    echo
    echo "======================================"
    echo " Apache installed successfully!"
    echo " Apache service is RUNNING."
    echo "======================================"
else
    echo
    echo "✗ Apache service failed to start."
    sudo systemctl status apache2 --no-pager
    exit 1
fi
