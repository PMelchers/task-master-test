from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.db.models import TradeStatus

class ScheduledTradeBase(BaseModel):
    trading_pair: str = Field(..., description="Trading pair (e.g., 'BTC/USDT')")
    amount: float = Field(..., gt=0, description="Amount to trade")
    buy_time: datetime = Field(..., description="Scheduled buy time")
    sell_time: datetime = Field(..., description="Scheduled sell time")

class ScheduledTradeCreate(ScheduledTradeBase):
    pass

class ScheduledTradeUpdate(BaseModel):
    trading_pair: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    buy_time: Optional[datetime] = None
    sell_time: Optional[datetime] = None
    status: Optional[TradeStatus] = None

class TradeBase(BaseModel):
    order_id: str
    side: str
    amount: float
    price: float
    status: TradeStatus

class TradeCreate(TradeBase):
    scheduled_trade_id: int

class ScheduledTrade(ScheduledTradeBase):
    id: int
    user_id: int
    status: TradeStatus
    created_at: datetime
    trades: list[TradeBase] = []

    class Config:
        from_attributes = True

class Trade(TradeBase):
    id: int
    scheduled_trade_id: int
    executed_at: datetime

    class Config:
        from_attributes = True 