# Check if Python is installed
try {
    python --version
} catch {
    Write-Host "Python is not installed. Please install Python."
    exit 1
}

# Check if pip is installed
try {
    pip --version
} catch {
    Write-Host "pip is not installed. Please install pip."
    exit 1
}

# Check if Node.js is installed
try {
    node --version
} catch {
    Write-Host "Node.js is not installed. Please install Node.js."
    exit 1
}

# Check if npm is installed
try {
    npm --version
} catch {
    Write-Host "npm is not installed. Please install npm."
    exit 1
}

# Setting up Python virtual environment
Write-Host "Setting up Python virtual environment..."
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Installing backend dependencies
Write-Host "Installing backend dependencies..."
pip install -r .\PyPackages\requirements.txt

# Prompt for backend environment variables
$apiKey = Read-Host "Enter your OpenAI API Key (or leave blank to fill later)"
$mongoUrl = Read-Host "Enter your MongoDB URL (or leave blank to use default)"
if ($mongoUrl -eq "") {
    $mongoUrl = "mongodb://localhost:27017/"
}

# Create backend .env file
Write-Host "Creating backend .env file..."
@"
OPENAI_API_KEY=$apiKey
MONGO_DB_URL=$mongoUrl
"@ | Out-File -FilePath backend\.env -Encoding utf8

# Installing frontend dependencies
Write-Host "Installing frontend dependencies..."
cd frontend
npm install

# Prompt for frontend environment variables
$backendProtocol = Read-Host "Enter backend protocol (http/s)"
$backendAddress = Read-Host "Enter backend address"
$backendPort = Read-Host "Enter backend port"
if ($backendProtocol -eq "") {
    $backendProtocol = "http"
}
if ($backendAddress -eq "") {
    $backendAddress = "127.0.0.1"
}
if ($backendPort -eq "") {
    $backendPort = "5000"
}

# Create frontend .env file
Write-Host "Creating frontend .env file..."
@"
VITE_API_URL=$backendProtocol://$backendAddress:$backendPort
"@ | Out-File -FilePath .env -Encoding utf8

# Building frontend
Write-Host "Building frontend..."
npm run build

Write-Host "Setup completed successfully!"
