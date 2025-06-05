from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import Trade, ScheduledTrade, User
from app.core.exchange import MEXCExchange
from app.core.config import settings

class PortfolioService:
    def __init__(self, db: Session, exchange: MEXCExchange):
        self.db = db
        self.exchange = exchange

    def get_portfolio_value(self, user_id: int) -> Dict:
        """Calculate total portfolio value and asset allocation."""
        # Get all executed trades for the user via ScheduledTrade
        trades = (
            self.db.query(Trade)
            .join(ScheduledTrade, Trade.scheduled_trade_id == ScheduledTrade.id)
            .filter(
                ScheduledTrade.user_id == user_id,
                Trade.status == 'executed'
            )
            .all()
        )

        # Calculate current holdings
        holdings: Dict[str, float] = {}
        for trade in trades:
            symbol = trade.symbol
            if trade.side == 'buy':
                holdings[symbol] = holdings.get(symbol, 0) + trade.amount
            else:
                holdings[symbol] = holdings.get(symbol, 0) - trade.amount

        # Get current prices
        total_value = 0
        assets = []
        for symbol, amount in holdings.items():
            if amount > 0:
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    value = amount * ticker['last']
                    total_value += value
                    assets.append({
                        'symbol': symbol,
                        'value': value,
                        'percentage': 0  # Will be calculated after total is known
                    })
                except Exception as e:
                    print(f"Error fetching price for {symbol}: {e}")

        # Calculate percentages
        if total_value > 0:
            for asset in assets:
                asset['percentage'] = (asset['value'] / total_value) * 100

        return {
            'totalValue': total_value,
            'assets': assets
        }

    def get_portfolio_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get portfolio value history over time."""
        # Get all executed trades within the time period via ScheduledTrade
        start_date = datetime.utcnow() - timedelta(days=days)
        trades = (
            self.db.query(Trade)
            .join(ScheduledTrade, Trade.scheduled_trade_id == ScheduledTrade.id)
            .filter(
                ScheduledTrade.user_id == user_id,
                Trade.status == 'executed',
                Trade.executed_at >= start_date  # <-- fix here
            )
            .order_by(Trade.executed_at)  # <-- and here
            .all()
        )

        # Calculate portfolio value at each trade
        history = []
        holdings: Dict[str, float] = {}
        current_value = 0

        for trade in trades:
            symbol = trade.symbol
            if trade.side == 'buy':
                holdings[symbol] = holdings.get(symbol, 0) + trade.amount
            else:
                holdings[symbol] = holdings.get(symbol, 0) - trade.amount

            # Calculate value at this point
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                value = holdings.get(symbol, 0) * ticker['last']
                current_value += value
                history.append({
                    'timestamp': trade.executed_at.isoformat(),  # <-- and here
                    'value': current_value
                })
            except Exception as e:
                print(f"Error fetching historical price for {symbol}: {e}")

        return history

    def get_trade_metrics(self, user_id: int) -> Dict:
        """Calculate trading performance metrics."""
        trades = (
            self.db.query(Trade)
            .join(ScheduledTrade, Trade.scheduled_trade_id == ScheduledTrade.id)
            .filter(
                ScheduledTrade.user_id == user_id,
                Trade.status == 'executed'
            )
            .all()
        )

        total_trades = len(trades)
        successful_trades = sum(1 for t in trades if t.profit > 0)
        win_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        total_profit = sum(t.profit for t in trades)
        average_return = (total_profit / total_trades) if total_trades > 0 else 0

        return {
            'totalTrades': total_trades,
            'successfulTrades': successful_trades,
            'winRate': win_rate,
            'averageReturn': average_return,
            'totalProfit': total_profit
        }

    def get_recent_trades(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent trades for the user."""
        trades = (
            self.db.query(Trade)
            .join(ScheduledTrade, Trade.scheduled_trade_id == ScheduledTrade.id)
            .filter(ScheduledTrade.user_id == user_id)
            .order_by(Trade.executed_at.desc())  # <-- fix here
            .limit(limit)
            .all()
        )

        return [{
            'id': str(trade.id),
            'symbol': trade.symbol,
            'side': trade.side,
            'amount': trade.amount,
            'price': trade.executed_price,
            'timestamp': trade.executed_at.isoformat(),  # <-- and here
            'status': trade.status
        } for trade in trades]