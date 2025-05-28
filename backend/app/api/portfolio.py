from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.deps import get_db, get_current_user
from app.services.portfolio import PortfolioService
from app.core.exchange import get_exchange
from app.db.models import User

router = APIRouter()

@router.get("/portfolio")
async def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """Get current portfolio value and asset allocation."""
    portfolio_service = PortfolioService(db, exchange)
    portfolio_data = portfolio_service.get_portfolio_value(current_user.id)
    history = portfolio_service.get_portfolio_history(current_user.id)
    
    return {
        "totalValue": portfolio_data["totalValue"],
        "history": history,
        "assets": portfolio_data["assets"]
    }

@router.get("/trades/metrics")
async def get_trade_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """Get trading performance metrics."""
    portfolio_service = PortfolioService(db, exchange)
    return portfolio_service.get_trade_metrics(current_user.id)

@router.get("/trades/recent")
async def get_recent_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """Get recent trades."""
    portfolio_service = PortfolioService(db, exchange)
    return portfolio_service.get_recent_trades(current_user.id) 