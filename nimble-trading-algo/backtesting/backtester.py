"""
Backtesting Engine
Pre-training module that simulates trading strategies on historical data.
Helps identify optimal parameters before live trading.
"""

import asyncio
from decimal import Decimal
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import json
from pathlib import Path

import pandas as pd
import numpy as np
from loguru import logger


@dataclass
class BacktestConfig:
    """Configuration for backtesting run."""
    start_date: datetime
    end_date: datetime
    initial_capital: Decimal
    num_trade_groups: int
    max_chain_length: int
    min_profit_threshold: float
    fee_percent: float
    slippage_percent: float
    price_volatility: float  # Simulated price movement


@dataclass
class BacktestTrade:
    """Record of a simulated trade."""
    timestamp: datetime
    path: str
    chain_length: int
    start_amount: Decimal
    end_amount: Decimal
    profit: Decimal
    profit_percent: float
    fees: Decimal
    execution_time: float
    success: bool


@dataclass
class BacktestResult:
    """Complete backtesting results."""
    config: BacktestConfig
    trades: List[BacktestTrade]
    total_profit: Decimal
    total_fees: Decimal
    net_profit: Decimal
    roi_percent: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    avg_profit_per_trade: float
    best_path: str
    worst_path: str
    execution_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            'start_date': self.config.start_date.isoformat(),
            'end_date': self.config.end_date.isoformat(),
            'initial_capital': float(self.config.initial_capital),
            'total_profit': float(self.total_profit),
            'total_fees': float(self.total_fees),
            'net_profit': float(self.net_profit),
            'roi_percent': self.roi_percent,
            'win_rate': self.win_rate,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'best_path': self.best_path,
            'worst_path': self.worst_path,
            'total_trades': len(self.trades)
        }


