import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import *

class TradingSimulator:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.capital = state_manager.state['capital']
        self.positions = state_manager.state['positions']
        self.trade_log = state_manager.state['trades']
        print(f"Simulator initialized with capital: {self.capital}")

    def simulate_day(self, date, stock_data, rules):
        """Simulate trading for a specific day"""
        day_trades = []
        
        print(f"Processing trades for date: {date}")
        
        for _, row in stock_data.iterrows():
            signal = self.process_trade_signal(row, rules)
            if signal != 'hold':
                try:
                    stock_name = row.get('Name of Company')
                    price = row.get('Holding Value in crores')
                    
                    if pd.isna(stock_name) or pd.isna(price) or price <= 0:
                        continue
                        
                    trade = self.execute_trade(
                        stock=stock_name,
                        price=float(price),
                        trade_type=signal,
                        quantity=int(INVESTMENT_PER_TRADE/float(price)),
                        date=date
                    )
                    if trade:
                        day_trades.append(trade)
                        print(f"Trade executed: {trade}")
                except Exception as e:
                    print(f"Error executing trade: {str(e)}")
                    continue
        
        return day_trades

    def process_trade_signal(self, row, rules):
        """Generate trading signals with higher probability of buys"""
        import random
        return random.choices(['buy', 'sell', 'hold'], weights=[0.4, 0.3, 0.3])[0]

    def execute_trade(self, stock, price, trade_type, quantity, date):
        """Execute a trade and log it"""
        try:
            trade_value = price * quantity
            profit = 0
            
            if trade_type == 'buy':
                if self.capital >= trade_value:
                    self.capital -= trade_value
                    self.positions[stock] = {
                        'quantity': quantity,
                        'entry_price': price
                    }
                else:
                    return None  # Not enough capital
            elif trade_type == 'sell':
                if stock in self.positions:
                    position = self.positions[stock]
                    profit = (price - position['entry_price']) * position['quantity']
                    self.capital += trade_value + profit
                    del self.positions[stock]
                else:
                    return None  # No position to sell
                    
            # Create trade record
            trade = {
                'date': date.isoformat() if isinstance(date, datetime) else date,
                'stock': stock,
                'type': trade_type,
                'price': float(price),
                'quantity': int(quantity),
                'value': float(trade_value),
                'profit': float(profit),
                'capital_remaining': float(self.capital)
            }
            
            # Log the trade
            self.trade_log.append(trade)
            print(f"Capital after trade: {self.capital}")
            return trade
            
        except Exception as e:
            print(f"Error in execute_trade: {str(e)}")
            return None

    def calculate_advanced_metrics(self):
        """Calculate and return performance metrics"""
        try:
            if not self.trade_log:
                return self._get_empty_metrics()
                
            df_trades = pd.DataFrame(self.trade_log)
            
            # Basic metrics
            total_trades = len(df_trades)
            profitable_trades = len(df_trades[df_trades['profit'] > 0])
            
            # Handle potential division by zero
            success_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate returns and Sharpe ratio
            df_trades['returns'] = df_trades['profit'] / df_trades['value']
            returns = df_trades['returns'].replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(returns) > 1:
                sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std() if returns.std() != 0 else 0)
            else:
                sharpe_ratio = 0
            
            # Calculate drawdown
            capital_over_time = df_trades['capital_remaining']
            rolling_max = capital_over_time.expanding().max()
            drawdowns = (capital_over_time - rolling_max) / rolling_max
            max_drawdown = float(drawdowns.min() * 100) if not drawdowns.empty else 0

            # Win/Loss ratio
            winning_trades = df_trades[df_trades['profit'] > 0]['profit'].sum()
            losing_trades = abs(df_trades[df_trades['profit'] < 0]['profit'].sum())
            win_loss_ratio = float(winning_trades / losing_trades) if losing_trades != 0 else float('inf')

            metrics = {
                'total_trades': int(total_trades),
                'profitable_trades': int(profitable_trades),
                'success_rate': float(success_rate),
                'final_capital': float(self.capital),
                'profit_loss': float(self.capital - self.state_manager.initial_capital),
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'win_loss_ratio': float(win_loss_ratio)
            }
            print(f"Calculated metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return self._get_empty_metrics()

    def _get_empty_metrics(self):
        return {metric: 0.0 for metric in METRICS_TO_TRACK} 