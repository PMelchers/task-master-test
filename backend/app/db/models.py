from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Association table for many-to-many User <-> Strategy
user_strategies = Table(
    'user_strategies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('strategy_id', Integer, ForeignKey('strategies.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key_encrypted = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scheduled_trades = relationship("ScheduledTrade", back_populates="user")
    strategies = relationship("Strategy", secondary=user_strategies, back_populates="users")

class ScheduledTrade(Base):
    __tablename__ = "scheduled_trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trading_pair = Column(String)
    buy_time = Column(DateTime)
    sell_time = Column(DateTime)
    amount = Column(Float)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="scheduled_trades")
    trades = relationship("Trade", back_populates="scheduled_trade")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    scheduled_trade_id = Column(Integer, ForeignKey("scheduled_trades.id"))
    order_id = Column(String)
    side = Column(String)  # "buy" or "sell"
    amount = Column(Float)
    price = Column(Float)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    scheduled_trade = relationship("ScheduledTrade", back_populates="trades")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    technical_indicators = Column(String)  # JSON string of technical indicators

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship("User", secondary=user_strategies, back_populates="strategies")