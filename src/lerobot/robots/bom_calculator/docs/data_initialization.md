# BOM Calculator - Data Initialization & Implementation Summary

## Implementation Summary

### Architecture Overview
```
src/lerobot/robots/bom_calculator/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── database.py          # Database manager
│   ├── models.py            # SQLAlchemy models
│   ├── services/
│   │   ├── bom_service.py
│   │   ├── assembly_calculator.py
│   │   ├── inventory_service.py
│   │   └── order_service.py
│   ├── api/
│   │   ├── inventory.py     # Inventory endpoints
│   │   ├── assembly.py      # Assembly endpoints
│   │   ├── orders.py        # Order endpoints
│   │   └── bom.py          # BOM endpoints
│   └── data/
│       ├── initial_boms.json
│       └── seed_inventory.json
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── InventoryTab.tsx
│   │   │   ├── AssemblyTab.tsx
│   │   │   ├── OrdersTab.tsx
│   │   │   └── TouchComponents.tsx
│   │   ├── services/
│   │   │   └── apiClient.ts
│   │   └── styles/
│   │       └── tablet.css
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── requirements.md
│   ├── domain_model.md
│   ├── pseudocode_backend.md
│   ├── pseudocode_frontend.md
│   └── data_initialization.md
└── README.md
```

## Initial Data - Robot BOMs

### SO-ARM100 (Leader + Follower Arm Set)

```json
{
  "model_id": "so-arm100",
  "name": "SO-ARM100",
  "description": "Complete arm set with 1 leader and 1 follower",
  "version": "1.0",
  "documentation_url": "https://github.com/TheRobotStudio/SO-ARM100",
  "parts": [
    {
      "part_id": "sts3215_12v_360",
      "name": "STS3215 12V 360° Servo",
      "category": "SERVO",
      "description": "High-torque servo for follower arm",
      "unit_cost": 45.00,
      "supplier": "Feetech",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "sts3215_5v_147",
      "name": "STS3215 5V 1/147 Gear Servo",
      "category": "SERVO",
      "description": "Precision servo for leader arm",
      "unit_cost": 48.00,
      "supplier": "Feetech",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "sts3215_5v_191",
      "name": "STS3215 5V 1/191 Gear Servo",
      "category": "SERVO",
      "description": "Precision servo for leader arm",
      "unit_cost": 48.00,
      "supplier": "Feetech",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "sts3215_5v_345",
      "name": "STS3215 5V 1/345 Gear Servo",
      "category": "SERVO",
      "description": "High-precision servo for leader arm",
      "unit_cost": 52.00,
      "supplier": "Feetech",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "bus_servo_adapter",
      "name": "Bus Servo Adapter Board",
      "category": "ELECTRONICS",
      "description": "Controller for servo communication",
      "unit_cost": 12.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "usb_a_to_c_cable",
      "name": "USB-A to USB-C Cable",
      "category": "ELECTRONICS",
      "description": "1m data cable",
      "unit_cost": 8.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "power_supply_5v_5a",
      "name": "5V 5A Power Supply",
      "category": "POWER",
      "description": "Power supply for leader arm",
      "unit_cost": 15.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "power_supply_12v_5a",
      "name": "12V 5A Power Supply",
      "category": "POWER",
      "description": "Power supply for follower arm",
      "unit_cost": 18.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "m2x6_screw",
      "name": "M2x6mm Screw",
      "category": "FASTENER",
      "description": "Small mounting screw",
      "unit_cost": 0.02,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "m3x6_screw",
      "name": "M3x6mm Screw",
      "category": "FASTENER",
      "description": "Standard mounting screw",
      "unit_cost": 0.03,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "assembly_clamp",
      "name": "Assembly Clamp",
      "category": "MECHANICAL",
      "description": "Clamp for assembly",
      "unit_cost": 5.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "precision_screwdriver_set",
      "name": "Precision Screwdriver Set",
      "category": "MECHANICAL",
      "description": "Tool for assembly",
      "unit_cost": 25.00,
      "supplier": "iFixit",
      "minimum_order_quantity": 1
    }
  ],
  "bom_items": [
    {"part_id": "sts3215_12v_360", "quantity": 6},
    {"part_id": "sts3215_5v_147", "quantity": 3},
    {"part_id": "sts3215_5v_191", "quantity": 2},
    {"part_id": "sts3215_5v_345", "quantity": 1},
    {"part_id": "bus_servo_adapter", "quantity": 2},
    {"part_id": "usb_a_to_c_cable", "quantity": 2},
    {"part_id": "power_supply_5v_5a", "quantity": 1},
    {"part_id": "power_supply_12v_5a", "quantity": 1},
    {"part_id": "m2x6_screw", "quantity": 48},
    {"part_id": "m3x6_screw", "quantity": 24},
    {"part_id": "assembly_clamp", "quantity": 2},
    {"part_id": "precision_screwdriver_set", "quantity": 1}
  ]
}
```

