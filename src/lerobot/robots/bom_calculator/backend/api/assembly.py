"""
Assembly API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from schemas import (
    Assembly as AssemblySchema,
    AssemblyCreate,
    AssemblyUpdate,
    BuildableResult,
    PartRequirement,
    OptimizationResult,
    SuccessResponse
)
from services.assembly_service import AssemblyCalculator

router = APIRouter()
assembly_calculator = AssemblyCalculator()


@router.get("/calculate/{robot_model_id}", response_model=BuildableResult)
async def calculate_buildable(
    robot_model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Calculate maximum buildable quantity for a robot model"""
    return await assembly_calculator.calculate_buildable_quantity(db, robot_model_id)


@router.get("/requirements/{robot_model_id}", response_model=List[PartRequirement])
async def get_parts_requirements(
    robot_model_id: str,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Get parts requirements for building specified quantity"""
    return await assembly_calculator.calculate_parts_needed(db, robot_model_id, quantity)


@router.post("/optimize")
async def optimize_build_mix(
    models: List[dict],  # [{"model_id": str, "quantity": int}, ...]
    db: AsyncSession = Depends(get_db)
):
    """Optimize build mix when resources are limited"""
    robot_models = [(m["model_id"], m["quantity"]) for m in models]
    return await assembly_calculator.optimize_build_mix(db, robot_models)


@router.post("/create", response_model=SuccessResponse)
async def create_assembly(
    robot_model_id: str,
    serial_number: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a new assembly record"""
    result = await assembly_calculator.create_assembly(
        db,
        robot_model_id=robot_model_id,
        serial_number=serial_number,
        notes=notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Assembly created successfully",
        data=result
    )


@router.put("/{assembly_id}/status", response_model=SuccessResponse)
async def update_assembly_status(
    assembly_id: str,
    status: str,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update assembly status"""
    result = await assembly_calculator.update_assembly_status(
        db,
        assembly_id=assembly_id,
        status=status,
        notes=notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Assembly status updated",
        data=result
    )


@router.get("/progress")
async def get_assembly_progress(db: AsyncSession = Depends(get_db)):
    """Get overall assembly progress statistics"""
    return await assembly_calculator.get_assembly_progress(db)


@router.get("/time-estimate/{robot_model_id}")
async def get_assembly_time_estimate(
    robot_model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get estimated assembly time based on historical data"""
    return await assembly_calculator.calculate_assembly_time(db, robot_model_id)


@router.get("/bottlenecks")
async def identify_bottlenecks(
    models: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Identify parts that are bottlenecks across multiple models"""
    from sqlalchemy import select
    from models import RobotModel
    
    # Get models to check
    if not models:
        query = select(RobotModel).where(RobotModel.is_active == True)
        result = await db.execute(query)
        robot_models = result.scalars().all()
        models = [m.model_id for m in robot_models]
    
    bottlenecks = {}
    
    for model_id in models:
        buildable = await assembly_calculator.calculate_buildable_quantity(db, model_id)
        
        for part_id in buildable.limiting_parts:
            if part_id not in bottlenecks:
                bottlenecks[part_id] = {
                    "affected_models": [],
                    "total_impact": 0
                }
            bottlenecks[part_id]["affected_models"].append(model_id)
            bottlenecks[part_id]["total_impact"] += 1
    
    # Sort by impact
    sorted_bottlenecks = sorted(
        bottlenecks.items(),
        key=lambda x: x[1]["total_impact"],
        reverse=True
    )
    
    return [
        {
            "part_id": part_id,
            "affected_models": data["affected_models"],
            "impact_score": data["total_impact"]
        }
        for part_id, data in sorted_bottlenecks
    ]