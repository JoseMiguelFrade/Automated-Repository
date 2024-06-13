# Check for Python
Write-Host "Checking for Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python."
    exit 1
}

# Check for pip
Write-Host "Checking for pip..."
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "pip is not installed. Please install pip."
    exit 1
}

# Check for Node.js
Write-Host "Checking for Node.js..."
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js is not installed. Please install Node.js."
    exit 1
}

# Check for npm
Write-Host "Checking for npm..."
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm is not installed. Please install npm."
    exit 1
}

# Setting up Python environment
Write-Host "Setting up Python environment..."
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Installing backend dependencies
Write-Host "Installing backend dependencies..."
foreach ($package in $packages) {
    Write-Host "Installing $package..."
    pip install --no-cache-dir $package
}

# Prompt user for backend configuration
$backendProtocol = Read-Host "Enter backend protocol (http/s)" -DefaultValue "http"
$backendAddress = Read-Host "Enter backend address" -DefaultValue "127.0.0.1"
$backendPort = Read-Host "Enter backend port" -DefaultValue "5000"

# Prompt user for OpenAI API key
$apiKey = Read-Host "Enter your OpenAI API Key (or leave blank to fill later)"

# Prompt user for MongoDB URL
$mongoUrl = Read-Host "Enter your MongoDB URL (or leave blank to use default)" -DefaultValue "mongodb://localhost:27017/"

# Create backend .env file
Write-Host "Creating backend .env file..."
Set-Content -Path ".\backend\.env" -Value "OPENAI_API_KEY=$apiKey`nMONGO_DB_URL=$mongoUrl"

# Installing frontend dependencies
Write-Host "Installing frontend dependencies..."
cd frontend
npm install

# Create frontend .env file
Write-Host "Creating frontend .env file..."
$viteApiUrl = "${backendProtocol}://${backendAddress}:${backendPort}"
Set-Content -Path ".\.env" -Value "VITE_API_URL=$viteApiUrl"

# Building frontend
Write-Host "Building frontend..."
npm run build

Write-Host "Setup completed successfully!"
