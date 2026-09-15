#!/usr/bin/env bash

set -e

KEYRING="/usr/share/keyrings/brave-browser-archive-keyring.gpg"
REPO_FILE="/etc/apt/sources.list.d/brave-browser-release.list"
REPO_URL="https://brave-browser-apt-release.s3.brave.com/"
KEY_URL="${REPO_URL}brave-browser-archive-keyring.gpg"

echo "======================================"
echo "       Install Brave Browser"
echo "======================================"

# Check if Brave is already installed
if command -v brave-browser >/dev/null 2>&1; then
    echo "✓ Brave Browser is already installed."
    brave-browser --version
    exit 0
fi

echo
echo "Installing required packages..."

sudo apt update
sudo apt install -y apt-transport-https curl

echo
echo "Installing Brave repository key..."

sudo curl -fsSLo "$KEYRING" "$KEY_URL"

echo
echo "Adding Brave repository..."

echo "deb [signed-by=$KEYRING arch=amd64] $REPO_URL stable main" | \
    sudo tee "$REPO_FILE" > /dev/null

echo
echo "Updating package lists..."

sudo apt update

echo
echo "Installing Brave Browser..."

sudo apt install -y brave-browser

echo
echo "======================================"
echo " Brave Browser installed successfully!"
echo "======================================"

brave-browser --version
