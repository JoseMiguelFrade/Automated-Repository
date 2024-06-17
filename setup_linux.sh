#!/bin/bash

# Function to output a message
output() {
    echo "$1"
}

# Function to run a command and capture its output in real-time
run_command() {
    command="$1"
    working_dir="$2"
    if [ -n "$working_dir" ]; then
        pushd "$working_dir" > /dev/null
    fi
    output "Running: $command"
    $command
    if [ $? -ne 0 ]; then
        output "Error running command: $command"
    fi
    if [ -n "$working_dir" ]; then
        popd > /dev/null
    fi
}

# Function to check for command availability
check_command() {
    command="$1"
    friendly_name="$2"
    if ! command -v $command &> /dev/null; then
        output "$friendly_name is not installed. Please install $friendly_name."
        exit 1
    fi
}

# Check for Python
output "Checking for Python..."
check_command "python3" "Python"

# Check for pip
output "Checking for pip..."
check_command "pip3" "pip"

# Check for Node.js
output "Checking for Node.js..."
check_command "node" "Node.js"

# Check for npm
output "Checking for npm..."
check_command "npm" "npm"

# Ensure python3-venv is installed
output "Ensuring python3-venv is installed..."
sudo apt install -y python3-venv

# Setting up Python environment
output "Setting up Python environment..."
run_command "python3 -m venv venv"

# Activate virtual environment
output "Activating virtual environment..."
source venv/bin/activate
output "Virtual environment activated."

# Install Python dependencies
output "Installing backend dependencies using pip..."
run_command "pip install --no-cache-dir -U -r PyPackages/requirements.txt"

# Prompt user for backend configuration
read -p "Enter backend protocol (http/s) [http]: " backendProtocol
backendProtocol=${backendProtocol:-http}

read -p "Enter backend address [127.0.0.1]: " backendAddress
backendAddress=${backendAddress:-127.0.0.1}

read -p "Enter backend port [5000]: " backendPort
backendPort=${backendPort:-5000}

# Prompt user for OpenAI API key
read -p "Enter your OpenAI API Key: " apiKey

# Prompt user for MongoDB URL
read -p "Enter your MongoDB URL [mongodb://localhost:27017/]: " mongoUrl
mongoUrl=${mongoUrl:-mongodb://localhost:27017/}

# Prompt user for MongoDB Database Name
read -p "Enter your MongoDB Database Name: " mongoDbName

# Prompt user for MongoDB Collection Name
read -p "Enter your MongoDB Collection Name: " mongoCollectionName

# Create backend .env file
output "Creating backend .env file..."
cat <<EOL > backend/.env
OPENAI_API_KEY=$apiKey
MONGO_DB_URL=$mongoUrl
MongoDB=$mongoDbName
MongoCollection=$mongoCollectionName
EOL
output "Backend .env file created."

# Installing frontend dependencies
output "Installing frontend dependencies..."
run_command "npm install" "frontend"

# Create frontend .env file
output "Creating frontend .env file..."
viteApiUrl="${backendProtocol}://${backendAddress}:${backendPort}"
cat <<EOL > frontend/.env
VITE_API_URL=$viteApiUrl
EOL
output "Frontend .env file created."

# Building frontend
output "Building frontend..."
run_command "npm run build" "frontend"

output "Setup completed successfully! Press any key to exit window."
read -n 1 -s
