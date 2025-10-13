# BOM Calculator Backend

FastAPI backend for the BOM Calculator application, providing inventory management, assembly calculation, and order generation for robot manufacturing.

## Features

- **Inventory Management**: Track parts inventory with real-time updates
- **BOM Expansion**: Hierarchical BOM expansion with circular dependency detection
- **Assembly Calculation**: Calculate buildable quantities and identify bottlenecks
- **Order Generation**: Generate purchase orders based on requirements
- **Real-time Updates**: WebSocket support for live inventory changes
- **RESTful API**: Comprehensive API for all operations

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd src/lerobot/robots/bom_calculator/backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

To reset the database (drops all data):
```bash
python init_db.py --reset
```

## Running the Server

### Development Mode

```bash
uvicorn main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or using the Python script:
```bash
python main.py
```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Parts
- `GET /api/v1/parts` - List all parts
- `GET /api/v1/parts/{part_id}` - Get specific part
- `POST /api/v1/parts` - Create new part
- `PUT /api/v1/parts/{part_id}` - Update part
- `DELETE /api/v1/parts/{part_id}` - Delete part

### Robot Models
- `GET /api/v1/robots` - List all robot models
- `GET /api/v1/robots/{model_id}` - Get specific model
- `GET /api/v1/robots/{model_id}/bom` - Get BOM for model
- `GET /api/v1/robots/{model_id}/cost` - Calculate build cost
- `POST /api/v1/robots/{model_id}/bom/import` - Import BOM

### Inventory
- `GET /api/v1/inventory` - Get all inventory
- `GET /api/v1/inventory/{part_id}` - Get inventory for part
- `POST /api/v1/inventory/update` - Update inventory
- `POST /api/v1/inventory/reserve/{robot_model_id}` - Reserve parts
- `GET /api/v1/inventory/low-stock/items` - Get low stock items

### Assembly
- `GET /api/v1/assembly/calculate/{robot_model_id}` - Calculate buildable quantity
- `GET /api/v1/assembly/requirements/{robot_model_id}` - Get parts requirements
- `POST /api/v1/assembly/optimize` - Optimize build mix
- `POST /api/v1/assembly/create` - Create assembly record
- `GET /api/v1/assembly/bottlenecks` - Identify bottleneck parts

### Orders
- `POST /api/v1/orders/generate/{robot_model_id}` - Generate order sheet
- `POST /api/v1/orders/create` - Create order from sheet
- `GET /api/v1/orders` - List all orders
- `POST /api/v1/orders/{order_id}/submit` - Submit order
- `POST /api/v1/orders/{order_id}/receive` - Receive order
- `GET /api/v1/orders/reorder-suggestions` - Get reorder suggestions

### WebSocket
- `WS /ws` - WebSocket endpoint for real-time updates

## WebSocket Messages

### Client to Server
```json
{
  "type": "subscribe",
  "events": ["inventory_update", "low_stock_alert"]
}
```

### Server to Client
```json
{
  "type": "inventory_update",
  "data": {
    "part_id": "sts3215_12v_360",
    "change_type": "ADD",
    "new_quantity": 30
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Database Schema

The application uses SQLAlchemy with the following main models:

- **Part**: Individual components
- **RobotModel**: Robot configurations
- **BOMItem**: Bill of Materials items
- **Inventory**: Current stock levels
- **Assembly**: Assembly records
- **Order**: Purchase orders
- **Reservation**: Part reservations

## Initial Data

The database is initialized with three robot models:

1. **SO-ARM100**: Basic arm set (leader + follower)
2. **LeKiwi**: Mobile manipulator (includes SO-ARM100)
3. **XLERobot**: Dual-arm robot (includes LeKiwi)

## Configuration

Edit `config.py` to modify:
- Database settings
- CORS origins
- API prefix
- Secret keys

## Testing

Run the backend and use the Swagger UI to test endpoints interactively.

## Troubleshooting

### Database Issues
- Ensure SQLite is installed
- Check file permissions in the backend directory
- Try resetting the database with `python init_db.py --reset`

### Import Errors
- Ensure you're running from the backend directory
- Check that all dependencies are installed
- Verify Python version is 3.9+

### Port Already in Use
- Change the port in the uvicorn command
- Kill any existing process on port 8000

## License

This project is part of the LeRobot ecosystem.