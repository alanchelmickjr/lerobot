@echo off
setlocal enabledelayedexpansion

REM BOM Calculator Startup Script for Windows
REM Starts both backend and frontend services with automatic port detection

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "PID_FILE=%SCRIPT_DIR%.bom_calculator.pid"

REM Default ports
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set MODE=%1
if "%MODE%"=="" set MODE=development

REM Colors for output (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %BLUE%=======================================
echo      BOM Calculator Startup Script
echo =======================================%NC%
echo.

REM Parse command
if "%1"=="stop" goto :stop_services
if "%1"=="restart" goto :restart_services
if "%1"=="status" goto :show_status
if "%1"=="help" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="production" set MODE=production
if "%1"=="development" set MODE=development

echo %YELLOW%Mode: %MODE%%NC%
echo.

REM Check dependencies
call :check_dependencies
if %ERRORLEVEL% neq 0 exit /b 1

REM Find available ports
call :find_available_port %BACKEND_PORT% BACKEND_PORT
call :find_available_port %FRONTEND_PORT% FRONTEND_PORT

echo %GREEN%Using backend port: %BACKEND_PORT%%NC%
echo %GREEN%Using frontend port: %FRONTEND_PORT%%NC%
echo.

REM Setup environments
call :setup_python_env
if %ERRORLEVEL% neq 0 exit /b 1
echo.

call :setup_node_env
if %ERRORLEVEL% neq 0 exit /b 1
echo.

REM Initialize database
call :init_database
if %ERRORLEVEL% neq 0 exit /b 1
echo.

REM Start services
call :start_backend %BACKEND_PORT%
if %ERRORLEVEL% neq 0 exit /b 1
echo.

call :start_frontend %FRONTEND_PORT% %BACKEND_PORT%
if %ERRORLEVEL% neq 0 exit /b 1
echo.

echo %GREEN%=======================================
echo     BOM Calculator is running!
echo =======================================%NC%
echo %BLUE%Frontend: http://localhost:%FRONTEND_PORT%%NC%
echo %BLUE%Backend API: http://localhost:%BACKEND_PORT%%NC%
echo %BLUE%API Docs: http://localhost:%BACKEND_PORT%/api/docs%NC%
echo %GREEN%=======================================%NC%
echo %YELLOW%Press Ctrl+C to stop all services%NC%
echo.
echo %YELLOW%Logs are available in: %LOG_DIR%%NC%
echo.

REM Keep window open
pause
call :stop_services
exit /b 0

REM ===== Functions =====

:check_dependencies
echo %BLUE%Checking dependencies...%NC%

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Python 3 is not installed or not in PATH!%NC%
    echo Please install Python from https://www.python.org/
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Node.js is not installed or not in PATH!%NC%
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM Check npm
npm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%npm is not installed!%NC%
    exit /b 1
)

echo %GREEN%All dependencies are installed%NC%
exit /b 0

:find_available_port
set start_port=%1
set port=%start_port%

:port_loop
netstat -an | findstr :%port% >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %YELLOW%Port %port% is in use, trying next port...%NC%
    set /a port+=1
    if !port! gtr !start_port!+100 (
        echo %RED%Could not find available port in range %start_port%-%port%%NC%
        exit /b 1
    )
    goto :port_loop
)

set %2=%port%
exit /b 0

:setup_python_env
echo %BLUE%Setting up Python environment...%NC%

cd /d "%BACKEND_DIR%"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo %YELLOW%Creating Python virtual environment...%NC%
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo %RED%Failed to create virtual environment!%NC%
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo %YELLOW%Installing Python dependencies...%NC%
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Failed to install Python dependencies!%NC%
    exit /b 1
)

echo %GREEN%Python environment ready%NC%
exit /b 0

:setup_node_env
echo %BLUE%Setting up Node environment...%NC%

cd /d "%FRONTEND_DIR%"

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo %YELLOW%Installing Node dependencies...%NC%
    call npm install
    if %ERRORLEVEL% neq 0 (
        echo %RED%Failed to install Node dependencies!%NC%
        exit /b 1
    )
)

echo %GREEN%Node environment ready%NC%
exit /b 0

