"""
WebSocket handler for real-time updates
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_info[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow()
        }
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        client_info = self.connection_info.pop(websocket, {})
        client_id = client_info.get("client_id", "unknown")
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connections"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcast JSON data to all connections"""
        message = json.dumps(data)
        await self.broadcast(message)


# Global connection manager
manager = ConnectionManager()


class WebSocketHandler:
    """Handles WebSocket messages and events"""
    
    def __init__(self):
        self.manager = manager
        self.heartbeat_interval = 30  # seconds
    
    async def handle_connection(self, websocket: WebSocket, client_id: str = None):
        """Handle a WebSocket connection"""
        await self.manager.connect(websocket, client_id)
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self.heartbeat(websocket))
        
        try:
            while True:
                # Receive and process messages
                data = await websocket.receive_text()
                await self.process_message(websocket, data)
                
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
            heartbeat_task.cancel()
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.manager.disconnect(websocket)
            heartbeat_task.cancel()
    
    async def process_message(self, websocket: WebSocket, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "subscribe":
                # Subscribe to specific events
                events = data.get("events", [])
                await self.subscribe_to_events(websocket, events)
            
            elif message_type == "inventory_update":
                # Broadcast inventory update to all clients
                await self.broadcast_inventory_update(data.get("data"))
            
            elif message_type == "assembly_status":
                # Broadcast assembly status update
                await self.broadcast_assembly_status(data.get("data"))
            
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Internal error processing message"
            })
    
    async def heartbeat(self, websocket: WebSocket):
        """Send periodic heartbeat to keep connection alive"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception:
                break
    
    async def subscribe_to_events(self, websocket: WebSocket, events: list):
        """Subscribe client to specific event types"""
        # Store subscription info
        if websocket in self.manager.connection_info:
            self.manager.connection_info[websocket]["subscriptions"] = events
        
        await websocket.send_json({
            "type": "subscription_confirmed",
            "events": events,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_inventory_update(self, data: Dict[str, Any]):
        """Broadcast inventory update to all clients"""
        await self.manager.broadcast_json({
            "type": "inventory_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_assembly_status(self, data: Dict[str, Any]):
        """Broadcast assembly status update"""
        await self.manager.broadcast_json({
            "type": "assembly_status_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_order_update(self, data: Dict[str, Any]):
        """Broadcast order update"""
        await self.manager.broadcast_json({
            "type": "order_update",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def broadcast_low_stock_alert(self, part_id: str, quantity: int):
        """Broadcast low stock alert"""
        await self.manager.broadcast_json({
            "type": "low_stock_alert",
            "data": {
                "part_id": part_id,
                "current_quantity": quantity
            },
            "timestamp": datetime.utcnow().isoformat()
        })


# Global WebSocket handler
websocket_handler = WebSocketHandler()


# Event notification functions (to be called from services)
async def notify_inventory_change(part_id: str, change_type: str, new_quantity: int):
    """Notify all clients of inventory change"""
    await websocket_handler.broadcast_inventory_update({
        "part_id": part_id,
        "change_type": change_type,
        "new_quantity": new_quantity
    })


async def notify_assembly_status_change(assembly_id: str, new_status: str):
    """Notify all clients of assembly status change"""
    await websocket_handler.broadcast_assembly_status({
        "assembly_id": assembly_id,
        "new_status": new_status
    })


async def notify_order_created(order_id: str, order_number: str, supplier: str):
    """Notify all clients of new order"""
    await websocket_handler.broadcast_order_update({
        "action": "created",
        "order_id": order_id,
        "order_number": order_number,
        "supplier": supplier
    })


async def notify_low_stock(part_id: str, current_quantity: int):
    """Notify all clients of low stock"""
    await websocket_handler.broadcast_low_stock_alert(part_id, current_quantity)