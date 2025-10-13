#!/usr/bin/env python3
"""
BOM Calculator - Python Launcher Script
A cross-platform launcher for the BOM Calculator application.
"""

import os
import sys
import time
import signal
import socket
import subprocess
import argparse
import platform
import webbrowser
import json
import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Application paths
BASE_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
LOG_DIR = BASE_DIR / "logs"
PID_FILE = BASE_DIR / ".bom_calculator.pid"
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE_FILE = BASE_DIR / ".env.example"

# Default configuration
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 3000
DEFAULT_MODE = "development"


class Mode(Enum):
    """Application run modes"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    DOCKER = "docker"
    TEST = "test"


class Color:
    """Terminal colors for output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


class BOMCalculatorLauncher:
    """Main launcher class for BOM Calculator"""
    
    def __init__(self, mode: Mode = Mode.DEVELOPMENT):
        self.mode = mode
        self.backend_port = DEFAULT_BACKEND_PORT
        self.frontend_port = DEFAULT_FRONTEND_PORT
        self.processes = []
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"{Color.YELLOW}Received shutdown signal...{Color.RESET}")
        self.stop()
        sys.exit(0)
        
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Color.BLUE}╔══════════════════════════════════════════╗
║       🤖 BOM Calculator Launcher 🤖       ║
║          Version 1.0.0                   ║
╚══════════════════════════════════════════╝{Color.RESET}
        """
        print(banner)
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        logger.info(f"{Color.BLUE}Checking dependencies...{Color.RESET}")
        
        # Check Python version
        if sys.version_info < (3, 7):
            logger.error(f"{Color.RED}Python 3.7 or higher is required!{Color.RESET}")
            logger.error(f"{Color.YELLOW}Current version: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}{Color.RESET}")
            logger.error(f"{Color.YELLOW}Please upgrade Python to version 3.7 or higher.{Color.RESET}")
            logger.error(f"{Color.CYAN}Visit https://www.python.org/downloads/ to download the latest version.{Color.RESET}")
            return False
        
        # Info about Python version compatibility
        if sys.version_info >= (3, 13):
            logger.info(f"{Color.CYAN}Python {sys.version_info.major}.{sys.version_info.minor} detected - using Pydantic v2 for compatibility{Color.RESET}")
        else:
            logger.info(f"{Color.GREEN}Python {sys.version_info.major}.{sys.version_info.minor} detected ✓{Color.RESET}")
            
        # Check for required commands
        required_commands = {
            "python3": "Python 3",
            "pip": "pip",
            "node": "Node.js",
            "npm": "npm"
        }
        
        if self.mode == Mode.DOCKER:
            required_commands["docker"] = "Docker"
            required_commands["docker-compose"] = "Docker Compose"
            
        missing = []
        for cmd, name in required_commands.items():
            if not self.command_exists(cmd):
                missing.append(name)
                
        if missing:
            logger.error(f"{Color.RED}Missing dependencies: {', '.join(missing)}{Color.RESET}")
            return False
            
        logger.info(f"{Color.GREEN}All dependencies are installed ✓{Color.RESET}")
        return True
        
    def command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        try:
            subprocess.run(
                [command, "--version"],
                capture_output=True,
                check=False
            )
            return True
        except FileNotFoundError:
            return False
            
    def find_available_port(self, start_port: int) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 100):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        raise RuntimeError(f"No available ports in range {start_port}-{start_port + 100}")
        
    def setup_environment(self) -> bool:
        """Setup environment variables"""
        logger.info(f"{Color.BLUE}Setting up environment...{Color.RESET}")
        
        # Create .env file if it doesn't exist
        if not ENV_FILE.exists() and ENV_EXAMPLE_FILE.exists():
            logger.info(f"{Color.YELLOW}Creating .env file from .env.example...{Color.RESET}")
            import shutil
            shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)
            
        # Load environment variables from .env file
        if ENV_FILE.exists():
            self.load_env_file(ENV_FILE)
            
        # Set default environment variables
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./bom_calculator.db")
        os.environ.setdefault("CORS_ORIGINS", f'["http://localhost:{self.frontend_port}"]')
        os.environ.setdefault("VITE_API_URL", f"http://localhost:{self.backend_port}")
        os.environ.setdefault("NODE_ENV", self.mode.value)
        
        logger.info(f"{Color.GREEN}Environment setup complete ✓{Color.RESET}")
        return True
        
    def load_env_file(self, env_file: Path):
        """Load environment variables from .env file"""
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ[key.strip()] = value.strip().strip('"\'')
                        
    def setup_backend(self) -> bool:
        """Setup Python backend environment"""
        logger.info(f"{Color.BLUE}Setting up backend...{Color.RESET}")
        
        # Create virtual environment if it doesn't exist
        venv_path = BACKEND_DIR / "venv"
        if not venv_path.exists():
            logger.info(f"{Color.YELLOW}Creating Python virtual environment...{Color.RESET}")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"{Color.RED}Failed to create virtual environment!{Color.RESET}")
                logger.error(f"{Color.RED}Error: {result.stderr}{Color.RESET}")
                return False
            
        # Get pip path
        pip_path = venv_path / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
        python_path = venv_path / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
        
        # Upgrade pip first
        logger.info(f"{Color.YELLOW}Upgrading pip...{Color.RESET}")
        result = subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.warning(f"{Color.YELLOW}Warning: Failed to upgrade pip: {result.stderr}{Color.RESET}")
        else:
            logger.info(f"{Color.GREEN}Pip upgraded successfully ✓{Color.RESET}")
        
        # Install requirements with fallback mechanism
        logger.info(f"{Color.YELLOW}Installing backend dependencies...{Color.RESET}")
        requirements_file = BACKEND_DIR / "requirements.txt"
        
        # First try to install all requirements at once
        logger.info(f"{Color.CYAN}Attempting bulk installation...{Color.RESET}")
        result = subprocess.run(
            [str(pip_path), "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.warning(f"{Color.YELLOW}Bulk installation failed. Trying fallback installation...{Color.RESET}")
            logger.debug(f"Error details: {result.stderr}")
            
            # Fallback: Install packages one by one
            failed_packages = []
            with open(requirements_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                package = line.split('#')[0].strip()  # Remove inline comments
                if not package:
                    continue
                    
                logger.info(f"{Color.CYAN}Installing: {package}{Color.RESET}")
                result = subprocess.run(
                    [str(pip_path), "install", package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"{Color.RED}Failed to install: {package}{Color.RESET}")
                    logger.debug(f"Error: {result.stderr}")
                    failed_packages.append(package)
                else:
                    logger.info(f"{Color.GREEN}✓ Installed: {package}{Color.RESET}")
            
            if failed_packages:
                logger.error(f"{Color.RED}Failed to install the following packages:{Color.RESET}")
                for pkg in failed_packages:
                    logger.error(f"  {Color.RED}- {pkg}{Color.RESET}")
                
                # Check if all essential packages are installed
                essential_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'aiosqlite']
                essential_failed = [pkg for pkg in failed_packages
                                   if any(ep in pkg.lower() for ep in essential_packages)]
                
                if essential_failed:
                    logger.error(f"{Color.RED}Essential packages failed to install!{Color.RESET}")
                    logger.error(f"{Color.RED}Please check your Python version and network connection.{Color.RESET}")
                    logger.error(f"{Color.YELLOW}Try running: pip install --upgrade pip{Color.RESET}")
                    return False
                else:
                    logger.warning(f"{Color.YELLOW}Some optional packages failed, but core functionality should work.{Color.RESET}")
                    logger.info(f"{Color.YELLOW}You can install additional packages later with:{Color.RESET}")
                    logger.info(f"{Color.CYAN}  pip install -r backend/requirements-full.txt{Color.RESET}")
        else:
            logger.info(f"{Color.GREEN}All dependencies installed successfully ✓{Color.RESET}")
        
        # Verify essential packages are installed
        logger.info(f"{Color.BLUE}Verifying essential packages...{Color.RESET}")
        essential_packages = {
            'fastapi': 'FastAPI',
            'uvicorn': 'Uvicorn',
            'sqlalchemy': 'SQLAlchemy',
            'pydantic': 'Pydantic'
        }
        
        missing_essential = []
        for package, name in essential_packages.items():
            result = subprocess.run(
                [str(python_path), "-c", f"import {package}"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                missing_essential.append(name)
        
        if missing_essential:
            logger.error(f"{Color.RED}Missing essential packages: {', '.join(missing_essential)}{Color.RESET}")
            logger.error(f"{Color.YELLOW}Please install them manually or check your Python environment.{Color.RESET}")
            return False
        
        logger.info(f"{Color.GREEN}Backend setup complete ✓{Color.RESET}")
        return True
        
    def setup_frontend(self) -> bool:
        """Setup Node.js frontend environment"""
        logger.info(f"{Color.BLUE}Setting up frontend...{Color.RESET}")
        
        # Check if node_modules exists
        if not (FRONTEND_DIR / "node_modules").exists():
            logger.info(f"{Color.YELLOW}Installing frontend dependencies...{Color.RESET}")
            subprocess.run(
                ["npm", "install"],
                cwd=str(FRONTEND_DIR),
                check=True
            )
            
        logger.info(f"{Color.GREEN}Frontend setup complete ✓{Color.RESET}")
        return True
        
    def init_database(self) -> bool:
        """Initialize database"""
        logger.info(f"{Color.BLUE}Initializing database...{Color.RESET}")
        
        db_file = BACKEND_DIR / "bom_calculator.db"
        if not db_file.exists():
            logger.info(f"{Color.YELLOW}Creating database and loading initial data...{Color.RESET}")
            
            # Get Python path in virtual environment
            python_path = BACKEND_DIR / "venv" / (
                "Scripts" if platform.system() == "Windows" else "bin"
            ) / "python"
            
            # Run database initialization
            subprocess.run(
                [str(python_path), "-m", "init_db"],
                cwd=str(BACKEND_DIR),
                check=True
            )
            logger.info(f"{Color.GREEN}Database initialized ✓{Color.RESET}")
        else:
            logger.info(f"{Color.GREEN}Database already exists ✓{Color.RESET}")
            
        return True
        
    def start_backend(self) -> subprocess.Popen:
        """Start backend server"""
        logger.info(f"{Color.BLUE}Starting backend on port {self.backend_port}...{Color.RESET}")
        
        # Create logs directory
        LOG_DIR.mkdir(exist_ok=True)
        
        # Get Python path in virtual environment
        python_path = BACKEND_DIR / "venv" / (
            "Scripts" if platform.system() == "Windows" else "bin"
        ) / "python"
        
        # Prepare command
        cmd = [
            str(python_path), "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(self.backend_port)
        ]
        
        if self.mode == Mode.DEVELOPMENT:
            cmd.append("--reload")
        elif self.mode == Mode.PRODUCTION:
            cmd.extend(["--workers", "4"])
            
        # Start backend process
        with open(LOG_DIR / "backend.log", "w") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=str(BACKEND_DIR),
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
            
        # Wait for backend to start
        time.sleep(3)
        
        # Check if backend is running
        if not self.check_health(f"http://localhost:{self.backend_port}/health"):
            logger.error(f"{Color.RED}Failed to start backend!{Color.RESET}")
            process.terminate()
            return None
            
        logger.info(f"{Color.GREEN}Backend started successfully ✓{Color.RESET}")
        return process
        
    def start_frontend(self) -> subprocess.Popen:
        """Start frontend server"""
        logger.info(f"{Color.BLUE}Starting frontend on port {self.frontend_port}...{Color.RESET}")
        
        # Prepare command
        if self.mode == Mode.PRODUCTION:
            # Build for production
            logger.info(f"{Color.YELLOW}Building frontend for production...{Color.RESET}")
            subprocess.run(
                ["npm", "run", "build"],
                cwd=str(FRONTEND_DIR),
                check=True
            )
            
            cmd = ["npx", "serve", "-s", "dist", "-l", str(self.frontend_port)]
        else:
            # Development mode
            cmd = ["npm", "run", "dev", "--", "--port", str(self.frontend_port), "--host"]
            
        # Start frontend process
        with open(LOG_DIR / "frontend.log", "w") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=str(FRONTEND_DIR),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env={**os.environ, "PORT": str(self.frontend_port)}
            )
            
        # Wait for frontend to start
        time.sleep(5)
        
        logger.info(f"{Color.GREEN}Frontend started successfully ✓{Color.RESET}")
        return process
        
    def start_docker(self) -> bool:
        """Start application using Docker Compose"""
        logger.info(f"{Color.BLUE}Starting with Docker Compose...{Color.RESET}")
        
        compose_file = BASE_DIR / "docker-compose.yml"
        if not compose_file.exists():
            logger.error(f"{Color.RED}docker-compose.yml not found!{Color.RESET}")
            return False
            
        # Prepare docker-compose command
        cmd = ["docker-compose", "-f", str(compose_file)]
        
        if self.mode == Mode.PRODUCTION:
            cmd.extend(["--profile", "production"])
            
        cmd.extend(["up", "-d"])
        
        # Run docker-compose
        subprocess.run(cmd, cwd=str(BASE_DIR), check=True)
        
        logger.info(f"{Color.GREEN}Docker containers started successfully ✓{Color.RESET}")
        return True
        
    def check_health(self, url: str, timeout: int = 10) -> bool:
        """Check if a service is healthy"""
        import urllib.request
        import urllib.error
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    return response.status == 200
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.5)
                
        return False
        
    def start(self) -> bool:
        """Start the BOM Calculator application"""
        self.print_banner()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
            
        # Find available ports
        self.backend_port = self.find_available_port(DEFAULT_BACKEND_PORT)
        self.frontend_port = self.find_available_port(DEFAULT_FRONTEND_PORT)
        
        logger.info(f"{Color.GREEN}Using backend port: {self.backend_port}{Color.RESET}")
        logger.info(f"{Color.GREEN}Using frontend port: {self.frontend_port}{Color.RESET}")
        
        # Setup environment
        if not self.setup_environment():
            return False
            
        if self.mode == Mode.DOCKER:
            # Start with Docker
            return self.start_docker()
        else:
            # Setup backend and frontend
            if not self.setup_backend():
                return False
                
            if not self.setup_frontend():
                return False
                
            # Initialize database
            if not self.init_database():
                return False
                
            # Start services
            backend_process = self.start_backend()
            if not backend_process:
                return False
            self.processes.append(backend_process)
            
            frontend_process = self.start_frontend()
            if not frontend_process:
                return False
            self.processes.append(frontend_process)
            
            # Save PIDs
            self.save_pids()
            
            # Print success message
            self.print_success()
            
            # Open browser
            if self.mode == Mode.DEVELOPMENT:
                time.sleep(2)
                webbrowser.open(f"http://localhost:{self.frontend_port}")
                
            # Keep running
            try:
                for process in self.processes:
                    process.wait()
            except KeyboardInterrupt:
                self.stop()
                
        return True
        
    def stop(self) -> bool:
        """Stop the BOM Calculator application"""
        logger.info(f"{Color.YELLOW}Stopping BOM Calculator...{Color.RESET}")
        
        if self.mode == Mode.DOCKER:
            # Stop Docker containers
            subprocess.run(
                ["docker-compose", "-f", str(BASE_DIR / "docker-compose.yml"), "down"],
                cwd=str(BASE_DIR),
                check=False
            )
        else:
            # Stop processes
            for process in self.processes:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        
            # Load PIDs from file
            if PID_FILE.exists():
                with open(PID_FILE, 'r') as f:
                    pids = [int(line.strip()) for line in f if line.strip()]
                    
                for pid in pids:
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                        
                PID_FILE.unlink()
                
        logger.info(f"{Color.GREEN}All services stopped ✓{Color.RESET}")
        return True
        
    def restart(self) -> bool:
        """Restart the application"""
        logger.info(f"{Color.YELLOW}Restarting BOM Calculator...{Color.RESET}")
        self.stop()
        time.sleep(2)
        return self.start()
        
    def status(self) -> Dict[str, bool]:
        """Check application status"""
        status = {
            "backend": False,
            "frontend": False,
            "database": False
        }
        
        # Check backend
        if self.check_health(f"http://localhost:{self.backend_port}/health", timeout=2):
            status["backend"] = True
            
        # Check frontend
        if self.check_health(f"http://localhost:{self.frontend_port}", timeout=2):
            status["frontend"] = True
            
        # Check database
        db_file = BACKEND_DIR / "bom_calculator.db"
        if db_file.exists():
            status["database"] = True
            
        return status
        
    def save_pids(self):
        """Save process PIDs to file"""
        with open(PID_FILE, 'w') as f:
            for process in self.processes:
                f.write(f"{process.pid}\n")
                
    def print_success(self):
        """Print success message with URLs"""
        message = f"""
{Color.GREEN}╔══════════════════════════════════════════════╗
║     🚀 BOM Calculator is running! 🚀         ║
╚══════════════════════════════════════════════╝{Color.RESET}

