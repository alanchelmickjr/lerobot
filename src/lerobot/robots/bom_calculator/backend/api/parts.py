"""
Parts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database import get_db
from models import Part, Inventory
from schemas import Part as PartSchema, PartCreate, PartUpdate, SuccessResponse, ErrorResponse

router = APIRouter()


@router.get("/", response_model=List[PartSchema])
async def get_all_parts(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    supplier: Optional[str] = None
):
    """Get all parts with optional filtering"""
    query = select(Part)
    
    if category:
        query = query.where(Part.category == category)
    if supplier:
        query = query.where(Part.supplier == supplier)
    
    result = await db.execute(query)
    parts = result.scalars().all()
    return parts


@router.get("/{part_id}", response_model=PartSchema)
async def get_part(part_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific part by ID"""
    query = select(Part).where(Part.part_id == part_id)
    result = await db.execute(query)
    part = result.scalar_one_or_none()
    
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    
    return part


@router.post("/", response_model=PartSchema)
async def create_part(part: PartCreate, db: AsyncSession = Depends(get_db)):
    """Create a new part"""
    # Check if part_id already exists
    if part.part_id:
        query = select(Part).where(Part.part_id == part.part_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"Part {part.part_id} already exists")
    
    db_part = Part(**part.dict())
    db.add(db_part)
    
    # Create inventory record
    inventory = Inventory(
        part_id=db_part.part_id,
        quantity_loose=0,
        quantity_assembled=0,
        quantity_reserved=0
    )
    db.add(inventory)
    
    await db.commit()
    await db.refresh(db_part)
    return db_part


@router.put("/{part_id}", response_model=PartSchema)
async def update_part(
    part_id: str,
    part_update: PartUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing part"""
    query = select(Part).where(Part.part_id == part_id)
    result = await db.execute(query)
    part = result.scalar_one_or_none()
    
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    
    # Update fields that are provided
    update_data = part_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(part, field, value)
    
    await db.commit()
    await db.refresh(part)
    return part


@router.delete("/{part_id}", response_model=SuccessResponse)
async def delete_part(part_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a part"""
    query = select(Part).where(Part.part_id == part_id)
    result = await db.execute(query)
    part = result.scalar_one_or_none()
    
    if not part:
        raise HTTPException(status_code=404, detail=f"Part {part_id} not found")
    
    await db.delete(part)
    await db.commit()
    
    return SuccessResponse(
        success=True,
        message=f"Part {part_id} deleted successfully"
    )


@router.get("/categories/list", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get list of unique part categories"""
    query = select(Part.category).distinct()
    result = await db.execute(query)
    categories = [cat for cat in result.scalars().all() if cat]
    return categories


@router.get("/suppliers/list", response_model=List[str])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    """Get list of unique suppliers"""
    query = select(Part.supplier).distinct()
    result = await db.execute(query)
    suppliers = [sup for sup in result.scalars().all() if sup]
    return suppliers