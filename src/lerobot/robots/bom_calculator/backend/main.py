"""
Main FastAPI application for BOM Calculator
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from config import settings
from database import db_manager, init_database
from api import inventory, assembly, orders, parts, robots
from api.websocket import websocket_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting BOM Calculator API...")
    await init_database()
    yield
    # Shutdown
    logger.info("Shutting down BOM Calculator API...")
    await db_manager.close()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(parts.router, prefix=f"{settings.api_prefix}/parts", tags=["Parts"])
app.include_router(robots.router, prefix=f"{settings.api_prefix}/robots", tags=["Robot Models"])
app.include_router(inventory.router, prefix=f"{settings.api_prefix}/inventory", tags=["Inventory"])
app.include_router(assembly.router, prefix=f"{settings.api_prefix}/assembly", tags=["Assembly"])
app.include_router(orders.router, prefix=f"{settings.api_prefix}/orders", tags=["Orders"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        await websocket_handler.handle_connection(websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/api/docs"
    }

# Serve static files (for frontend if needed)
# Uncomment when frontend is built
# app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )