from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.db.models import User
from app.db.database import SessionLocal
from app.services.websocket import websocket_manager
import asyncio
import logging

websocket_router = APIRouter(tags=["websocket"])
market_data_router = APIRouter(prefix="/market-data", tags=["market-data"])

logger = logging.getLogger(__name__)

@websocket_router.websocket("/ws/market-data")
async def market_data_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time market data."""
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        await websocket.close(code=1008)
        return

    await websocket_manager.connect(websocket, 'market_data')
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, 'market_data')
    except Exception as e:
        logger.error(f"Error in market data WebSocket: {str(e)}")
        websocket_manager.disconnect(websocket, 'market_data')

@websocket_router.websocket("/ws/trade-updates")
async def trade_updates_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time trade updates."""
    await websocket.accept()
    token = websocket.query_params.get("token")
    logger.info(f"Received token: {token}")
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
    try:
        while True:
            await asyncio.sleep(1)
    except (WebSocketDisconnect, asyncio.CancelledError):
        websocket_manager.disconnect(websocket, 'trade_updates')
    except Exception as e:
        logger.error(f"Error in trade updates WebSocket: {str(e)}")
        websocket_manager.disconnect(websocket, 'trade_updates')

@websocket_router.websocket("/ws/auth")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user is None:
        await websocket.close(code=1008)
        return

    # Now you can proceed with your WebSocket logic for the authenticated user
    try:
        while True:
            data = await websocket.receive_text()
            # handle data...
    except WebSocketDisconnect:
        pass

@market_data_router.get("/trading-pairs")
async def get_trading_pairs():
    # Replace this with your actual trading pairs source
    trading_pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    return JSONResponse(content=trading_pairs)