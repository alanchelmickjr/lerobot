# BOM Calculator - Manual Setup (No BS)

## Backend Setup (Python 3.13)
```bash
cd src/lerobot/robots/bom_calculator/backend

# Install deps (use latest compatible versions for Python 3.13)
pip install fastapi uvicorn sqlalchemy aiosqlite python-dotenv
pip install pydantic pydantic-settings  # Will get v2.x automatically

# Create .env file
echo "DATABASE_URL=sqlite+aiosqlite:///./bom_calculator.db" > .env

# Initialize database
python init_db.py

# Start backend
uvicorn main:app --reload --port 8000
```

## Frontend Setup
```bash
cd src/lerobot/robots/bom_calculator/frontend

# Install deps
npm install

# Create missing components if needed
mkdir -p src/components/Layout src/components/Common

# Start frontend
npm run dev
```

## Verify
- Backend: http://localhost:8000/api/docs
- Frontend: http://localhost:3000

## Known Issues with Python 3.13
- pydantic 2.5.0 won't install (use latest v2.x instead)
- Some MUI date-picker components need date-fns v3

## Quick Fix for Missing Components
Create minimal stub files in frontend/src/components/:
- Layout/Layout.tsx - Just render `<Outlet />`
- Common/LoadingScreen.tsx - Just return `<div>Loading...</div>`

That's it. No fancy scripts, just the basics to get it running.