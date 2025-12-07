"""
Institutional Grade Trade Executor
Executes trade groups with full financial tracking and risk management.
"""

import asyncio
import uuid
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from loguru import logger

from src.api.coinbase_client import CoinbaseClient, OrderResult, OrderStatus
from src.core.path_finder import PathFinder, TradePath, ConversionStep
from src.core.allocation_engine import AllocationEngine, AllocationPlan, AllocationDecision
from src.audit.audit_logger import AuditLogger, AuditEventType
from src.audit.financial_tracker import FinancialTracker, TradeRecord


class ExecutionStatus(Enum):
    """Status of trade group execution."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class GroupExecutionResult:
    """Result of executing a single trade group."""
    group_id: str
    decision: AllocationDecision
    status: ExecutionStatus
    orders: List[OrderResult]
    
    # Financial results
    start_amount: Decimal
    end_amount: Decimal
    gross_profit: Decimal
    total_fees: Decimal
    net_profit: Decimal
    
    # Execution metrics
    execution_time_ms: float
    slippage_total: Decimal
    steps_completed: int
    steps_total: int
    
    # Analysis
    expected_profit: Decimal
    actual_vs_expected: Decimal
    
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None


@dataclass
class RoundExecutionResult:
    """Result of executing a complete trading round."""
    round_id: str
    allocation_plan: AllocationPlan
    group_results: List[GroupExecutionResult]
    
    # Aggregate financials
    total_start: Decimal
    total_end: Decimal
    gross_profit: Decimal
    total_fees: Decimal
    net_profit: Decimal
    
    # Success metrics
    groups_completed: int
    groups_failed: int
    success_rate: float
    
    # Timing
    total_execution_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)


class TradeExecutor:
    """
    Production-grade trade execution engine.
    
    Features:
    - Concurrent group execution with isolation
    - Full financial tracking
    - Risk management with circuit breakers
    - Comprehensive audit logging
    - Learning from results
    """
    
    def __init__(
        self,
        client: CoinbaseClient,
        path_finder: PathFinder,
        allocation_engine: AllocationEngine,
        audit_logger: AuditLogger,
        financial_tracker: FinancialTracker,
        trading_mode: str = 'live',
        max_daily_loss_pct: float = 5.0,
        circuit_breaker_threshold: int = 5
    ):
        self.client = client
        self.path_finder = path_finder
        self.allocation_engine = allocation_engine
        self.audit = audit_logger
        self.tracker = financial_tracker
        self.trading_mode = trading_mode
        self.max_daily_loss_pct = max_daily_loss_pct
        self.circuit_breaker_threshold = circuit_breaker_threshold
        
        # State tracking
        self.active_tokens: Set[str] = set()
        self.consecutive_failures = 0
        self.circuit_breaker_active = False
        
        # Daily tracking
        self.daily_start_balance = Decimal('0')
        self.daily_pnl = Decimal('0')
        
        # Round counter
        self._round_counter = 0
    
    async def execute_round(
        self,
        available_capital: Decimal,
        num_groups: int = 5
    ) -> RoundExecutionResult:
        """
        Execute a complete trading round.
        
        Args:
            available_capital: Capital available for trading
            num_groups: Target number of trade groups
            
        Returns:
            RoundExecutionResult with all details
        """
        start_time = datetime.now()
        self._round_counter += 1
        round_id = f"R{self._round_counter:04d}_{start_time.strftime('%H%M%S')}"
        
        logger.info(f"🚀 Starting round {round_id} with ${available_capital}")
        
        # Check circuit breaker
        if self.circuit_breaker_active:
            logger.warning("⚠️ Circuit breaker active - skipping round")
            return self._create_empty_result(round_id, available_capital)
        
        # Log round start
        await self.audit.log_round_start(
            round_id=round_id,
            capital=str(available_capital),
            num_groups=num_groups
        )
        
        # Update prices
        await self.path_finder.update_prices()
        
        # Find profitable paths
        all_paths = self.path_finder.find_profitable_paths(
            start_currency='USDC',
            amount=available_capital / num_groups,
            max_paths=num_groups * 2
        )
        
        # Select non-overlapping paths
        selected_paths = self.path_finder.get_non_overlapping_paths(all_paths, num_groups)
        
        if not selected_paths:
            logger.warning("No profitable paths found")
            await self.audit.log_round_end(round_id, '0', '0', 0, 0)
            return self._create_empty_result(round_id, available_capital)
        
        # Create allocation plan
        allocation_plan = self.allocation_engine.create_allocation_plan(
            paths=selected_paths,
            available_capital=available_capital,
            num_groups=num_groups,
            path_history=self.path_finder.path_history
        )
        
        # Execute all groups concurrently
        tasks = []
        for decision in allocation_plan.decisions:
            task = self._execute_group(round_id, decision)
            tasks.append(task)
        
        group_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        valid_results = []
        for result in group_results:
            if isinstance(result, Exception):
                logger.error(f"Group execution error: {result}")
            elif isinstance(result, GroupExecutionResult):
                valid_results.append(result)
        
        # Calculate aggregates
        total_end = sum(r.end_amount for r in valid_results)
        gross_profit = sum(r.gross_profit for r in valid_results)
        total_fees = sum(r.total_fees for r in valid_results)
        net_profit = sum(r.net_profit for r in valid_results)
        
        completed = sum(1 for r in valid_results if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in valid_results if r.status == ExecutionStatus.FAILED)
        
        # Update daily P&L
        self.daily_pnl += net_profit
        
        # Check daily loss limit
        self._check_daily_loss()
        
        # Update circuit breaker
        if failed > 0:
            self.consecutive_failures += failed
            if self.consecutive_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_active = True
                await self.audit.log_risk_event(
                    AuditEventType.CIRCUIT_BREAKER,
                    "Consecutive failures exceeded threshold",
                    str(self.consecutive_failures),
                    str(self.circuit_breaker_threshold)
                )
        else:
            self.consecutive_failures = 0
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        # Log round end
        await self.audit.log_round_end(
            round_id=round_id,
            profit=str(net_profit),
            fees=str(total_fees),
            success_count=completed,
            failure_count=failed
        )
        
        # Record path results for learning
        for result in valid_results:
            success = result.status == ExecutionStatus.COMPLETED and result.net_profit > 0
            self.path_finder.record_path_result(
                result.decision.path,
                success,
                float(result.net_profit / result.start_amount * 100) if result.start_amount > 0 else 0
            )
        
        result = RoundExecutionResult(
            round_id=round_id,
            allocation_plan=allocation_plan,
            group_results=valid_results,
            total_start=allocation_plan.allocated_capital,
            total_end=total_end,
            gross_profit=gross_profit,
            total_fees=total_fees,
            net_profit=net_profit,
            groups_completed=completed,
            groups_failed=failed,
            success_rate=(completed / len(valid_results) * 100) if valid_results else 0,
            total_execution_time_ms=total_time
        )
        
        logger.info(
            f"✅ Round {round_id} complete: "
            f"${net_profit:+.2f} net profit, "
            f"{completed}/{len(valid_results)} successful"
        )
        
        return result
    
    async def _execute_group(
        self,
        round_id: str,
        decision: AllocationDecision
    ) -> GroupExecutionResult:
        """Execute a single trade group."""
        start_time = datetime.now()
        group_id = f"{round_id}_G{decision.group_id}"
        path = decision.path
        allocation = decision.allocation
        
        orders: List[OrderResult] = []
        current_amount = allocation
        total_fees = Decimal('0')
        total_slippage = Decimal('0')
        steps_completed = 0
        error_msg = None
        
        # Lock tokens
        tokens_to_lock = set(path.currencies) - {'USDC', 'USD', 'USDT'}
        
        try:
            # Check for conflicts
            if tokens_to_lock.intersection(self.active_tokens):
                raise Exception("Token conflict with active group")
            
            self.active_tokens.update(tokens_to_lock)
            
            logger.debug(f"Executing {group_id}: {path.currency_path_str}")
            
            # Execute each step
            for step in path.steps:
                order = await self._execute_step(step, current_amount)
                orders.append(order)
                
                if order.status != OrderStatus.FILLED:
                    raise Exception(f"Order not filled: {order.status.value}")
                
                # Update current amount
                if step.side == 'buy':
                    current_amount = order.filled_size
                else:
                    current_amount = order.filled_size * order.average_price - order.fee
                
                total_fees += order.fee
                total_slippage += Decimal(str(order.slippage_percent))
                steps_completed += 1
                
                # Log order
                await self.audit.log_order(
                    AuditEventType.ORDER_FILLED,
                    order.to_audit_dict()
                )
                
                # Small delay between trades
                await asyncio.sleep(0.1)
            
            status = ExecutionStatus.COMPLETED
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Group {group_id} failed at step {steps_completed + 1}: {e}")
            status = ExecutionStatus.FAILED if steps_completed == 0 else ExecutionStatus.PARTIAL
        
        finally:
            self.active_tokens -= tokens_to_lock
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        gross_profit = current_amount - allocation
        net_profit = gross_profit - total_fees
        expected_profit = path.profit_amount
        
        result = GroupExecutionResult(
            group_id=group_id,
            decision=decision,
            status=status,
            orders=orders,
            start_amount=allocation,
            end_amount=current_amount,
            gross_profit=gross_profit,
            total_fees=total_fees,
            net_profit=net_profit,
            execution_time_ms=execution_time,
            slippage_total=total_slippage,
            steps_completed=steps_completed,
            steps_total=len(path.steps),
            expected_profit=expected_profit,
            actual_vs_expected=net_profit - expected_profit,
            error_message=error_msg
        )
        
        # Record to financial tracker
        trade_record = TradeRecord(
            trade_id=group_id,
            round_id=round_id,
            group_id=decision.group_id,
            timestamp=start_time,
            path_str=path.currency_path_str,
            currencies=path.currencies,
            chain_length=path.chain_length,
            allocation=allocation,
            probability=decision.probability,
            confidence=decision.confidence_level,
            executed=status != ExecutionStatus.FAILED,
            start_amount=allocation,
            end_amount=current_amount,
            gross_profit=gross_profit,
            total_fees=total_fees,
            net_profit=net_profit,
            profit_percent=(net_profit / allocation * 100) if allocation > 0 else Decimal('0'),
            expected_profit=expected_profit,
            slippage=total_slippage,
            execution_time_ms=execution_time,
            success=status == ExecutionStatus.COMPLETED and net_profit > 0,
            error_message=error_msg
        )
        
        self.tracker.record_trade(trade_record)
        
        return result
    
    async def _execute_step(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> OrderResult:
        """Execute a single conversion step."""
        if self.trading_mode == 'paper':
            return await self._simulate_order(step, amount)
        else:
            return await self._execute_live_order(step, amount)
    
    async def _simulate_order(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> OrderResult:
        """Simulate order for paper trading."""
        await asyncio.sleep(0.05)  # Simulate latency
        
        output = (amount * step.fee_adjusted_rate).quantize(
            Decimal('0.00000001'),
            rounding=ROUND_DOWN
        )
        
        fee = (amount * Decimal('0.006')).quantize(Decimal('0.00000001'))
        
        return OrderResult(
            order_id=f"sim_{uuid.uuid4().hex[:12]}",
            product_id=step.product_id,
            side=step.side,
            order_type='market',
            size=amount if step.side == 'sell' else output,
            filled_size=output if step.side == 'buy' else amount,
            price=step.rate,
            average_price=step.rate,
            fee=fee,
            status=OrderStatus.FILLED,
            created_at=datetime.now(),
            completed_at=datetime.now(),
            execution_time_ms=50,
            slippage_percent=0.01,
            request_hash='sim',
            response_hash='sim'
        )
    
    async def _execute_live_order(
        self,
        step: ConversionStep,
        amount: Decimal
    ) -> OrderResult:
        """Execute live order on Coinbase."""
        if step.side == 'buy':
            return await self.client.execute_market_order(
                product_id=step.product_id,
                side='buy',
                quote_size=amount,
                expected_price=step.rate
            )
        else:
            return await self.client.execute_market_order(
                product_id=step.product_id,
                side='sell',
                size=amount,
                expected_price=step.rate
            )
    
    def _check_daily_loss(self) -> None:
        """Check if daily loss limit has been hit."""
        if self.daily_start_balance <= 0:
            return
        
        loss_pct = float(self.daily_pnl / self.daily_start_balance * 100)
        
        if loss_pct < -self.max_daily_loss_pct:
            self.circuit_breaker_active = True
            logger.warning(f"⛔ Daily loss limit hit: {loss_pct:.2f}%")
    
    def _create_empty_result(
        self,
        round_id: str,
        capital: Decimal
    ) -> RoundExecutionResult:
        """Create empty result for skipped rounds."""
        return RoundExecutionResult(
            round_id=round_id,
            allocation_plan=AllocationPlan(
                round_id=round_id,
                total_capital=capital,
                allocated_capital=Decimal('0'),
                reserved_capital=capital,
                decisions=[]
            ),
            group_results=[],
            total_start=Decimal('0'),
            total_end=Decimal('0'),
            gross_profit=Decimal('0'),
            total_fees=Decimal('0'),
            net_profit=Decimal('0'),
            groups_completed=0,
            groups_failed=0,
            success_rate=0,
            total_execution_time_ms=0
        )
    
    def reset_daily_tracking(self, balance: Decimal) -> None:
        """Reset daily tracking."""
        self.daily_start_balance = balance
        self.daily_pnl = Decimal('0')
        self.consecutive_failures = 0
        self.circuit_breaker_active = False
        logger.info(f"Daily tracking reset: ${balance}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            'circuit_breaker_active': self.circuit_breaker_active,
            'consecutive_failures': self.consecutive_failures,
            'daily_pnl': float(self.daily_pnl),
            'daily_loss_limit': self.max_daily_loss_pct,
            'active_tokens': list(self.active_tokens),
            'rounds_executed': self._round_counter
        }
