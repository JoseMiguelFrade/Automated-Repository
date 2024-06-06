@echo off

REM Function to prompt user for input with a default value
setlocal enabledelayedexpansion
set promptInputDefault=%1
set promptInputMessage=%2

:promptInput
set /p "userInput=%promptInputMessage% [%promptInputDefault%]: "
if "%userInput%"=="" (
    set userInput=%promptInputDefault%
)
endlocal & set "%~3=%userInput%"
goto :EOF

REM Check for Python and pip
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python.
    exit /b 1
)

pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Please install pip.
    exit /b 1
)

REM Check for Node.js and npm
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Node.js is not installed. Please install Node.js.
    exit /b 1
)

npm --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo npm is not installed. Please install npm.
    exit /b 1
)

REM Setting up Python environment
echo Setting up Python environment...
python -m venv venv

REM Activate virtual environment (Windows)
call venv\Scripts\activate

REM Installing backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

REM Create backend .env file
echo Creating backend .env file...
set /p "api_key=Enter your OpenAI API Key (or leave blank to fill later): "
set /p "mongo_url=Enter your MongoDB URL (or leave blank to use default): "
if "%mongo_url%"=="" (
    set mongo_url=mongodb://localhost:27017/
)
echo OPENAI_API_KEY=%api_key% > backend\.env
echo MONGO_DB_URL=%mongo_url% >> backend\.env

REM Installing frontend dependencies
echo Installing frontend dependencies...
cd frontend
npm install

REM Create frontend .env file
echo Creating frontend .env file...
call :promptInput http "Enter backend protocol (http/s)" "backend_protocol"
call :promptInput 127.0.0.1 "Enter backend address" "backend_address"
call :promptInput 5000 "Enter backend port" "backend_port"
echo VITE_API_URL=%backend_protocol%://%backend_address%:%backend_port% > .env

REM Building frontend
echo Building frontend...
npm run build

echo Setup completed successfully!
pause
