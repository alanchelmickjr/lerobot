"""
Orders API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import csv
import io

from database import get_db
from models import Order
from schemas import (
    Order as OrderSchema,
    OrderCreate,
    OrderSheet,
    SuccessResponse
)
from services.order_service import OrderService

router = APIRouter()
order_service = OrderService()


@router.post("/generate/{robot_model_id}", response_model=OrderSheet)
async def generate_order_sheet(
    robot_model_id: str,
    quantity: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Generate order sheet for parts needed to build robots"""
    return await order_service.generate_order_sheet(db, robot_model_id, quantity)


@router.post("/create", response_model=SuccessResponse)
async def create_order_from_sheet(
    order_sheet: OrderSheet,
    supplier: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Create order(s) from an order sheet"""
    result = await order_service.create_order_from_sheet(db, order_sheet, supplier)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message=f"Created {result['total_orders']} order(s)",
        data=result["orders_created"]
    )


@router.get("/", response_model=List[OrderSchema])
async def get_all_orders(
    status: Optional[str] = None,
    supplier: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders with optional filtering"""
    query = select(Order)
    
    if status:
        query = query.where(Order.status == status)
    if supplier:
        query = query.where(Order.supplier == supplier)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    return orders


@router.get("/pending", response_model=List[OrderSchema])
async def get_pending_orders(db: AsyncSession = Depends(get_db)):
    """Get all pending (submitted but not received) orders"""
    return await order_service.get_pending_orders(db)


@router.get("/summary")
async def get_order_summary(db: AsyncSession = Depends(get_db)):
    """Get summary statistics for orders"""
    return await order_service.get_order_summary(db)


@router.get("/reorder-suggestions")
async def get_reorder_suggestions(db: AsyncSession = Depends(get_db)):
    """Get parts that need reordering based on reorder points"""
    return await order_service.calculate_reorder_suggestions(db)


@router.post("/{order_id}/submit", response_model=SuccessResponse)
async def submit_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Submit a draft order"""
    result = await order_service.submit_order(db, order_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Order submitted successfully",
        data=result
    )


@router.post("/{order_id}/receive", response_model=SuccessResponse)
async def receive_order(
    order_id: str,
    received_items: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Mark order as received and update inventory"""
    result = await order_service.receive_order(db, order_id, received_items)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return SuccessResponse(
        success=True,
        message="Order received and inventory updated",
        data=result
    )


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific order by ID"""
    query = select(Order).where(Order.order_id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return order


@router.delete("/{order_id}", response_model=SuccessResponse)
async def cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order (only if in DRAFT status)"""
    query = select(Order).where(Order.order_id == order_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    if order.status != "DRAFT":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order in {order.status} status"
        )
    
    order.status = "CANCELLED"
    await db.commit()
    
    return SuccessResponse(
        success=True,
        message=f"Order {order.order_number} cancelled"
    )


@router.get("/export/csv")
async def export_orders_csv(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export orders as CSV"""
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Order Number", "Status", "Supplier", 
        "Order Date", "Total Cost", "Expected Date"
    ])
    
    # Write data
    for order in orders:
        writer.writerow([
            order.order_number,
            order.status,
            order.supplier or "",
            order.order_date.isoformat() if order.order_date else "",
            order.total_cost,
            order.expected_date.isoformat() if order.expected_date else ""
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )


@router.post("/generate-bulk")
async def generate_bulk_orders(
    models: List[dict],  # [{"model_id": str, "quantity": int}, ...]
    db: AsyncSession = Depends(get_db)
):
    """Generate order sheets for multiple robot models"""
    order_sheets = []
    total_cost = 0.0
    
    for model_spec in models:
        sheet = await order_service.generate_order_sheet(
            db,
            model_spec["model_id"],
            model_spec["quantity"]
        )
        order_sheets.append(sheet.dict())
        total_cost += sheet.estimated_cost
    
    # Combine all items by supplier
    combined_by_supplier = {}
    for sheet in order_sheets:
        for supplier, items in sheet["grouped_by_supplier"].items():
            if supplier not in combined_by_supplier:
                combined_by_supplier[supplier] = []
            combined_by_supplier[supplier].extend(items)
    
    return {
        "order_sheets": order_sheets,
        "combined_by_supplier": combined_by_supplier,
        "total_estimated_cost": total_cost
    }