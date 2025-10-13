# BOM Calculator API Reference

Complete API documentation for the BOM Calculator REST API and WebSocket interface.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Rate Limiting](#rate-limiting)
5. [Error Handling](#error-handling)
6. [REST Endpoints](#rest-endpoints)
   - [Parts](#parts)
   - [Robot Models](#robot-models)
   - [Inventory](#inventory)
   - [Assembly](#assembly)
   - [Orders](#orders)
   - [Export](#export)
7. [WebSocket Events](#websocket-events)
8. [Data Types](#data-types)
9. [Code Examples](#code-examples)
10. [Postman Collection](#postman-collection)

---

## Overview

The BOM Calculator API is a RESTful API that provides programmatic access to inventory management, assembly calculations, and order generation for robot manufacturing.

### API Features

- **RESTful Design**: Resource-based URLs with standard HTTP methods
- **JSON Format**: All requests and responses use JSON
- **Real-time Updates**: WebSocket support for live data
- **Pagination**: Efficient handling of large datasets
- **Filtering**: Query parameters for data filtering
- **Versioning**: Stable API with version in URL

### Quick Start

```bash
# Get all inventory items
curl -X GET "https://api.bomcalculator.com/api/v1/inventory" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update inventory quantity
curl -X PATCH "https://api.bomcalculator.com/api/v1/inventory/servo_12v" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 50}'
```

---

## Authentication

### JWT Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refreshing a Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Token Expiration

- Access tokens expire after 1 hour
- Refresh tokens expire after 30 days
- Use refresh token to obtain new access token

---

## Base URL

All API requests should be made to:

```
Production:  https://api.bomcalculator.com/api/v1
Staging:     https://staging-api.bomcalculator.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Rate Limiting

API requests are rate limited to prevent abuse:

| Tier | Requests per Minute | Requests per Hour |
|------|-------------------|-------------------|
| Anonymous | 10 | 100 |
| Authenticated | 100 | 1000 |
| Premium | 1000 | 10000 |

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641024000
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      "resource": "part",
      "id": "invalid_part_id"
    }
  },
  "request_id": "req_1234567890"
}
```

### HTTP Status Codes

| Status Code | Description |
|------------|-------------|
| 200 OK | Successful request |
| 201 Created | Resource created successfully |
| 204 No Content | Successful request with no response body |
| 400 Bad Request | Invalid request parameters |
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Insufficient permissions |
| 404 Not Found | Resource not found |
| 409 Conflict | Conflict with current state |
| 422 Unprocessable Entity | Validation errors |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server error |
| 503 Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request format is invalid |
| `AUTHENTICATION_REQUIRED` | Authentication is required |
| `INVALID_TOKEN` | Authentication token is invalid |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `RESOURCE_ALREADY_EXISTS` | Resource with same ID already exists |
| `VALIDATION_ERROR` | Request data failed validation |
| `QUANTITY_INSUFFICIENT` | Insufficient inventory quantity |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

---

## REST Endpoints

### Parts

#### List All Parts

```http
GET /api/v1/parts
```

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | - |
| `search` | string | Search in name/description | - |
| `page` | integer | Page number | 1 |
| `limit` | integer | Items per page (max 100) | 20 |
| `sort` | string | Sort field (`name`, `category`, `cost`) | `name` |
| `order` | string | Sort order (`asc`, `desc`) | `asc` |

**Response:**
```json
{
  "data": [
    {
      "id": "servo_12v",
      "name": "Servo Motor 12V",
      "category": "Motors",
      "unit_cost": 45.99,
      "supplier": "ServoTech Inc",
      "lead_time_days": 7,
      "image_url": "/images/parts/servo_12v.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Get Part Details

```http
GET /api/v1/parts/{part_id}
```

**Response:**
```json
{
  "id": "servo_12v",
  "name": "Servo Motor 12V",
  "category": "Motors",
  "description": "High-torque servo motor, 12V, 25kg-cm",
  "unit_cost": 45.99,
  "supplier": "ServoTech Inc",
  "supplier_part_number": "ST-12V-25",
  "lead_time_days": 7,
  "minimum_order_quantity": 1,
  "specifications": {
    "voltage": "12V",
    "torque": "25kg-cm",
    "speed": "0.15s/60°",
    "weight": "55g"
  },
  "image_url": "/images/parts/servo_12v.jpg",
  "datasheet_url": "/datasheets/servo_12v.pdf",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Part

```http
POST /api/v1/parts
Content-Type: application/json

{
  "id": "new_part",
  "name": "New Part Name",
  "category": "Electronics",
  "unit_cost": 12.50,
  "supplier": "Supplier Name",
  "lead_time_days": 14
}
```

#### Update Part

```http
PUT /api/v1/parts/{part_id}
Content-Type: application/json

{
  "name": "Updated Part Name",
  "unit_cost": 13.00,
  "lead_time_days": 10
}
```

#### Delete Part

```http
DELETE /api/v1/parts/{part_id}
```

---

### Robot Models

#### List Robot Models

```http
GET /api/v1/robots
```

**Response:**
```json
{
  "data": [
    {
      "id": "so-arm100",
      "name": "SO-ARM100",
      "description": "Dual-arm robot with leader-follower configuration",
      "image_url": "/images/robots/so-arm100.jpg",
      "documentation_url": "https://github.com/TheRobotStudio/SO-ARM100",
      "complexity": "medium",
      "assembly_time_hours": 4
    },
    {
      "id": "lekiwi",
      "name": "LeKiwi",
      "description": "Mobile manipulator with omnidirectional wheels",
      "image_url": "/images/robots/lekiwi.jpg",
      "documentation_url": "https://github.com/SIGRobotics-UIUC/LeKiwi",
      "complexity": "high",
      "assembly_time_hours": 8
    }
  ]
}
```

#### Get Robot BOM

```http
GET /api/v1/robots/{robot_id}/bom
```

**Response:**
```json
{
  "robot_id": "so-arm100",
  "robot_name": "SO-ARM100",
  "version": "1.0.0",
  "total_parts": 24,
  "total_cost": 485.50,
  "items": [
    {
      "part_id": "servo_12v",
      "part_name": "Servo Motor 12V",
      "quantity": 6,
      "unit_cost": 45.99,
      "total_cost": 275.94,
      "category": "Motors",
      "notes": "3 for leader, 3 for follower"
    },
    {
      "part_id": "servo_5v_270",
      "part_name": "Servo Motor 5V 270°",
      "quantity": 2,
      "unit_cost": 25.00,
      "total_cost": 50.00,
      "category": "Motors",
      "notes": "Gripper servos"
    }
  ]
}
```

#### Update Robot BOM

```http
PUT /api/v1/robots/{robot_id}/bom
Content-Type: application/json

{
  "version": "1.1.0",
  "items": [
    {
      "part_id": "servo_12v",
      "quantity": 6
    },
    {
      "part_id": "servo_5v_270",
      "quantity": 4
    }
  ]
}
```

---

### Inventory

#### Get Inventory Status

```http
GET /api/v1/inventory
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by part category |
| `low_stock` | boolean | Show only low stock items |
| `location` | string | Filter by storage location |
| `search` | string | Search in part names |

**Response:**
```json
{
  "data": [
    {
      "part_id": "servo_12v",
      "part_name": "Servo Motor 12V",
      "category": "Motors",
      "quantity_loose": 45,
      "quantity_assembled": 12,
      "quantity_total": 57,
      "reorder_point": 20,
      "reorder_quantity": 50,
      "location": "Shelf A3",
      "status": "adequate",
      "last_updated": "2024-01-15T10:30:00Z",
      "updated_by": "user123"
    }
  ],
  "summary": {
    "total_items": 150,
    "low_stock_items": 8,
    "out_of_stock_items": 2,
    "total_value": 12450.00
  }
}
```

#### Get Single Inventory Item

```http
GET /api/v1/inventory/{part_id}
```

**Response:**
```json
{
  "part_id": "servo_12v",
  "part_name": "Servo Motor 12V",
  "category": "Motors",
  "quantity_loose": 45,
  "quantity_assembled": 12,
  "quantity_reserved": 6,
  "quantity_available": 39,
  "reorder_point": 20,
  "reorder_quantity": 50,
  "location": "Shelf A3",
  "status": "adequate",
  "value": 2069.55,
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "add",
      "quantity_change": 10,
      "quantity_after": 45,
      "user": "user123",
      "notes": "Received from supplier"
    }
  ]
}
```

#### Update Inventory Quantity

```http
PATCH /api/v1/inventory/{part_id}
Content-Type: application/json

{
  "quantity": 50,
  "location": "Shelf A3",
  "notes": "Manual count adjustment"
}
```

#### Bulk Update Inventory

```http
POST /api/v1/inventory/bulk-update
Content-Type: application/json

{
  "updates": [
    {
      "part_id": "servo_12v",
      "quantity": 50
    },
    {
      "part_id": "frame_aluminum",
      "quantity": 12
    }
  ],
  "notes": "Weekly inventory audit"
}
```

#### Inventory Transaction

```http
POST /api/v1/inventory/transaction
Content-Type: application/json

{
  "type": "add",  // "add", "remove", "transfer", "adjust"
  "items": [
    {
      "part_id": "servo_12v",
      "quantity": 20,
      "location": "Shelf A3"
    }
  ],
  "reference": "PO-2024-001",
  "notes": "Received from supplier order"
}
```

---

### Assembly

#### Calculate Buildable Quantity

```http
GET /api/v1/assembly/calculate/{robot_id}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `include_reserved` | boolean | Include reserved inventory |
| `target_quantity` | integer | Check feasibility for target |

**Response:**
```json
{
  "robot_id": "so-arm100",
  "robot_name": "SO-ARM100",
  "max_buildable": 7,
  "currently_available": 45,
  "after_build_remaining": 3,
  "bottlenecks": [
    {
      "part_id": "servo_12v",
      "part_name": "Servo Motor 12V",
      "required_per_unit": 6,
      "available": 45,
      "limiting_factor": true,
      "max_units": 7,
      "shortage_for_target": 0
    }
  ],
  "build_time_estimate_hours": 28,
  "total_cost": 3398.50,
  "cost_per_unit": 485.50
}
```

#### Calculate Multi-Model Build

```http
POST /api/v1/assembly/calculate-multi
Content-Type: application/json

{
  "models": [
    {
      "robot_id": "so-arm100",
      "target_quantity": 5
    },
    {
      "robot_id": "lekiwi",
      "target_quantity": 2
    }
  ]
}
```

**Response:**
```json
{
  "feasible": false,
  "results": [
    {
      "robot_id": "so-arm100",
      "target_quantity": 5,
      "max_buildable": 3,
      "feasible": false
    },
    {
      "robot_id": "lekiwi",
      "target_quantity": 2,
      "max_buildable": 2,
      "feasible": true
    }
  ],
  "shared_parts_conflicts": [
    {
      "part_id": "raspberry_pi_5",
      "total_required": 7,
      "available": 5,
      "shortage": 2
    }
  ],
  "optimization_suggestion": {
    "so-arm100": 3,
    "lekiwi": 1
  }
}
```

#### Create Assembly Plan

```http
POST /api/v1/assembly/plan
Content-Type: application/json

{
  "robot_id": "so-arm100",
  "quantity": 5,
  "target_date": "2024-02-01",
  "priority": "high",
  "notes": "Customer order #12345"
}
```

**Response:**
```json
{
  "plan_id": "plan_20240115_001",
  "robot_id": "so-arm100",
  "quantity": 5,
  "status": "reserved",
  "target_date": "2024-02-01",
  "parts_reserved": true,
  "pick_list_url": "/api/v1/assembly/plan/plan_20240115_001/pick-list",
  "estimated_completion": "2024-01-31T17:00:00Z"
}
```

#### Update Assembly Progress

```http
PATCH /api/v1/assembly/plan/{plan_id}
Content-Type: application/json

{
  "status": "in_progress",
  "completed_units": 2,
  "notes": "2 units completed, 3 in progress"
}
```

#### Complete Assembly

```http
POST /api/v1/assembly/complete
Content-Type: application/json

{
  "plan_id": "plan_20240115_001",
  "completed_units": 5,
  "defective_units": 0,
  "notes": "All units passed QC"
}
```

---

### Orders

#### List Orders

```http
GET /api/v1/orders
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (`draft`, `submitted`, `pending`, `completed`) |
| `supplier` | string | Filter by supplier |
| `date_from` | date | Start date (ISO 8601) |
| `date_to` | date | End date (ISO 8601) |

**Response:**
```json
{
  "data": [
    {
      "id": "order_20240115_001",
      "order_number": "PO-2024-001",
      "status": "submitted",
      "supplier": "ServoTech Inc",
      "total_items": 5,
      "total_quantity": 50,
      "total_cost": 2299.50,
      "created_at": "2024-01-15T10:00:00Z",
      "submitted_at": "2024-01-15T14:30:00Z",
      "expected_delivery": "2024-01-22T00:00:00Z"
    }
  ]
}
```

#### Get Order Details

```http
GET /api/v1/orders/{order_id}
```

**Response:**
```json
{
  "id": "order_20240115_001",
  "order_number": "PO-2024-001",
  "status": "submitted",
  "supplier": {
    "name": "ServoTech Inc",
    "contact": "orders@servotech.com",
    "phone": "+1-555-0100"
  },
  "items": [
    {
      "part_id": "servo_12v",
      "part_name": "Servo Motor 12V",
      "quantity": 20,
      "unit_cost": 45.99,
      "total_cost": 919.80
    }
  ],
  "totals": {
    "subtotal": 2199.50,
    "tax": 0,
    "shipping": 100.00,
    "total": 2299.50
  },
  "notes": "Rush delivery requested",
  "created_at": "2024-01-15T10:00:00Z",
  "created_by": "user123"
}
```

#### Generate Order

```http
POST /api/v1/orders/generate
Content-Type: application/json

{
  "robot_id": "so-arm100",
  "quantity": 10,
  "include_safety_stock": true,
  "group_by_supplier": true
}
```

**Response:**
```json
{
  "orders": [
    {
      "supplier": "ServoTech Inc",
      "items": [
        {
          "part_id": "servo_12v",
          "part_name": "Servo Motor 12V",
          "current_stock": 45,
          "required": 60,
          "to_order": 20,
          "unit_cost": 45.99,
          "total_cost": 919.80
        }
      ],
      "total_cost": 919.80
    }
  ],
  "summary": {
    "total_suppliers": 3,
    "total_parts": 8,
    "total_quantity": 45,
    "total_cost": 3250.00
  }
}
```

#### Submit Order

```http
POST /api/v1/orders/{order_id}/submit
Content-Type: application/json

{
  "supplier_order_number": "ST-ORD-123456",
  "expected_delivery": "2024-01-22",
  "notes": "Confirmed via email"
}
```

#### Receive Order

```http
POST /api/v1/orders/{order_id}/receive
Content-Type: application/json

{
  "items": [
    {
      "part_id": "servo_12v",
      "quantity_received": 20,
      "quantity_accepted": 19,
      "quantity_rejected": 1,
      "rejection_reason": "Damaged in shipping"
    }
  ],
  "notes": "One unit damaged, replacement requested"
}
```

---

### Export

#### Export Inventory

```http
GET /api/v1/export/inventory
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Export format (`csv`, `excel`, `pdf`) |
| `include_zero` | boolean | Include zero quantity items |

**Response:**
Returns file download in requested format.

#### Export Order Sheet

```http
GET /api/v1/export/order/{order_id}
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Export format (`pdf`, `excel`) |
| `template` | string | Template name (`standard`, `detailed`) |

#### Export Assembly Report

```http
GET /api/v1/export/assembly-report
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `date_from` | date | Start date |
| `date_to` | date | End date |
| `format` | string | Export format |

---

## WebSocket Events

### Connection

```javascript
const ws = new WebSocket('wss://api.bomcalculator.com/ws');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

### Event Types

#### Server → Client Events

**Inventory Updated**
```json
{
  "type": "inventory:updated",
  "data": {
    "part_id": "servo_12v",
    "old_quantity": 45,
    "new_quantity": 50,
    "user": "user123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

**Assembly Completed**
```json
{
  "type": "assembly:completed",
  "data": {
    "plan_id": "plan_20240115_001",
    "robot_id": "so-arm100",
    "quantity": 5,
    "timestamp": "2024-01-15T17:00:00Z"
  }
}
```

**Order Status Changed**
```json
{
  "type": "order:status_changed",
  "data": {
    "order_id": "order_20240115_001",
    "old_status": "submitted",
    "new_status": "delivered",
    "timestamp": "2024-01-22T09:00:00Z"
  }
}
```

**Low Stock Alert**
```json
{
  "type": "stock:low_alert",
  "data": {
    "part_id": "raspberry_pi_5",
    "current_quantity": 2,
    "reorder_point": 5,
    "severity": "critical"
  }
}
```

#### Client → Server Events

**Subscribe to Updates**
```json
{
  "type": "subscribe",
  "channels": ["inventory", "assembly", "orders"]
}
```

**Unsubscribe**
```json
{
  "type": "unsubscribe",
  "channels": ["orders"]
}
```

**Ping/Pong (Keep-alive)**
```json
{
  "type": "ping"
}
```

---

## Data Types

### Common Types

```typescript
// Pagination
interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

// Timestamp
type Timestamp = string; // ISO 8601 format

// Money
type Money = number; // Decimal with 2 places

// Status Enums
type InventoryStatus = 'adequate' | 'low' | 'critical' | 'out_of_stock';
type OrderStatus = 'draft' | 'submitted' | 'pending' | 'delivered' | 'completed' | 'cancelled';
type AssemblyStatus = 'planned' | 'reserved' | 'in_progress' | 'completed' | 'cancelled';
```

### Request/Response Schemas

```typescript
// Part
interface Part {
  id: string;
  name: string;
  category: string;
  description?: string;
  unit_cost: Money;
  supplier?: string;
  supplier_part_number?: string;
  lead_time_days: number;
  minimum_order_quantity?: number;
  specifications?: Record<string, any>;
  image_url?: string;
  datasheet_url?: string;
  created_at: Timestamp;
  updated_at: Timestamp;
}

// Inventory Item
interface InventoryItem {
  part_id: string;
  part_name: string;
  category: string;
  quantity_loose: number;
  quantity_assembled: number;
  quantity_reserved: number;
  quantity_available: number;
  reorder_point: number;
  reorder_quantity: number;
  location?: string;
  status: InventoryStatus;
  value: Money;
  last_updated: Timestamp;
  updated_by?: string;
}

// BOM Item
interface BOMItem {
  part_id: string;
  part_name: string;
  quantity: number;
  unit_cost: Money;
  total_cost: Money;
  category: string;
  notes?: string;
}

// Assembly Result
interface AssemblyResult {
  robot_id: string;
  robot_name: string;
  max_buildable: number;
  bottlenecks: Bottleneck[];
  total_cost: Money;
  cost_per_unit: Money;
}

// Order
interface Order {
  id: string;
  order_number: string;
  status: OrderStatus;
  supplier: Supplier;
  items: OrderItem[];
  totals: OrderTotals;
  notes?: string;
  created_at: Timestamp;
  created_by: string;
  submitted_at?: Timestamp;
  expected_delivery?: Timestamp;
  completed_at?: Timestamp;
}
```

---

## Code Examples

### JavaScript/TypeScript

```typescript
// API Client Class
class BOMCalculatorAPI {
  private baseURL = 'https://api.bomcalculator.com/api/v1';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  // Get inventory
  async getInventory(params?: { category?: string; low_stock?: boolean }) {
    const query = new URLSearchParams(params as any).toString();
    return this.request<InventoryResponse>(`/inventory?${query}`);
  }

  // Update inventory
  async updateInventory(partId: string, quantity: number) {
    return this.request(`/inventory/${partId}`, {
      method: 'PATCH',
      body: JSON.stringify({ quantity }),
    });
  }

  // Calculate buildable
  async calculateBuildable(robotId: string) {
    return this.request<AssemblyResult>(`/assembly/calculate/${robotId}`);
  }

  // Generate order
  async generateOrder(robotId: string, quantity: number) {
    return this.request('/orders/generate', {
      method: 'POST',
      body: JSON.stringify({ robot_id: robotId, quantity }),
    });
  }
}

// Usage
const api = new BOMCalculatorAPI('your-token');

// Get low stock items
const lowStock = await api.getInventory({ low_stock: true });

// Calculate buildable robots
const result = await api.calculateBuildable('so-arm100');
console.log(`Can build ${result.max_buildable} units`);
```

### Python

```python
import requests
from typing import Optional, Dict, Any

class BOMCalculatorAPI:
    def __init__(self, token: str, base_url: str = "https://api.bomcalculator.com/api/v1"):
        self.token = token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
    
    def get_inventory(self, category: Optional[str] = None, 
                     low_stock: Optional[bool] = None) -> Dict[str, Any]:
        """Get inventory items"""
        params = {}
        if category:
            params["category"] = category
        if low_stock is not None:
            params["low_stock"] = low_stock
        
        response = self.session.get(f"{self.base_url}/inventory", params=params)
        response.raise_for_status()
        return response.json()
    
    def update_inventory(self, part_id: str, quantity: int) -> Dict[str, Any]:
        """Update inventory quantity"""
        data = {"quantity": quantity}
        response = self.session.patch(
            f"{self.base_url}/inventory/{part_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_buildable(self, robot_id: str) -> Dict[str, Any]:
        """Calculate buildable quantity for a robot"""
        response = self.session.get(
            f"{self.base_url}/assembly/calculate/{robot_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def generate_order(self, robot_id: str, quantity: int) -> Dict[str, Any]:
        """Generate order for robot build"""
        data = {
            "robot_id": robot_id,
            "quantity": quantity,
            "include_safety_stock": True
        }
        response = self.session.post(
            f"{self.base_url}/orders/generate",
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
api = BOMCalculatorAPI("your-token")

# Get low stock items
low_stock = api.get_inventory(low_stock=True)
for item in low_stock["data"]:
    print(f"{item['part_name']}: {item['quantity_loose']} units")

# Calculate buildable
result = api.calculate_buildable("so-arm100")
print(f"Can build {result['max_buildable']} SO-ARM100 robots")

# Check bottlenecks
for bottleneck in result["bottlenecks"]:
    print(f"- {bottleneck['part_name']}: need {bottleneck['shortage_for_target']} more")
```

### cURL

```bash
# Get inventory
curl -X GET "https://api.bomcalculator.com/api/v1/inventory" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update inventory
curl -X PATCH "https://api.bomcalculator.com/api/v1/inventory/servo_12v" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 50}'

# Calculate buildable
curl -X GET "https://api.bomcalculator.com/api/v1/assembly/calculate/so-arm100" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate order
curl -X POST "https://api.bomcalculator.com/api/v1/orders/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"robot_id": "so-arm100", "quantity": 10}'
```

---

## Postman Collection

Import this collection into Postman for easy API testing:

```json
{
  "info": {
    "name": "BOM Calculator API",
    "version": "1.0.0",
    "description": "Complete API collection for BOM Calculator"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.bomcalculator.com/api/v1"
    },
    {
      "key": "access_token",
      "value": "your-token-here"
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/login",
            "body": {
              "mode": "raw",
              "raw": {
                "username": "user@example.com",
                "password": "password"
              }
            }
          }
        }
      ]
    },
    {
      "name": "Inventory",
      "item": [
        {
          "name": "Get Inventory",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/inventory"
          }
        },
        {
          "name": "Update Inventory",
          "request": {
            "method": "PATCH",
            "url": "{{base_url}}/inventory/servo_12v",
            "body": {
              "mode": "raw",
              "raw": {
                "quantity": 50
              }
            }
          }
        }
      ]
    }
  ]
}
```

---

## API Changelog

### Version 1.0.0 (2024-01-01)
- Initial API release
- Basic CRUD operations for parts, inventory, orders
- Assembly calculation endpoints
- WebSocket support for real-time updates

### Version 1.1.0 (Planned)
- GraphQL endpoint
- Batch operations
- Advanced filtering
- Webhook support

---

## Support

For API support and questions:

- **Documentation**: https://docs.bomcalculator.com
- **Status Page**: https://status.bomcalculator.com
- **GitHub Issues**: https://github.com/yourusername/lerobot/issues
- **Email**: api-support@bomcalculator.com
- **Discord**: https://discord.gg/bomcalculator

---

**API Version**: 1.0.0  
**Last Updated**: January 2024  
**OpenAPI Spec**: [Download](https://api.bomcalculator.com/openapi.json)

For deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).  
For troubleshooting, see the [Troubleshooting Guide](TROUBLESHOOTING.md).