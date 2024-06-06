#!/bin/bash

# Function to prompt user for input with a default value
prompt_input() {
    local prompt_message="$1"
    local default_value="$2"
    local input_variable_name="$3"
    read -p "$prompt_message [$default_value]: " user_input
    if [ -z "$user_input" ]; then
        user_input="$default_value"
    fi
    eval "$input_variable_name='$user_input'"
}

# Check for Python and pip
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Please install pip."
    exit 1
fi

# Check for Node.js and npm
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install npm."
    exit 1
fi

# Setting up Python environment
echo "Setting up Python environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Installing backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Create backend .env file
echo "Creating backend .env file..."
read -p "Enter your OpenAI API Key (or leave blank to fill later): " api_key
prompt_input "Enter your MongoDB URL (or leave blank to use default)" "mongodb://localhost:27017/" mongo_url
echo "OPENAI_API_KEY=$api_key" > backend/.env
echo "MONGO_DB_URL=$mongo_url" >> backend/.env

# Installing frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

# Create frontend .env file
echo "Creating frontend .env file..."
prompt_input "Enter backend protocol" "http" backend_protocol
prompt_input "Enter backend address" "127.0.0.1" backend_address
prompt_input "Enter backend port" "5000" backend_port
echo "VITE_API_URL=$backend_protocol://$backend_address:$backend_port" > .env

# Building frontend
echo "Building frontend..."
npm run build

echo "Setup completed successfully!"