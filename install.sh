#!/bin/bash

echo "========================================"
echo " Goal Tracker App - Setup Script"
echo "========================================"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install Python
echo "[Step 1/4] Checking Python installation..."
if command_exists python3; then
    echo "✓ Python is already installed!"
    python3 --version
else
    echo "Python not found. Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    echo "✓ Python installed successfully!"
    python3 --version
fi

echo ""

# Check and install Node.js
echo "[Step 2/4] Checking Node.js installation..."
if command_exists node; then
    echo "✓ Node.js is already installed!"
    node --version
else
    echo "Node.js not found. Installing Node.js..."
    # Install Node.js 20.x
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✓ Node.js installed successfully!"
    node --version
fi

echo ""

# Install Backend Dependencies
echo "[Step 3/4] Installing Backend dependencies..."
cd backend || { echo "Error: backend directory not found"; exit 1; }

if command_exists pip3; then
    pip3 install -r requirements.txt
else
    python3 -m pip install -r requirements.txt
fi

if [ $? -eq 0 ]; then
    echo "✓ Backend dependencies installed successfully!"
else
    echo "✗ Failed to install backend dependencies"
    exit 1
fi

cd ..
echo ""

# Install Frontend Dependencies
echo "[Step 4/4] Installing Frontend dependencies..."
cd frontend || { echo "Error: frontend directory not found"; exit 1; }

if [ -d "node_modules" ]; then
    echo "✓ Frontend dependencies already installed."
else
    npm install
    if [ $? -eq 0 ]; then
        echo "✓ Frontend dependencies installed successfully!"
    else
        echo "✗ Failed to install frontend dependencies"
        exit 1
    fi
fi

cd ..

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1: cd backend && python3 main.py"
echo "  Terminal 2: cd frontend && npm start"
echo ""
echo "Then open: http://localhost:3000"
echo "========================================"
