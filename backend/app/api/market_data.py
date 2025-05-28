from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.db.models import User
from app.core.exchange import MEXCExchange
from app.services.market_data import MarketDataService
from app.core.config import settings

router = APIRouter(prefix="/market-data", tags=["market-data"])

def get_market_data_service() -> MarketDataService:
    """Dependency to get market data service instance."""
    exchange = MEXCExchange(
        api_key=settings.MEXC_API_KEY,
        api_secret=settings.MEXC_API_SECRET
    )
    return MarketDataService(exchange)

@router.get("/ticker/{symbol}")
async def get_ticker(
    symbol: str,
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current ticker data for a symbol."""
    return await market_data_service.get_ticker(symbol)

@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    timeframe: str = Query('1h', description="Timeframe for OHLCV data"),
    limit: int = Query(100, description="Number of candles to return"),
    since: Optional[datetime] = None,
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get OHLCV data for a symbol."""
    return await market_data_service.get_ohlcv(symbol, timeframe, limit, since)

@router.get("/order-book/{symbol}")
async def get_order_book(
    symbol: str,
    limit: int = Query(20, description="Number of orders to return"),
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get order book data for a symbol."""
    return await market_data_service.get_order_book(symbol, limit)

@router.get("/trading-pairs")
async def get_trading_pairs(
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available trading pairs."""
    return await market_data_service.get_available_trading_pairs()

@router.get("/summary/{symbol}")
async def get_market_summary(
    symbol: str,
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive market summary for a symbol."""
    return await market_data_service.get_market_summary(symbol)

@router.get("/cached/{symbol}")
async def get_cached_market_data(
    symbol: str,
    since: Optional[datetime] = None,
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get cached market data from the database."""
    return await market_data_service.get_cached_market_data(db, symbol, since) 