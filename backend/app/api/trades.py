from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.db.models import User, ScheduledTrade, Trade, TradeStatus
from app.schemas.trade import (
    ScheduledTradeCreate,
    ScheduledTradeUpdate,
    ScheduledTrade as ScheduledTradeSchema,
    Trade as TradeSchema
)

router = APIRouter(prefix="/trades", tags=["trades"])

@router.post("/scheduled", response_model=ScheduledTradeSchema)
async def create_scheduled_trade(
    trade: ScheduledTradeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate times
    if trade.buy_time >= trade.sell_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buy time must be before sell time"
        )
    
    if trade.buy_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buy time must be in the future"
        )
    
    # Create scheduled trade
    db_trade = ScheduledTrade(
        user_id=current_user.id,
        trading_pair=trade.trading_pair,
        amount=trade.amount,
        buy_time=trade.buy_time,
        sell_time=trade.sell_time,
        status=TradeStatus.PENDING
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@router.get("/scheduled", response_model=List[ScheduledTradeSchema])
async def get_scheduled_trades(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(ScheduledTrade).filter(ScheduledTrade.user_id == current_user.id).all()

@router.get("/scheduled/{trade_id}", response_model=ScheduledTradeSchema)
async def get_scheduled_trade(
    trade_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    trade = db.query(ScheduledTrade).filter(
        ScheduledTrade.id == trade_id,
        ScheduledTrade.user_id == current_user.id
    ).first()
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled trade not found"
        )
    return trade

@router.put("/scheduled/{trade_id}", response_model=ScheduledTradeSchema)
async def update_scheduled_trade(
    trade_id: int,
    trade_update: ScheduledTradeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_trade = db.query(ScheduledTrade).filter(
        ScheduledTrade.id == trade_id,
        ScheduledTrade.user_id == current_user.id
    ).first()
    if not db_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled trade not found"
        )
    
    # Update trade fields
    for field, value in trade_update.dict(exclude_unset=True).items():
        setattr(db_trade, field, value)
    
    db.commit()
    db.refresh(db_trade)
    return db_trade

@router.delete("/scheduled/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_trade(
    trade_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_trade = db.query(ScheduledTrade).filter(
        ScheduledTrade.id == trade_id,
        ScheduledTrade.user_id == current_user.id
    ).first()
    if not db_trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled trade not found"
        )
    
    db.delete(db_trade)
    db.commit()
    return None

@router.get("/history", response_model=List[TradeSchema])
async def get_trade_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Trade).join(ScheduledTrade).filter(
        ScheduledTrade.user_id == current_user.id
    ).all() 