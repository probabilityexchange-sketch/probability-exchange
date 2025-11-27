#!/bin/bash

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Kill any existing server on port 3000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "Killing existing server on port 3000..."
  kill $(lsof -Pi :3000 -sTCP:LISTEN -t) 2>/dev/null || true
  sleep 1
fi

# Start the server with logging
echo "Starting waitlist landing page server..."
echo "Directory: $(pwd)"
echo "URL: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo "---"

node server.js