### LeKiwi (Mobile Manipulator)

```json
{
  "model_id": "lekiwi",
  "name": "LeKiwi",
  "description": "Mobile manipulator with SO-ARM100 and omnidirectional base",
  "version": "1.0",
  "documentation_url": "https://github.com/SIGRobotics-UIUC/LeKiwi",
  "parent_model_id": "so-arm100",
  "parts": [
    {
      "part_id": "raspberry_pi_5",
      "name": "Raspberry Pi 5",
      "category": "ELECTRONICS",
      "description": "Main compute unit",
      "unit_cost": 80.00,
      "supplier": "Raspberry Pi Foundation",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "omni_wheel",
      "name": "Omni Wheel",
      "category": "MECHANICAL",
      "description": "Omnidirectional wheel",
      "unit_cost": 15.00,
      "supplier": "Generic",
      "minimum_order_quantity": 3
    },
    {
      "part_id": "pi_case",
      "name": "Raspberry Pi Case",
      "category": "STRUCTURAL",
      "description": "Protective case for Pi",
      "unit_cost": 12.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "m3x12_screw",
      "name": "M3x12mm Screw",
      "category": "FASTENER",
      "description": "Medium length screw",
      "unit_cost": 0.04,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "m3x16_screw",
      "name": "M3x16mm Screw",
      "category": "FASTENER",
      "description": "Long screw",
      "unit_cost": 0.05,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "m3x20_screw",
      "name": "M3x20mm Screw",
      "category": "FASTENER",
      "description": "Extra long screw",
      "unit_cost": 0.06,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "m4x18_screw",
      "name": "M4x18mm Screw",
      "category": "FASTENER",
      "description": "Heavy duty screw",
      "unit_cost": 0.08,
      "supplier": "McMaster-Carr",
      "minimum_order_quantity": 100
    },
    {
      "part_id": "base_plate_set",
      "name": "3D Printed Base Plates",
      "category": "STRUCTURAL",
      "description": "Set of base mounting plates",
      "unit_cost": 45.00,
      "supplier": "Custom 3D Print",
      "minimum_order_quantity": 1
    }
  ],
  "bom_items": [
    {"sub_model_id": "so-arm100", "quantity": 1},
    {"part_id": "sts3215_12v_360", "quantity": 3},
    {"part_id": "raspberry_pi_5", "quantity": 1},
    {"part_id": "omni_wheel", "quantity": 3},
    {"part_id": "pi_case", "quantity": 1},
    {"part_id": "m3x12_screw", "quantity": 12},
    {"part_id": "m3x16_screw", "quantity": 21},
    {"part_id": "m3x20_screw", "quantity": 4},
    {"part_id": "m4x18_screw", "quantity": 27},
    {"part_id": "base_plate_set", "quantity": 1},
    {"part_id": "bus_servo_adapter", "quantity": 1},
    {"part_id": "power_supply_12v_5a", "quantity": 1}
  ]
}
```

### XLERobot (Dual-Arm Mobile Robot)

