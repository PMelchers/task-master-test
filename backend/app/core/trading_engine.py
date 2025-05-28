from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import logging
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.core.exchange import MEXCExchange
from app.db.models import ScheduledTrade, Trade, TradeStatus
from app.db.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScheduledTradeEngine:
    def __init__(self):
        """Initialize the scheduled trading engine."""
        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
        }
        
        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        # Create scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone='UTC'
        )
        
        # Initialize exchange connection
        self.exchange = MEXCExchange(
            api_key=settings.MEXC_API_KEY,
            api_secret=settings.MEXC_API_SECRET
        )

    async def start(self):
        """Start the trading engine."""
        try:
            # Validate exchange connection
            await self.exchange.validate_connection()
            
            # Start the scheduler
            self.scheduler.start()
            
            # Load existing scheduled trades
            await self.load_scheduled_trades()
            
            logger.info("Scheduled trading engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start trading engine: {str(e)}")
            raise

    async def load_scheduled_trades(self):
        """Load existing scheduled trades from database."""
        db = next(get_db())
        try:
            # Get all pending scheduled trades
            scheduled_trades = db.query(ScheduledTrade).filter(
                ScheduledTrade.status == TradeStatus.PENDING
            ).all()
            
            # Schedule each trade
            for trade in scheduled_trades:
                await self.schedule_trade(trade)
                
            logger.info(f"Loaded {len(scheduled_trades)} scheduled trades")
        except Exception as e:
            logger.error(f"Error loading scheduled trades: {str(e)}")
            raise
        finally:
            db.close()

    async def schedule_trade(self, trade: ScheduledTrade):
        """Schedule a new trade."""
        try:
            # Schedule buy order
            self.scheduler.add_job(
                self.execute_buy_order,
                'date',
                run_date=trade.buy_time,
                args=[trade.id],
                id=f"buy_{trade.id}",
                replace_existing=True
            )
            
            # Schedule sell order
            self.scheduler.add_job(
                self.execute_sell_order,
                'date',
                run_date=trade.sell_time,
                args=[trade.id],
                id=f"sell_{trade.id}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled trade {trade.id} for {trade.trading_pair}")
        except Exception as e:
            logger.error(f"Error scheduling trade {trade.id}: {str(e)}")
            raise

    async def execute_buy_order(self, trade_id: int):
        """Execute a buy order for a scheduled trade."""
        db = next(get_db())
        try:
            # Get trade details
            trade = db.query(ScheduledTrade).filter(
                ScheduledTrade.id == trade_id
            ).first()
            
            if not trade or trade.status != TradeStatus.PENDING:
                logger.warning(f"Trade {trade_id} not found or not pending")
                return
            
            # Execute market buy order
            order = await self.exchange.create_market_order(
                trade.trading_pair,
                'buy',
                trade.amount
            )
            
            # Create trade record
            trade_record = Trade(
                scheduled_trade_id=trade.id,
                order_id=order['id'],
                side='buy',
                amount=trade.amount,
                price=order['price'],
                status=TradeStatus.COMPLETED,
                executed_at=datetime.utcnow()
            )
            
            db.add(trade_record)
            db.commit()
            
            logger.info(f"Executed buy order for trade {trade_id}")
        except Exception as e:
            logger.error(f"Error executing buy order for trade {trade_id}: {str(e)}")
            # Update trade status to failed
            trade.status = TradeStatus.FAILED
            db.commit()
        finally:
            db.close()

    async def execute_sell_order(self, trade_id: int):
        """Execute a sell order for a scheduled trade."""
        db = next(get_db())
        try:
            # Get trade details
            trade = db.query(ScheduledTrade).filter(
                ScheduledTrade.id == trade_id
            ).first()
            
            if not trade or trade.status != TradeStatus.PENDING:
                logger.warning(f"Trade {trade_id} not found or not pending")
                return
            
            # Execute market sell order
            order = await self.exchange.create_market_order(
                trade.trading_pair,
                'sell',
                trade.amount
            )
            
            # Create trade record
            trade_record = Trade(
                scheduled_trade_id=trade.id,
                order_id=order['id'],
                side='sell',
                amount=trade.amount,
                price=order['price'],
                status=TradeStatus.COMPLETED,
                executed_at=datetime.utcnow()
            )
            
            # Update scheduled trade status
            trade.status = TradeStatus.COMPLETED
            
            db.add(trade_record)
            db.commit()
            
            logger.info(f"Executed sell order for trade {trade_id}")
        except Exception as e:
            logger.error(f"Error executing sell order for trade {trade_id}: {str(e)}")
            # Update trade status to failed
            trade.status = TradeStatus.FAILED
            db.commit()
        finally:
            db.close()

    async def cancel_scheduled_trade(self, trade_id: int):
        """Cancel a scheduled trade."""
        try:
            # Remove scheduled jobs
            self.scheduler.remove_job(f"buy_{trade_id}")
            self.scheduler.remove_job(f"sell_{trade_id}")
            
            # Update trade status in database
            db = next(get_db())
            trade = db.query(ScheduledTrade).filter(
                ScheduledTrade.id == trade_id
            ).first()
            
            if trade:
                trade.status = TradeStatus.CANCELLED
                db.commit()
            
            logger.info(f"Cancelled scheduled trade {trade_id}")
        except Exception as e:
            logger.error(f"Error cancelling trade {trade_id}: {str(e)}")
            raise
        finally:
            db.close()

    async def stop(self):
        """Stop the trading engine."""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduled trading engine stopped")
        except Exception as e:
            logger.error(f"Error stopping trading engine: {str(e)}")
            raise 