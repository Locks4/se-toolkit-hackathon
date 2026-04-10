#!/bin/bash

echo "========================================"
echo " Goal Tracker - VM Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if command_exists python3; then
    echo -e "${GREEN}✓ Python3 found:$(python3 --version)${NC}"
else
    echo "Installing Python3..."
    sudo apt update -qq
    sudo apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
    echo -e "${GREEN}✓ Python3 installed!${NC}"
fi

echo ""
echo -e "${YELLOW}[2/5] Checking Node.js...${NC}"
if command_exists node; then
    echo -e "${GREEN}✓ Node.js found:$(node --version)${NC}"
else
    echo "Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y nodejs > /dev/null 2>&1
    echo -e "${GREEN}✓ Node.js installed!${NC}"
fi

echo ""
echo -e "${YELLOW}[3/5] Installing Backend dependencies...${NC}"
cd backend
pip3 install -r requirements.txt --break-system-packages -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed!${NC}"
else
    echo -e "${RED}✗ Backend installation failed!${NC}"
    exit 1
fi
cd ..

echo ""
echo -e "${YELLOW}[4/5] Installing Frontend dependencies...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed!${NC}"
    else
        echo -e "${RED}✗ Frontend installation failed!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Frontend dependencies already installed!${NC}"
fi
cd ..

echo ""
echo -e "${YELLOW}[5/5] Building Frontend for production...${NC}"
cd frontend
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend built successfully!${NC}"
else
    echo -e "${RED}✗ Frontend build failed!${NC}"
    exit 1
fi
cd ..

echo ""
echo "========================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "========================================"
echo ""
echo "To start the app, run:"
echo ""
echo "  ./start.sh"
echo ""
echo "Then access the app at:"
echo "  http://YOUR_VM_IP:3000"
echo ""
echo "========================================"
