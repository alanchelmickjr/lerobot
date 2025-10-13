#!/bin/bash

# BOM Calculator Startup Script
# Starts both backend and frontend services with automatic port detection

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/.bom_calculator.pid"

# Default ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
MODE=${1:-development}  # development or production

# Function to print colored output
print_color() {
    echo -e "${2}${1}${NC}"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Function to find available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while ! check_port $port; do
        print_color "Port $port is in use, trying next port..." "$YELLOW"
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            print_color "Could not find available port in range $start_port-$port" "$RED"
            exit 1
        fi
    done
    
    echo $port
}

# Function to check dependencies
check_dependencies() {
    print_color "Checking dependencies..." "$BLUE"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_color "Python 3 is not installed!" "$RED"
        exit 1
    fi
    
    # Check Node
    if ! command -v node &> /dev/null; then
        print_color "Node.js is not installed!" "$RED"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_color "npm is not installed!" "$RED"
        exit 1
    fi
    
    print_color "All dependencies are installed ✓" "$GREEN"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_color "Setting up Python environment..." "$BLUE"
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_color "Creating Python virtual environment..." "$YELLOW"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/upgrade pip
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install dependencies
    print_color "Installing Python dependencies..." "$YELLOW"
    pip install -r requirements.txt > /dev/null 2>&1
    
    print_color "Python environment ready ✓" "$GREEN"
}

# Function to setup Node environment
setup_node_env() {
    print_color "Setting up Node environment..." "$BLUE"
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_color "Installing Node dependencies..." "$YELLOW"
        npm install
    fi
    
    print_color "Node environment ready ✓" "$GREEN"
}

# Function to initialize database
init_database() {
    print_color "Initializing database..." "$BLUE"
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Check if database exists
    if [ ! -f "bom_calculator.db" ]; then
        print_color "Creating database and loading initial data..." "$YELLOW"
        python -m init_db
        print_color "Database initialized ✓" "$GREEN"
    else
        print_color "Database already exists ✓" "$GREEN"
    fi
}

# Function to start backend
start_backend() {
    local port=$1
    
    print_color "Starting backend on port $port..." "$BLUE"
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOG_DIR"
    
    # Set environment variables
    export DATABASE_URL="sqlite+aiosqlite:///./bom_calculator.db"
    export CORS_ORIGINS="[\"http://localhost:$FRONTEND_PORT\"]"
    
    if [ "$MODE" == "production" ]; then
        # Production mode
        nohup uvicorn main:app \
            --host 0.0.0.0 \
            --port $port \
            --workers 4 \
            > "$LOG_DIR/backend.log" 2>&1 &
    else
        # Development mode with auto-reload
        nohup uvicorn main:app \
            --host 0.0.0.0 \
            --port $port \
            --reload \
            > "$LOG_DIR/backend.log" 2>&1 &
    fi
    
    local backend_pid=$!
    echo $backend_pid >> "$PID_FILE"
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if kill -0 $backend_pid 2>/dev/null; then
        print_color "Backend started successfully ✓" "$GREEN"
        print_color "Backend API: http://localhost:$port" "$BLUE"
        print_color "API Docs: http://localhost:$port/api/docs" "$BLUE"
    else
        print_color "Failed to start backend!" "$RED"
        tail -n 20 "$LOG_DIR/backend.log"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    local port=$1
    local backend_port=$2
    
    print_color "Starting frontend on port $port..." "$BLUE"
    
    cd "$FRONTEND_DIR"
    
    # Set environment variables
    export VITE_API_URL="http://localhost:$backend_port"
    export PORT=$port
    
    if [ "$MODE" == "production" ]; then
        # Build for production
        print_color "Building frontend for production..." "$YELLOW"
        npm run build
        
        # Serve using a simple HTTP server
        npx serve -s dist -l $port > "$LOG_DIR/frontend.log" 2>&1 &
    else
        # Development mode with hot reload
        npm run dev -- --port $port --host > "$LOG_DIR/frontend.log" 2>&1 &
    fi
    
    local frontend_pid=$!
    echo $frontend_pid >> "$PID_FILE"
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend is running
    if kill -0 $frontend_pid 2>/dev/null; then
        print_color "Frontend started successfully ✓" "$GREEN"
        print_color "Frontend URL: http://localhost:$port" "$BLUE"
    else
        print_color "Failed to start frontend!" "$RED"
        tail -n 20 "$LOG_DIR/frontend.log"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_color "Stopping BOM Calculator services..." "$YELLOW"
    
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                kill $pid 2>/dev/null || true
                print_color "Stopped process $pid" "$GREEN"
            fi
        done < "$PID_FILE"
        rm "$PID_FILE"
    fi
    
    # Also kill any remaining uvicorn/node processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "serve -s dist" 2>/dev/null || true
    
    print_color "All services stopped ✓" "$GREEN"
}

