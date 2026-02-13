"""
Consensus AI - Multi-Agent Investment Committee
FastAPI Backend Entry Point
"""
import sys
import os
import io

# Force UTF-8 encoding BEFORE any other imports to prevent UnicodeEncodeError on Windows
if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'encoding') and sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import traceback
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add current directory (backend) to sys.path so imports like 'from api...' work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes import router
from api.websocket import websocket_endpoint
from config.settings import settings
from api.paid_service import router as paid_service_router
from api.zk_routes import router as zk_router
from execution.payment_manager import payment_manager
from execution.budget_manager import budget_manager
from execution.bite_manager import bite_manager
from agents.virtuals_agent import virtuals_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Consensus AI",
    description="Multi-Agent Investment Committee - AI agents debate before trading",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST routes
app.include_router(router)
app.include_router(paid_service_router)
app.include_router(zk_router)

# WebSocket endpoint
app.add_websocket_route("/ws/debate", websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Consensus AI",
        "description": "Multi-Agent Investment Committee",
        "version": "1.0.0",
        "docs": "/docs",
        "payment_system": payment_manager.mode,
        "bite_status": "active"
    }


@app.post("/api/zk/virtuals/analysis")
async def trigger_virtuals_analysis(request: Dict[str, str]):
    """Triggers an analysis via the Virtuals G.A.M.E. wrapper."""
    symbol = request.get("symbol", settings.default_symbol)
    result = await virtuals_agent.run_analysis(symbol)
    return {"status": "success", "result": result}


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    try:
        print("Consensus AI starting up...")
        print(f"Default symbol: {settings.default_symbol}")
        print(f"Max leverage: {settings.max_leverage}x")
        print(f"API running at http://{settings.host}:{settings.port}")
        
        # Initialize Systems
        await payment_manager.initialize()
        logger.info("Payment Manager initialized.")
        logger.info(f"Budget Manager Loaded. Total Spend: ${budget_manager.total_spend}")
        logger.info(f"BITE Manager Initialized. Pending Txs: {len(bite_manager.encrypted_pool)}")
    except Exception as e:
        logger.error(f"FATAL STARTUP ERROR: {e}")
        logger.error(traceback.format_exc())


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    try:
        from agents.debate_engine import debate_engine
        await debate_engine.stop()
    except ImportError:
        pass
    print("Consensus AI shutting down...")


if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=False
        )
    except Exception as e:
        print(f"CRITICAL: Uvicorn failed to start: {e}")
        traceback.print_exc()
