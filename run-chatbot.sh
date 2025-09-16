#!/bin/bash

# Script to run the JPetStore chatbot integration

echo "Starting JPetStore Chatbot Integration..."

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $MCP_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start the backend API (if not already running)
echo "Starting backend API..."
cd jpetstore-api
if ! lsof -i:8081 > /dev/null 2>&1; then
    mvn spring-boot:run &
    BACKEND_PID=$!
    echo "Backend API starting on port 8081..."
    sleep 10  # Give backend time to start
else
    echo "Backend API already running on port 8081"
fi
cd ..

# Start the MCP HTTP wrapper
echo "Starting MCP server HTTP wrapper..."
cd mcp-servers/petstore-assistant
python http_wrapper.py &
MCP_PID=$!
echo "MCP server starting on port 3001..."
sleep 3  # Give MCP server time to start
cd ../..

# Start the frontend
echo "Starting frontend..."
cd jpetstore-frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend starting on port 3000..."
cd ..

echo ""
echo "All services started!"
echo "- Backend API: http://localhost:8081"
echo "- MCP Server: http://localhost:3001"
echo "- Frontend: http://localhost:3000"
echo ""
echo "The chatbot should be available in the bottom-right corner of the frontend."
echo "Press Ctrl+C to stop all services."

# Wait for user to stop
wait
