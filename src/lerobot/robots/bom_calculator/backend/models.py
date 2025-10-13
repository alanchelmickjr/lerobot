"""
SQLAlchemy models for BOM Calculator
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a unique identifier"""
    return str(uuid.uuid4())


class Part(Base):
    """Part model representing individual components"""
    __tablename__ = "parts"
    
    part_id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    unit_cost = Column(Float, default=0.0)
    supplier = Column(String)
    minimum_order_quantity = Column(Integer, default=1)
    lead_time_days = Column(Integer, default=0)
    is_assembly = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory = relationship("Inventory", back_populates="part", uselist=False, cascade="all, delete-orphan")
    bom_items = relationship("BOMItem", back_populates="part", cascade="all, delete-orphan")


class RobotModel(Base):
    """Robot model representing different robot configurations"""
    __tablename__ = "robot_models"
    
    model_id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String)
    documentation_url = Column(String)
    parent_model_id = Column(String, ForeignKey("robot_models.model_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bom_items = relationship("BOMItem", back_populates="robot_model", cascade="all, delete-orphan", foreign_keys="BOMItem.robot_model_id")
    assemblies = relationship("Assembly", back_populates="robot_model")
    parent_model = relationship("RobotModel", remote_side=[model_id])


class BOMItem(Base):
    """BOM items linking robot models to parts or sub-models"""
    __tablename__ = "bom_items"
    
    item_id = Column(String, primary_key=True, default=generate_uuid)
    robot_model_id = Column(String, ForeignKey("robot_models.model_id"), nullable=False)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=True)
    sub_model_id = Column(String, ForeignKey("robot_models.model_id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    is_optional = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraint to ensure either part_id or sub_model_id is set
    __table_args__ = (
        CheckConstraint('(part_id IS NOT NULL AND sub_model_id IS NULL) OR (part_id IS NULL AND sub_model_id IS NOT NULL)', 
                       name='check_part_or_submodel'),
    )
    
    # Relationships
    robot_model = relationship("RobotModel", back_populates="bom_items", foreign_keys=[robot_model_id])
    part = relationship("Part", back_populates="bom_items")
    sub_model = relationship("RobotModel", foreign_keys=[sub_model_id])


class Inventory(Base):
    """Inventory tracking for parts"""
    __tablename__ = "inventory"
    
    inventory_id = Column(String, primary_key=True, default=generate_uuid)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=False, unique=True)
    quantity_loose = Column(Integer, default=0)
    quantity_assembled = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    location = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    part = relationship("Part", back_populates="inventory")
    
    @property
    def available_quantity(self):
        """Calculate available quantity (loose minus reserved)"""
        return self.quantity_loose - self.quantity_reserved
    
    @property
    def total_quantity(self):
        """Calculate total quantity (loose plus assembled)"""
        return self.quantity_loose + self.quantity_assembled


class Assembly(Base):
    """Assembly records for robot builds"""
    __tablename__ = "assemblies"
    
    assembly_id = Column(String, primary_key=True, default=generate_uuid)
    robot_model_id = Column(String, ForeignKey("robot_models.model_id"), nullable=False)
    serial_number = Column(String, unique=True)
    status = Column(String, nullable=False, default="PLANNED")  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    assembly_date = Column(DateTime)
    completion_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    robot_model = relationship("RobotModel", back_populates="assemblies")
    consumed_parts = relationship("ConsumedPart", back_populates="assembly", cascade="all, delete-orphan")


class ConsumedPart(Base):
    """Parts consumed in assemblies"""
    __tablename__ = "consumed_parts"
    
    consumed_id = Column(String, primary_key=True, default=generate_uuid)
    assembly_id = Column(String, ForeignKey("assemblies.assembly_id"), nullable=False)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    consumed_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assembly = relationship("Assembly", back_populates="consumed_parts")
    part = relationship("Part")


class Order(Base):
    """Purchase orders for parts"""
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True, default=generate_uuid)
    order_number = Column(String, unique=True)
    status = Column(String, nullable=False, default="DRAFT")  # DRAFT, SUBMITTED, RECEIVED, CANCELLED
    supplier = Column(String)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_date = Column(DateTime)
    received_date = Column(DateTime)
    total_cost = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Items in purchase orders"""
    __tablename__ = "order_items"
    
    item_id = Column(String, primary_key=True, default=generate_uuid)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)
    received_quantity = Column(Integer, default=0)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    part = relationship("Part")


class Reservation(Base):
    """Part reservations for planned assemblies"""
    __tablename__ = "reservations"
    
    reservation_id = Column(String, primary_key=True, default=generate_uuid)
    robot_model_id = Column(String, ForeignKey("robot_models.model_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, CONSUMED, CANCELLED, EXPIRED
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    robot_model = relationship("RobotModel")
    reserved_parts = relationship("ReservedPart", back_populates="reservation", cascade="all, delete-orphan")


class ReservedPart(Base):
    """Parts reserved for a specific reservation"""
    __tablename__ = "reserved_parts"
    
    reserved_id = Column(String, primary_key=True, default=generate_uuid)
    reservation_id = Column(String, ForeignKey("reservations.reservation_id"), nullable=False)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    reservation = relationship("Reservation", back_populates="reserved_parts")
    part = relationship("Part")


class InventoryAudit(Base):
    """Audit trail for inventory changes"""
    __tablename__ = "inventory_audits"
    
    audit_id = Column(String, primary_key=True, default=generate_uuid)
    part_id = Column(String, ForeignKey("parts.part_id"), nullable=False)
    change_quantity = Column(Integer, nullable=False)
    change_type = Column(String, nullable=False)  # ADD, REMOVE, ADJUST, RESERVE, CONSUME
    reason = Column(String)
    resulting_quantity = Column(Integer)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    part = relationship("Part")