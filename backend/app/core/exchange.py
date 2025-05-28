import ccxt.async_support as ccxt
from typing import Dict, List, Optional
from datetime import datetime
import time
from fastapi import HTTPException
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MEXCExchange:
    def __init__(self, api_key: str, api_secret: str):
        """Initialize MEXC exchange connection with API credentials."""
        self.exchange = ccxt.mexc({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'recvWindow': 60000,  # Increased from default 5000
                'adjustForTimeDifference': True
            }
        })
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _rate_limit(self):
        """Implement rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    async def validate_connection(self) -> bool:
        """Validate API connection and credentials."""
        try:
            self._rate_limit()
            await self.exchange.fetch_balance()
            return True
        except ccxt.AuthenticationError:
            raise HTTPException(
                status_code=401,
                detail="Invalid API credentials"
            )
        except Exception as e:
            logger.error(f"Connection validation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to MEXC"
            )

    async def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch current ticker data for a trading pair."""
        try:
            self._rate_limit()
            return await self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch ticker data for {symbol}"
            )

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """Fetch OHLCV (candlestick) data for a trading pair."""
        try:
            self._rate_limit()
            return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch OHLCV data for {symbol}"
            )

    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Fetch order book data for a trading pair."""
        try:
            self._rate_limit()
            return await self.exchange.fetch_order_book(symbol, limit)
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch order book for {symbol}"
            )

    async def create_market_order(self, symbol: str, side: str, amount: float) -> Dict:
        """Create a market order."""
        try:
            self._rate_limit()
            return await self.exchange.create_market_order(symbol, side, amount)
        except ccxt.InsufficientFunds:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds for order"
            )
        except Exception as e:
            logger.error(f"Error creating market order for {symbol}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create market order for {symbol}"
            )

    async def create_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Create a limit order."""
        try:
            self._rate_limit()
            return await self.exchange.create_limit_order(symbol, side, amount, price)
        except ccxt.InsufficientFunds:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds for order"
            )
        except Exception as e:
            logger.error(f"Error creating limit order for {symbol}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create limit order for {symbol}"
            )

    async def fetch_order(self, order_id: str, symbol: Optional[str] = None) -> Dict:
        """Fetch order status by ID."""
        try:
            self._rate_limit()
            return await self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch order {order_id}"
            )

    async def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict:
        """Cancel an existing order."""
        try:
            self._rate_limit()
            return await self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to cancel order {order_id}"
            )

    async def fetch_balance(self) -> Dict:
        """Fetch account balance."""
        try:
            self._rate_limit()
            return await self.exchange.fetch_balance()
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch account balance"
            )

    async def close(self):
        """Close the exchange connection."""
        await self.exchange.close()

def get_exchange():
    return MEXCExchange(api_key=settings.MEXC_API_KEY, api_secret=settings.MEXC_API_SECRET) 