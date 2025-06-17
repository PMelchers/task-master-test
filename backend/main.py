from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.core.exchange import exchange_instance
import logging

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
    allow_origins=["http://localhost:3000"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Welcome to Scheduled Trader API"}

async def initialize_components():
    try:
        from app.db.database import engine
        from app.db.models import Base
        from app.api import auth, trades, portfolio, websocket, market_data, strategy  # Import strategy

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Include routers
        app.include_router(auth.router)
        app.include_router(trades.router)
        app.include_router(portfolio.router)
        app.include_router(websocket.websocket_router)
        app.include_router(market_data.router)
        app.include_router(strategy.router)  # Include strategy router
        logger.info("Routers included successfully")

        # The following is commented out for now:
        # from app.core.trading_engine import ScheduledTradeEngine
        # from app.services.websocket import websocket_manager
        # from app.core.exchange import MEXCExchange
        # from app.core.config import settings
        # exchange = MEXCExchange(...)
        # trading_engine = ScheduledTradeEngine()
        # websocket_manager.set_exchange(exchange)
        # await trading_engine.start()
        # await websocket_manager.start_market_data_stream(["BTC/USDT", "ETH/USDT", "BNB/USDT"])
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        # Don't raise the exception to allow the server to start

@app.on_event("startup")
async def startup_event():
    await initialize_components()

@app.on_event("shutdown")
async def shutdown_event():
    try:
        from app.services.websocket import websocket_manager
        await exchange_instance.close()
        logger.info("Exchange connection closed successfully")

        await websocket_manager.close_all_connections()
        logger.info("All WebSocket connections closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on http://0.0.0.0:8084")
    print("MAIN.PY STARTED")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8084,
        log_level="debug",
    )