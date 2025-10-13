"""
Inventory API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from schemas import (
    Inventory as InventorySchema,
    InventoryUpdateRequest,
    SuccessResponse,
    ErrorResponse
)
from services.inventory_service import InventoryService

router = APIRouter()
inventory_service = InventoryService()


@router.get("/", response_model=List[InventorySchema])
async def get_all_inventory(db: AsyncSession = Depends(get_db)):
    """Get all inventory items"""
    items = await inventory_service.get_all_inventory(db)
    return items


@router.get("/{part_id}", response_model=InventorySchema)
async def get_inventory_for_part(
    part_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get inventory for a specific part"""
    inventory = await inventory_service.get_inventory(db, part_id)
    
    if not inventory:
        raise HTTPException(status_code=404, detail=f"Inventory for part {part_id} not found")
    
    return inventory


@router.post("/update", response_model=SuccessResponse)
async def update_inventory(
    request: InventoryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update inventory for a part"""
    result = await inventory_service.update_stock(
        db,
        part_id=request.part_id,
        quantity_change=request.quantity,
        change_type=request.change_type,
        reason=request.reason or "Manual update"
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Inventory updated successfully",
        data={
            "part_id": request.part_id,
            "new_quantity": result["new_quantity"]
        }
    )


@router.post("/bulk-update", response_model=SuccessResponse)
async def bulk_update_inventory(
    updates: List[InventoryUpdateRequest],
    db: AsyncSession = Depends(get_db)
):
    """Bulk update inventory for multiple parts"""
    results = []
    errors = []
    
    for update in updates:
        result = await inventory_service.update_stock(
            db,
            part_id=update.part_id,
            quantity_change=update.quantity,
            change_type=update.change_type,
            reason=update.reason or "Bulk update"
        )
        
        if result["success"]:
            results.append({
                "part_id": update.part_id,
                "new_quantity": result["new_quantity"]
            })
        else:
            errors.append({
                "part_id": update.part_id,
                "error": result["error"]
            })
    
    if errors:
        return SuccessResponse(
            success=False,
            message=f"Some updates failed: {len(errors)} errors",
            data={"successful": results, "errors": errors}
        )
    
    return SuccessResponse(
        success=True,
        message=f"Successfully updated {len(results)} inventory items",
        data=results
    )


@router.get("/value/total")
async def get_inventory_value(db: AsyncSession = Depends(get_db)):
    """Get total inventory value"""
    return await inventory_service.get_inventory_value(db)


@router.get("/low-stock/items")
async def get_low_stock_items(db: AsyncSession = Depends(get_db)):
    """Get items that are at or below reorder point"""
    items = await inventory_service.get_all_inventory(db)
    
    low_stock = []
    for item in items:
        available = item.quantity_loose - item.quantity_reserved
        if available <= item.reorder_point and item.reorder_point > 0:
            low_stock.append({
                "part_id": item.part_id,
                "available": available,
                "reorder_point": item.reorder_point,
                "quantity_loose": item.quantity_loose,
                "quantity_reserved": item.quantity_reserved
            })
    
    return low_stock


@router.post("/reserve/{robot_model_id}")
async def reserve_parts(
    robot_model_id: str,
    quantity: int = 1,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Reserve parts for a robot build"""
    result = await inventory_service.reserve_parts(
        db,
        robot_model_id=robot_model_id,
        quantity=quantity,
        notes=notes or ""
    )
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return result


@router.post("/reserve/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a reservation and release parts"""
    result = await inventory_service.cancel_reservation(db, reservation_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Reservation cancelled successfully",
        data=result
    )


@router.post("/consume")
async def consume_parts(
    assembly_id: str,
    parts: List[dict],
    db: AsyncSession = Depends(get_db)
):
    """Consume parts for an assembly"""
    result = await inventory_service.consume_parts(db, assembly_id, parts)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Parts consumed successfully",
        data=result
    )