```json
{
  "model_id": "xlerobot",
  "name": "XLERobot",
  "description": "Dual-arm mobile robot with LeKiwi base and additional SO-ARM100",
  "version": "1.0",
  "documentation_url": "https://xlerobot.readthedocs.io",
  "parent_model_id": "lekiwi",
  "parts": [
    {
      "part_id": "ikea_raskog_cart",
      "name": "IKEA RÅSKOG Cart",
      "category": "STRUCTURAL",
      "description": "Mobile cart base",
      "unit_cost": 49.99,
      "supplier": "IKEA",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "anker_300wh_battery",
      "name": "Anker 300Wh Battery",
      "category": "POWER",
      "description": "Portable power station",
      "unit_cost": 299.00,
      "supplier": "Anker",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "usbc_to_usbc_cable",
      "name": "USB-C to USB-C Cable",
      "category": "ELECTRONICS",
      "description": "1m power delivery cable",
      "unit_cost": 12.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "wrist_rgb_camera",
      "name": "Wrist RGB Camera",
      "category": "SENSOR",
      "description": "RGB camera for wrist vision",
      "unit_cost": 45.00,
      "supplier": "Generic",
      "minimum_order_quantity": 1
    },
    {
      "part_id": "head_depth_camera",
      "name": "Head Depth Camera",
      "category": "SENSOR",
      "description": "Depth camera for 3D vision",
      "unit_cost": 125.00,
      "supplier": "Intel RealSense",
      "minimum_order_quantity": 1
    }
  ],
  "bom_items": [
    {"sub_model_id": "lekiwi", "quantity": 1},
    {"sub_model_id": "so-arm100", "quantity": 1},
    {"part_id": "sts3215_12v_360", "quantity": 2},
    {"part_id": "ikea_raskog_cart", "quantity": 1},
    {"part_id": "anker_300wh_battery", "quantity": 1},
    {"part_id": "usbc_to_usbc_cable", "quantity": 3},
    {"part_id": "wrist_rgb_camera", "quantity": 2},
    {"part_id": "head_depth_camera", "quantity": 1}
  ]
}
```

## Initial Inventory Seed Data

```json
{
  "inventory": [
    {"part_id": "sts3215_12v_360", "quantity_loose": 25, "reorder_point": 10},
    {"part_id": "sts3215_5v_147", "quantity_loose": 10, "reorder_point": 5},
    {"part_id": "sts3215_5v_191", "quantity_loose": 8, "reorder_point": 4},
    {"part_id": "sts3215_5v_345", "quantity_loose": 5, "reorder_point": 2},
    {"part_id": "bus_servo_adapter", "quantity_loose": 12, "reorder_point": 4},
    {"part_id": "usb_a_to_c_cable", "quantity_loose": 15, "reorder_point": 5},
    {"part_id": "power_supply_5v_5a", "quantity_loose": 6, "reorder_point": 2},
    {"part_id": "power_supply_12v_5a", "quantity_loose": 8, "reorder_point": 3},
    {"part_id": "m2x6_screw", "quantity_loose": 500, "reorder_point": 200},
    {"part_id": "m3x6_screw", "quantity_loose": 400, "reorder_point": 150},
    {"part_id": "m3x12_screw", "quantity_loose": 200, "reorder_point": 100},
    {"part_id": "m3x16_screw", "quantity_loose": 150, "reorder_point": 75},
    {"part_id": "m3x20_screw", "quantity_loose": 100, "reorder_point": 50},
    {"part_id": "m4x18_screw", "quantity_loose": 200, "reorder_point": 100},
    {"part_id": "assembly_clamp", "quantity_loose": 8, "reorder_point": 2},
    {"part_id": "precision_screwdriver_set", "quantity_loose": 3, "reorder_point": 1},
    {"part_id": "raspberry_pi_5", "quantity_loose": 2, "reorder_point": 1},
    {"part_id": "omni_wheel", "quantity_loose": 6, "reorder_point": 3},
    {"part_id": "pi_case", "quantity_loose": 2, "reorder_point": 1},
    {"part_id": "base_plate_set", "quantity_loose": 1, "reorder_point": 1},
    {"part_id": "ikea_raskog_cart", "quantity_loose": 0, "reorder_point": 1},
    {"part_id": "anker_300wh_battery", "quantity_loose": 0, "reorder_point": 1},
    {"part_id": "usbc_to_usbc_cable", "quantity_loose": 3, "reorder_point": 2},
    {"part_id": "wrist_rgb_camera", "quantity_loose": 1, "reorder_point": 2},
    {"part_id": "head_depth_camera", "quantity_loose": 0, "reorder_point": 1}
  ]
}
```

## Database Initialization Script

