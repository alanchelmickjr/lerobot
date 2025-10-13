"""
Inventory Service for managing stock levels and reservations
"""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
import logging
import uuid

from models import (
    Part, Inventory, InventoryAudit,
    Reservation, ReservedPart, ConsumedPart, Assembly
)
from schemas import (
    InventoryUpdateRequest, ReservationResult,
    InventoryUpdate, InventoryCreate
)
from services.bom_service import BOMService

logger = logging.getLogger(__name__)


class InsufficientStockError(Exception):
    """Raised when there is insufficient stock for an operation"""
    pass


class InventoryService:
    """Service for inventory operations"""
    
    def __init__(self):
        self.observers = []
    
    async def get_inventory(self, db: AsyncSession, part_id: str) -> Optional[Inventory]:
        """
        Get inventory for a specific part
        
        Args:
            db: Database session
            part_id: Part ID
        
        Returns:
            Inventory object or None
        """
        query = select(Inventory).where(Inventory.part_id == part_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_inventory(self, db: AsyncSession) -> List[Inventory]:
        """
        Get all inventory items
        
        Args:
            db: Database session
        
        Returns:
            List of inventory items
        """
        query = select(Inventory)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_stock(
        self, 
        db: AsyncSession,
        part_id: str, 
        quantity_change: int, 
        change_type: str = "loose",
        reason: str = "Manual update"
    ) -> Dict[str, any]:
        """
        Update stock levels for a part
        
        Args:
            db: Database session
            part_id: Part ID
            quantity_change: Amount to change (positive or negative)
            change_type: Type of change (loose, assembled, reserved)
            reason: Reason for the change
        
        Returns:
            Update result dictionary
        """
        try:
            # Get or create inventory record
            inventory = await self.get_inventory(db, part_id)
            
            if not inventory:
                # Check if part exists
                query = select(Part).where(Part.part_id == part_id)
                result = await db.execute(query)
                part = result.scalar_one_or_none()
                
                if not part:
                    return {
                        "success": False,
                        "error": f"Part {part_id} not found"
                    }
                
                # Create new inventory record
                inventory = Inventory(
                    part_id=part_id,
                    quantity_loose=0,
                    quantity_assembled=0,
                    quantity_reserved=0
                )
                db.add(inventory)
            
            # Apply the change based on type
            if change_type == "loose":
                new_quantity = inventory.quantity_loose + quantity_change
                if new_quantity < 0:
                    raise InsufficientStockError(f"Cannot reduce loose stock below 0 for {part_id}")
                inventory.quantity_loose = new_quantity
                
            elif change_type == "assembled":
                new_quantity = inventory.quantity_assembled + quantity_change
                if new_quantity < 0:
                    raise InsufficientStockError(f"Cannot reduce assembled stock below 0 for {part_id}")
                inventory.quantity_assembled = new_quantity
                
            elif change_type == "reserved":
                new_quantity = inventory.quantity_reserved + quantity_change
                if new_quantity < 0:
                    raise InsufficientStockError(f"Cannot reduce reserved stock below 0 for {part_id}")
                inventory.quantity_reserved = new_quantity
            else:
                return {
                    "success": False,
                    "error": f"Invalid change type: {change_type}"
                }
            
            inventory.last_updated = datetime.utcnow()
            
            # Create audit record
            audit = InventoryAudit(
                part_id=part_id,
                change_quantity=quantity_change,
                change_type=change_type.upper(),
                reason=reason,
                resulting_quantity=new_quantity,
                timestamp=datetime.utcnow()
            )
            db.add(audit)
            
            await db.commit()
            
            # Check for low stock alert
            if inventory.quantity_loose <= inventory.reorder_point:
                await self.notify_low_stock(part_id, inventory.quantity_loose)
            
            return {
                "success": True,
                "new_quantity": new_quantity,
                "part_id": part_id,
                "change_type": change_type
            }
            
        except InsufficientStockError as e:
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update stock: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update stock: {str(e)}"
            }
    
    async def reserve_parts(
        self, 
        db: AsyncSession,
        robot_model_id: str, 
        quantity: int,
        notes: str = ""
    ) -> ReservationResult:
        """
        Reserve parts for a robot build
        
        Args:
            db: Database session
            robot_model_id: Robot model to build
            quantity: Number of robots to build
            notes: Optional notes for the reservation
        
        Returns:
            Reservation result
        """
        try:
            # Expand BOM to get all required parts
            bom_service = BOMService()
            expanded_bom = await bom_service.expand_bom(db, robot_model_id, quantity)
            
            # Check availability for all parts
            insufficient_parts = []
            for part_id, needed_quantity in expanded_bom.items():
                inventory = await self.get_inventory(db, part_id)
                
                if not inventory:
                    insufficient_parts.append({
                        "part_id": part_id,
                        "needed": needed_quantity,
                        "available": 0
                    })
                else:
                    available = inventory.quantity_loose - inventory.quantity_reserved
                    if available < needed_quantity:
                        insufficient_parts.append({
                            "part_id": part_id,
                            "needed": needed_quantity,
                            "available": available
                        })
            
            # If any parts are insufficient, return error
            if insufficient_parts:
                error_msg = "Insufficient stock for parts: " + ", ".join(
                    [f"{p['part_id']} (need {p['needed']}, have {p['available']})" 
                     for p in insufficient_parts]
                )
                return ReservationResult(
                    success=False,
                    error=error_msg
                )
            
            # Create reservation
            reservation_id = str(uuid.uuid4())
            reservation = Reservation(
                reservation_id=reservation_id,
                robot_model_id=robot_model_id,
                quantity=quantity,
                status="ACTIVE",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                notes=notes
            )
            db.add(reservation)
            
            # Reserve parts and create reserved part records
            reserved_parts = []
            for part_id, needed_quantity in expanded_bom.items():
                # Update inventory
                inventory = await self.get_inventory(db, part_id)
                inventory.quantity_reserved += needed_quantity
                inventory.last_updated = datetime.utcnow()
                
                # Create reserved part record
                reserved_part = ReservedPart(
                    reservation_id=reservation_id,
                    part_id=part_id,
                    quantity=needed_quantity
                )
                db.add(reserved_part)
                
                reserved_parts.append({
                    "part_id": part_id,
                    "quantity": needed_quantity
                })
                
                # Create audit record
                audit = InventoryAudit(
                    part_id=part_id,
                    change_quantity=needed_quantity,
                    change_type="RESERVE",
                    reason=f"Reserved for {robot_model_id} x{quantity}",
                    resulting_quantity=inventory.quantity_reserved,
                    timestamp=datetime.utcnow()
                )
                db.add(audit)
            
            await db.commit()
            
            return ReservationResult(
                success=True,
                reservation_id=reservation_id,
                reserved_parts=reserved_parts
            )
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to reserve parts: {str(e)}")
            return ReservationResult(
                success=False,
                error=f"Failed to reserve parts: {str(e)}"
            )
    
    async def cancel_reservation(
        self, 
        db: AsyncSession,
        reservation_id: str
    ) -> Dict[str, any]:
        """
        Cancel a reservation and release reserved parts
        
        Args:
            db: Database session
            reservation_id: Reservation ID to cancel
        
        Returns:
            Result dictionary
        """
        try:
            # Get reservation
            query = select(Reservation).where(Reservation.reservation_id == reservation_id)
            result = await db.execute(query)
            reservation = result.scalar_one_or_none()
            
            if not reservation:
                return {
                    "success": False,
                    "error": f"Reservation {reservation_id} not found"
                }
            
            if reservation.status != "ACTIVE":
                return {
                    "success": False,
                    "error": f"Reservation is not active (status: {reservation.status})"
                }
            
            # Get reserved parts
            query = select(ReservedPart).where(ReservedPart.reservation_id == reservation_id)
            result = await db.execute(query)
            reserved_parts = result.scalars().all()
            
            # Release reserved quantities
            for reserved_part in reserved_parts:
                inventory = await self.get_inventory(db, reserved_part.part_id)
                if inventory:
                    inventory.quantity_reserved -= reserved_part.quantity
                    inventory.last_updated = datetime.utcnow()
                    
                    # Create audit record
                    audit = InventoryAudit(
                        part_id=reserved_part.part_id,
                        change_quantity=-reserved_part.quantity,
                        change_type="RELEASE",
                        reason=f"Released from reservation {reservation_id}",
                        resulting_quantity=inventory.quantity_reserved,
                        timestamp=datetime.utcnow()
                    )
                    db.add(audit)
            
            # Update reservation status
            reservation.status = "CANCELLED"
            
            await db.commit()
            
            return {
                "success": True,
                "reservation_id": reservation_id,
                "released_parts": len(reserved_parts)
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to cancel reservation: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to cancel reservation: {str(e)}"
            }
    
    async def consume_parts(
        self, 
        db: AsyncSession,
        assembly_id: str, 
        parts_list: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Consume parts for an assembly
        
        Args:
            db: Database session
            assembly_id: Assembly ID
            parts_list: List of parts to consume with quantities
        
        Returns:
            Consumption result
        """
        try:
            # Get assembly
            query = select(Assembly).where(Assembly.assembly_id == assembly_id)
            result = await db.execute(query)
            assembly = result.scalar_one_or_none()
            
            if not assembly:
                return {
                    "success": False,
                    "error": f"Assembly {assembly_id} not found"
                }
            
            consumed_records = []
            
            for part in parts_list:
                part_id = part["part_id"]
                quantity = part["quantity"]
                
                # Get inventory
                inventory = await self.get_inventory(db, part_id)
                
                if not inventory or inventory.quantity_loose < quantity:
                    return {
                        "success": False,
                        "error": f"Insufficient stock for {part_id} (need {quantity}, have {inventory.quantity_loose if inventory else 0})"
                    }
                
                # Update inventory
                inventory.quantity_loose -= quantity
                inventory.quantity_assembled += quantity
                inventory.last_updated = datetime.utcnow()
                
                # If parts were reserved, reduce reservation
                if inventory.quantity_reserved >= quantity:
                    inventory.quantity_reserved -= quantity
                
                # Create consumed part record
                consumed = ConsumedPart(
                    assembly_id=assembly_id,
                    part_id=part_id,
                    quantity=quantity,
                    consumed_date=datetime.utcnow()
                )
                db.add(consumed)
                consumed_records.append(consumed)
                
                # Create audit record
                audit = InventoryAudit(
                    part_id=part_id,
                    change_quantity=-quantity,
                    change_type="CONSUME",
                    reason=f"Consumed for assembly {assembly_id}",
                    resulting_quantity=inventory.quantity_loose,
                    timestamp=datetime.utcnow()
                )
                db.add(audit)
            
            # Update assembly status
            if assembly.status == "PLANNED":
                assembly.status = "IN_PROGRESS"
                assembly.assembly_date = datetime.utcnow()
            
            await db.commit()
            
            return {
                "success": True,
                "assembly_id": assembly_id,
                "consumed_parts": len(consumed_records)
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to consume parts: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to consume parts: {str(e)}"
            }
    
    async def notify_low_stock(self, part_id: str, current_quantity: int):
        """
        Notify observers about low stock
        
        Args:
            part_id: Part with low stock
            current_quantity: Current quantity
        """
        # This would typically send notifications via email, websocket, etc.
        logger.warning(f"Low stock alert: Part {part_id} has only {current_quantity} units")
        
        for observer in self.observers:
            try:
                await observer.notify_low_stock(part_id, current_quantity)
            except Exception as e:
                logger.error(f"Failed to notify observer: {str(e)}")
    
    async def get_inventory_value(self, db: AsyncSession) -> Dict[str, float]:
        """
        Calculate total inventory value
        
        Args:
            db: Database session
        
        Returns:
            Dictionary with value breakdown
        """
        query = select(Inventory)
        result = await db.execute(query)
        inventory_items = result.scalars().all()
        
        total_value = 0.0
        loose_value = 0.0
        assembled_value = 0.0
        
        for inventory in inventory_items:
            # Get part details
            query = select(Part).where(Part.part_id == inventory.part_id)
            result = await db.execute(query)
            part = result.scalar_one_or_none()
            
            if part and part.unit_cost:
                loose_value += inventory.quantity_loose * part.unit_cost
                assembled_value += inventory.quantity_assembled * part.unit_cost
        
        total_value = loose_value + assembled_value
        
        return {
            "total_value": total_value,
            "loose_value": loose_value,
            "assembled_value": assembled_value
        }