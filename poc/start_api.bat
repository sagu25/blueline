@echo off
cd /d %~dp0
echo.
echo  ██████╗ ██╗     ██╗   ██╗███████╗██╗     ██╗███╗   ██╗███████╗
echo  ██╔══██╗██║     ██║   ██║██╔════╝██║     ██║████╗  ██║██╔════╝
echo  ██████╔╝██║     ██║   ██║█████╗  ██║     ██║██╔██╗ ██║█████╗
echo  ██╔══██╗██║     ██║   ██║██╔══╝  ██║     ██║██║╚██╗██║██╔══╝
echo  ██████╔╝███████╗╚██████╔╝███████╗███████╗██║██║ ╚████║███████╗
echo  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
echo.
echo  Starting BlueLine API on http://localhost:8000
echo  React UI should run separately: cd frontend ^&^& npm run dev
echo.
uvicorn api:app --reload --port 8000
pause
