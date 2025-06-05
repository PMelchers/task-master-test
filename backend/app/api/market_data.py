from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime
from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.db.models import User
from app.core.exchange import MEXCExchange
from app.services.market_data import MarketDataService
from app.core.config import settings
from app.core.deps import get_exchange
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/market-data", tags=["market-data"])

def get_market_data_service() -> MarketDataService:
    """Dependency to get market data service instance."""
    exchange = get_exchange()
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

@router.get("/summary/{symbol:path}")
async def get_market_summary(
    symbol: str,
    market_data_service: MarketDataService = Depends(get_market_data_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive market summary for a symbol."""
    try:
        logger.info(f"Fetching ticker for {symbol}")
        ticker = await market_data_service.exchange.fetch_ticker(symbol)
        logger.info(f"Ticker for {symbol}: {ticker}")
        order_book = await market_data_service.exchange.fetch_order_book(symbol, limit=5)
        logger.info(f"Order book for {symbol}: {order_book}")
    except Exception as e:
        logger.error(f"Error fetching market summary for {symbol}: {str(e)}")
        return {
            'symbol': symbol,
            'last_price': 0,
            '24h_high': 0,
            '24h_low': 0,
            '24h_volume': 0,
            'bid': 0,
            'ask': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
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

async def get_market_summary(self, symbol: str) -> Dict:
    """Get only the fields used by the frontend from MEXC."""
    try:
        ticker = await self.exchange.fetch_ticker(symbol)
        order_book = await self.exchange.fetch_order_book(symbol, limit=5)

        return {
            'symbol': symbol,
            'last_price': ticker.get('last', 0.0),
            '24h_high': ticker.get('high', 0.0),
            '24h_low': ticker.get('low', 0.0),
            '24h_volume': ticker.get('quoteVolume', 0.0),
            'bid': order_book['bids'][0][0] if order_book.get('bids') else None,
            'ask': order_book['asks'][0][0] if order_book.get('asks') else None,
            'timestamp': datetime.utcnow().isoformat(),
            'order_book': {
                'symbol': order_book.get('symbol', symbol),
                'bids': order_book.get('bids', []),
                'asks': order_book.get('asks', []),
                'timestamp': order_book.get('timestamp'),
                'datetime': order_book.get('datetime'),
                'nonce': order_book.get('nonce'),
            }
        }
    except Exception as e:
        logger.error(f"Error fetching market summary for {symbol}: {str(e)}")
        return {
            'symbol': symbol,
            'last_price': 0.0,
            '24h_high': 0.0,
            '24h_low': 0.0,
            '24h_volume': 0.0,
            'bid': None,
            'ask': None,
            'timestamp': datetime.utcnow().isoformat(),
            'order_book': {
                'symbol': symbol,
                'bids': [],
                'asks': [],
                'timestamp': None,
                'datetime': None,
                'nonce': None,
            }
        }