"""
Nimble Trading Strategy
Core strategy implementation for quick-turn arbitrage trading.
"""

import asyncio
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from config.settings import TradingConfig
from src.api.coinbase_client import CoinbaseClient
from src.core.path_finder import PathFinder, TradePath
from src.core.trade_executor import TradeExecutor, RoundResult
from src.utils.excel_logger import ExcelLogger


class StrategyState(Enum):
    """Current state of the trading strategy."""
    IDLE = "idle"
    SCANNING = "scanning"
    EXECUTING = "executing"
    COOLING_DOWN = "cooling_down"
    STOPPED = "stopped"


@dataclass
class StrategyMetrics:
    """Real-time strategy performance metrics."""
    total_rounds: int = 0
    successful_rounds: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    total_profit: Decimal = Decimal('0')
    total_fees: Decimal = Decimal('0')
    current_capital: Decimal = Decimal('0')
    best_trade_profit: Decimal = Decimal('0')
    worst_trade_loss: Decimal = Decimal('0')
    avg_execution_time: float = 0.0
    uptime_hours: float = 0.0


class NimbleStrategy:
    """
    Nimble Trading Strategy for quick-turn arbitrage.
    
    Key characteristics:
    1. Quick in/out positions - targets fast conversions
    2. Multi-token paths (2-7 tokens) for arbitrage opportunities
    3. Concurrent non-overlapping trade groups (4-8)
    4. Automatic profit conversion to USDC
    5. Real-time fee accounting and net profit tracking
    """
    
    def __init__(self, config: TradingConfig):
        """
        Initialize the nimble strategy.
        
        Args:
            config: Trading configuration
        """
        self.config = config
        self.state = StrategyState.IDLE
        
        # Initialize components
        self.client = CoinbaseClient(
            api_key=config.coinbase_api_key,
            api_secret=config.coinbase_api_secret
        )
        
        self.path_finder = PathFinder(
            client=self.client,
            fee_percent=config.coinbase_fee_percent,
            max_chain_length=config.max_chain_length,
            min_profit_threshold=config.min_profit_threshold
        )
        
        self.executor = TradeExecutor(
            client=self.client,
            path_finder=self.path_finder,
            trading_mode=config.trading_mode,
            order_timeout=config.order_timeout,
            max_retry_attempts=config.max_retry_attempts,
            slippage_tolerance=config.slippage_tolerance
        )
        
        self.logger = ExcelLogger(config.excel_log_path)
        
        # Metrics tracking
        self.metrics = StrategyMetrics()
        self.metrics.current_capital = config.initial_capital
        
        self.start_time: Optional[datetime] = None
        self._running = False
        
    async def initialize(self) -> None:
        """Initialize strategy components."""
        logger.info("Initializing Nimble Trading Strategy...")
        
        # Connect to Coinbase
        self.client.connect()
        
        # Build token graph
        await self.path_finder.build_token_graph()
        
        # Initialize daily tracking
        balance = await self.client.get_account_balance('USDC')
        if balance > 0:
            self.metrics.current_capital = balance
        self.executor.reset_daily_tracking(self.metrics.current_capital)
        
        self.start_time = datetime.now()
        self.state = StrategyState.IDLE
        
        logger.info(f"Strategy initialized with ${self.metrics.current_capital} capital")
    
    async def run(self, max_rounds: Optional[int] = None) -> None:
        """
        Run the trading strategy.
        
        Args:
            max_rounds: Maximum rounds to execute (None for continuous)
        """
        self._running = True
        round_count = 0
        
        logger.info("Starting Nimble Trading Strategy...")
        
        while self._running:
            try:
                # Check daily loss limit
                if self.executor.check_daily_loss_limit(self.config.max_daily_loss_percent):
                    logger.warning("Daily loss limit reached. Stopping strategy.")
                    break
                
                # Execute trading round
                self.state = StrategyState.SCANNING
                result = await self.execute_round()
                
                if result:
                    round_count += 1
                    self._update_metrics(result)
                    
                    # Log to Excel
                    self.logger.log_round(result)
                    
                    logger.info(
                        f"Round {round_count}: "
                        f"Profit=${result.total_profit:.2f}, "
                        f"Success Rate={result.success_rate:.1f}%"
                    )
                
                # Check max rounds
                if max_rounds and round_count >= max_rounds:
                    logger.info(f"Completed {max_rounds} rounds. Stopping.")
                    break
                
                # Cooldown between rounds
                self.state = StrategyState.COOLING_DOWN
                await asyncio.sleep(self.config.path_recalc_interval)
                
            except KeyboardInterrupt:
                logger.info("Strategy stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in trading round: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        self.state = StrategyState.STOPPED
        self._running = False
        
        # Final summary
        self._log_final_summary()
    
    async def execute_round(self) -> Optional[RoundResult]:
        """
        Execute a single trading round.
        
        Returns:
            RoundResult if successful, None otherwise
        """
        self.state = StrategyState.EXECUTING
        
        try:
            result = await self.executor.execute_round(
                capital=self.metrics.current_capital,
                num_groups=self.config.num_trade_groups,
                min_profit_threshold=Decimal(str(self.config.min_profit_threshold))
            )
            
            # Update capital
            self.metrics.current_capital = result.total_end
            
            return result
            
        except Exception as e:
            logger.error(f"Round execution failed: {e}")
            return None
    
    def _update_metrics(self, result: RoundResult) -> None:
        """Update strategy metrics from round result."""
        self.metrics.total_rounds += 1
        if result.total_profit > 0:
            self.metrics.successful_rounds += 1
        
        for group in result.group_results:
            self.metrics.total_trades += len(group.trades)
            if group.net_profit > 0:
                self.metrics.winning_trades += 1
            
            if group.net_profit > self.metrics.best_trade_profit:
                self.metrics.best_trade_profit = group.net_profit
            if group.net_profit < self.metrics.worst_trade_loss:
                self.metrics.worst_trade_loss = group.net_profit
        
        self.metrics.total_profit += result.total_profit
        self.metrics.total_fees += result.total_fees
        
        if self.start_time:
            self.metrics.uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
    
    def _log_final_summary(self) -> None:
        """Log final trading summary."""
        logger.info("=" * 50)
        logger.info("TRADING SESSION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Rounds: {self.metrics.total_rounds}")
        logger.info(f"Successful Rounds: {self.metrics.successful_rounds}")
        logger.info(f"Total Trades: {self.metrics.total_trades}")
        logger.info(f"Win Rate: {(self.metrics.winning_trades / self.metrics.total_trades * 100) if self.metrics.total_trades > 0 else 0:.1f}%")
        logger.info(f"Total Profit: ${self.metrics.total_profit:.2f}")
        logger.info(f"Total Fees: ${self.metrics.total_fees:.2f}")
        logger.info(f"Net Profit: ${self.metrics.total_profit - self.metrics.total_fees:.2f}")
        logger.info(f"Final Capital: ${self.metrics.current_capital:.2f}")
        logger.info(f"Best Trade: +${self.metrics.best_trade_profit:.2f}")
        logger.info(f"Worst Trade: ${self.metrics.worst_trade_loss:.2f}")
        logger.info(f"Uptime: {self.metrics.uptime_hours:.2f} hours")
        logger.info("=" * 50)
        
        # Update Excel with final metrics
        self.logger.update_performance_metrics({
            'Total Rounds': self.metrics.total_rounds,
            'Successful Rounds': self.metrics.successful_rounds,
            'Win Rate (%)': f"{(self.metrics.winning_trades / self.metrics.total_trades * 100) if self.metrics.total_trades > 0 else 0:.1f}",
            'Total Profit ($)': f"{self.metrics.total_profit:.2f}",
            'Total Fees ($)': f"{self.metrics.total_fees:.2f}",
            'Net Profit ($)': f"{self.metrics.total_profit - self.metrics.total_fees:.2f}",
            'ROI (%)': f"{((self.metrics.current_capital - self.config.initial_capital) / self.config.initial_capital * 100):.2f}",
            'Final Capital ($)': f"{self.metrics.current_capital:.2f}",
            'Uptime (hours)': f"{self.metrics.uptime_hours:.2f}"
        })
    
    def stop(self) -> None:
        """Stop the strategy gracefully."""
        logger.info("Stopping strategy...")
        self._running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current strategy status."""
        return {
            'state': self.state.value,
            'current_capital': float(self.metrics.current_capital),
            'total_profit': float(self.metrics.total_profit),
            'total_rounds': self.metrics.total_rounds,
            'win_rate': (self.metrics.winning_trades / self.metrics.total_trades * 100) if self.metrics.total_trades > 0 else 0,
            'uptime_hours': self.metrics.uptime_hours
        }
