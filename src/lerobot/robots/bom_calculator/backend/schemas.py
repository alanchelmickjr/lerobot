"""
Pydantic schemas for API validation and serialization
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class PartCategory(str, Enum):
    SERVO = "SERVO"
    ELECTRONICS = "ELECTRONICS"
    POWER = "POWER"
    FASTENER = "FASTENER"
    MECHANICAL = "MECHANICAL"
    STRUCTURAL = "STRUCTURAL"
    SENSOR = "SENSOR"
    GENERAL = "GENERAL"


class AssemblyStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class ReservationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CONSUMED = "CONSUMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# Part schemas
class PartBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[PartCategory] = PartCategory.GENERAL
    unit_cost: Optional[float] = 0.0
    supplier: Optional[str] = None
    minimum_order_quantity: Optional[int] = 1
    lead_time_days: Optional[int] = 0
    is_assembly: Optional[bool] = False


class PartCreate(PartBase):
    part_id: Optional[str] = None


class PartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[PartCategory] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    minimum_order_quantity: Optional[int] = None
    lead_time_days: Optional[int] = None
    is_assembly: Optional[bool] = None


class Part(PartBase):
    part_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Robot Model schemas
class RobotModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    documentation_url: Optional[str] = None
    parent_model_id: Optional[str] = None
    is_active: Optional[bool] = True


class RobotModelCreate(RobotModelBase):
    model_id: Optional[str] = None


class RobotModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    documentation_url: Optional[str] = None
    parent_model_id: Optional[str] = None
    is_active: Optional[bool] = None


class RobotModel(RobotModelBase):
    model_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# BOM Item schemas
class BOMItemBase(BaseModel):
    robot_model_id: str
    part_id: Optional[str] = None
    sub_model_id: Optional[str] = None
    quantity: int = Field(gt=0)
    is_optional: Optional[bool] = False
    notes: Optional[str] = None
    
    @validator('part_id', 'sub_model_id')
    def validate_part_or_submodel(cls, v, values):
        if 'part_id' in values and 'sub_model_id' in values:
            if (values.get('part_id') is None) == (values.get('sub_model_id') is None):
                raise ValueError('Either part_id or sub_model_id must be set, but not both')
        return v


class BOMItemCreate(BOMItemBase):
    pass


class BOMItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    is_optional: Optional[bool] = None
    notes: Optional[str] = None


class BOMItem(BOMItemBase):
    item_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory schemas
class InventoryBase(BaseModel):
    part_id: str
    quantity_loose: Optional[int] = 0
    quantity_assembled: Optional[int] = 0
    quantity_reserved: Optional[int] = 0
    reorder_point: Optional[int] = 0
    location: Optional[str] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity_loose: Optional[int] = None
    quantity_assembled: Optional[int] = None
    quantity_reserved: Optional[int] = None
    reorder_point: Optional[int] = None
    location: Optional[str] = None


class Inventory(InventoryBase):
    inventory_id: str
    last_updated: datetime
    available_quantity: int = Field(description="Calculated field: loose - reserved")
    total_quantity: int = Field(description="Calculated field: loose + assembled")
    
    class Config:
        from_attributes = True


class InventoryUpdateRequest(BaseModel):
    part_id: str
    quantity: int
    change_type: str = Field(description="Type of change: loose, assembled, reserved")
    reason: Optional[str] = None


# Assembly schemas
class AssemblyBase(BaseModel):
    robot_model_id: str
    serial_number: Optional[str] = None
    status: Optional[AssemblyStatus] = AssemblyStatus.PLANNED
    assembly_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None


class AssemblyCreate(AssemblyBase):
    pass


class AssemblyUpdate(BaseModel):
    status: Optional[AssemblyStatus] = None
    assembly_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None


class Assembly(AssemblyBase):
    assembly_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Order schemas
class OrderItemBase(BaseModel):
    part_id: str
    quantity: int = Field(gt=0)
    unit_cost: Optional[float] = 0.0
    line_total: Optional[float] = 0.0
    received_quantity: Optional[int] = 0


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    item_id: str
    order_id: str
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_number: Optional[str] = None
    status: Optional[OrderStatus] = OrderStatus.DRAFT
    supplier: Optional[str] = None
    order_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    total_cost: Optional[float] = 0.0
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    supplier: Optional[str] = None
    expected_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    notes: Optional[str] = None


class Order(OrderBase):
    order_id: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True


# Calculation result schemas
class BuildableResult(BaseModel):
    robot_model_id: str
    max_quantity: int
    limiting_parts: List[str]
    inventory_status: Dict[str, Dict[str, Any]]


class PartRequirement(BaseModel):
    part_id: str
    part_name: Optional[str] = None
    required_quantity: int
    available_quantity: int
    shortage_quantity: int
    is_critical: bool


class OrderSheet(BaseModel):
    robot_model_id: str
    target_quantity: int
    order_items: List[Dict[str, Any]]
    grouped_by_supplier: Dict[str, List[Dict[str, Any]]]
    estimated_cost: float
    generation_date: datetime


class ReservationResult(BaseModel):
    success: bool
    reservation_id: Optional[str] = None
    reserved_parts: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class OptimizationResult(BaseModel):
    requested: List[tuple[str, int]]
    optimized: Dict[str, int]
    constraints: List[Dict[str, Any]]


# BOM Import/Export schemas
class BOMImportRequest(BaseModel):
    robot_model_id: str
    bom_data: Dict[str, Any]


class BOMExportResponse(BaseModel):
    robot_model_id: str
    expanded: bool = False
    items: List[Dict[str, Any]]


# WebSocket message schemas
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Response schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None