#!/bin/bash

echo "========================================"
echo " Goal Tracker - Starting..."
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get VM IP address
VM_IP=$(hostname -I | awk '{print $1}')
echo -e "${YELLOW}🌐 Detected VM IP: $VM_IP${NC}"
echo ""

# 1. Fix CORS to allow remote access
echo "🔧 Configuring Backend CORS..."
sed -i 's/allow_origins=\[.*\]/allow_origins=["*"]/' backend/main.py

# 2. Fix Frontend API URL (replace localhost with VM IP)
echo "🔧 Configuring Frontend API URL..."
find frontend/build -name "*.js" -exec sed -i "s|http://localhost:8000|http://$VM_IP:8000|g" {} \;

# 3. Open Firewall
echo "🔓 Opening Firewall..."
sudo ufw allow 3000/tcp > /dev/null 2>&1
sudo ufw allow 8000/tcp > /dev/null 2>&1

# 4. Kill old instances if running
pkill -f "python3 main.py" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null

# 5. Start Servers in background
echo "🚀 Starting Servers..."
cd backend
nohup python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ../frontend/build
nohup python3 -m http.server 3000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../../..

echo ""
echo "Waiting for servers to initialize..."
sleep 3

# Check if servers are running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start!${NC}"
    echo "Check logs: tail -f /tmp/backend.log"
    exit 1
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start!${NC}"
    echo "Check logs: tail -f /tmp/frontend.log"
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ App is Running!${NC}"
echo "========================================"
echo ""
echo "🌐 Access the app at:"
echo -e "   \033[0;32mhttp://$VM_IP:3000\033[0m"
echo ""
echo "📚 Backend API & Docs:"
echo -e "   \033[0;34mhttp://$VM_IP:8000/docs\033[0m"
echo ""
echo "To stop the app, run:"
echo "   ./stop.sh"
echo ""
echo "========================================"
