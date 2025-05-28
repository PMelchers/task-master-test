from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.core.exchange import MEXCExchange
from app.db.database import get_db
from app.db.models import MarketData
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self, exchange: MEXCExchange):
        self.exchange = exchange

    async def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol."""
        return await self.exchange.fetch_ticker(symbol)

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """Get OHLCV data for a symbol."""
        return await self.exchange.fetch_ohlcv(symbol, timeframe, limit)

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Get order book data for a symbol."""
        return await self.exchange.fetch_order_book(symbol, limit)

    async def cache_market_data(self, db: Session, symbol: str) -> None:
        """Cache market data in the database."""
        try:
            # Fetch current market data
            ticker = await self.exchange.fetch_ticker(symbol)
            
            # Create market data record
            market_data = MarketData(
                symbol=symbol,
                price=ticker['last'],
                timestamp=datetime.utcnow(),
                volume=ticker['quoteVolume'],
                technical_indicators={}  # Can be populated with calculated indicators
            )
            
            # Save to database
            db.add(market_data)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error caching market data for {symbol}: {str(e)}")
            db.rollback()
            raise

    async def get_cached_market_data(
        self,
        db: Session,
        symbol: str,
        since: Optional[datetime] = None
    ) -> List[MarketData]:
        """Get cached market data from the database."""
        query = db.query(MarketData).filter(MarketData.symbol == symbol)
        
        if since:
            query = query.filter(MarketData.timestamp >= since)
            
        return query.order_by(MarketData.timestamp.desc()).all()

    async def update_market_data_cache(self, db: Session, symbols: List[str]) -> None:
        """Update market data cache for multiple symbols."""
        for symbol in symbols:
            await self.cache_market_data(db, symbol)

    async def get_available_trading_pairs(self) -> List[str]:
        """Get list of available trading pairs."""
        try:
            markets = await self.exchange.fetch_markets()
            return [market['symbol'] for market in markets if market['active']]
        except Exception as e:
            logger.error(f"Error fetching trading pairs: {str(e)}")
            raise

    async def get_market_summary(self, symbol: str) -> Dict:
        """Get comprehensive market summary for a symbol."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            order_book = await self.exchange.fetch_order_book(symbol, limit=5)
            
            return {
                'symbol': symbol,
                'last_price': ticker['last'],
                '24h_high': ticker['high'],
                '24h_low': ticker['low'],
                '24h_volume': ticker['quoteVolume'],
                'bid': order_book['bids'][0][0] if order_book['bids'] else None,
                'ask': order_book['asks'][0][0] if order_book['asks'] else None,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching market summary for {symbol}: {str(e)}")
            raise 