#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Start the backend server
echo "Starting backend server..."
cd backend
nohup flask run &

# Start the frontend server
echo "Starting frontend server..."
cd ../frontend
npm run dev

# Notify the user
echo "Frontend server started. Visit http://localhost:3000 to view the application."