class Backtester:
    """
    Backtesting engine for the trading algorithm.
    
    Simulates trading activity using historical patterns and
    synthetic price movements to validate strategy parameters.
    """
    
    # Common trading pairs for simulation
    SIMULATED_TOKENS = [
        'BTC', 'ETH', 'SOL', 'DOGE', 'SHIB', 'AVAX', 'MATIC', 'LINK',
        'UNI', 'AAVE', 'CRV', 'MKR', 'COMP', 'SNX', 'YFI', 'SUSHI',
        'XRP', 'ADA', 'DOT', 'ATOM', 'ALGO', 'FIL', 'NEAR', 'FTM',
        'ONE', 'SAND', 'MANA', 'AXS', 'GALA', 'ENJ', 'LRC', 'IMX'
    ]
    
    def __init__(self, config: BacktestConfig):
        """
        Initialize the backtester.
        
        Args:
            config: Backtesting configuration
        """
        self.config = config
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Tuple[datetime, Decimal]] = []
        self.path_stats: Dict[str, Dict] = {}
        
    def generate_simulated_prices(self) -> Dict[str, List[Dict]]:
        """
        Generate simulated price data for backtesting.
        
        Returns:
            Dictionary of token -> price history
        """
        prices = {}
        base_prices = {
            'BTC': 95000, 'ETH': 3500, 'SOL': 180, 'DOGE': 0.35,
            'SHIB': 0.000024, 'AVAX': 35, 'MATIC': 0.50, 'LINK': 14,
            'UNI': 12, 'AAVE': 180, 'CRV': 0.70, 'MKR': 1800,
            'COMP': 50, 'SNX': 2.50, 'YFI': 8000, 'SUSHI': 1.20,
            'XRP': 2.20, 'ADA': 0.95, 'DOT': 7, 'ATOM': 10,
            'ALGO': 0.35, 'FIL': 5, 'NEAR': 5.50, 'FTM': 0.70,
            'ONE': 0.02, 'SAND': 0.50, 'MANA': 0.45, 'AXS': 6,
            'GALA': 0.04, 'ENJ': 0.20, 'LRC': 0.20, 'IMX': 1.50
        }
        
        num_periods = (self.config.end_date - self.config.start_date).days * 24 * 60  # Per minute
        
        for token in self.SIMULATED_TOKENS:
            base_price = base_prices.get(token, 10)
            price_history = []
            current_price = base_price
            
            current_time = self.config.start_date
            for _ in range(min(num_periods, 10000)):  # Limit for memory
                # Random walk with mean reversion
                volatility = self.config.price_volatility / 100
                change = random.gauss(0, volatility) - 0.0001 * (current_price - base_price) / base_price
                current_price *= (1 + change)
                current_price = max(current_price * 0.5, min(current_price * 1.5, current_price))
                
                price_history.append({
                    'timestamp': current_time,
                    'price': current_price,
                    'bid': current_price * 0.9995,
                    'ask': current_price * 1.0005
                })
                
                current_time += timedelta(minutes=1)
            
            prices[token] = price_history
        
        return prices
    
    def find_simulated_paths(
        self,
        prices: Dict[str, List[Dict]],
        time_index: int,
        num_paths: int = 8
    ) -> List[Dict]:
        """
        Find profitable paths at a given time point.
        
        Args:
            prices: Price history data
            time_index: Index into price history
            num_paths: Number of paths to generate
            
        Returns:
            List of path dictionaries with profit estimates
        """
        paths = []
        available_tokens = list(prices.keys())
        
        for _ in range(num_paths * 2):  # Generate extra to filter
            # Random path length
            chain_length = random.randint(2, self.config.max_chain_length)
            
            # Build path
            path_tokens = ['USDC']
            used = set()
            
            for _ in range(chain_length - 1):
                available = [t for t in available_tokens if t not in used]
                if not available:
                    break
                next_token = random.choice(available)
                path_tokens.append(next_token)
                used.add(next_token)
            
            path_tokens.append('USDC')
            
            if len(path_tokens) < 3:
                continue
            
            # Calculate simulated profit
            amount = Decimal('1')
            for i in range(len(path_tokens) - 1):
                from_token = path_tokens[i]
                to_token = path_tokens[i + 1]
                
                # Get prices
                if from_token == 'USDC':
                    if to_token in prices and time_index < len(prices[to_token]):
                        price = Decimal(str(prices[to_token][time_index]['ask']))
                        amount = amount / price
                elif to_token == 'USDC':
                    if from_token in prices and time_index < len(prices[from_token]):
                        price = Decimal(str(prices[from_token][time_index]['bid']))
                        amount = amount * price
                else:
                    # Token to token via cross rate
                    if from_token in prices and to_token in prices:
                        from_price = Decimal(str(prices[from_token][time_index]['bid']))
                        to_price = Decimal(str(prices[to_token][time_index]['ask']))
                        amount = (amount * from_price) / to_price
                
                # Apply fee
                fee_mult = Decimal('1') - Decimal(str(self.config.fee_percent)) / Decimal('100')
                amount *= fee_mult
            
            profit_pct = float((amount - Decimal('1')) * 100)
            
            if profit_pct > self.config.min_profit_threshold:
                paths.append({
                    'path': ' -> '.join(path_tokens),
                    'tokens': path_tokens,
                    'chain_length': len(path_tokens) - 1,
                    'profit_percent': profit_pct,
                    'expected_output': float(amount)
                })
        
        # Sort by profit and return top paths
        paths.sort(key=lambda x: x['profit_percent'], reverse=True)
        return paths[:num_paths]
    
    def run_backtest(self) -> BacktestResult:
        """
        Execute the full backtesting simulation.
        
        Returns:
            BacktestResult with all metrics
        """
        start_time = datetime.now()
        logger.info(f"Starting backtest from {self.config.start_date} to {self.config.end_date}")
        
        # Generate price data
        prices = self.generate_simulated_prices()
        
        # Initialize tracking
        current_capital = self.config.initial_capital
        self.equity_curve = [(self.config.start_date, current_capital)]
        self.trades = []
        
        # Simulate trading periods (hourly)
        num_periods = min(
            (self.config.end_date - self.config.start_date).days * 24,
            1000  # Limit iterations
        )
        
        for period in range(num_periods):
            time_index = period * 60  # Convert to minute index
            current_time = self.config.start_date + timedelta(hours=period)
            
            # Find profitable paths
            paths = self.find_simulated_paths(prices, time_index, self.config.num_trade_groups)
            
            if not paths:
                continue
            
            # Execute groups
            allocation = current_capital / self.config.num_trade_groups
            period_profit = Decimal('0')
            period_fees = Decimal('0')
            
            # Select non-overlapping paths
            selected_paths = self._select_non_overlapping(paths)
            
            for path_info in selected_paths[:self.config.num_trade_groups]:
                # Simulate execution with slippage
                slippage = 1 - (self.config.slippage_percent / 100 * random.random())
                actual_output = Decimal(str(path_info['expected_output'] * slippage))
                
                # Add random execution variation
                execution_variation = 1 + random.gauss(0, 0.001)
                actual_output *= Decimal(str(execution_variation))
                
                trade_profit = (actual_output - Decimal('1')) * allocation
                trade_fees = allocation * Decimal(str(self.config.fee_percent / 100)) * len(path_info['tokens'])
                
                success = actual_output > Decimal('1')
                
                trade = BacktestTrade(
                    timestamp=current_time,
                    path=path_info['path'],
                    chain_length=path_info['chain_length'],
                    start_amount=allocation,
                    end_amount=allocation * actual_output,
                    profit=trade_profit,
                    profit_percent=float((actual_output - Decimal('1')) * 100),
                    fees=trade_fees,
                    execution_time=random.uniform(0.5, 2.0),
                    success=success
                )
                
                self.trades.append(trade)
                period_profit += trade_profit
                period_fees += trade_fees
                
                # Update path stats
                path_str = path_info['path']
                if path_str not in self.path_stats:
                    self.path_stats[path_str] = {
                        'total_profit': 0,
                        'count': 0,
                        'wins': 0,
                        'avg_profit': 0
                    }
                self.path_stats[path_str]['total_profit'] += float(trade_profit)
                self.path_stats[path_str]['count'] += 1
                if success:
                    self.path_stats[path_str]['wins'] += 1
            
            current_capital += period_profit
            self.equity_curve.append((current_time, current_capital))
        
        # Calculate final metrics
        result = self._calculate_metrics(start_time)
        
        logger.info(
            f"Backtest complete: ROI={result.roi_percent:.2f}%, "
            f"Win Rate={result.win_rate:.1f}%, "
            f"Sharpe={result.sharpe_ratio:.2f}"
        )
        
        return result
    
    def _select_non_overlapping(self, paths: List[Dict]) -> List[Dict]:
        """Select paths with no overlapping tokens."""
        selected = []
        used_tokens = set()
        
        for path_info in paths:
            path_tokens = set(path_info['tokens']) - {'USDC'}
            if not path_tokens.intersection(used_tokens):
                selected.append(path_info)
                used_tokens.update(path_tokens)
        
        return selected
    
    def _calculate_metrics(self, start_time: datetime) -> BacktestResult:
        """Calculate all performance metrics."""
        total_profit = sum(t.profit for t in self.trades)
        total_fees = sum(t.fees for t in self.trades)
        net_profit = total_profit - total_fees
        
        wins = sum(1 for t in self.trades if t.success)
        win_rate = (wins / len(self.trades) * 100) if self.trades else 0
        
        roi = float(net_profit / self.config.initial_capital * 100)
        avg_profit = float(total_profit / len(self.trades)) if self.trades else 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        # Calculate Sharpe ratio
        sharpe = self._calculate_sharpe_ratio()
        
        # Find best and worst paths
        best_path = max(self.path_stats.items(), key=lambda x: x[1]['total_profit'])[0] if self.path_stats else ''
        worst_path = min(self.path_stats.items(), key=lambda x: x[1]['total_profit'])[0] if self.path_stats else ''
        
        return BacktestResult(
            config=self.config,
            trades=self.trades,
            total_profit=total_profit,
            total_fees=total_fees,
            net_profit=net_profit,
            roi_percent=roi,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            avg_profit_per_trade=avg_profit,
            best_path=best_path,
            worst_path=worst_path,
            execution_time=(datetime.now() - start_time).total_seconds()
        )
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown percentage."""
        if not self.equity_curve:
            return 0
        
        peak = self.equity_curve[0][1]
        max_dd = 0
        
        for _, equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = float((peak - equity) / peak * 100)
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe ratio."""
        if len(self.trades) < 2:
            return 0
        
        returns = [float(t.profit_percent) for t in self.trades]
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0
        
        # Annualized (assuming hourly returns)
        annualization_factor = np.sqrt(24 * 365)
        sharpe = (mean_return - risk_free_rate / (24 * 365)) / std_return * annualization_factor
        
        return float(sharpe)
    
    def export_results(self, output_dir: str) -> None:
        """Export backtest results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export trades to CSV
        trades_df = pd.DataFrame([
            {
                'timestamp': t.timestamp,
                'path': t.path,
                'chain_length': t.chain_length,
                'start_amount': float(t.start_amount),
                'end_amount': float(t.end_amount),
                'profit': float(t.profit),
                'profit_percent': t.profit_percent,
                'fees': float(t.fees),
                'execution_time': t.execution_time,
                'success': t.success
            }
            for t in self.trades
        ])
        trades_df.to_csv(output_path / 'backtest_trades.csv', index=False)
        
        # Export equity curve
        equity_df = pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
        equity_df.to_csv(output_path / 'equity_curve.csv', index=False)
        
        # Export path stats
        path_df = pd.DataFrame([
            {'path': k, **v}
            for k, v in self.path_stats.items()
        ])
        path_df.to_csv(output_path / 'path_stats.csv', index=False)
        
        logger.info(f"Exported backtest results to {output_path}")


def run_parameter_optimization(
    initial_capital: Decimal,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Run parameter optimization to find best settings.
    
    Tests various combinations of:
    - Number of trade groups
    - Chain lengths
    - Profit thresholds
    
    Returns:
        Dictionary with optimal parameters
    """
    logger.info("Running parameter optimization...")
    
    best_result = None
    best_params = {}
    
    param_grid = {
        'num_groups': [4, 5, 6, 7, 8],
        'max_chain': [3, 4, 5, 6, 7],
        'min_profit': [0.3, 0.5, 0.7, 1.0]
    }
    
    for num_groups in param_grid['num_groups']:
        for max_chain in param_grid['max_chain']:
            for min_profit in param_grid['min_profit']:
                config = BacktestConfig(
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                    num_trade_groups=num_groups,
                    max_chain_length=max_chain,
                    min_profit_threshold=min_profit,
                    fee_percent=0.60,
                    slippage_percent=0.1,
                    price_volatility=2.0
                )
                
                backtester = Backtester(config)
                result = backtester.run_backtest()
                
                # Score based on ROI and Sharpe ratio
                score = result.roi_percent * 0.5 + result.sharpe_ratio * 10 + result.win_rate * 0.3
                
                if best_result is None or score > best_result:
                    best_result = score
                    best_params = {
                        'num_trade_groups': num_groups,
                        'max_chain_length': max_chain,
                        'min_profit_threshold': min_profit,
                        'roi_percent': result.roi_percent,
                        'sharpe_ratio': result.sharpe_ratio,
                        'win_rate': result.win_rate,
                        'score': score
                    }
    
    logger.info(f"Optimal parameters: {best_params}")
    return best_params
