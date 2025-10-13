"""
Order Service for generating and managing purchase orders
"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
import math
import uuid

from models import Part, Order, OrderItem, Inventory
from schemas import OrderSheet, OrderCreate, PartRequirement
from services.assembly_service import AssemblyCalculator

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order management"""
    
    def __init__(self):
        self.assembly_calculator = AssemblyCalculator()
    
    async def generate_order_sheet(
        self, 
        db: AsyncSession,
        robot_model_id: str, 
        quantity: int
    ) -> OrderSheet:
        """
        Generate order sheet for parts needed
        
        Args:
            db: Database session
            robot_model_id: Robot model to build
            quantity: Number of units to build
        
        Returns:
            Order sheet with grouped items
        """
        # Calculate parts needed
        parts_needed = await self.assembly_calculator.calculate_parts_needed(
            db, robot_model_id, quantity
        )
        
        order_items = []
        grouped_by_supplier = {}
        total_cost = 0.0
        
        for requirement in parts_needed:
            if requirement.shortage_quantity > 0:
                # Get part details
                query = select(Part).where(Part.part_id == requirement.part_id)
                result = await db.execute(query)
                part = result.scalar_one_or_none()
                
                if not part:
                    continue
                
                # Adjust for minimum order quantity
                order_quantity = requirement.shortage_quantity
                if part.minimum_order_quantity and part.minimum_order_quantity > 1:
                    # Round up to nearest multiple of minimum order quantity
                    order_quantity = math.ceil(
                        requirement.shortage_quantity / part.minimum_order_quantity
                    ) * part.minimum_order_quantity
                
                # Calculate costs
                unit_cost = part.unit_cost or 0.0
                line_total = order_quantity * unit_cost
                
                order_item = {
                    "part_id": requirement.part_id,
                    "part_name": part.name,
                    "category": part.category,
                    "quantity_needed": requirement.shortage_quantity,
                    "quantity_to_order": order_quantity,
                    "unit_cost": unit_cost,
                    "line_total": line_total,
                    "supplier": part.supplier or "Unknown",
                    "lead_time_days": part.lead_time_days or 0
                }
                
                order_items.append(order_item)
                total_cost += line_total
                
                # Group by supplier
                supplier = order_item["supplier"]
                if supplier not in grouped_by_supplier:
                    grouped_by_supplier[supplier] = []
                grouped_by_supplier[supplier].append(order_item)
        
        # Sort items within each supplier group
        for supplier in grouped_by_supplier:
            grouped_by_supplier[supplier].sort(key=lambda x: x["part_name"])
        
        return OrderSheet(
            robot_model_id=robot_model_id,
            target_quantity=quantity,
            order_items=order_items,
            grouped_by_supplier=grouped_by_supplier,
            estimated_cost=total_cost,
            generation_date=datetime.utcnow()
        )
    
    async def create_order_from_sheet(
        self, 
        db: AsyncSession,
        order_sheet: OrderSheet,
        supplier: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Create order from order sheet
        
        Args:
            db: Database session
            order_sheet: Order sheet to create from
            supplier: Optional specific supplier (otherwise create for all)
        
        Returns:
            Result dictionary with order details
        """
        try:
            orders_created = []
            
            # Determine which suppliers to create orders for
            if supplier:
                suppliers = [supplier] if supplier in order_sheet.grouped_by_supplier else []
            else:
                suppliers = list(order_sheet.grouped_by_supplier.keys())
            
            for supplier_name in suppliers:
                items = order_sheet.grouped_by_supplier[supplier_name]
                
                # Generate order number
                order_number = self.generate_order_number()
                
                # Calculate total for this supplier
                supplier_total = sum(item["line_total"] for item in items)
                
                # Create order
                order = Order(
                    order_number=order_number,
                    status="DRAFT",
                    supplier=supplier_name,
                    order_date=datetime.utcnow(),
                    total_cost=supplier_total
                )
                db.add(order)
                
                # Flush to get order_id
                await db.flush()
                
                # Create order items
                for item_data in items:
                    order_item = OrderItem(
                        order_id=order.order_id,
                        part_id=item_data["part_id"],
                        quantity=item_data["quantity_to_order"],
                        unit_cost=item_data["unit_cost"],
                        line_total=item_data["line_total"]
                    )
                    db.add(order_item)
                
                orders_created.append({
                    "order_id": order.order_id,
                    "order_number": order.order_number,
                    "supplier": supplier_name,
                    "total_cost": supplier_total,
                    "item_count": len(items)
                })
            
            await db.commit()
            
            return {
                "success": True,
                "orders_created": orders_created,
                "total_orders": len(orders_created)
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create order: {str(e)}"
            }
    
    async def submit_order(
        self, 
        db: AsyncSession,
        order_id: str
    ) -> Dict[str, any]:
        """
        Submit order (change status from DRAFT to SUBMITTED)
        
        Args:
            db: Database session
            order_id: Order ID to submit
        
        Returns:
            Result dictionary
        """
        try:
            # Get order
            query = select(Order).where(Order.order_id == order_id)
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            
            if not order:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
            
            if order.status != "DRAFT":
                return {
                    "success": False,
                    "error": f"Order is not in DRAFT status (current: {order.status})"
                }
            
            # Update status
            order.status = "SUBMITTED"
            order.order_date = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            
            await db.commit()
            
            return {
                "success": True,
                "order_id": order_id,
                "order_number": order.order_number,
                "status": "SUBMITTED"
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to submit order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to submit order: {str(e)}"
            }
    
    async def receive_order(
        self, 
        db: AsyncSession,
        order_id: str,
        received_items: Optional[Dict[str, int]] = None
    ) -> Dict[str, any]:
        """
        Mark order as received and update inventory
        
        Args:
            db: Database session
            order_id: Order ID
            received_items: Optional dict of part_id -> received_quantity
        
        Returns:
            Result dictionary
        """
        try:
            # Get order with items
            query = select(Order).where(Order.order_id == order_id)
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            
            if not order:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
            
            # Get order items
            query = select(OrderItem).where(OrderItem.order_id == order_id)
            result = await db.execute(query)
            order_items = result.scalars().all()
            
            inventory_updates = []
            
            for item in order_items:
                # Determine received quantity
                if received_items and item.part_id in received_items:
                    received_qty = received_items[item.part_id]
                else:
                    received_qty = item.quantity
                
                # Update order item
                item.received_quantity = received_qty
                
                # Update inventory
                query = select(Inventory).where(Inventory.part_id == item.part_id)
                result = await db.execute(query)
                inventory = result.scalar_one_or_none()
                
                if not inventory:
                    inventory = Inventory(
                        part_id=item.part_id,
                        quantity_loose=received_qty
                    )
                    db.add(inventory)
                else:
                    inventory.quantity_loose += received_qty
                    inventory.last_updated = datetime.utcnow()
                
                inventory_updates.append({
                    "part_id": item.part_id,
                    "quantity_received": received_qty
                })
            
            # Update order status
            order.status = "RECEIVED"
            order.received_date = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            
            await db.commit()
            
            return {
                "success": True,
                "order_id": order_id,
                "order_number": order.order_number,
                "inventory_updates": inventory_updates
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to receive order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to receive order: {str(e)}"
            }
    
    async def get_pending_orders(self, db: AsyncSession) -> List[Order]:
        """
        Get all pending (submitted but not received) orders
        
        Args:
            db: Database session
        
        Returns:
            List of pending orders
        """
        query = select(Order).where(Order.status == "SUBMITTED")
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_order_summary(self, db: AsyncSession) -> Dict[str, any]:
        """
        Get summary statistics for orders
        
        Args:
            db: Database session
        
        Returns:
            Summary statistics
        """
        query = select(Order)
        result = await db.execute(query)
        orders = result.scalars().all()
        
        summary = {
            "total_orders": len(orders),
            "draft": 0,
            "submitted": 0,
            "received": 0,
            "cancelled": 0,
            "total_value": 0.0,
            "pending_value": 0.0
        }
        
        for order in orders:
            status_key = order.status.lower()
            if status_key in summary:
                summary[status_key] += 1
            
            summary["total_value"] += order.total_cost
            
            if order.status == "SUBMITTED":
                summary["pending_value"] += order.total_cost
        
        return summary
    
    async def calculate_reorder_suggestions(
        self, 
        db: AsyncSession
    ) -> List[Dict[str, any]]:
        """
        Calculate parts that need reordering based on reorder points
        
        Args:
            db: Database session
        
        Returns:
            List of reorder suggestions
        """
        suggestions = []
        
        # Get all inventory items with parts
        query = select(Inventory)
        result = await db.execute(query)
        inventory_items = result.scalars().all()
        
        for inventory in inventory_items:
            # Check if below reorder point
            available = inventory.quantity_loose - inventory.quantity_reserved
            
            if available <= inventory.reorder_point and inventory.reorder_point > 0:
                # Get part details
                query = select(Part).where(Part.part_id == inventory.part_id)
                result = await db.execute(query)
                part = result.scalar_one_or_none()
                
                if part:
                    # Calculate suggested order quantity
                    # Order enough to get to 2x reorder point
                    suggested_qty = (inventory.reorder_point * 2) - available
                    
                    # Adjust for minimum order quantity
                    if part.minimum_order_quantity and part.minimum_order_quantity > 1:
                        suggested_qty = math.ceil(
                            suggested_qty / part.minimum_order_quantity
                        ) * part.minimum_order_quantity
                    
                    suggestions.append({
                        "part_id": inventory.part_id,
                        "part_name": part.name,
                        "current_stock": available,
                        "reorder_point": inventory.reorder_point,
                        "suggested_quantity": suggested_qty,
                        "supplier": part.supplier,
                        "unit_cost": part.unit_cost,
                        "total_cost": suggested_qty * (part.unit_cost or 0)
                    })
        
        # Sort by urgency (lowest stock ratio first)
        suggestions.sort(
            key=lambda x: x["current_stock"] / max(x["reorder_point"], 1)
        )
        
        return suggestions
    
    def generate_order_number(self) -> str:
        """
        Generate unique order number
        
        Returns:
            Order number string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"PO-{timestamp}-{unique_id}"