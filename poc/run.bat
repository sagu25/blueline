@echo off
echo.
echo  ================================
echo   Project BlueLine POC - Starting
echo  ================================
echo.

REM Install dependencies if not already installed
pip install -r requirements.txt --quiet

REM Copy .env.example to .env if .env doesn't exist
if not exist .env (
    copy .env.example .env
    echo  Created .env file. Please add your ANTHROPIC_API_KEY to .env
    echo  Then run this script again.
    pause
    exit /b
)

REM Launch the Streamlit app
echo  Launching BlueLine POC at http://localhost:8501
echo  Press Ctrl+C to stop.
echo.
streamlit run app.py --server.port 8501
