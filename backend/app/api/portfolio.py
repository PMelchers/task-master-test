from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.deps import get_db, get_current_user
from app.services.portfolio import PortfolioService
from app.core.exchange import get_exchange
from app.db.models import User

router = APIRouter(prefix="/trades", tags=["trades"])

@router.get("/portfolio", response_model=Dict[str, Any], summary="Get current portfolio value and asset allocation")
async def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """
    Returns the current user's total portfolio value, value history, and asset allocation.
    """
    portfolio_service = PortfolioService(db, exchange)
    portfolio_data = portfolio_service.get_portfolio_value(current_user.id)
    history = portfolio_service.get_portfolio_history(current_user.id)
    return {
        "totalValue": portfolio_data["totalValue"],
        "history": history,
        "assets": portfolio_data["assets"]
    }

@router.get("/metrics", response_model=Dict[str, Any], summary="Get trading performance metrics")
async def get_trade_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """
    Returns trading performance metrics for the current user.
    """
    portfolio_service = PortfolioService(db, exchange)
    return portfolio_service.get_trade_metrics(current_user.id)

@router.get("/recent", response_model=List[Dict[str, Any]], summary="Get recent trades")
async def get_recent_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    exchange = Depends(get_exchange)
):
    """
    Returns a list of the current user's most recent trades.
    """
    portfolio_service = PortfolioService(db, exchange)
    return portfolio_service.get_recent_trades(current_user.id)