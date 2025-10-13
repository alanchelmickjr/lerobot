"""
Robot Models API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import RobotModel, BOMItem
from schemas import (
    RobotModel as RobotModelSchema,
    RobotModelCreate,
    RobotModelUpdate,
    BOMExportResponse,
    BOMImportRequest,
    SuccessResponse
)
from services.bom_service import BOMService

router = APIRouter()
bom_service = BOMService()


@router.get("/", response_model=List[RobotModelSchema])
async def get_all_robot_models(
    db: AsyncSession = Depends(get_db),
    active_only: bool = True
):
    """Get all robot models"""
    query = select(RobotModel)
    
    if active_only:
        query = query.where(RobotModel.is_active == True)
    
    result = await db.execute(query)
    models = result.scalars().all()
    return models


@router.get("/{model_id}", response_model=RobotModelSchema)
async def get_robot_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific robot model by ID"""
    query = select(RobotModel).where(RobotModel.model_id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Robot model {model_id} not found")
    
    return model


@router.post("/", response_model=RobotModelSchema)
async def create_robot_model(
    model: RobotModelCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new robot model"""
    # Check if model_id already exists
    if model.model_id:
        query = select(RobotModel).where(RobotModel.model_id == model.model_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"Model {model.model_id} already exists")
    
    db_model = RobotModel(**model.dict())
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    return db_model


@router.put("/{model_id}", response_model=RobotModelSchema)
async def update_robot_model(
    model_id: str,
    model_update: RobotModelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing robot model"""
    query = select(RobotModel).where(RobotModel.model_id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Robot model {model_id} not found")
    
    # Update fields that are provided
    update_data = model_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    await db.commit()
    await db.refresh(model)
    return model


@router.delete("/{model_id}", response_model=SuccessResponse)
async def delete_robot_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a robot model"""
    query = select(RobotModel).where(RobotModel.model_id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Robot model {model_id} not found")
    
    await db.delete(model)
    await db.commit()
    
    return SuccessResponse(
        success=True,
        message=f"Robot model {model_id} deleted successfully"
    )


@router.get("/{model_id}/bom", response_model=BOMExportResponse)
async def get_bom(
    model_id: str,
    expanded: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get BOM for a robot model"""
    # Check if model exists
    query = select(RobotModel).where(RobotModel.model_id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Robot model {model_id} not found")
    
    return await bom_service.export_bom(db, model_id, expanded)


@router.post("/{model_id}/bom/import", response_model=SuccessResponse)
async def import_bom(
    model_id: str,
    bom_request: BOMImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import BOM data for a robot model"""
    success = await bom_service.import_bom_from_json(
        db, 
        bom_request.bom_data, 
        model_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to import BOM")
    
    return SuccessResponse(
        success=True,
        message=f"BOM imported successfully for {model_id}"
    )


@router.get("/{model_id}/cost")
async def get_bom_cost(
    model_id: str,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Calculate cost for building robots"""
    # Check if model exists
    query = select(RobotModel).where(RobotModel.model_id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail=f"Robot model {model_id} not found")
    
    return await bom_service.get_bom_cost(db, model_id, quantity)


@router.post("/{model_id}/validate", response_model=SuccessResponse)
async def validate_bom(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate BOM for missing parts and circular dependencies"""
    result = await bom_service.validate_bom(db, model_id)
    
    if not result["is_valid"]:
        return SuccessResponse(
            success=False,
            message="BOM validation failed",
            data=result
        )
    
    return SuccessResponse(
        success=True,
        message="BOM is valid",
        data=result
    )