from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.auth import get_current_active_user
from app.db.models import User
from app.services.websocket import websocket_manager
import asyncio
import logging

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

@router.websocket("/ws/market-data")
async def market_data_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_active_user)
):
    """WebSocket endpoint for real-time market data."""
    await websocket_manager.connect(websocket, 'market_data')
    try:
        while True:
            # Keep the connection alive and handle client messages
            data = await websocket.receive_text()
            # Handle any client messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, 'market_data')
    except Exception as e:
        logger.error(f"Error in market data WebSocket: {str(e)}")
        websocket_manager.disconnect(websocket, 'market_data')

@router.websocket("/ws/trade-updates")
async def trade_updates_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_active_user)
):
    """WebSocket endpoint for real-time trade updates."""
    await websocket_manager.connect(websocket, 'trade_updates')
    try:
        while True:
            # Keep the connection alive and handle client messages
            data = await websocket.receive_text()
            # Handle any client messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, 'trade_updates')
    except Exception as e:
        logger.error(f"Error in trade updates WebSocket: {str(e)}")
        websocket_manager.disconnect(websocket, 'trade_updates') 