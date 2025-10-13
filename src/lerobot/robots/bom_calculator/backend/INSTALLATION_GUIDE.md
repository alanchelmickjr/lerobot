# BOM Calculator Backend - Installation Guide

## Overview

The BOM Calculator backend has been optimized with a tiered installation approach to handle various system configurations and dependency conflicts. We provide two requirement files:

1. **requirements.txt** - Minimal essential packages for core functionality
2. **requirements-full.txt** - Complete package set with all features

## Installation Options

### Option 1: Automatic Installation (Recommended)

The launcher script handles installation automatically with smart fallback mechanisms:

```bash
# From the bom_calculator directory
python bom_calculator.py start
```

The launcher will:
1. Create a virtual environment if needed
2. Upgrade pip, setuptools, and wheel
3. Attempt bulk installation of requirements
4. If bulk fails, install packages one-by-one
5. Verify essential packages are installed
6. Continue even if optional packages fail

### Option 2: Manual Minimal Installation

For systems with installation issues, start with the minimal requirements:

```bash
# Create virtual environment
python -m venv backend/venv

# Activate virtual environment
# On Linux/Mac:
source backend/venv/bin/activate
# On Windows:
backend\venv\Scripts\activate

# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel

# Install minimal requirements
pip install -r backend/requirements.txt
```

### Option 3: Full Installation

After confirming the minimal installation works, optionally add advanced features:

```bash
# With virtual environment activated
pip install -r backend/requirements-full.txt
```

## Requirements Files

### requirements.txt (Minimal - 6 packages)
Essential packages that should install on most systems:
- **fastapi** (0.104.1) - Web framework
- **uvicorn[standard]** (0.24.0) - ASGI server
- **sqlalchemy** (2.0.23) - Database ORM
- **aiosqlite** (0.19.0) - Async SQLite support
- **pydantic** (2.5.2) - Data validation
- **python-dotenv** (1.0.0) - Environment management

### requirements-full.txt (Complete - 30+ packages)
Includes all packages for advanced features:
- Authentication & Security (python-jose, passlib)
- Testing & Quality (pytest, black, mypy)
- Caching & Tasks (redis, celery)
- Data Export (pandas, openpyxl)
- Monitoring (prometheus-client, structlog)
- Performance (orjson, aiocache)

## Troubleshooting

### Common Issues and Solutions

#### 1. pip Installation Failures

**Problem**: "error: Microsoft Visual C++ 14.0 or greater is required"

**Solution**: 
- Install Visual Studio Build Tools from: https://visualstudio.microsoft.com/downloads/
- Or use pre-compiled wheels: `pip install --only-binary :all: package-name`

#### 2. Network/Proxy Issues

**Problem**: Connection timeouts or SSL errors

**Solution**:
```bash
# Use alternative index
pip install -r requirements.txt --index-url https://pypi.python.org/simple/

# Or with trusted host
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

#### 3. Permission Errors

**Problem**: "Permission denied" errors

**Solution**:
```bash
# Install to user directory (not recommended for production)
pip install --user -r requirements.txt

# Or fix permissions (Linux/Mac)
sudo chown -R $USER:$USER backend/venv
```

#### 4. Incompatible Python Version

**Problem**: Package requires different Python version

**Solution**:
- Ensure Python 3.8+ is installed
- Use pyenv or conda to manage Python versions
- Check with: `python --version`

### Manual Package Installation

If automated installation fails, install packages individually in this order:

```bash
# Core packages (install these first)
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.2

# Database support
pip install aiosqlite==0.19.0

# Environment
pip install python-dotenv==1.0.0

# Optional packages (can fail without breaking core)
pip install httpx==0.25.2
pip install pytest==7.4.3
```

### Verification

After installation, verify the setup:

```bash
# Check installed packages
pip list

# Test imports
python -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('Core packages OK')"

# Run the application
python -m uvicorn main:app --reload
```

## Platform-Specific Notes

### Windows
- Use Python 3.8+ from python.org
- Install Visual Studio Build Tools for packages with C extensions
- Use PowerShell or Command Prompt as Administrator if needed

### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew Python: `brew install python@3.11`
- May need to install additional development headers

### Linux
- Install python3-dev package: `sudo apt-get install python3-dev` (Ubuntu/Debian)
- Or: `sudo yum install python3-devel` (RHEL/CentOS)
- Ensure gcc and build essentials are installed

## Docker Alternative

If local installation continues to fail, use Docker:

```bash
# From bom_calculator directory
docker-compose up -d
```

This bypasses all local dependency issues by running in containers.

## Getting Help

If you continue to experience issues:

1. Check the logs in `bom_calculator/logs/`
2. Run with verbose mode: `python bom_calculator.py start --verbose`
3. Try the Docker deployment option
4. Report issues with:
   - Your OS and Python version
   - Complete error messages
   - Output of `pip --version` and `python --version`

## Next Steps

After successful installation:

1. Initialize the database: `python -m init_db`
2. Start the backend: `python -m uvicorn main:app --reload`
3. Access API docs at: http://localhost:8000/docs
4. Configure the frontend to connect to the backend