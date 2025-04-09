#!/bin/bash

# Update and upgrade system packages
sudo apt update && sudo apt upgrade -y

# Remove any existing Go installation
sudo rm -rf /usr/local/go

# Download Go 1.22.0
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz

# Extract to /usr/local
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz

# Add Go to PATH
if ! grep -q "/usr/local/go/bin" "$HOME/.bashrc"; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> "$HOME/.bashrc"
fi

# Setup GOPATH
mkdir -p "$HOME/go/{bin,pkg,src}"

if ! grep -q "GOPATH" "$HOME/.bashrc"; then
    echo 'export GOPATH=$HOME/go' >> "$HOME/.bashrc"
    echo 'export PATH=$PATH:$GOPATH/bin' >> "$HOME/.bashrc"
fi

# Source the updated bashrc
source "$HOME/.bashrc"

# Display Go version to verify installation
go version
