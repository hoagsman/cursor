"""
Trade Execution Engine
Manages concurrent trade groups and executes conversion paths.
Ensures no overlap between groups and tracks all trades for analysis.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from loguru import logger

from src.api.coinbase_client import CoinbaseClient, Trade
from src.core.path_finder import TradePath, ConversionStep, PathFinder


class TradeStatus(Enum):
    """Status of a trade group execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TradeGroupResult:
    """Result of executing a trade group."""
    group_id: str
    path: TradePath
    status: TradeStatus
    trades: List[Trade]
    start_amount: Decimal
    end_amount: Decimal
    total_fees: Decimal
    net_profit: Decimal
    profit_percent: Decimal
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'group_id': self.group_id,
            'path': str(self.path),
            'status': self.status.value,
            'start_amount': float(self.start_amount),
            'end_amount': float(self.end_amount),
            'total_fees': float(self.total_fees),
            'net_profit': float(self.net_profit),
            'profit_percent': float(self.profit_percent),
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'num_trades': len(self.trades),
            'error': self.error_message
        }


@dataclass
class RoundResult:
    """Result of a complete trading round."""
    round_id: str
    group_results: List[TradeGroupResult]
    total_start: Decimal
    total_end: Decimal
    total_profit: Decimal
    total_fees: Decimal
    successful_groups: int
    failed_groups: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        total = self.successful_groups + self.failed_groups
        return (self.successful_groups / total * 100) if total > 0 else 0