# Function to show status
show_status() {
    print_color "BOM Calculator Service Status:" "$BLUE"
    
    if [ -f "$PID_FILE" ]; then
        local running=0
        while read pid; do
            if kill -0 $pid 2>/dev/null; then
                local cmd=$(ps -p $pid -o comm=)
                print_color "  Process $pid ($cmd) is running ✓" "$GREEN"
                running=1
            fi
        done < "$PID_FILE"
        
        if [ $running -eq 0 ]; then
            print_color "  No services are running" "$YELLOW"
        fi
    else
        print_color "  No services are running" "$YELLOW"
    fi
}

# Function to show help
show_help() {
    echo "BOM Calculator Startup Script"
    echo ""
    echo "Usage: $0 [command] [mode]"
    echo ""
    echo "Commands:"
    echo "  start [mode]  - Start all services (default: development)"
    echo "  stop         - Stop all services"
    echo "  restart      - Restart all services"
    echo "  status       - Show service status"
    echo "  help         - Show this help message"
    echo ""
    echo "Modes:"
    echo "  development  - Run with hot reload and debug features (default)"
    echo "  production   - Run optimized for production"
    echo ""
    echo "Examples:"
    echo "  $0              # Start in development mode"
    echo "  $0 start        # Start in development mode"
    echo "  $0 production   # Start in production mode"
    echo "  $0 stop         # Stop all services"
}

# Main execution
main() {
    print_color "🤖 BOM Calculator Startup Script" "$BLUE"
    print_color "================================" "$BLUE"
    
    # Parse command
    case "${1:-start}" in
        start)
            MODE=${2:-development}
            ;;
        stop)
            stop_services
            exit 0
            ;;
        restart)
            MODE=${2:-development}
            stop_services
            sleep 2
            ;;
        status)
            show_status
            exit 0
            ;;
        help|--help|-h)
            show_help
            exit 0
            ;;
        development|production)
            MODE=$1
            ;;
        *)
            print_color "Unknown command: $1" "$RED"
            show_help
            exit 1
            ;;
    esac
    
    print_color "Mode: $MODE" "$YELLOW"
    echo ""
    
    # Check dependencies
    check_dependencies
    echo ""
    
    # Find available ports
    BACKEND_PORT=$(find_available_port $BACKEND_PORT)
    FRONTEND_PORT=$(find_available_port $FRONTEND_PORT)
    
    print_color "Using backend port: $BACKEND_PORT" "$GREEN"
    print_color "Using frontend port: $FRONTEND_PORT" "$GREEN"
    echo ""
    
    # Setup environments
    setup_python_env
    echo ""
    setup_node_env
    echo ""
    
    # Initialize database
    init_database
    echo ""
    
    # Start services
    start_backend $BACKEND_PORT
    echo ""
    start_frontend $FRONTEND_PORT $BACKEND_PORT
    echo ""
    
    print_color "🚀 BOM Calculator is running!" "$GREEN"
    print_color "================================" "$GREEN"
    print_color "Frontend: http://localhost:$FRONTEND_PORT" "$BLUE"
    print_color "Backend API: http://localhost:$BACKEND_PORT" "$BLUE"
    print_color "API Docs: http://localhost:$BACKEND_PORT/api/docs" "$BLUE"
    print_color "================================" "$GREEN"
    print_color "Press Ctrl+C to stop all services" "$YELLOW"
    echo ""
    print_color "Logs are available in: $LOG_DIR" "$YELLOW"
    echo ""
    
    # Trap shutdown signals
    trap stop_services EXIT INT TERM
    
    # Keep script running and show logs
    tail -f "$LOG_DIR/backend.log" "$LOG_DIR/frontend.log" 2>/dev/null
}

# Run main function
main "$@"