# Function to prompt user for input with a default value
function Prompt-Input {
    param (
        [string]$DefaultValue,
        [string]$Message,
        [string]$GlobalVarName
    )

    $userInput = Read-Host "$Message [$DefaultValue]"
    if ([string]::IsNullOrEmpty($userInput)) {
        $userInput = $DefaultValue
    }
    Set-Variable -Name $GlobalVarName -Value $userInput -Scope Global
}

# Check for Python and pip
Write-Output "Checking for Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Output "Python is not installed. Please install Python."
    exit 1
}

Write-Output "Checking for pip..."
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Output "pip is not installed. Please install pip."
    exit 1
}

# Check for Node.js and npm
Write-Output "Checking for Node.js..."
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Output "Node.js is not installed. Please install Node.js."
    exit 1
}

Write-Output "Checking for npm..."
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Output "npm is not installed. Please install npm."
    exit 1
}

# Setting up Python environment
Write-Output "Setting up Python environment..."
python -m venv venv

# Activate virtual environment (Windows)
Write-Output "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Installing backend dependencies
Write-Output "Installing backend dependencies..."
pip install -r .\PyPackages\requirments.txt

# Create backend .env file
Write-Output "Creating backend .env file..."
$api_key = Read-Host "Enter your OpenAI API Key (or leave blank to fill later)"
$mongo_url = Read-Host "Enter your MongoDB URL (or leave blank to use default)"
if ([string]::IsNullOrEmpty($mongo_url)) {
    $mongo_url = "mongodb://localhost:27017/"
}
Set-Content -Path "backend\.env" -Value "OPENAI_API_KEY=$api_key`nMONGO_DB_URL=$mongo_url"

# Installing frontend dependencies
Write-Output "Installing frontend dependencies..."
cd frontend
npm install

# Create frontend .env file
Write-Output "Creating frontend .env file..."
Prompt-Input -DefaultValue "http" -Message "Enter backend protocol (http/s)" -GlobalVarName "backend_protocol"
Prompt-Input -DefaultValue "127.0.0.1" -Message "Enter backend address" -GlobalVarName "backend_address"
Prompt-Input -DefaultValue "5000" -Message "Enter backend port" -GlobalVarName "backend_port"
Set-Content -Path ".env" -Value "VITE_API_URL=$backend_protocol`://$backend_address`:$backend_port"

# Building frontend
Write-Output "Building frontend..."
npm run build

Write-Output "Setup completed successfully!"
pause
