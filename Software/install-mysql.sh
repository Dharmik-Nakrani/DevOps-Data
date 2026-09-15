#!/usr/bin/env bash

set -e

echo "======================================"
echo "          Install MySQL Server"
echo "======================================"

echo
echo "Updating package lists..."
sudo apt update

echo
echo "Installing MySQL Server..."
sudo apt install -y mysql-server

echo
echo "Starting MySQL..."
sudo systemctl start mysql

echo
echo "Enabling MySQL to start automatically on boot..."
sudo systemctl enable mysql

echo
echo "Checking MySQL service..."

if systemctl is-active --quiet mysql; then
    echo
    echo "======================================"
    echo " MySQL installed successfully!"
    echo " MySQL service is RUNNING."
    echo "======================================"
else
    echo
    echo "✗ MySQL failed to start."
    sudo systemctl status mysql --no-pager
    exit 1
fi

echo
echo "MySQL version:"
mysql --version

echo
echo "Opening MySQL shell..."
echo "Type 'exit' to leave MySQL."
echo

sudo mysql
