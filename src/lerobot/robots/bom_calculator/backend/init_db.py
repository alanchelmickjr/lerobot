"""
Simplified database initialization script for BOM Calculator
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_manager
from models import Part, RobotModel, BOMItem, Inventory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_sample_parts(session: AsyncSession):
    """Create sample parts in the database"""
    logger.info("Creating sample parts...")
    
    parts = [
        Part(
            part_id="SERVO-001",
            name="Servo Motor",
            description="High-torque servo motor",
            category="Motors",
            unit_cost=15.50,
            supplier="ServoTech",
            lead_time_days=7
        ),
        Part(
            part_id="BOARD-001",
            name="Control Board",
            description="Main control board",
            category="Electronics",
            unit_cost=45.00,
            supplier="ElectroSupply",
            lead_time_days=10
        ),
        Part(
            part_id="FRAME-001",
            name="Aluminum Frame",
            description="Main robot frame",
            category="Structural",
            unit_cost=25.00,
            supplier="MetalWorks",
            lead_time_days=5
        ),
        Part(
            part_id="SENSOR-001",
            name="Distance Sensor",
            description="Ultrasonic distance sensor",
            category="Sensors",
            unit_cost=8.50,
            supplier="SensorCo",
            lead_time_days=3
        ),
        Part(
            part_id="WHEEL-001",
            name="Robot Wheel",
            description="Rubber wheel with encoder",
            category="Mobility",
            unit_cost=12.00,
            supplier="WheelTech",
            lead_time_days=4
        ),
        Part(
            part_id="BATTERY-001",
            name="LiPo Battery",
            description="11.1V 2200mAh battery",
            category="Power",
            unit_cost=35.00,
            supplier="PowerSupply",
            lead_time_days=5
        ),
    ]
    
    for part in parts:
        session.add(part)
    
    await session.commit()
    logger.info(f"✓ Created {len(parts)} sample parts")


async def create_robot_models(session: AsyncSession):
    """Create sample robot models"""
    logger.info("Creating robot models...")
    
    models = [
        RobotModel(
            model_id="BASIC-ROBOT-V1",
            name="Basic Robot v1",
            description="Entry-level educational robot",
            version="1.0",
            is_active=True
        ),
        RobotModel(
            model_id="ADVANCED-ROBOT-V1",
            name="Advanced Robot v1",
            description="Advanced robot with sensors",
            version="1.0",
            is_active=True
        ),
    ]
    
    for model in models:
        session.add(model)
    
    await session.commit()
    logger.info(f"✓ Created {len(models)} robot models")


async def create_bom_items(session: AsyncSession):
    """Create BOM items linking parts to robot models"""
    logger.info("Creating BOM items...")
    
    bom_items = [
        # Basic Robot BOM
        BOMItem(
            robot_model_id="BASIC-ROBOT-V1",
            part_id="SERVO-001",
            quantity=2,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="BASIC-ROBOT-V1",
            part_id="BOARD-001",
            quantity=1,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="BASIC-ROBOT-V1",
            part_id="FRAME-001",
            quantity=1,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="BASIC-ROBOT-V1",
            part_id="WHEEL-001",
            quantity=2,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="BASIC-ROBOT-V1",
            part_id="BATTERY-001",
            quantity=1,
            is_optional=False
        ),
        # Advanced Robot BOM
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="SERVO-001",
            quantity=4,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="BOARD-001",
            quantity=1,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="FRAME-001",
            quantity=1,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="SENSOR-001",
            quantity=3,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="WHEEL-001",
            quantity=2,
            is_optional=False
        ),
        BOMItem(
            robot_model_id="ADVANCED-ROBOT-V1",
            part_id="BATTERY-001",
            quantity=1,
            is_optional=False
        ),
    ]
    
    for item in bom_items:
        session.add(item)
    
    await session.commit()
    logger.info(f"✓ Created {len(bom_items)} BOM items")


async def create_initial_inventory(session: AsyncSession):
    """Create initial inventory records"""
    logger.info("Creating initial inventory...")
    
    inventory_items = [
        Inventory(
            part_id="SERVO-001",
            quantity_loose=20,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=10
        ),
        Inventory(
            part_id="BOARD-001",
            quantity_loose=10,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=5
        ),
        Inventory(
            part_id="FRAME-001",
            quantity_loose=15,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=5
        ),
        Inventory(
            part_id="SENSOR-001",
            quantity_loose=25,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=10
        ),
        Inventory(
            part_id="WHEEL-001",
            quantity_loose=30,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=15
        ),
        Inventory(
            part_id="BATTERY-001",
            quantity_loose=8,
            quantity_assembled=0,
            quantity_reserved=0,
            reorder_point=5
        ),
    ]
    
    for item in inventory_items:
        session.add(item)
    
    await session.commit()
    logger.info(f"✓ Created {len(inventory_items)} inventory records")


async def initialize_database():
    """Main database initialization function"""
    logger.info("=" * 60)
    logger.info("BOM Calculator Database Initialization (Simplified)")
    logger.info("=" * 60)
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        await db_manager.create_tables()
        logger.info("✓ Database tables created")
        
        # Add sample data
        async with db_manager.get_session() as session:
            await create_sample_parts(session)
            await create_robot_models(session)
            await create_bom_items(session)
            await create_initial_inventory(session)
        
        logger.info("=" * 60)
        logger.info("Database initialization complete!")
        logger.info("Sample data has been added successfully.")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise


async def reset_database():
    """Reset database (drop and recreate all tables)"""
    logger.warning("=" * 60)
    logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
    logger.warning("=" * 60)
    
    try:
        # Drop existing tables
        logger.info("Dropping existing tables...")
        await db_manager.drop_tables()
        logger.info("✓ Tables dropped")
        
        # Reinitialize
        await initialize_database()
        
    except Exception as e:
        logger.error(f"Error during database reset: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # Reset database if --reset flag is provided
        asyncio.run(reset_database())
    else:
        # Normal initialization
        asyncio.run(initialize_database())