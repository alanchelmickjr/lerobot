"""
Assembly Service for calculating buildable quantities and managing assemblies
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
import math

from models import Part, RobotModel, Assembly, Inventory
from schemas import BuildableResult, PartRequirement, OptimizationResult
from services.bom_service import BOMService
from services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class AssemblyCalculator:
    """Calculator for assembly operations"""
    
    def __init__(self):
        self.bom_service = BOMService()
        self.inventory_service = InventoryService()
    
    async def calculate_buildable_quantity(
        self, 
        db: AsyncSession,
        robot_model_id: str
    ) -> BuildableResult:
        """
        Calculate maximum buildable quantity based on current inventory
        
        Args:
            db: Database session
            robot_model_id: Robot model to calculate for
        
        Returns:
            BuildableResult with max quantity and limiting parts
        """
        # Expand BOM to get all required parts
        expanded_bom = await self.bom_service.expand_bom(db, robot_model_id)
        
        inventory_status = {}
        limiting_parts = []
        max_buildable = float('inf')
        
        for part_id, required_quantity in expanded_bom.items():
            # Get inventory for this part
            inventory = await self.inventory_service.get_inventory(db, part_id)
            
            if inventory:
                available = inventory.quantity_loose - inventory.quantity_reserved
            else:
                available = 0
            
            # Calculate how many units can be built with this part
            possible_units = available // required_quantity if required_quantity > 0 else 0
            
            inventory_status[part_id] = {
                "required": required_quantity,
                "available": available,
                "possible_units": possible_units
            }
            
            # Track limiting parts
            if possible_units < max_buildable:
                max_buildable = possible_units
                limiting_parts = [part_id]
            elif possible_units == max_buildable and max_buildable != float('inf'):
                limiting_parts.append(part_id)
        
        # Convert infinity to 0 if no parts available
        if max_buildable == float('inf'):
            max_buildable = 0
        
        return BuildableResult(
            robot_model_id=robot_model_id,
            max_quantity=int(max_buildable),
            limiting_parts=limiting_parts,
            inventory_status=inventory_status
        )
    
    async def calculate_parts_needed(
        self, 
        db: AsyncSession,
        robot_model_id: str, 
        target_quantity: int
    ) -> List[PartRequirement]:
        """
        Calculate parts needed to build target quantity
        
        Args:
            db: Database session
            robot_model_id: Robot model to build
            target_quantity: Number of units to build
        
        Returns:
            List of part requirements with shortages
        """
        if target_quantity <= 0:
            return []
        
        # Expand BOM for target quantity
        expanded_bom = await self.bom_service.expand_bom(db, robot_model_id, target_quantity)
        
        requirements = []
        
        for part_id, total_needed in expanded_bom.items():
            # Get inventory
            inventory = await self.inventory_service.get_inventory(db, part_id)
            
            if inventory:
                available = inventory.quantity_loose - inventory.quantity_reserved
            else:
                available = 0
            
            shortage = max(0, total_needed - available)
            
            # Get part details
            query = select(Part).where(Part.part_id == part_id)
            result = await db.execute(query)
            part = result.scalar_one_or_none()
            
            requirement = PartRequirement(
                part_id=part_id,
                part_name=part.name if part else "Unknown",
                required_quantity=total_needed,
                available_quantity=available,
                shortage_quantity=shortage,
                is_critical=(shortage > 0)
            )
            requirements.append(requirement)
        
        return requirements
    
    async def optimize_build_mix(
        self, 
        db: AsyncSession,
        robot_models: List[Tuple[str, int]]
    ) -> OptimizationResult:
        """
        Optimize build mix when resources are limited
        
        Args:
            db: Database session
            robot_models: List of (model_id, desired_quantity) tuples
        
        Returns:
            Optimization result with best mix
        """
        # Collect total requirements
        total_requirements = {}
        model_requirements = {}
        
        for model_id, desired_quantity in robot_models:
            expanded = await self.bom_service.expand_bom(db, model_id, desired_quantity)
            model_requirements[model_id] = expanded
            
            for part_id, quantity in expanded.items():
                if part_id in total_requirements:
                    total_requirements[part_id] += quantity
                else:
                    total_requirements[part_id] = quantity
        
        # Check inventory constraints
        constraints = []
        constraint_parts = set()
        
        for part_id, needed in total_requirements.items():
            inventory = await self.inventory_service.get_inventory(db, part_id)
            
            if inventory:
                available = inventory.quantity_loose - inventory.quantity_reserved
            else:
                available = 0
            
            if available < needed:
                constraints.append({
                    "part_id": part_id,
                    "available": available,
                    "needed": needed,
                    "shortage": needed - available
                })
                constraint_parts.add(part_id)
        
        # If no constraints, return original quantities
        if not constraints:
            optimized_quantities = {model_id: qty for model_id, qty in robot_models}
        else:
            # Simple optimization: reduce quantities proportionally
            optimized_quantities = {}
            
            for model_id, desired_quantity in robot_models:
                # Find the most constraining part for this model
                min_ratio = 1.0
                
                for part_id, part_quantity in model_requirements[model_id].items():
                    if part_id in constraint_parts:
                        inventory = await self.inventory_service.get_inventory(db, part_id)
                        available = inventory.quantity_loose - inventory.quantity_reserved if inventory else 0
                        
                        # Calculate what fraction of desired quantity can be built
                        if part_quantity > 0:
                            ratio = available / part_quantity
                            min_ratio = min(min_ratio, ratio)
                
                # Set optimized quantity
                optimized_quantities[model_id] = int(desired_quantity * min_ratio)
        
        return OptimizationResult(
            requested=robot_models,
            optimized=optimized_quantities,
            constraints=constraints
        )
    
    async def create_assembly(
        self, 
        db: AsyncSession,
        robot_model_id: str,
        serial_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Create a new assembly record
        
        Args:
            db: Database session
            robot_model_id: Robot model for assembly
            serial_number: Optional serial number
            notes: Optional notes
        
        Returns:
            Result dictionary with assembly details
        """
        try:
            # Generate serial number if not provided
            if not serial_number:
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                serial_number = f"{robot_model_id}-{timestamp}"
            
            # Create assembly record
            assembly = Assembly(
                robot_model_id=robot_model_id,
                serial_number=serial_number,
                status="PLANNED",
                notes=notes,
                created_at=datetime.utcnow()
            )
            db.add(assembly)
            
            await db.commit()
            
            return {
                "success": True,
                "assembly_id": assembly.assembly_id,
                "serial_number": assembly.serial_number,
                "status": assembly.status
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create assembly: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create assembly: {str(e)}"
            }
    
    async def update_assembly_status(
        self, 
        db: AsyncSession,
        assembly_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Update assembly status
        
        Args:
            db: Database session
            assembly_id: Assembly ID
            status: New status
            notes: Optional notes
        
        Returns:
            Result dictionary
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
            
            # Update status
            assembly.status = status
            assembly.updated_at = datetime.utcnow()
            
            # Set dates based on status
            if status == "IN_PROGRESS" and not assembly.assembly_date:
                assembly.assembly_date = datetime.utcnow()
            elif status == "COMPLETED" and not assembly.completion_date:
                assembly.completion_date = datetime.utcnow()
            
            if notes:
                assembly.notes = notes
            
            await db.commit()
            
            return {
                "success": True,
                "assembly_id": assembly_id,
                "status": status
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update assembly status: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to update assembly status: {str(e)}"
            }
    
    async def get_assembly_progress(
        self, 
        db: AsyncSession
    ) -> Dict[str, any]:
        """
        Get overall assembly progress statistics
        
        Args:
            db: Database session
        
        Returns:
            Progress statistics
        """
        query = select(Assembly)
        result = await db.execute(query)
        assemblies = result.scalars().all()
        
        stats = {
            "total": len(assemblies),
            "planned": 0,
            "in_progress": 0,
            "completed": 0,
            "cancelled": 0
        }
        
        for assembly in assemblies:
            status_key = assembly.status.lower().replace("_", "_")
            if status_key in stats:
                stats[status_key] += 1
        
        return stats
    
    async def calculate_assembly_time(
        self, 
        db: AsyncSession,
        robot_model_id: str
    ) -> Dict[str, any]:
        """
        Estimate assembly time based on historical data
        
        Args:
            db: Database session
            robot_model_id: Robot model
        
        Returns:
            Time estimates
        """
        # Get completed assemblies for this model
        query = select(Assembly).where(
            (Assembly.robot_model_id == robot_model_id) &
            (Assembly.status == "COMPLETED") &
            (Assembly.assembly_date.isnot(None)) &
            (Assembly.completion_date.isnot(None))
        )
        result = await db.execute(query)
        completed_assemblies = result.scalars().all()
        
        if not completed_assemblies:
            # Return default estimates
            return {
                "estimated_hours": 4,
                "min_hours": 3,
                "max_hours": 6,
                "sample_size": 0
            }
        
        # Calculate statistics
        durations = []
        for assembly in completed_assemblies:
            duration = (assembly.completion_date - assembly.assembly_date).total_seconds() / 3600
            durations.append(duration)
        
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        return {
            "estimated_hours": round(avg_duration, 1),
            "min_hours": round(min_duration, 1),
            "max_hours": round(max_duration, 1),
            "sample_size": len(durations)
        }