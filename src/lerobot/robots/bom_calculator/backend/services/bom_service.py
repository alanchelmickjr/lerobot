"""
BOM Service for expanding BOMs and managing BOM operations
"""
from typing import Dict, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging
import json

from models import Part, RobotModel, BOMItem
from schemas import BOMImportRequest, BOMExportResponse

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected in BOM"""
    pass


class BOMService:
    """Service for BOM operations"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, int]] = {}
    
    async def expand_bom(
        self, 
        db: AsyncSession,
        robot_model_id: str, 
        multiplier: int = 1,
        visited: Optional[Set[str]] = None
    ) -> Dict[str, int]:
        """
        Expand BOM recursively to get all parts with quantities
        
        Args:
            db: Database session
            robot_model_id: Robot model to expand
            multiplier: Quantity multiplier
            visited: Set of visited models for circular dependency detection
        
        Returns:
            Dictionary of part_id -> quantity
        """
        # Check cache first
        cache_key = f"{robot_model_id}:{multiplier}"
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        # Initialize visited set for circular dependency detection
        if visited is None:
            visited = set()
        
        # Check for circular dependency
        if robot_model_id in visited:
            raise CircularDependencyError(f"Circular dependency detected: {robot_model_id}")
        
        visited.add(robot_model_id)
        
        # Get BOM items for this model
        query = select(BOMItem).where(BOMItem.robot_model_id == robot_model_id)
        result = await db.execute(query)
        bom_items = result.scalars().all()
        
        expanded_parts = {}
        
        for item in bom_items:
            if item.part_id:
                # Direct part reference
                part_id = item.part_id
                quantity = item.quantity * multiplier
                
                if part_id in expanded_parts:
                    expanded_parts[part_id] += quantity
                else:
                    expanded_parts[part_id] = quantity
                    
            elif item.sub_model_id:
                # Recursive expansion for sub-models
                sub_parts = await self.expand_bom(
                    db, 
                    item.sub_model_id, 
                    item.quantity * multiplier, 
                    visited.copy()
                )
                
                for sub_part_id, sub_quantity in sub_parts.items():
                    if sub_part_id in expanded_parts:
                        expanded_parts[sub_part_id] += sub_quantity
                    else:
                        expanded_parts[sub_part_id] = sub_quantity
        
        # Cache the result
        self.cache[cache_key] = expanded_parts.copy()
        
        return expanded_parts
    
    async def validate_bom(self, db: AsyncSession, robot_model_id: str) -> Dict[str, any]:
        """
        Validate BOM for missing parts and circular dependencies
        
        Args:
            db: Database session
            robot_model_id: Robot model to validate
        
        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Try to expand BOM to detect circular dependencies
            expanded = await self.expand_bom(db, robot_model_id)
            
            # Check if all parts exist in database
            for part_id in expanded.keys():
                query = select(Part).where(Part.part_id == part_id)
                result = await db.execute(query)
                part = result.scalar_one_or_none()
                
                if not part:
                    result["is_valid"] = False
                    result["errors"].append(f"Part {part_id} not found in database")
            
            # Check for empty BOM
            if not expanded:
                result["warnings"].append("BOM is empty")
                
        except CircularDependencyError as e:
            result["is_valid"] = False
            result["errors"].append(str(e))
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    async def import_bom_from_json(
        self, 
        db: AsyncSession, 
        bom_data: Dict, 
        robot_model_id: str
    ) -> bool:
        """
        Import BOM from JSON data
        
        Args:
            db: Database session
            bom_data: JSON data containing BOM information
            robot_model_id: Robot model ID to import
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create robot model if not exists
            query = select(RobotModel).where(RobotModel.model_id == robot_model_id)
            result = await db.execute(query)
            model = result.scalar_one_or_none()
            
            if not model:
                model = RobotModel(
                    model_id=robot_model_id,
                    name=bom_data.get("name", robot_model_id),
                    description=bom_data.get("description", ""),
                    version=bom_data.get("version", "1.0"),
                    documentation_url=bom_data.get("documentation_url", ""),
                    parent_model_id=bom_data.get("parent_model_id")
                )
                db.add(model)
            
            # Import parts if provided
            if "parts" in bom_data:
                for part_data in bom_data["parts"]:
                    part_id = part_data.get("part_id", part_data.get("id"))
                    
                    query = select(Part).where(Part.part_id == part_id)
                    result = await db.execute(query)
                    part = result.scalar_one_or_none()
                    
                    if not part:
                        part = Part(
                            part_id=part_id,
                            name=part_data["name"],
                            description=part_data.get("description", ""),
                            category=part_data.get("category", "GENERAL"),
                            unit_cost=part_data.get("unit_cost", 0.0),
                            supplier=part_data.get("supplier", ""),
                            minimum_order_quantity=part_data.get("minimum_order_quantity", 1),
                            lead_time_days=part_data.get("lead_time_days", 0)
                        )
                        db.add(part)
            
            # Import BOM items
            if "bom_items" in bom_data:
                # Clear existing BOM items for this model
                query = select(BOMItem).where(BOMItem.robot_model_id == robot_model_id)
                result = await db.execute(query)
                existing_items = result.scalars().all()
                for item in existing_items:
                    await db.delete(item)
                
                # Add new BOM items
                for item_data in bom_data["bom_items"]:
                    bom_item = BOMItem(
                        robot_model_id=robot_model_id,
                        part_id=item_data.get("part_id"),
                        sub_model_id=item_data.get("sub_model_id"),
                        quantity=item_data["quantity"],
                        is_optional=item_data.get("is_optional", False),
                        notes=item_data.get("notes", "")
                    )
                    db.add(bom_item)
            
            await db.commit()
            
            # Clear cache for this model
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(robot_model_id)}
            
            logger.info(f"Successfully imported BOM for {robot_model_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to import BOM: {str(e)}")
            return False
    
    async def export_bom(
        self, 
        db: AsyncSession, 
        robot_model_id: str, 
        expanded: bool = False
    ) -> BOMExportResponse:
        """
        Export BOM as structured data
        
        Args:
            db: Database session
            robot_model_id: Robot model to export
            expanded: Whether to export expanded BOM
        
        Returns:
            BOM export response
        """
        items = []
        
        if expanded:
            # Export expanded BOM
            expanded_bom = await self.expand_bom(db, robot_model_id)
            
            for part_id, quantity in expanded_bom.items():
                query = select(Part).where(Part.part_id == part_id)
                result = await db.execute(query)
                part = result.scalar_one_or_none()
                
                items.append({
                    "part_id": part_id,
                    "part_name": part.name if part else "Unknown",
                    "quantity": quantity,
                    "category": part.category if part else "Unknown",
                    "unit_cost": part.unit_cost if part else 0.0,
                    "supplier": part.supplier if part else ""
                })
        else:
            # Export direct BOM items
            query = select(BOMItem).where(BOMItem.robot_model_id == robot_model_id)
            result = await db.execute(query)
            bom_items = result.scalars().all()
            
            for item in bom_items:
                item_data = {
                    "quantity": item.quantity,
                    "is_optional": item.is_optional,
                    "notes": item.notes
                }
                
                if item.part_id:
                    query = select(Part).where(Part.part_id == item.part_id)
                    result = await db.execute(query)
                    part = result.scalar_one_or_none()
                    
                    item_data.update({
                        "type": "part",
                        "part_id": item.part_id,
                        "part_name": part.name if part else "Unknown",
                        "category": part.category if part else "Unknown"
                    })
                elif item.sub_model_id:
                    query = select(RobotModel).where(RobotModel.model_id == item.sub_model_id)
                    result = await db.execute(query)
                    sub_model = result.scalar_one_or_none()
                    
                    item_data.update({
                        "type": "sub_model",
                        "sub_model_id": item.sub_model_id,
                        "sub_model_name": sub_model.name if sub_model else "Unknown"
                    })
                
                items.append(item_data)
        
        return BOMExportResponse(
            robot_model_id=robot_model_id,
            expanded=expanded,
            items=items
        )
    
    async def get_bom_cost(
        self, 
        db: AsyncSession, 
        robot_model_id: str, 
        quantity: int = 1
    ) -> Dict[str, any]:
        """
        Calculate total cost for building robots
        
        Args:
            db: Database session
            robot_model_id: Robot model
            quantity: Number of robots to build
        
        Returns:
            Cost breakdown dictionary
        """
        expanded_bom = await self.expand_bom(db, robot_model_id, quantity)
        
        total_cost = 0.0
        cost_breakdown = []
        missing_costs = []
        
        for part_id, qty in expanded_bom.items():
            query = select(Part).where(Part.part_id == part_id)
            result = await db.execute(query)
            part = result.scalar_one_or_none()
            
            if part:
                part_cost = part.unit_cost * qty
                total_cost += part_cost
                
                cost_breakdown.append({
                    "part_id": part_id,
                    "part_name": part.name,
                    "quantity": qty,
                    "unit_cost": part.unit_cost,
                    "total_cost": part_cost
                })
                
                if part.unit_cost == 0:
                    missing_costs.append(part_id)
            else:
                missing_costs.append(part_id)
        
        return {
            "robot_model_id": robot_model_id,
            "quantity": quantity,
            "total_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "missing_costs": missing_costs
        }
    
    def clear_cache(self, robot_model_id: Optional[str] = None):
        """
        Clear BOM cache
        
        Args:
            robot_model_id: Optional specific model to clear, otherwise clear all
        """
        if robot_model_id:
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(robot_model_id)}
        else:
            self.cache.clear()