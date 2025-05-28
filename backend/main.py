from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Scheduled Trader API",
    description="API for managing scheduled cryptocurrency trades",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Scheduled Trader API"}

# Initialize components with error handling
async def initialize_components():
    try:
        # Import components here to avoid circular imports
        from app.db.database import engine
        from app.db.models import Base
        from app.core.trading_engine import ScheduledTradeEngine
        from app.services.websocket import websocket_manager
        from app.core.exchange import MEXCExchange
        from app.core.config import settings
        from app.api import auth, trades, websocket, portfolio

        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Initialize exchange and trading engine
        exchange = MEXCExchange(
            api_key=settings.MEXC_API_KEY,
            api_secret=settings.MEXC_API_SECRET
        )
        trading_engine = ScheduledTradeEngine()

        # Set exchange in WebSocket manager
        websocket_manager.set_exchange(exchange)

        # Include routers
        app.include_router(auth.router, prefix="/auth", tags=["auth"])
        app.include_router(trades.router, prefix="/trades", tags=["trades"])
        app.include_router(websocket.router, tags=["websocket"])
        app.include_router(portfolio.router, tags=["portfolio"])
        logger.info("Routers included successfully")

        # Start the trading engine
        await trading_engine.start()
        logger.info("Trading engine started successfully")

        # Start market data stream
        await websocket_manager.start_market_data_stream(["BTC/USDT", "ETH/USDT", "BNB/USDT"])
        logger.info("Market data stream started successfully")

    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        # Don't raise the exception to allow the server to start
        # The health check endpoint will indicate if components are working

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    await initialize_components()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on application shutdown."""
    try:
        from app.core.trading_engine import ScheduledTradeEngine
        from app.services.websocket import websocket_manager
        from app.core.exchange import MEXCExchange

        # Stop the trading engine
        await ScheduledTradeEngine().stop()
        logger.info("Trading engine stopped successfully")

        # Close exchange connection
        await MEXCExchange().close()
        logger.info("Exchange connection closed successfully")

        # Close all WebSocket connections
        await websocket_manager.close_all_connections()
        logger.info("All WebSocket connections closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://127.0.0.1:8084")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8084,
        log_level="debug",  # Changed to debug for more detailed logs
        reload=True  # Enable auto-reload for development
    ) 