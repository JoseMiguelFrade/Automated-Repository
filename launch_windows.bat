@echo off
REM Activate the virtual environment

call venv\Scripts\activate

REM Start the backend server
echo Starting backend server...
start /B cmd /c "cd backend && flask run"

REM Start the frontend server
echo Starting frontend server...

cd frontend
npm run dev

REM Notify the user
