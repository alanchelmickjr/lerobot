# BOM Calculator Developer Guide

Complete developer documentation for the Bill of Materials Calculator application.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Database Schema](#database-schema)
7. [API Development](#api-development)
8. [Component Library](#component-library)
9. [State Management](#state-management)
10. [Testing Strategy](#testing-strategy)
11. [Adding New Robot Models](#adding-new-robot-models)
12. [Performance Optimization](#performance-optimization)
13. [Security Implementation](#security-implementation)
14. [Contributing Guidelines](#contributing-guidelines)
15. [Code Standards](#code-standards)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   React PWA │  │   Service   │  │  IndexedDB  │        │
│  │   (Tablet)  │  │   Worker    │  │   (Cache)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ├── HTTP/WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FastAPI   │  │  WebSocket  │  │    Redis    │        │
│  │   REST API  │  │   Server    │  │    Cache    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   BOM    │  │Inventory │  │ Assembly │  │  Order   │   │
│  │ Service  │  │ Service  │  │Calculator│  │ Service  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │  SQLite/PostgreSQL  │  │   File Storage     │          │
│  │     Database        │  │   (Exports/Docs)   │          │
│  └─────────────────────┘  └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Frontend | React | 18+ | UI Framework |
| Frontend | TypeScript | 5.0+ | Type Safety |
| Frontend | Material-UI | 5.14+ | Component Library |
| Frontend | Zustand | 4.4+ | State Management |
| Frontend | React Query | 3.39+ | Server State |
| Frontend | Vite | 4.5+ | Build Tool |
| Backend | Python | 3.9+ | Runtime |
| Backend | FastAPI | 0.100+ | Web Framework |
| Backend | SQLAlchemy | 2.0+ | ORM |
| Backend | Pydantic | 2.0+ | Data Validation |
| Backend | Redis | 7.0+ | Caching |
| Database | SQLite/PostgreSQL | 3.40+/15+ | Data Storage |
| Testing | pytest/Jest | 7.4+/29+ | Test Frameworks |
| Tools | Docker | 24+ | Containerization |

---

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Git
- Docker (optional)
- VS Code or preferred IDE

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/lerobot.git
cd lerobot/src/lerobot/robots/bom_calculator

# Option 1: Automatic setup
python bom_calculator.py --mode development

# Option 2: Manual setup
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m init_db

# Frontend
cd ../frontend
npm install
```

### Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Key environment variables:

```env
# Backend
DATABASE_URL=sqlite:///./bom_calculator.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
REDIS_URL=redis://localhost:6379
DEBUG=true

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENV=development
```

### Running Development Servers

```bash
# Backend (with hot reload)
cd backend
uvicorn main:app --reload --port 8000

# Frontend (with hot reload)
cd frontend
npm run dev

# Or use the launcher
python bom_calculator.py --mode development
```

---

## Project Structure

### Complete Directory Structure

```
bom_calculator/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── init_db.py              # Database initialization
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── inventory.py        # Inventory endpoints
│   │   ├── assembly.py         # Assembly calculator
│   │   ├── orders.py           # Order management
│   │   ├── parts.py            # Parts CRUD
│   │   ├── robots.py           # Robot models
│   │   └── websocket.py        # WebSocket handlers
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── bom_service.py      # BOM expansion logic
│   │   ├── inventory_service.py # Inventory management
│   │   ├── assembly_service.py  # Assembly calculations
│   │   └── order_service.py     # Order generation
│   │
│   ├── data/                   # Initial data
│   │   ├── boms/               # BOM JSON files
│   │   └── seed.json           # Seed data
│   │
│   └── tests/                  # Backend tests
│       ├── unit/
│       └── integration/
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   ├── App.tsx             # Main application
│   │   ├── types.ts            # TypeScript types
│   │   │
│   │   ├── components/         # Reusable components
│   │   │   ├── common/         # Shared components
│   │   │   ├── inventory/      # Inventory components
│   │   │   ├── assembly/       # Assembly components
│   │   │   └── orders/         # Order components
│   │   │
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Inventory.tsx
│   │   │   ├── Assembly.tsx
│   │   │   └── Orders.tsx
│   │   │
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useInventory.ts
│   │   │   ├── useAssembly.ts
│   │   │   └── useWebSocket.ts
│   │   │
│   │   ├── services/           # API clients
│   │   │   ├── api.ts          # Base API client
│   │   │   └── websocket.ts    # WebSocket client
│   │   │
│   │   ├── store/              # State management
│   │   │   └── store.ts        # Zustand store
│   │   │
│   │   └── styles/             # Styling
│   │       ├── theme.ts        # MUI theme
│   │       └── global.css      # Global styles
│   │
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   └── vite.config.ts          # Vite configuration
│
├── docs/                       # Documentation
├── docker/                     # Docker files
├── scripts/                    # Utility scripts
├── .env.example               # Environment template
├── docker-compose.yml         # Docker compose
├── bom_calculator.py          # Main launcher
└── README.md                  # Project overview
```

---

## Backend Development

### FastAPI Application Structure

```python
# main.py - Application initialization
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await init_database()
    yield
    # Shutdown
    await db_manager.close()

app = FastAPI(
    title="BOM Calculator API",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Models

```python
# models.py - SQLAlchemy models
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Part(Base):
    __tablename__ = "parts"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit_cost = Column(Float, default=0.0)
    supplier = Column(String)
    lead_time_days = Column(Integer, default=7)
    
    # Relationships
    inventory = relationship("Inventory", back_populates="part", uselist=False)
    bom_items = relationship("BOMItem", back_populates="part")

class RobotModel(Base):
    __tablename__ = "robot_models"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    
    # Relationships
    bom = relationship("BOM", back_populates="robot_model", uselist=False)

class BOM(Base):
    __tablename__ = "boms"
    
    id = Column(Integer, primary_key=True)
    robot_model_id = Column(String, ForeignKey("robot_models.id"))
    version = Column(String, default="1.0.0")
    
    # Relationships
    robot_model = relationship("RobotModel", back_populates="bom")
    items = relationship("BOMItem", back_populates="bom")

class BOMItem(Base):
    __tablename__ = "bom_items"
    
    id = Column(Integer, primary_key=True)
    bom_id = Column(Integer, ForeignKey("boms.id"))
    part_id = Column(String, ForeignKey("parts.id"))
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    bom = relationship("BOM", back_populates="items")
    part = relationship("Part", back_populates="bom_items")

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(String, ForeignKey("parts.id"), unique=True)
    quantity_loose = Column(Integer, default=0)
    quantity_assembled = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    part = relationship("Part", back_populates="inventory")
```

### Service Layer Implementation

```python
# services/assembly_service.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models import BOM, Inventory, Part

class AssemblyService:
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_buildable(self, robot_model_id: str) -> Dict:
        """Calculate maximum buildable units for a robot model"""
        # Get BOM for robot model
        bom = self.db.query(BOM).filter(
            BOM.robot_model_id == robot_model_id
        ).first()
        
        if not bom:
            raise ValueError(f"BOM not found for {robot_model_id}")
        
        # Calculate buildable quantity
        max_buildable = float('inf')
        bottlenecks = []
        
        for item in bom.items:
            inventory = self.db.query(Inventory).filter(
                Inventory.part_id == item.part_id
            ).first()
            
            if inventory:
                available = inventory.quantity_loose
                required = item.quantity
                possible = available // required if required > 0 else 0
                
                if possible < max_buildable:
                    max_buildable = possible
                    
                if available < required:
                    bottlenecks.append({
                        "part_id": item.part_id,
                        "part_name": item.part.name,
                        "required": required,
                        "available": available,
                        "shortage": required - available
                    })
        
        return {
            "robot_model_id": robot_model_id,
            "max_buildable": max_buildable if max_buildable != float('inf') else 0,
            "bottlenecks": bottlenecks,
            "status": "ready" if max_buildable > 0 else "insufficient"
        }
    
    async def reserve_parts(self, robot_model_id: str, quantity: int) -> Dict:
        """Reserve parts for assembly"""
        # Implementation here
        pass
```

### API Endpoint Development

```python
# api/assembly.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import BuildableResponse, AssemblyRequest
from ..services import AssemblyService

router = APIRouter()

@router.get("/calculate/{robot_model_id}", response_model=BuildableResponse)
async def calculate_buildable(
    robot_model_id: str,
    db: Session = Depends(get_db)
):
    """Calculate maximum buildable units for a robot model"""
    service = AssemblyService(db)
    try:
        result = await service.calculate_buildable(robot_model_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/reserve")
async def reserve_parts(
    request: AssemblyRequest,
    db: Session = Depends(get_db)
):
    """Reserve parts for planned assembly"""
    service = AssemblyService(db)
    result = await service.reserve_parts(
        request.robot_model_id,
        request.quantity
    )
    return result
```

---

## Frontend Development

### React Component Architecture

```typescript
// components/inventory/InventoryGrid.tsx
import React, { useState, useCallback } from 'react';
import { Grid, Card, CardContent, Typography, IconButton } from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { useInventory } from '../../hooks/useInventory';
import { InventoryItem } from '../../types';
import TouchNumberInput from '../common/TouchNumberInput';

interface InventoryGridProps {
  category?: string;
  onEdit: (item: InventoryItem) => void;
}

const InventoryGrid: React.FC<InventoryGridProps> = ({ category, onEdit }) => {
  const { items, updateQuantity, isLoading } = useInventory(category);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const handleQuantityChange = useCallback(async (itemId: string, newQuantity: number) => {
    await updateQuantity(itemId, newQuantity);
    setEditingId(null);
  }, [updateQuantity]);
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <Grid container spacing={2}>
      {items.map((item) => (
        <Grid item xs={12} sm={6} md={4} key={item.id}>
          <Card 
            sx={{ 
              height: '100%',
              borderLeft: `4px solid ${getStockColor(item)}`,
            }}
          >
            <CardContent>
              <Typography variant="h6">{item.name}</Typography>
              <Typography color="text.secondary" gutterBottom>
                {item.category}
              </Typography>
              
              {editingId === item.id ? (
                <TouchNumberInput
                  value={item.quantity}
                  onChange={(val) => handleQuantityChange(item.id, val)}
                  min={0}
                  max={9999}
                  label="Quantity"
                />
              ) : (
                <Typography variant="h4" onClick={() => setEditingId(item.id)}>
                  {item.quantity}
                </Typography>
              )}
              
              <Typography variant="caption" display="block">
                Reorder: {item.reorderPoint}
              </Typography>
              
              <IconButton onClick={() => onEdit(item)}>
                <Edit />
              </IconButton>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

function getStockColor(item: InventoryItem): string {
  if (item.quantity === 0) return '#f44336'; // Red
  if (item.quantity < item.reorderPoint) return '#ff9800'; // Orange
  return '#4caf50'; // Green
}

export default InventoryGrid;
```

### Custom Hooks

```typescript
// hooks/useInventory.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../services/api';
import { InventoryItem } from '../types';

export function useInventory(category?: string) {
  const queryClient = useQueryClient();
  
  // Fetch inventory
  const { data: items = [], isLoading, error } = useQuery(
    ['inventory', category],
    () => api.getInventory(category),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      staleTime: 10000,
    }
  );
  
  // Update quantity mutation
  const updateMutation = useMutation(
    ({ itemId, quantity }: { itemId: string; quantity: number }) =>
      api.updateInventory(itemId, quantity),
    {
      onMutate: async ({ itemId, quantity }) => {
        // Optimistic update
        await queryClient.cancelQueries(['inventory']);
        const previousItems = queryClient.getQueryData<InventoryItem[]>(['inventory']);
        
        queryClient.setQueryData<InventoryItem[]>(['inventory'], (old) =>
          old?.map((item) =>
            item.id === itemId ? { ...item, quantity } : item
          ) || []
        );
        
        return { previousItems };
      },
      onError: (err, variables, context) => {
        // Rollback on error
        if (context?.previousItems) {
          queryClient.setQueryData(['inventory'], context.previousItems);
        }
      },
      onSettled: () => {
        queryClient.invalidateQueries(['inventory']);
      },
    }
  );
  
  return {
    items,
    isLoading,
    error,
    updateQuantity: (itemId: string, quantity: number) =>
      updateMutation.mutate({ itemId, quantity }),
  };
}
```

### State Management with Zustand

```typescript
// store/store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface BOMStore {
  // State
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  selectedRobotModel: string | null;
  inventoryFilter: {
    category: string | null;
    lowStockOnly: boolean;
    searchTerm: string;
  };
  
  // Actions
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  selectRobotModel: (modelId: string | null) => void;
  updateInventoryFilter: (filter: Partial<BOMStore['inventoryFilter']>) => void;
  resetFilters: () => void;
}

export const useBOMStore = create<BOMStore>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        theme: 'light',
        sidebarOpen: true,
        selectedRobotModel: null,
        inventoryFilter: {
          category: null,
          lowStockOnly: false,
          searchTerm: '',
        },
        
        // Actions
        setTheme: (theme) => set({ theme }),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        selectRobotModel: (modelId) => set({ selectedRobotModel: modelId }),
        updateInventoryFilter: (filter) =>
          set((state) => ({
            inventoryFilter: { ...state.inventoryFilter, ...filter },
          })),
        resetFilters: () =>
          set({
            inventoryFilter: {
              category: null,
              lowStockOnly: false,
              searchTerm: '',
            },
          }),
      }),
      {
        name: 'bom-calculator-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    )
  )
);
```

---

## Database Schema

### Entity Relationship Diagram

```sql
-- Parts table
CREATE TABLE parts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(10, 2) DEFAULT 0.00,
    supplier VARCHAR(100),
    lead_time_days INTEGER DEFAULT 7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Robot models table
CREATE TABLE robot_models (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- BOMs table
CREATE TABLE boms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    robot_model_id VARCHAR(50) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (robot_model_id) REFERENCES robot_models(id)
);

-- BOM items table
CREATE TABLE bom_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bom_id INTEGER NOT NULL,
    part_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (bom_id) REFERENCES boms(id),
    FOREIGN KEY (part_id) REFERENCES parts(id),
    UNIQUE(bom_id, part_id)
);

-- Inventory table
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id VARCHAR(50) UNIQUE NOT NULL,
    quantity_loose INTEGER DEFAULT 0,
    quantity_assembled INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 10,
    location VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    total_cost DECIMAL(10, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    part_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (part_id) REFERENCES parts(id)
);

-- Audit log table
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    user_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_parts_category ON parts(category);
CREATE INDEX idx_inventory_part_id ON inventory(part_id);
CREATE INDEX idx_bom_items_part_id ON bom_items(part_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
```

---

## API Development

### RESTful API Design Principles

1. **Resource-Based URLs**
   - `/api/v1/parts` - Parts collection
   - `/api/v1/parts/{id}` - Specific part
   - `/api/v1/inventory` - Inventory items
   - `/api/v1/assembly/calculate` - Assembly calculations

2. **HTTP Methods**
   - GET: Retrieve resources
   - POST: Create new resources
   - PUT/PATCH: Update resources
   - DELETE: Remove resources

3. **Status Codes**
   - 200: Success
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 404: Not Found
   - 500: Server Error

### API Versioning Strategy

```python
# config.py
API_V1_PREFIX = "/api/v1"

# main.py
app.include_router(
    inventory_router,
    prefix=f"{API_V1_PREFIX}/inventory",
    tags=["inventory-v1"]
)
```

### Request/Response Schemas

```python
# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PartBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    unit_cost: float = Field(0.0, ge=0)
    supplier: Optional[str] = None
    lead_time_days: int = Field(7, ge=0)

class PartCreate(PartBase):
    id: str = Field(..., min_length=1, max_length=50)

class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    lead_time_days: Optional[int] = None

class PartResponse(PartBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)
    location: Optional[str] = None

class BuildableRequest(BaseModel):
    robot_model_id: str
    target_quantity: Optional[int] = None

class BuildableResponse(BaseModel):
    robot_model_id: str
    max_buildable: int
    bottlenecks: List[dict]
    status: str
```

---

## Testing Strategy

### Backend Testing

```python
# tests/unit/test_assembly_service.py
import pytest
from unittest.mock import Mock, MagicMock
from services.assembly_service import AssemblyService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def assembly_service(mock_db):
    return AssemblyService(mock_db)

class TestAssemblyService:
    @pytest.mark.asyncio
    async def test_calculate_buildable_sufficient_inventory(
        self, assembly_service, mock_db
    ):
        # Arrange
        mock_bom = Mock()
        mock_bom.items = [
            Mock(part_id="servo_12v", quantity=2, part=Mock(name="Servo 12V")),
            Mock(part_id="frame", quantity=1, part=Mock(name="Frame"))
        ]
        
        mock_db.query().filter().first.return_value = mock_bom
        mock_db.query().filter().first.side_effect = [
            Mock(quantity_loose=10),  # 10 servos available
            Mock(quantity_loose=5)    # 5 frames available
        ]
        
        # Act
        result = await assembly_service.calculate_buildable("so-arm100")
        
        # Assert
        assert result["max_buildable"] == 5  # Limited by servos (10/2)
        assert result["status"] == "ready"
        assert len(result["bottlenecks"]) == 0

    @pytest.mark.asyncio
    async def test_calculate_buildable_with_bottlenecks(
        self, assembly_service, mock_db
    ):
        # Test implementation here
        pass
```

### Frontend Testing

```typescript
// tests/components/InventoryGrid.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import InventoryGrid from '../../src/components/inventory/InventoryGrid';
import { api } from '../../src/services/api';

jest.mock('../../src/services/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('InventoryGrid', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('should display inventory items', async () => {
    const mockItems = [
      { id: '1', name: 'Servo', category: 'Motors', quantity: 10, reorderPoint: 5 },
      { id: '2', name: 'Frame', category: 'Mechanical', quantity: 3, reorderPoint: 2 },
    ];
    
    (api.getInventory as jest.Mock).mockResolvedValue(mockItems);
    
    render(<InventoryGrid />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText('Servo')).toBeInTheDocument();
      expect(screen.getByText('Frame')).toBeInTheDocument();
    });
  });
  
  it('should update quantity on edit', async () => {
    // Test implementation
  });
});
```

### Integration Testing

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestInventoryAPI:
    def test_get_inventory(self):
        response = client.get("/api/v1/inventory")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_update_inventory(self):
        data = {"quantity": 50}
        response = client.patch("/api/v1/inventory/servo_12v", json=data)
        assert response.status_code == 200
        assert response.json()["quantity"] == 50
```

### End-to-End Testing

```javascript
// test_e2e.js
const { chromium } = require('playwright');

describe('BOM Calculator E2E', () => {
  let browser;
  let page;
  
  beforeAll(async () => {
    browser = await chromium.launch();
    page = await browser.newPage();
  });
  
  afterAll(async () => {
    await browser.close();
  });
  
  test('Complete inventory update workflow', async () => {
    // Navigate to inventory
    await page.goto('http://localhost:3000/inventory');
    
    // Search for part
    await page.fill('[placeholder="Search parts..."]', 'servo');
    
    // Click on first result
    await page.click('.inventory-card:first-child');
    
    // Update quantity
    await page.click('.quantity-input');
    await page.fill('.quantity-input', '25');
    await page.click('button:has-text("Save")');
    
    // Verify update
    await page.waitForSelector('.success-message');
    const message = await page.textContent('.success-message');
    expect(message).toBe('Inventory updated successfully');
  });
});
```

---

## Adding New Robot Models

### Step-by-Step Guide

#### 1. Define the BOM Data

Create a JSON file in `backend/data/boms/`:

```json
{
  "model_id": "new_robot",
  "name": "New Robot Model",
  "description": "Description of the new robot",
  "image_url": "/images/new_robot.jpg",
  "bom": [
    {
      "part_id": "servo_12v",
      "quantity": 4,
      "notes": "Main arm servos"
    },
    {
      "part_id": "raspberry_pi_5",
      "quantity": 1,
      "notes": "Main controller"
    }
  ]
}
```

#### 2. Update Database

```python
# scripts/add_robot_model.py
import json
from backend.database import SessionLocal
from backend.models import RobotModel, BOM, BOMItem

def add_robot_model(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    db = SessionLocal()
    
    # Create robot model
    robot = RobotModel(
        id=data['model_id'],
        name=data['name'],
        description=data['description'],
        image_url=data['image_url']
    )
    db.add(robot)
    
    # Create BOM
    bom = BOM(robot_model_id=data['model_id'])
    db.add(bom)
    db.flush()
    
    # Add BOM items
    for item in data['bom']:
        bom_item = BOMItem(
            bom_id=bom.id,
            part_id=item['part_id'],
            quantity=item['quantity'],
            notes=item.get('notes')
        )
        db.add(bom_item)
    
    db.commit()
    print(f"Added robot model: {data['name']}")

if __name__ == "__main__":
    add_robot_model('backend/data/boms/new_robot.json')
```

#### 3. Update Frontend

Add robot to the models list:

```typescript
// src/constants/robots.ts
export const ROBOT_MODELS = [
  {
    id: 'so-arm100',
    name: 'SO-ARM100',
    image: '/images/so-arm100.jpg',
  },
  {
    id: 'lekiwi',
    name: 'LeKiwi',
    image: '/images/lekiwi.jpg',
  },
  {
    id: 'xlerobot',
    name: 'XLERobot',
    image: '/images/xlerobot.jpg',
  },
  // Add new robot
  {
    id: 'new_robot',
    name: 'New Robot Model',
    image: '/images/new_robot.jpg',
  },
];
```

#### 4. Test the Addition

```bash
# Run tests
pytest tests/unit/test_new_robot.py
npm test -- --testNamePattern="new robot"
```

---

## Performance Optimization

### Backend Optimization

```python
# Caching with Redis
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="bom-cache:")

@router.get("/assembly/calculate/{model_id}")
@cache(expire=300)  # Cache for 5 minutes
async def calculate_buildable(model_id: str):
    # Calculation logic
    pass
```

### Database Optimization

```python
# Query optimization with eager loading
from sqlalchemy.orm import selectinload

def get_bom_with_parts(model_id: str, db: Session):
    return db.query(BOM)\
        .options(
            selectinload(BOM.items).selectinload(BOMItem.part)
        )\
        .filter(BOM.robot_model_id == model_id)\
        .first()
```

### Frontend Optimization

```typescript
// Lazy loading components
const InventoryPage = lazy(() => import('./pages/Inventory'));
const AssemblyPage = lazy(() => import('./pages/Assembly'));

// Memoization
const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = useMemo(() => 
    processData(data), [data]
  );
  
  return <div>{/* Render */}</div>;
});

// Virtual scrolling for large lists
import { VariableSizeList } from 'react-window';

const VirtualList = ({ items }) => (
  <VariableSizeList
    height={600}
    itemCount={items.length}
    itemSize={getItemSize}
    width="100%"
  >
    {Row}
  </VariableSizeList>
);
```

---

## Security Implementation

### Authentication & Authorization

```python
# JWT implementation
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

jwt_authentication = JWTAuthentication(
    secret=SECRET_KEY,
    lifetime_seconds=3600,
)

# Protected routes
@router.post("/inventory/update")
async def update_inventory(
    current_user = Depends(current_active_user)
):
    if not current_user.has_permission("inventory.update"):
        raise HTTPException(status_code=403)
    # Update logic
```

### Input Validation

```python
# Pydantic validation
from pydantic import BaseModel, validator

class InventoryUpdate(BaseModel):
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity must be non-negative')
        if v > 99999:
            raise ValueError('Quantity exceeds maximum')
        return v
```

### SQL Injection Prevention

```python
# Use parameterized queries
from sqlalchemy import text

# Safe
result = db.execute(
    text("SELECT * FROM parts WHERE id = :part_id"),
    {"part_id": user_input}
)

# Never do this
# query = f"SELECT * FROM parts WHERE id = '{user_input}'"
```

---

## Contributing Guidelines

### Development Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/yourusername/lerobot.git
   cd lerobot
   git remote add upstream https://github.com/original/lerobot.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Write code following style guides
   - Add tests for new functionality
   - Update documentation

4. **Test Locally**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **Push & Create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Clearly describe changes
- **Tests**: Include test coverage
- **Documentation**: Update if needed
- **Screenshots**: For UI changes

### Code Review Process

1. Automated checks must pass
2. At least one reviewer approval
3. No merge conflicts
4. Documentation updated

---

## Code Standards

### Python Style Guide

```python
# Follow PEP 8
# Use Black for formatting
# Type hints required

from typing import List, Optional
from datetime import datetime

class InventoryService:
    """Service for managing inventory operations."""
    
    def __init__(self, db_session: Session) -> None:
        """Initialize inventory service.
        
        Args:
            db_session: Database session instance
        """
        self.db = db_session
    
    async def update_quantity(
        self,
        part_id: str,
        quantity: int,
        user_id: Optional[str] = None
    ) -> InventoryItem:
        """Update inventory quantity for a part.
        
        Args:
            part_id: Unique identifier of the part
            quantity: New quantity value
            user_id: Optional user ID for audit trail
            
        Returns:
            Updated inventory item
            
        Raises:
            ValueError: If part not found
            ValidationError: If quantity invalid
        """
        # Implementation
        pass
```

### TypeScript Style Guide

```typescript
// Use ESLint and Prettier
// Strict TypeScript settings
// Functional components preferred

import React, { useState, useCallback } from 'react';

interface InventoryItemProps {
  item: {
    id: string;
    name: string;
    quantity: number;
  };
  onUpdate: (id: string, quantity: number) => Promise<void>;
}

/**
 * Component for displaying and editing inventory item
 */
const InventoryItem: React.FC<InventoryItemProps> = ({ item, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [quantity, setQuantity] = useState(item.quantity);
  
  const handleSave = useCallback(async () => {
    try {
      await onUpdate(item.id, quantity);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update:', error);
    }
  }, [item.id, quantity, onUpdate]);
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};

export default InventoryItem;
```

### Git Commit Messages

Follow Conventional Commits:

```
feat: add inventory bulk update
fix: correct calculation in assembly service
docs: update API documentation
style: format code with Black
refactor: simplify database queries
test: add tests for order service
chore: update dependencies
```

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Repository**: https://github.com/yourusername/lerobot

For user documentation, see the [User Guide](USER_GUIDE.md).  
For deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).