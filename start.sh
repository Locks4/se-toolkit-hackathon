#!/bin/bash

echo "========================================"
echo " Goal Tracker - Starting..."
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get VM IP address
VM_IP=$(hostname -I | awk '{print $1}')

echo -e "${YELLOW}Starting Backend Server...${NC}"
cd backend
nohup python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${YELLOW}Starting Frontend Server...${NC}"
cd frontend/build
nohup python3 -m http.server 80 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo ""
echo "Waiting for servers to start..."
sleep 3

# Check if servers are running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Backend running (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start!${NC}"
    echo "Check logs: cat /tmp/backend.log"
    exit 1
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend running (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start!${NC}"
    echo "Check logs: cat /tmp/frontend.log"
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN}✓ App is Running!${NC}"
echo "========================================"
echo ""
echo "Access the app at:"
echo "  http://$VM_IP:80"
echo ""
echo "Backend API:"
echo "  http://$VM_IP:8000"
echo "  http://$VM_IP:8000/docs (API Docs)"
echo ""
echo "To stop the app, run:"
echo "  ./stop.sh"
echo ""
echo "========================================"

# Save PIDs for stop script
echo "$BACKEND_PID" > /tmp/goal_tracker_backend.pid
echo "$FRONTEND_PID" > /tmp/goal_tracker_frontend.pid