```python
# src/lerobot/robots/bom_calculator/backend/init_db.py

import json
from pathlib import Path
from database import DatabaseManager
from services.bom_service import BOMService

def initialize_database():
    """
    Initialize database with robot models and initial inventory
    
    TEST: Database initialized with all models
    TEST: Inventory seeded correctly
    TEST: BOM relationships established
    """
    
    db = DatabaseManager("bom_calculator.db")
    bom_service = BOMService(db)
    
    data_dir = Path(__file__).parent / "data"
    
    # Load and import BOMs for each robot model
    robot_models = ["so-arm100", "lekiwi", "xlerobot"]
    
    for model_name in robot_models:
        with open(data_dir / f"{model_name}_bom.json", "r") as f:
            bom_data = json.load(f)
            
        success = bom_service.import_bom_from_json(bom_data, model_name)
        if success:
            print(f"✓ Imported BOM for {model_name}")
        else:
            print(f"✗ Failed to import BOM for {model_name}")
    
    # Load and seed initial inventory
    with open(data_dir / "seed_inventory.json", "r") as f:
        inventory_data = json.load(f)
    
    for item in inventory_data["inventory"]:
        db.update_inventory(
            part_id=item["part_id"],
            quantity_change=item["quantity_loose"],
            change_type="loose"
        )
        
        # Set reorder point
        inventory = db.get_inventory(item["part_id"])
        inventory.reorder_point = item["reorder_point"]
        db.save_inventory(inventory)
    
    print("✓ Database initialization complete")
    
    # Verify by calculating buildable quantities
    for model_name in robot_models:
        from services.assembly_calculator import AssemblyCalculator
        calculator = AssemblyCalculator(db, bom_service)
        result = calculator.calculate_buildable_quantity(model_name)
        print(f"  {model_name}: Can build {result.max_quantity} units")

if __name__ == "__main__":
    initialize_database()
```

## Key Implementation Notes

### 1. Hierarchical BOM Support
- LeKiwi includes SO-ARM100 as a sub-assembly
- XLERobot includes LeKiwi (which includes SO-ARM100)
- BOM expansion must handle recursive relationships
- Circular dependency detection is critical

### 2. Shared Parts Management
- STS3215 12V servos are used across all models
- Fasteners are shared across models
- Power supplies and adapters are reused
- Inventory calculations must account for competition

### 3. Touch Optimization
- All inputs use large touch targets (minimum 44x44px)
- Number inputs have increment/decrement buttons
- Swipe gestures for quick actions
- Haptic feedback for confirmations

### 4. Offline Capability
- API requests queued when offline
- Local state management with optimistic updates
- Sync when connection restored
- Critical data cached in localStorage

### 5. Performance Optimization
- BOM calculations cached
- Debounced inventory updates
- Lazy loading for large lists
- Virtual scrolling for inventory table

### 6. Testing Strategy
- Unit tests for all calculators
- Integration tests for API endpoints
- E2E tests for critical workflows
- Performance tests for large inventories

## Deployment Configuration

### Backend (FastAPI)
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BOM Calculator API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend build
app.mount("/", StaticFiles(directory="../frontend/build", html=True))
```

### Frontend (React)
```json
// package.json
{
  "name": "bom-calculator-frontend",
  "version": "1.0.0",
  "proxy": "http://localhost:8000",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Build frontend
FROM node:16 as frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Copy built frontend to backend
COPY --from=frontend-build /frontend/build /app/frontend/build

# Copy backend code
COPY backend/ /app/backend/

# Initialize database
RUN python backend/init_db.py

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Next Steps for Implementation

1. **Phase 1: Backend Core (Week 1)**
   - Set up FastAPI project structure
   - Implement database models with SQLAlchemy
   - Create BOM service with expansion logic
   - Build assembly calculator
   - Develop inventory management

2. **Phase 2: API Layer (Week 2)**
   - Implement all REST endpoints
   - Add input validation
   - Create error handling
   - Set up CORS configuration
   - Add API documentation (Swagger)

3. **Phase 3: Frontend Core (Week 3)**
   - Initialize React/TypeScript project
   - Build component architecture
   - Implement state management
   - Create API client with offline support
   - Develop touch-optimized components

4. **Phase 4: Integration (Week 4)**
   - Connect frontend to backend
   - Implement real-time updates
   - Add comprehensive error handling
   - Optimize performance
   - Complete E2E testing

5. **Phase 5: Polish & Deploy (Week 5)**
   - Finalize UI/UX
   - Add comprehensive documentation
   - Performance optimization
   - Security audit
   - Production deployment