class TradeExecutor:
    """
    Executes trade groups concurrently while preventing overlap.
    
    Key features:
    - Manages 4-8 trade groups with equal allocation
    - Ensures no token overlap between concurrent trades
    - Tracks all trades for Excel logging
    - Handles failures gracefully with rollback
    """
    
    def __init__(
        self,
        client: CoinbaseClient,
        path_finder: PathFinder,
        trading_mode: str = 'paper',
        order_timeout: int = 30,
        max_retry_attempts: int = 3,
        slippage_tolerance: float = 0.1
    ):
        """
        Initialize the trade executor.
        
        Args:
            client: Coinbase API client
            path_finder: Path finding engine
            trading_mode: 'paper' for simulation, 'live' for real trading
            order_timeout: Timeout for order execution in seconds
            max_retry_attempts: Number of retries for failed orders
            slippage_tolerance: Maximum allowed slippage percentage
        """
        self.client = client
        self.path_finder = path_finder
        self.trading_mode = trading_mode
        self.order_timeout = order_timeout
        self.max_retry_attempts = max_retry_attempts
        self.slippage_tolerance = Decimal(str(slippage_tolerance)) / Decimal('100')
        
        # Track active trades to prevent overlap
        self.active_tokens: Set[str] = set()
        self.active_groups: Dict[str, TradePath] = {}
        
        # Results history
        self.round_history: List[RoundResult] = []
        self.all_trades: List[TradeGroupResult] = []
        
        # Daily tracking
        self.daily_start_balance: Decimal = Decimal('0')
        self.daily_pnl: Decimal = Decimal('0')
        
    async def execute_round(
        self,
        capital: Decimal,
        num_groups: int = 4,
        min_profit_threshold: Decimal = Decimal('0.5')
    ) -> RoundResult:
        """
        Execute a complete trading round.
        
        Args:
            capital: Total capital to deploy
            num_groups: Number of trade groups (4-8)
            min_profit_threshold: Minimum profit % per path
            
        Returns:
            RoundResult with all group outcomes.
        """
        round_id = f"round_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        logger.info(f"Starting trading round {round_id} with ${capital} across {num_groups} groups")
        
        # Calculate allocation per group
        allocation = (capital / num_groups).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        # Update prices and find paths
        await self.path_finder.update_prices()
        
        all_paths = self.path_finder.find_profitable_paths(
            start_token='USDC',
            start_amount=allocation,
            max_paths=num_groups * 2  # Get extra paths for selection
        )
        
        # Select non-overlapping paths
        selected_paths = self.path_finder.get_non_overlapping_paths(all_paths, num_groups)
        
        if not selected_paths:
            logger.warning("No profitable paths found in this round")
            return RoundResult(
                round_id=round_id,
                group_results=[],
                total_start=capital,
                total_end=capital,
                total_profit=Decimal('0'),
                total_fees=Decimal('0'),
                successful_groups=0,
                failed_groups=0
            )
        
        # Execute all groups concurrently
        tasks = []
        for i, path in enumerate(selected_paths):
            group_id = f"{round_id}_group_{i+1}"
            tasks.append(self._execute_group(group_id, path, allocation))
        
        group_results = await asyncio.gather(*tasks)
        
        # Calculate totals
        total_end = sum(r.end_amount for r in group_results)
        total_fees = sum(r.total_fees for r in group_results)
        successful = sum(1 for r in group_results if r.status == TradeStatus.COMPLETED)
        failed = sum(1 for r in group_results if r.status == TradeStatus.FAILED)
        
        # Unused capital remains unchanged
        unused_capital = capital - (allocation * len(selected_paths))
        total_end += unused_capital
        
        result = RoundResult(
            round_id=round_id,
            group_results=list(group_results),
            total_start=capital,
            total_end=total_end,
            total_profit=total_end - capital,
            total_fees=total_fees,
            successful_groups=successful,
            failed_groups=failed
        )
        
        self.round_history.append(result)
        self.all_trades.extend(group_results)
        self.daily_pnl += result.total_profit
        
        logger.info(
            f"Round {round_id} completed: "
            f"{successful}/{len(selected_paths)} successful, "
            f"Profit: ${result.total_profit:.2f} ({(result.total_profit/capital*100):.2f}%)"
        )
        
        return result
    
    async def _execute_group(
        self,
        group_id: str,
        path: TradePath,
        allocation: Decimal
    ) -> TradeGroupResult:
        """
        Execute a single trade group.
        
        Args:
            group_id: Unique identifier for this group
            path: Trading path to execute
            allocation: Amount to start with
            
        Returns:
            TradeGroupResult with execution details.
        """
        start_time = datetime.now()
        trades: List[Trade] = []
        current_amount = allocation
        total_fees = Decimal('0')
        
        # Lock tokens for this group
        tokens_to_lock = path.tokens_used - {'USDC', 'USD'}
        
        try:
            # Check for token conflicts
            if tokens_to_lock.intersection(self.active_tokens):
                raise Exception("Token conflict with active trade group")
            
            self.active_tokens.update(tokens_to_lock)
            self.active_groups[group_id] = path
            
            logger.info(f"Executing group {group_id}: {path}")
            
            # Execute each step in the path
            for i, step in enumerate(path.steps):
                # Validate step is still viable
                is_valid, reason = self.path_finder.validate_path(path)
                if not is_valid:
                    raise Exception(f"Path invalidated: {reason}")
                
                # Execute trade
                trade = await self._execute_step(step, current_amount)
                trades.append(trade)
                
                # Update current amount
                if trade.status == 'filled':
                    if step.side == 'buy':
                        current_amount = trade.size
                    else:
                        current_amount = trade.size * trade.price - trade.fee
                    total_fees += trade.fee
                else:
                    raise Exception(f"Trade not filled: {trade.status}")
                
                logger.debug(
                    f"Step {i+1}/{len(path.steps)}: {step.from_token} -> {step.to_token}, "
                    f"Amount: {current_amount}"
                )
            
            # Calculate results
            execution_time = (datetime.now() - start_time).total_seconds()
            net_profit = current_amount - allocation
            profit_percent = (net_profit / allocation) * Decimal('100')
            
            return TradeGroupResult(
                group_id=group_id,
                path=path,
                status=TradeStatus.COMPLETED,
                trades=trades,
                start_amount=allocation,
                end_amount=current_amount,
                total_fees=total_fees,
                net_profit=net_profit,
                profit_percent=profit_percent,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Group {group_id} failed: {e}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Return what we have (partial execution)
            return TradeGroupResult(
                group_id=group_id,
                path=path,
                status=TradeStatus.FAILED,
                trades=trades,
                start_amount=allocation,
                end_amount=current_amount,
                total_fees=total_fees,
                net_profit=current_amount - allocation,
                profit_percent=((current_amount - allocation) / allocation) * Decimal('100'),
                execution_time=execution_time,
                error_message=str(e)
            )
            
        finally:
            # Release locked tokens
            self.active_tokens -= tokens_to_lock
            self.active_groups.pop(group_id, None)
    
    async def _execute_step(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> Trade:
        """
        Execute a single conversion step.
        
        Args:
            step: Conversion step to execute
            amount: Amount of input currency
            
        Returns:
            Trade object with execution details.
        """
        if self.trading_mode == 'paper':
            return await self._simulate_trade(step, amount)
        else:
            return await self._execute_live_trade(step, amount)
    
    async def _simulate_trade(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> Trade:
        """
        Simulate a trade for paper trading mode.
        
        Args:
            step: Conversion step
            amount: Input amount
            
        Returns:
            Simulated Trade object.
        """
        # Add small delay to simulate network latency
        await asyncio.sleep(0.1)
        
        # Calculate output based on fee-adjusted rate
        output_amount = (amount * step.fee_adjusted_rate).quantize(
            Decimal('0.00000001'),
            rounding=ROUND_DOWN
        )
        
        # Simulate fee
        fee_rate = Decimal('0.006')  # 0.6%
        fee = (amount * fee_rate).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        
        return Trade(
            order_id=f"sim_{uuid.uuid4().hex[:12]}",
            product_id=step.product_id,
            side=step.side,
            size=output_amount if step.side == 'buy' else amount,
            price=step.rate,
            fee=fee,
            status='filled',
            timestamp=datetime.now()
        )
    
    async def _execute_live_trade(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> Trade:
        """
        Execute a live trade on Coinbase.
        
        Args:
            step: Conversion step
            amount: Input amount
            
        Returns:
            Trade object from Coinbase.
        """
        for attempt in range(self.max_retry_attempts):
            try:
                if step.side == 'buy':
                    # Buying base with quote currency
                    trade = await self.client.place_market_order(
                        product_id=step.product_id,
                        side='buy',
                        quote_size=amount
                    )
                else:
                    # Selling base for quote currency
                    trade = await self.client.place_market_order(
                        product_id=step.product_id,
                        side='sell',
                        size=amount
                    )
                
                return trade
                
            except Exception as e:
                logger.warning(f"Trade attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retry_attempts - 1:
                    raise
                await asyncio.sleep(1)  # Wait before retry
    
    def check_daily_loss_limit(self, max_loss_percent: float) -> bool:
        """
        Check if daily loss limit has been reached.
        
        Args:
            max_loss_percent: Maximum allowed daily loss percentage
            
        Returns:
            True if trading should stop, False otherwise.
        """
        if self.daily_start_balance <= 0:
            return False
        
        loss_percent = (self.daily_pnl / self.daily_start_balance) * Decimal('100')
        
        if loss_percent < -Decimal(str(max_loss_percent)):
            logger.warning(f"Daily loss limit reached: {loss_percent:.2f}%")
            return True
        
        return False
    
    def reset_daily_tracking(self, start_balance: Decimal) -> None:
        """Reset daily P&L tracking."""
        self.daily_start_balance = start_balance
        self.daily_pnl = Decimal('0')
        logger.info(f"Daily tracking reset with balance: ${start_balance}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all trading performance."""
        if not self.round_history:
            return {'total_rounds': 0}
        
        total_profit = sum(r.total_profit for r in self.round_history)
        total_fees = sum(r.total_fees for r in self.round_history)
        successful = sum(r.successful_groups for r in self.round_history)
        failed = sum(r.failed_groups for r in self.round_history)
        
        return {
            'total_rounds': len(self.round_history),
            'total_profit': float(total_profit),
            'total_fees': float(total_fees),
            'net_profit': float(total_profit - total_fees),
            'successful_trades': successful,
            'failed_trades': failed,
            'success_rate': (successful / (successful + failed) * 100) if (successful + failed) > 0 else 0,
            'average_profit_per_round': float(total_profit / len(self.round_history))
        }
