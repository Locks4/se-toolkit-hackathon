#!/bin/bash

echo "Stopping Goal Tracker..."

if [ -f /tmp/goal_tracker_backend.pid ]; then
    kill $(cat /tmp/goal_tracker_backend.pid) 2>/dev/null
    echo "✓ Backend stopped"
    rm /tmp/goal_tracker_backend.pid
fi

if [ -f /tmp/goal_tracker_frontend.pid ]; then
    kill $(cat /tmp/goal_tracker_frontend.pid) 2>/dev/null
    echo "✓ Frontend stopped"
    rm /tmp/goal_tracker_frontend.pid
fi

echo "Done!"
