# BOM Calculator for Robot Assembly Management

A comprehensive Bill of Materials (BOM) calculator and inventory management system for robotic platforms, specifically designed for SO-ARM100, LeKiwi, and XLERobot assembly tracking.

## 📋 Overview

This application provides a tablet-optimized web interface for managing robot parts inventory, calculating assembly capacity, and generating order sheets. It supports hierarchical BOMs where complex robots (like XLERobot) include simpler robots (like LeKiwi) as sub-assemblies.

### 📚 Quick Documentation Links

| Guide | Description |
|-------|-------------|
| **[User Guide](USER_GUIDE.md)** | Complete guide for end users with tutorials and best practices |
| **[Developer Guide](DEVELOPER_GUIDE.md)** | Development setup, architecture, and contribution guidelines |
| **[API Reference](API_REFERENCE.md)** | Complete REST API and WebSocket documentation |
| **[Deployment Guide](DEPLOYMENT_GUIDE.md)** | Production deployment instructions for all platforms |
| **[Troubleshooting](TROUBLESHOOTING.md)** | Solutions for common issues and diagnostic procedures |

## 🎯 Key Features

### Inventory Management
- **Tabular Entry**: Easy bulk editing of parts inventory
- **Real-time Updates**: Instant calculation of buildable quantities
- **Low Stock Alerts**: Visual indicators for parts below reorder points
- **Audit Trail**: Complete history of inventory changes

### Assembly Calculator
- **Build Capacity**: Calculate maximum buildable robots from current inventory
- **Bottleneck Analysis**: Identify limiting parts preventing additional builds
- **Partial Assembly**: Track partially completed assemblies
- **Multi-Model Support**: Simultaneous calculation for all robot types

### Order Generation
- **Smart Ordering**: Generate order sheets for target quantities
- **Supplier Grouping**: Organize orders by supplier for efficiency
- **Minimum Quantities**: Respect supplier minimum order requirements
- **Cost Estimation**: Calculate total costs including shipping estimates

### Tablet Optimization
- **10-inch Display**: Optimized for standard tablet screens
- **Touch Gestures**: Swipe actions and large touch targets
- **Responsive Layout**: Works in portrait and landscape orientations
- **Offline Support**: Queue changes when offline, sync when connected

## 🤖 Supported Robot Models