:init_database
echo %BLUE%Initializing database...%NC%

cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat

REM Check if database exists
if not exist "bom_calculator.db" (
    echo %YELLOW%Creating database and loading initial data...%NC%
    python -m init_db
    if %ERRORLEVEL% neq 0 (
        echo %RED%Failed to initialize database!%NC%
        exit /b 1
    )
    echo %GREEN%Database initialized%NC%
) else (
    echo %GREEN%Database already exists%NC%
)

exit /b 0

:start_backend
set port=%1

echo %BLUE%Starting backend on port %port%...%NC%

cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Set environment variables
set DATABASE_URL=sqlite+aiosqlite:///./bom_calculator.db
set CORS_ORIGINS=["http://localhost:%FRONTEND_PORT%"]

if "%MODE%"=="production" (
    REM Production mode
    start /b uvicorn main:app --host 0.0.0.0 --port %port% --workers 4 > "%LOG_DIR%\backend.log" 2>&1
) else (
    REM Development mode with auto-reload
    start /b uvicorn main:app --host 0.0.0.0 --port %port% --reload > "%LOG_DIR%\backend.log" 2>&1
)

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:%port%/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %RED%Failed to start backend!%NC%
    type "%LOG_DIR%\backend.log"
    exit /b 1
)

echo %GREEN%Backend started successfully%NC%
echo %BLUE%Backend API: http://localhost:%port%%NC%
echo %BLUE%API Docs: http://localhost:%port%/api/docs%NC%

exit /b 0

:start_frontend
set port=%1
set backend_port=%2

echo %BLUE%Starting frontend on port %port%...%NC%

cd /d "%FRONTEND_DIR%"

REM Set environment variables
set VITE_API_URL=http://localhost:%backend_port%
set PORT=%port%

if "%MODE%"=="production" (
    REM Build for production
    echo %YELLOW%Building frontend for production...%NC%
    call npm run build
    if %ERRORLEVEL% neq 0 (
        echo %RED%Failed to build frontend!%NC%
        exit /b 1
    )
    
    REM Serve using a simple HTTP server
    start /b npx serve -s dist -l %port% > "%LOG_DIR%\frontend.log" 2>&1
) else (
    REM Development mode with hot reload
    start /b npm run dev -- --port %port% --host > "%LOG_DIR%\frontend.log" 2>&1
)

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo %GREEN%Frontend started successfully%NC%
echo %BLUE%Frontend URL: http://localhost:%port%%NC%

exit /b 0

:stop_services
echo %YELLOW%Stopping BOM Calculator services...%NC%

REM Kill Python processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1

REM Kill Node processes
taskkill /f /im node.exe >nul 2>&1

REM Clean up PID file
if exist "%PID_FILE%" del "%PID_FILE%"

echo %GREEN%All services stopped%NC%
exit /b 0

:restart_services
call :stop_services
timeout /t 2 /nobreak >nul
set MODE=%2
if "%MODE%"=="" set MODE=development
goto :main_start

:show_status
echo %BLUE%BOM Calculator Service Status:%NC%

REM Check backend
curl -s http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %GREEN%  Backend is running%NC%
) else (
    echo %YELLOW%  Backend is not running%NC%
)

REM Check frontend
curl -s http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo %GREEN%  Frontend is running%NC%
) else (
    echo %YELLOW%  Frontend is not running%NC%
)

exit /b 0

:show_help
echo BOM Calculator Startup Script for Windows
echo.
echo Usage: %~nx0 [command] [mode]
echo.
echo Commands:
echo   start [mode]  - Start all services (default: development)
echo   stop          - Stop all services
echo   restart       - Restart all services
echo   status        - Show service status
echo   help          - Show this help message
echo.
echo Modes:
echo   development   - Run with hot reload and debug features (default)
echo   production    - Run optimized for production
echo.
echo Examples:
echo   %~nx0              # Start in development mode
echo   %~nx0 start        # Start in development mode
echo   %~nx0 production   # Start in production mode
echo   %~nx0 stop         # Stop all services
echo.
exit /b 0

:main_start
REM Main execution continues from top