from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List, Set
import json
import logging
from datetime import datetime
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exchange import MEXCExchange
from app.db.database import get_db, SessionLocal
from app.db.models import Trade, TradeStatus, User

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'market_data': set(),
            'trade_updates': set()
        }
        self.exchange = None

    def set_exchange(self, exchange: MEXCExchange):
        self.exchange = exchange

    async def connect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].add(websocket)
        logger.info(f"New {client_type} WebSocket connection established")

    def disconnect(self, websocket: WebSocket, client_type: str):
        self.active_connections[client_type].remove(websocket)
        logger.info(f"{client_type} WebSocket connection closed")

    async def broadcast_market_data(self, data: dict):
        """Broadcast market data to all connected clients."""
        for connection in self.active_connections['market_data']:
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(connection, 'market_data')
            except Exception as e:
                logger.error(f"Error broadcasting market data: {str(e)}")

    async def broadcast_trade_update(self, data: dict):
        """Broadcast trade updates to all connected clients."""
        for connection in self.active_connections['trade_updates']:
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(connection, 'trade_updates')
            except Exception as e:
                logger.error(f"Error broadcasting trade update: {str(e)}")

    async def start_market_data_stream(self, symbols: List[str]):
        """Start streaming market data for specified symbols."""
        if not self.exchange:
            raise ValueError("Exchange not initialized")

        while True:
            try:
                for symbol in symbols:
                    ticker = await self.exchange.fetch_ticker(symbol)
                    data = {
                        'type': 'market_data',
                        'symbol': symbol,
                        'data': {
                            'price': ticker['last'],
                            'volume': ticker['quoteVolume'],
                            'high': ticker['high'],
                            'low': ticker['low'],
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    }
                    await self.broadcast_market_data(data)
            except Exception as e:
                logger.error(f"Error in market data stream: {str(e)}")
                continue

    async def monitor_trade_status(self, trade_id: int):
        """Monitor and broadcast trade status updates."""
        db = next(get_db())
        try:
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                return

            data = {
                'type': 'trade_update',
                'trade_id': trade_id,
                'status': trade.status,
                'executed_at': trade.executed_at.isoformat() if trade.executed_at else None,
                'price': trade.price,
                'amount': trade.amount
            }
            await self.broadcast_trade_update(data)
        except Exception as e:
            logger.error(f"Error monitoring trade status: {str(e)}")
        finally:
            db.close()

# Create global WebSocket manager instance
websocket_manager = WebSocketManager()

# Define the router at the top of the file if not already present
websocket_router = APIRouter(tags=["websocket"])

@websocket_router.websocket("/ws/trade-updates")
async def trade_updates_websocket(websocket: WebSocket):
    await websocket.accept()  # Accept here, only once!
    # ... authentication logic ...
    token = None  # Extract token from the request
    if not token:
        logger.warning("No token provided")
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        logger.info(f"Decoded payload: {payload}")
        username = payload.get("sub")
        if username is None:
            logger.warning("No username in token")
            await websocket.close(code=1008)
            return
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        logger.warning(f"User not found: {username}")
        await websocket.close(code=1008)
        return

    await websocket_manager.connect(websocket, 'trade_updates')
    # ... rest of your logic ...