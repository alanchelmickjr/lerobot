# BOM Calculator Troubleshooting Guide

Comprehensive troubleshooting guide for common issues and their solutions.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Connection Problems](#connection-problems)
4. [Database Issues](#database-issues)
5. [Frontend Issues](#frontend-issues)
6. [API Errors](#api-errors)
7. [Performance Problems](#performance-problems)
8. [Docker Issues](#docker-issues)
9. [Authentication Issues](#authentication-issues)
10. [Data Issues](#data-issues)
11. [Known Issues](#known-issues)
12. [Debug Mode](#debug-mode)
13. [Log Analysis](#log-analysis)
14. [Recovery Procedures](#recovery-procedures)
15. [Getting Help](#getting-help)

---

## Quick Diagnostics

### System Health Check

Run this command to perform a complete system health check:

```bash
python bom_calculator.py diagnose
```

This will check:
- ✓ System requirements
- ✓ Port availability
- ✓ Database connection
- ✓ File permissions
- ✓ Dependencies
- ✓ Network connectivity

### Manual Health Checks

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is accessible
curl http://localhost:3000

# Check database connection
python -c "from backend.database import test_connection; test_connection()"

# Check Redis (if using)
redis-cli ping

# Check disk space
df -h

# Check memory usage
free -m

# Check process status
ps aux | grep -E "(python|node|postgres)"
```

---

## Installation Issues

### Issue: Python Version Error

**Error:**
```
ERROR: Python 3.9+ is required, but you have Python 3.8
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# macOS
brew install python@3.9

# Windows
# Download from https://www.python.org/downloads/

# Use specific Python version
python3.9 bom_calculator.py
```

### Issue: Node.js Version Error

**Error:**
```
ERROR: Node.js 16+ is required
```

**Solution:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@16

# Windows
# Download from https://nodejs.org/
```

### Issue: pip Install Fails

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# If SSL error
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: npm Install Fails

**Error:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock
rm -rf node_modules package-lock.json

# Try with legacy peer deps
npm install --legacy-peer-deps

# Or use yarn
yarn install

# If permission error on Linux/Mac
sudo npm install -g npm@latest
```

---

## Connection Problems

### Issue: Port Already in Use

**Error:**
```
ERROR: Port 8000 is already in use
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different ports
python bom_calculator.py --backend-port 8080 --frontend-port 3001

# Update .env file
BACKEND_PORT=8080
FRONTEND_PORT=3001
```

### Issue: Cannot Connect to Backend

**Error:**
```
Failed to fetch: net::ERR_CONNECTION_REFUSED
```

**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn
systemctl status bom-calculator-api

# Restart backend
cd backend
uvicorn main:app --reload --port 8000

# Check firewall
sudo ufw status
sudo ufw allow 8000

# Check CORS settings in .env
CORS_ORIGINS=["http://localhost:3000"]
```

### Issue: WebSocket Connection Failed

**Error:**
```
WebSocket connection to 'ws://localhost:8000/ws' failed
```

**Solution:**
```javascript
// Check WebSocket URL in frontend
// src/config.ts
const WS_URL = process.env.NODE_ENV === 'production'
  ? 'wss://your-domain.com/ws'
  : 'ws://localhost:8000/ws';

// Enable WebSocket in nginx.conf
location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## Database Issues

### Issue: Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
sudo systemctl start postgresql

# Check connection settings
psql -U postgres -h localhost

# Reset password if needed
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:new_password@localhost/bom_calculator

# For SQLite, check file permissions
chmod 664 backend/bom_calculator.db
```

### Issue: Database Migration Failed

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'head'
```

**Solution:**
```bash
# Reset migrations
cd backend
rm -rf migrations/versions/*

# Recreate migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# If tables exist, drop and recreate
python -c "from database import Base, engine; Base.metadata.drop_all(engine)"
python -m init_db
```

### Issue: Database Locked (SQLite)

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```python
# Increase timeout in database.py
engine = create_engine(
    "sqlite:///bom_calculator.db",
    connect_args={"check_same_thread": False, "timeout": 30}
)

# Or switch to PostgreSQL for production
DATABASE_URL=postgresql://user:pass@localhost/bom_calculator
```

---

## Frontend Issues

### Issue: Blank White Screen

**Error:**
```
Uncaught SyntaxError: Unexpected token '<'
```

**Solution:**
```bash
# Rebuild frontend
cd frontend
npm run build

# Check if build files exist
ls -la dist/

# Check base URL in index.html
# Ensure correct base path
<base href="/">

# Clear browser cache
# Chrome: Ctrl+Shift+Del
# Firefox: Ctrl+Shift+Del
# Safari: Cmd+Shift+Del
```

### Issue: Components Not Rendering

**Error:**
```
Error: Cannot find module '@mui/material'
```

**Solution:**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check for missing dependencies
npm ls

# Install missing packages
npm install @mui/material @emotion/react @emotion/styled

# Check imports in components
# Use correct import paths
import { Button } from '@mui/material';
```

### Issue: State Not Updating

**Problem:** UI doesn't reflect changes

**Solution:**
```typescript
// Check React Query cache
import { useQueryClient } from 'react-query';

const queryClient = useQueryClient();
// Invalidate cache after mutation
queryClient.invalidateQueries(['inventory']);

// Check Zustand store
const { inventory, updateInventory } = useBOMStore();
// Ensure state updates are called correctly
updateInventory(newData);

// Enable React DevTools
if (process.env.NODE_ENV === 'development') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__.inject = function() {}
}
```

---

## API Errors

### Issue: 401 Unauthorized

**Error:**
```json
{
  "detail": "Not authenticated"
}
```

**Solution:**
```javascript
// Check token in request headers
const token = localStorage.getItem('access_token');
if (!token) {
  // Redirect to login
  window.location.href = '/login';
}

// Include token in API calls
fetch('/api/v1/inventory', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Refresh token if expired
if (response.status === 401) {
  await refreshToken();
  // Retry request
}
```

### Issue: 422 Validation Error

**Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**Solution:**
```python
# Check request payload matches schema
# backend/schemas.py
class InventoryUpdate(BaseModel):
    quantity: int = Field(..., gt=0, le=99999)
    location: Optional[str] = Field(None, max_length=100)

# Validate before sending
if (quantity > 0 && quantity <= 99999) {
  await api.updateInventory(partId, quantity);
} else {
  showError('Quantity must be between 1 and 99999');
}
```

### Issue: 500 Internal Server Error

**Error:**
```
500 Internal Server Error
```

**Solution:**
```bash
# Check backend logs
tail -f /var/log/bom-calculator/error.log
journalctl -u bom-calculator-api -f

# Enable debug mode
# .env
DEBUG=true
LOG_LEVEL=debug

# Check for Python errors
cd backend
python -c "from main import app"

# Common fixes:
# 1. Missing environment variables
# 2. Database connection issues
# 3. Import errors
# 4. Permission issues
```

---

## Performance Problems

### Issue: Slow Page Load

**Symptoms:**
- Page takes > 3 seconds to load
- High Time to First Byte (TTFB)

**Solution:**
```bash
# Enable production mode
NODE_ENV=production npm run build

# Enable compression in nginx
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# Optimize bundle size
npm run build -- --analyze

# Lazy load components
const InventoryPage = lazy(() => import('./pages/Inventory'));

# Enable caching
# Backend
@cache(expire=300)
async def get_inventory():
    pass

# Frontend
const { data } = useQuery(
  ['inventory'],
  fetchInventory,
  { staleTime: 5 * 60 * 1000 }
);
```

### Issue: High Memory Usage

**Symptoms:**
- Backend using > 1GB RAM
- Frontend build fails with heap error

**Solution:**
```bash
# Limit worker processes
# gunicorn.conf.py
workers = 2  # Instead of CPU count * 2

# Increase Node memory for build
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Use pagination for large datasets
GET /api/v1/inventory?page=1&limit=50

# Clear unused caches
redis-cli FLUSHDB

# Monitor memory usage
htop
ps aux --sort=-%mem | head
```

### Issue: Database Queries Slow

**Symptoms:**
- API responses > 1 second
- Database CPU high

**Solution:**
```sql
-- Add indexes
CREATE INDEX idx_inventory_part_id ON inventory(part_id);
CREATE INDEX idx_bom_items_bom_id ON bom_items(bom_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM inventory WHERE part_id = 'servo_12v';

-- Vacuum and analyze
VACUUM ANALYZE;

-- Use query optimization
# backend/services/inventory_service.py
# Use joinedload for relationships
query = db.query(Inventory).options(
    joinedload(Inventory.part)
).filter(...)
```

---

## Docker Issues

### Issue: Container Won't Start

**Error:**
```
docker: Error response from daemon: Conflict. The container name "/bom-calculator" is already in use
```

**Solution:**
```bash
# Remove existing container
docker rm -f bom-calculator

# Clean up all containers
docker-compose down
docker system prune -a

# Rebuild and start
docker-compose up --build -d

# Check logs
docker-compose logs -f api
```

### Issue: Can't Connect to Container

**Error:**
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Solution:**
```bash
# Check if container is running
docker ps

# Check port mapping
docker port bom-calculator-api

# Inspect network
docker network ls
docker network inspect bom_calculator_default

# Use container IP
docker inspect bom-calculator-api | grep IPAddress

# Correct docker-compose.yml
services:
  api:
    ports:
      - "8000:8000"
```

### Issue: Permission Denied in Container

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/app/data'
```

**Solution:**
```dockerfile
# Dockerfile
# Create user with proper permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Or fix volume permissions
docker exec bom-calculator-api chmod 755 /app/data
```

---

## Authentication Issues

### Issue: Can't Login

**Error:**
```
Invalid username or password
```

**Solution:**
```bash
# Reset password via CLI
cd backend
python -c "from manage import reset_password; reset_password('user@example.com', 'new_password')"

# Create new admin user
python -c "from manage import create_admin; create_admin('admin@example.com', 'password')"

# Check user exists in database
psql bom_calculator -c "SELECT * FROM users WHERE email='user@example.com';"

# Verify password hash
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt']); print(pwd_context.verify('password', '$2b$12$...'))"
```

### Issue: Token Expired

**Error:**
```
JWT token has expired
```

**Solution:**
```javascript
// Implement token refresh
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data.access_token;
  }
  
  // Redirect to login if refresh fails
  window.location.href = '/login';
}

// Auto-refresh before expiry
setInterval(refreshAccessToken, 55 * 60 * 1000); // 55 minutes
```

---

## Data Issues

### Issue: BOM Data Not Loading

**Error:**
```
No BOM found for robot model: so-arm100
```

**Solution:**
```bash
# Reinitialize database with BOMs
cd backend
python -m init_db --force

# Check if BOM files exist
ls -la data/boms/

# Manually import BOM
python -c "from init_db import import_bom; import_bom('data/boms/so-arm100.json')"

# Verify in database
psql bom_calculator -c "SELECT * FROM boms WHERE robot_model_id='so-arm100';"
```

### Issue: Inventory Count Mismatch

**Problem:** Physical count doesn't match system

**Solution:**
```python
# Run inventory audit
python scripts/audit_inventory.py

# Fix discrepancies
UPDATE inventory 
SET quantity_loose = 45 
WHERE part_id = 'servo_12v';

# Add audit trail
INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, user_id, notes)
VALUES ('inventory', 'servo_12v', 'adjust', '50', '45', 'admin', 'Physical count correction');
```

### Issue: Calculations Incorrect

**Problem:** Assembly calculations wrong

**Solution:**
```python
# Verify BOM quantities
SELECT bi.part_id, bi.quantity, p.name 
FROM bom_items bi 
JOIN parts p ON bi.part_id = p.id 
WHERE bi.bom_id = 1;

# Check calculation logic
# backend/services/assembly_service.py
def calculate_buildable(self, robot_model_id):
    # Debug: Print each calculation step
    for item in bom.items:
        available = inventory.quantity_loose
        required = item.quantity
        possible = available // required
        print(f"{item.part_id}: {available}/{required} = {possible}")
```

---

## Known Issues

### Current Limitations

1. **Maximum file upload size**: 10MB
   - Workaround: Compress files before upload

2. **Concurrent user limit**: 100
   - Workaround: Use load balancer for scaling

3. **Excel export limit**: 10,000 rows
   - Workaround: Use CSV for larger exports

4. **WebSocket reconnection**: Manual refresh needed
   - Workaround: Implement auto-reconnect in frontend

5. **Safari touch gestures**: Some gestures not working
   - Workaround: Use click instead of swipe

### Planned Fixes

- Version 1.1.0: WebSocket auto-reconnect
- Version 1.2.0: Increased file upload limit
- Version 1.3.0: Safari gesture support

---

## Debug Mode

### Enable Debug Mode

```bash
# Backend debug mode
# .env
DEBUG=true
LOG_LEVEL=debug

# Run with debug
uvicorn main:app --reload --log-level debug

# Frontend debug mode
# .env
VITE_DEBUG=true

# Run with source maps
npm run dev -- --sourcemap
```

### Debug Tools

```python
# Backend debugging
import pdb; pdb.set_trace()  # Breakpoint

# Use IPython for better debugging
pip install ipython
import IPython; IPython.embed()

# Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

```javascript
// Frontend debugging
console.log('Debug:', data);
debugger; // Breakpoint

// React DevTools
// Chrome Extension: React Developer Tools

// Network debugging
window.addEventListener('fetch', (e) => {
  console.log('Fetch:', e.request.url);
});
```

---

## Log Analysis

### Log Locations

```bash
# System logs
/var/log/bom-calculator/
├── access.log     # API access logs
├── error.log      # Error logs
├── app.log        # Application logs
└── audit.log      # Audit trail

# Docker logs
docker logs bom-calculator-api
docker-compose logs -f

# Systemd logs
journalctl -u bom-calculator-api -f
```

### Log Analysis Commands

```bash
# Find errors in last hour
grep ERROR /var/log/bom-calculator/error.log | tail -100

# Count requests by endpoint
awk '{print $7}' /var/log/bom-calculator/access.log | sort | uniq -c | sort -rn

# Find slow queries
grep "duration:" /var/log/bom-calculator/app.log | awk '{if ($2 > 1000) print}'

# Monitor in real-time
tail -f /var/log/bom-calculator/*.log
```

### Structured Logging

```python
# Use structured logging
import structlog

logger = structlog.get_logger()

logger.info(
    "inventory_updated",
    part_id=part_id,
    old_quantity=old_qty,
    new_quantity=new_qty,
    duration_ms=duration
)
```

---

## Recovery Procedures

### Emergency Recovery

```bash
#!/bin/bash
# emergency_recovery.sh

echo "Starting emergency recovery..."

# 1. Stop all services
systemctl stop bom-calculator-api
systemctl stop nginx

# 2. Backup current state
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /home/bomcalc/lerobot/src/lerobot/robots/bom_calculator

# 3. Restore from last known good backup
tar -xzf /backups/last_known_good.tar.gz -C /

# 4. Reset database
psql bom_calculator < /backups/last_known_good.sql

# 5. Clear caches
redis-cli FLUSHALL

# 6. Restart services
systemctl start bom-calculator-api
systemctl start nginx

echo "Recovery complete. Please verify system functionality."
```

### Data Recovery

```sql
-- Restore from backup
psql bom_calculator < backup_20240115.sql

-- Recover deleted records
SELECT * FROM audit_log 
WHERE action = 'delete' 
AND timestamp > '2024-01-15'
ORDER BY timestamp DESC;

-- Rollback transaction
BEGIN;
-- Make changes
ROLLBACK; -- If something goes wrong
```

### Rollback Deployment

```bash
# Using Git tags
git checkout v1.0.0
npm install
npm run build

# Using Docker
docker pull bom-calculator:v1.0.0
docker-compose up -d

# Database rollback
alembic downgrade -1
```

---

## Getting Help

### Self-Help Resources

1. **Check Documentation**
   - [User Guide](USER_GUIDE.md)
   - [Developer Guide](DEVELOPER_GUIDE.md)
   - [API Reference](API_REFERENCE.md)

2. **Search Issues**
   - GitHub Issues: https://github.com/yourusername/lerobot/issues
   - Stack Overflow: Tag `bom-calculator`

3. **Review Logs**
   - Check error logs
   - Enable debug mode
   - Use browser developer tools

### Community Support

- **Discord**: https://discord.gg/bomcalculator
- **Forum**: https://forum.bomcalculator.com
- **Slack**: bomcalculator.slack.com

### Professional Support

For critical issues:
- **Email**: support@bomcalculator.com
- **Priority Support**: Available with enterprise license
- **Phone**: +1-555-BOM-CALC (business hours)

### Reporting Bugs

When reporting issues, include:

```markdown
## Environment
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120]
- Python version: [e.g., 3.9.5]
- Node version: [e.g., 16.14.0]
- Deployment: [Docker/Manual/Cloud]

## Description
[Clear description of the issue]

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Error Messages
```
[Paste any error messages]
```

## Logs
```
[Relevant log entries]
```

## Screenshots
[If applicable]

## Attempted Solutions
[What you've tried]
```

### Quick Fixes Checklist

Before seeking help, try these:

- [ ] Clear browser cache and cookies
- [ ] Restart all services
- [ ] Check disk space (`df -h`)
- [ ] Check memory (`free -m`)
- [ ] Verify database connection
- [ ] Check network connectivity
- [ ] Review recent changes
- [ ] Check for system updates
- [ ] Verify file permissions
- [ ] Test in incognito/private mode

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Emergency Hotline**: +1-555-911-CALC (24/7 for critical production issues)

For development setup, see the [Developer Guide](DEVELOPER_GUIDE.md).  
For deployment, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).