### SO-ARM100
- Leader + Follower arm set
- 12 servo motors (6x 12V, 6x 5V with various gear ratios)
- Complete with power supplies and mounting hardware
- [Documentation](https://github.com/TheRobotStudio/SO-ARM100)

### LeKiwi
- Mobile manipulator platform
- Includes 1x SO-ARM100 arm set
- 3x omnidirectional wheels for mobility
- Raspberry Pi 5 compute unit
- [Documentation](https://github.com/SIGRobotics-UIUC/LeKiwi)

### XLERobot
- Dual-arm mobile robot
- Includes 1x LeKiwi base + 1x additional SO-ARM100
- 2-DOF neck mechanism
- Vision system with RGB and depth cameras
- [Documentation](https://xlerobot.readthedocs.io)

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: React 18+ with TypeScript
- **Database**: SQLite (standalone) or PostgreSQL (production)
- **Styling**: Tailwind CSS with tablet-optimized components

### Project Structure
```
bom_calculator/
├── backend/           # FastAPI backend
│   ├── api/          # REST endpoints
│   ├── services/     # Business logic
│   ├── models/       # Database models
│   └── data/         # Initial BOMs and seed data
├── frontend/         # React frontend
│   ├── components/   # UI components
│   ├── services/     # API client
│   └── styles/       # Tablet-optimized CSS
└── docs/            # Specifications and documentation
```

## 📖 Documentation

### Comprehensive Guides

Complete documentation is organized into focused guides for different audiences:

#### For Users
- **[📚 User Guide](USER_GUIDE.md)**: Complete end-user documentation with tutorials, feature walkthroughs, and best practices
- **[🛠️ Troubleshooting Guide](TROUBLESHOOTING.md)**: Common issues, solutions, and diagnostic procedures

#### For Developers
- **[💻 Developer Guide](DEVELOPER_GUIDE.md)**: Architecture overview, development setup, component documentation, and contribution guidelines
- **[🔌 API Reference](API_REFERENCE.md)**: Complete REST API and WebSocket documentation with examples

#### For DevOps
- **[🚀 Deployment Guide](DEPLOYMENT_GUIDE.md)**: Production deployment, Docker, cloud platforms, SSL configuration, and monitoring
- **[🛠️ Troubleshooting Guide](TROUBLESHOOTING.md)**: System diagnostics, performance tuning, and recovery procedures

### Technical Specifications

Detailed technical documentation in the `docs/` directory:

- **[Requirements Specification](docs/requirements.md)**: Complete functional and non-functional requirements
- **[Domain Model](docs/domain_model.md)**: Entity definitions, relationships, and business rules
- **[System Architecture](docs/architecture.md)**: Complete technical architecture with deployment strategies
- **[UI/UX Design](docs/ui_ux_design.md)**: Material Design 3 implementation and tablet optimization
- **[Backend Pseudocode](docs/pseudocode_backend.md)**: Detailed backend implementation with TDD anchors
- **[Frontend Pseudocode](docs/pseudocode_frontend.md)**: React component architecture with touch optimization
- **[Data Initialization](docs/data_initialization.md)**: BOM data and seed configuration
- **[Implementation Roadmap](docs/implementation_roadmap.md)**: 12-week development plan with milestones
- **[Architecture Summary](ARCHITECTURE_SUMMARY.md)**: High-level overview of the complete system design

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Docker (optional, for containerized deployment)

### 🔧 First-Time Setup (Linux/macOS)

If you're running the application for the first time on Linux or macOS, you need to make the scripts executable:

```bash
cd src/lerobot/robots/bom_calculator

# Make the shell script executable
chmod +x start.sh

# Optional: Make the Python script executable too
chmod +x bom_calculator.py
```

After this one-time setup, you can run the application with:
- `./start.sh` (shell script)
- `./bom_calculator.py` (Python script)
- `python bom_calculator.py` (Python interpreter)

### ⚡ One-Command Launch

The easiest way to start the BOM Calculator:

#### Linux/macOS:

**First-time setup** (only needed once):
```bash
cd src/lerobot/robots/bom_calculator
chmod +x start.sh  # Make the script executable
```

**Starting the application**:
```bash
./start.sh
```

#### Windows:
```cmd
cd src\lerobot\robots\bom_calculator
start.bat
```

#### Python (Cross-platform):
```bash
cd src/lerobot/robots/bom_calculator
python bom_calculator.py
```

> **Note**: Both `start.sh` and `bom_calculator.py` have proper shebang lines (`#!/bin/bash` and `#!/usr/bin/env python3` respectively), so you can run them directly after making them executable.

The application will automatically:
- ✅ Check and install dependencies
- ✅ Find available ports
- ✅ Set up Python and Node environments
- ✅ Initialize the database
- ✅ Start both backend and frontend
- ✅ Open your browser to the application

### 🎯 Launch Options

#### Development Mode (default)
```bash
# With hot reload and debug features
./start.sh development
# or
python bom_calculator.py --mode development
```

#### Production Mode
```bash
# Optimized build and performance
./start.sh production
# or
python bom_calculator.py --mode production
```

#### Docker Mode
```bash
# Run in containers
docker-compose up
# or
python bom_calculator.py --mode docker
```

#### Custom Ports
```bash
# Specify custom ports
python bom_calculator.py --backend-port 8080 --frontend-port 3001
```

### 📦 Manual Installation

If you prefer manual setup:

1. Clone the repository:
```bash
cd src/lerobot/robots/bom_calculator
```

2. Copy environment configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m init_db  # Initialize database with BOMs
```

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

5. Start the services:
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev -- --port 3000
```

6. Open your browser to `http://localhost:3000`

### 🔧 Service Management

#### Start Services
```bash
./start.sh start
# or
python bom_calculator.py start
```

#### Stop Services
```bash
./start.sh stop
# or
python bom_calculator.py stop
```

#### Restart Services
```bash
./start.sh restart
# or
python bom_calculator.py restart
```

#### Check Status
```bash
./start.sh status
# or
python bom_calculator.py status
```

## 🧪 Testing

### Running All Tests
```bash
# Run complete test suite
python bom_calculator.py test
```

### Backend Tests (Python)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Unit tests
pytest tests/unit -v

# Integration tests
python ../test_integration.py

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Frontend Tests (JavaScript/React)
```bash
cd frontend

# Unit tests
npm test

# With coverage
npm run test:coverage

# Watch mode for development
npm test -- --watch
```

### End-to-End Tests (Playwright)
```bash
# Install Playwright browsers first time
npx playwright install

# Run E2E tests
node test_e2e.js

# Run with visible browser
HEADLESS=false node test_e2e.js

# Run with specific browser
BROWSER=firefox node test_e2e.js
```

### API Testing
The API can be tested interactively:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Postman Collection: Available in `tests/postman/`

## 📱 Tablet Usage

The application is optimized for 10-inch tablets:

### Touch Gestures
- **Tap**: Select items or open details
- **Long Press**: Enter bulk edit mode
- **Swipe Left**: Quick delete (with confirmation)
- **Swipe Right**: Quick edit
- **Pinch**: Zoom in/out on assembly diagrams

### Optimized Controls
- Large touch targets (minimum 44x44px)
- Number inputs with +/- buttons
- Dropdown menus with touch-friendly spacing
- Haptic feedback for actions (on supported devices)

## 🔄 Offline Support

The application works offline with automatic synchronization:

1. **Viewing**: All data cached locally for offline viewing
2. **Editing**: Changes queued when offline
3. **Syncing**: Automatic sync when connection restored
4. **Conflicts**: Smart conflict resolution with user notification

## 📊 API Documentation

Complete API documentation with examples and code samples is available in the **[API Reference](API_REFERENCE.md)**.

### Interactive Documentation
Once the backend is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Inventory
- `GET /api/v1/inventory` - List all inventory items
- `PATCH /api/v1/inventory/{part_id}` - Update single item
- `POST /api/v1/inventory/bulk-update` - Bulk update

#### Assembly
- `GET /api/v1/assembly/calculate/{model_id}` - Calculate buildable quantity
- `POST /api/v1/assembly/plan` - Create assembly plan
- `GET /api/v1/assembly/plan/{plan_id}` - Get assembly details

#### Orders
- `POST /api/v1/orders/generate` - Generate order sheet
- `GET /api/v1/orders/{order_id}` - Get order details
- `GET /api/v1/export/inventory` - Export inventory CSV

For complete endpoint documentation including request/response schemas, authentication, and WebSocket events, see the **[API Reference](API_REFERENCE.md)**.

## 🔐 Security

- User authentication via JWT tokens
- Role-based access control (Admin, Manager, Technician, Viewer)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration for production

## 🚢 Deployment

### 🐳 Docker Deployment

#### Quick Start with Docker Compose
```bash
# Development
docker-compose up

# Production (with nginx, SSL, monitoring)
docker-compose --profile production up

# With custom environment
docker-compose --env-file .env.production up
```

#### Build Images Separately
```bash
# Backend
docker build -f Dockerfile.backend -t bom-calculator-backend .

# Frontend
docker build -f Dockerfile.frontend -t bom-calculator-frontend .

# Run containers
docker run -p 8000:8000 bom-calculator-backend
docker run -p 3000:80 bom-calculator-frontend
```

### ☁️ Cloud Deployment

#### AWS/EC2
```bash
# Use provided scripts
./deploy/aws-deploy.sh

# Or manually with terraform
cd deploy/terraform
terraform init
terraform plan
terraform apply
```

#### Heroku
```bash
# Create app
heroku create bom-calculator

# Set buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# Deploy
git push heroku main
```

#### Digital Ocean
```bash
# Using App Platform
doctl apps create --spec deploy/digitalocean-app.yaml
```

### 🔒 Production Configuration

1. **Environment Variables**:
```bash
# Copy and edit production environment
cp .env.example .env.production

# Key settings to configure:
DATABASE_URL=postgresql://user:pass@host:5432/bom_calculator
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=["https://your-domain.com"]
NODE_ENV=production
DEBUG=false
```

2. **Database Migration** (PostgreSQL):
```bash
# Run migrations
cd backend
alembic upgrade head
```

3. **SSL/TLS Setup**:
```bash
# Using Let's Encrypt
certbot --nginx -d your-domain.com
```

4. **Process Management**:
```bash
# Using systemd (Linux)
sudo cp deploy/bom-calculator.service /etc/systemd/system/
sudo systemctl enable bom-calculator
sudo systemctl start bom-calculator

# Using PM2 (Node.js)
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

5. **Monitoring Setup**:
```bash
# Prometheus + Grafana (included in docker-compose)
docker-compose --profile monitoring up

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

## 🛠️ Troubleshooting

For comprehensive troubleshooting, see the **[Troubleshooting Guide](TROUBLESHOOTING.md)**.

### Quick Diagnostics

Run a complete system health check:
```bash
python bom_calculator.py diagnose
```

### Common Issues

#### Permission Denied (Linux/macOS)
```bash
# If you get "Permission denied" when running ./start.sh
chmod +x start.sh
./start.sh

# If you get "Permission denied" when running ./bom_calculator.py
chmod +x bom_calculator.py
./bom_calculator.py

# Alternative: Run with Python interpreter (no chmod needed)
python bom_calculator.py
```

#### Port Already in Use
```bash
# Use different ports
python bom_calculator.py --backend-port 8080 --frontend-port 3001

# Or kill existing processes
lsof -ti:8000 | xargs kill -9
```

#### Database Connection Error
```bash
# Re-initialize database
cd backend
python -m init_db --force
```

#### Frontend Build Error
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

For detailed solutions to these and other issues including:
- WebSocket connection problems
- Docker issues
- Authentication errors
- Performance optimization
- Data recovery procedures

See the complete **[Troubleshooting Guide](TROUBLESHOOTING.md)**.

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup
1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/lerobot.git
cd lerobot/src/lerobot/robots/bom_calculator
```

3. Create a feature branch:
```bash
git checkout -b feature/amazing-feature
```

4. Make your changes and test:
```bash
# Run tests
python test_integration.py
node test_e2e.js

# Check code style
cd backend && black . && flake8
cd ../frontend && npm run lint
```

5. Commit with clear message:
```bash
git commit -m "feat: add amazing feature

- Detailed description of changes
- Any breaking changes
- Related issue numbers"
```

6. Push to your fork:
```bash
git push origin feature/amazing-feature
```

7. Open a Pull Request with:
   - Clear description of changes
   - Screenshots for UI changes
   - Test coverage report
   - Documentation updates

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ESLint with Prettier
- **Commits**: Follow [Conventional Commits](https://www.conventionalcommits.org/)

## 📄 License

This project is part of the LeRobot ecosystem and follows the same licensing terms.

## 🆘 Support

### Getting Help

1. **Documentation**: Start with our comprehensive guides:
   - [User Guide](USER_GUIDE.md) - For end users
   - [Developer Guide](DEVELOPER_GUIDE.md) - For developers
   - [API Reference](API_REFERENCE.md) - For API integration
   - [Deployment Guide](DEPLOYMENT_GUIDE.md) - For DevOps
   - [Troubleshooting](TROUBLESHOOTING.md) - For solving issues
2. **Technical Specs**: Check the [docs](docs/) directory for detailed specifications
3. **FAQ**: See common questions below
4. **Issues**: Search [existing issues](https://github.com/huggingface/lerobot/issues?q=label:bom-calculator)
5. **Discord**: Join the LeRobot community
6. **Email**: support@lerobot.ai (for critical issues)

### Frequently Asked Questions

**Q: Can I use this with other robot models?**
A: Yes! You can add custom BOMs by editing `backend/data/custom_boms.json`

**Q: Does it work offline?**
A: Yes, the app has offline support with automatic sync when reconnected

**Q: Can multiple users access simultaneously?**
A: Yes, with real-time updates via WebSocket connections

**Q: How do I backup my data?**
A: Run `python bom_calculator.py backup` or use the admin interface

**Q: Can I import existing inventory data?**
A: Yes, use CSV import: `python -m backend.import_csv your_data.csv`

### Reporting Issues

When reporting issues, please include:
- OS and browser version
- Steps to reproduce
- Error messages and logs
- Screenshots if applicable

Use this template:
```markdown
**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 118]
- Mode: [development/production/docker]

**Description:**
[Clear description of the issue]

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Logs:**
```
[Paste relevant logs]
```

**Screenshots:**
[If applicable]
```

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core inventory management
- ✅ Assembly calculation
- ✅ Order generation
- ✅ Tablet optimization

### Phase 2 (Planned)
- 📱 Native mobile apps
- 📊 Analytics dashboard
- 🔗 ERP integration
- 📷 Barcode scanning

### Phase 3 (Future)
- 🤖 AI-powered demand forecasting
- 🌐 Multi-warehouse support
- 📈 Supply chain optimization
- 🔄 Real-time collaboration

## 🙏 Acknowledgments

- SO-ARM100 by [The Robot Studio](https://github.com/TheRobotStudio)
- LeKiwi by [SIG Robotics UIUC](https://github.com/SIGRobotics-UIUC)
- XLERobot documentation contributors
- LeRobot community for feedback and testing

---

**Built with ❤️ for the robotics community**