{Color.BLUE}Frontend:{Color.RESET} http://localhost:{self.frontend_port}
{Color.BLUE}Backend API:{Color.RESET} http://localhost:{self.backend_port}
{Color.BLUE}API Docs:{Color.RESET} http://localhost:{self.backend_port}/api/docs
{Color.BLUE}Mode:{Color.RESET} {self.mode.value}

{Color.YELLOW}Press Ctrl+C to stop all services{Color.RESET}
{Color.YELLOW}Logs available in:{Color.RESET} {LOG_DIR}
        """
        print(message)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BOM Calculator Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status"],
        nargs="?",
        default="start",
        help="Command to execute (default: start)"
    )
    
    parser.add_argument(
        "--mode",
        choices=["development", "production", "docker", "test"],
        default="development",
        help="Run mode (default: development)"
    )
    
    parser.add_argument(
        "--backend-port",
        type=int,
        default=DEFAULT_BACKEND_PORT,
        help=f"Backend port (default: {DEFAULT_BACKEND_PORT})"
    )
    
    parser.add_argument(
        "--frontend-port",
        type=int,
        default=DEFAULT_FRONTEND_PORT,
        help=f"Frontend port (default: {DEFAULT_FRONTEND_PORT})"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create launcher
    mode = Mode(args.mode)
    launcher = BOMCalculatorLauncher(mode)
    
    # Override ports if specified
    if args.backend_port:
        launcher.backend_port = args.backend_port
    if args.frontend_port:
        launcher.frontend_port = args.frontend_port
        
    # Execute command
    try:
        if args.command == "start":
            success = launcher.start()
            sys.exit(0 if success else 1)
        elif args.command == "stop":
            success = launcher.stop()
            sys.exit(0 if success else 1)
        elif args.command == "restart":
            success = launcher.restart()
            sys.exit(0 if success else 1)
        elif args.command == "status":
            status = launcher.status()
            print(f"\n{Color.BLUE}BOM Calculator Status:{Color.RESET}")
            for service, running in status.items():
                icon = "✓" if running else "✗"
                color = Color.GREEN if running else Color.RED
                print(f"  {color}{icon} {service.capitalize()}: {'Running' if running else 'Stopped'}{Color.RESET}")
            sys.exit(0)
    except KeyboardInterrupt:
        launcher.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"{Color.RED}Error: {e}{Color.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()