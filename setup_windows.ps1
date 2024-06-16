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

# Install Python dependencies
Write-Host "Installing backend dependencies using pip..."
pip install --no-cache-dir -U -r .\PyPackages\requirements.txt

# Prompt user for backend configuration with default values
function Prompt-With-Default {
    param (
        [string]$Message,
        [string]$Default
    )
    $input = Read-Host "$Message [$Default]"
    if ([string]::IsNullOrWhiteSpace($input)) {
        return $Default
    }
    return $input
}

# Prompt user for backend configuration
$backendProtocol = Prompt-With-Default "Enter backend protocol (http/s)" "http"
$backendAddress = Prompt-With-Default "Enter backend address" "127.0.0.1"
$backendPort = Prompt-With-Default "Enter backend port" "5000"

# Prompt user for OpenAI API key
$apiKey = Read-Host "Enter your OpenAI API Key (or leave blank to fill later)"

# Prompt user for MongoDB URL
$mongoUrl = Prompt-With-Default "Enter your MongoDB URL" "mongodb://localhost:27017/"

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
Write-Host "Success... press any key to exit window"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
