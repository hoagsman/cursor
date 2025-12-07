"""
Minimal Pretrain Strategy
Uses real money trading to discover unique patterns that heavily pretrained algorithms miss.
"""

import asyncio
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, time
from enum import Enum

from loguru import logger

from config.settings import AlgoConfig
from src.api.coinbase_client import CoinbaseClient
from src.core.path_finder import PathFinder
from src.core.allocation_engine import AllocationEngine
from src.core.trade_executor import TradeExecutor, RoundExecutionResult
from src.audit.audit_logger import AuditLogger, AuditEventType
from src.audit.financial_tracker import FinancialTracker


class StrategyState(Enum):
    """Strategy execution state."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    SCANNING = "scanning"
    EXECUTING = "executing"
    LEARNING = "learning"
    PAUSED = "paused"
    STOPPED = "stopped"


class MinimalPretrainStrategy:
    """
    Minimal Pretrain Trading Strategy.
    
    Philosophy: Learn from real money trades to discover patterns
    that heavily pretrained models miss due to overfitting to historical data.
    
    Key principles:
    1. Start with minimal assumptions
    2. Let the market teach through real execution
    3. Track everything for analysis
    4. Adapt based on what actually works
    """
    
    def __init__(self, config: AlgoConfig):
        self.config = config
        self.state = StrategyState.INITIALIZING
        
        # Initialize components
        self.client = CoinbaseClient(
            api_key=config.coinbase_api_key,
            api_secret=config.coinbase_api_secret,
            max_retries=config.max_retry_attempts,
            timeout=config.order_timeout
        )
        
        self.path_finder = PathFinder(
            client=self.client,
            fee_percent=config.coinbase_fee_percent,
            min_chain_length=config.min_chain_length,
            max_chain_length=config.max_chain_length,
            min_profit_threshold=config.min_profit_threshold
        )
        
        self.allocation_engine = AllocationEngine(
            min_allocation=config.min_group_allocation,
            max_allocation=config.max_group_allocation,
            default_allocation=config.default_group_allocation,
            high_confidence_threshold=config.high_confidence_threshold,
            low_confidence_threshold=config.low_confidence_threshold,
            max_total_capital=config.max_account_usage
        )
        
        self.audit = AuditLogger(
            log_dir=config.audit_log_path,
            retention_days=config.audit_retention_days
        )
        
        self.tracker = FinancialTracker(
            excel_path=config.excel_log_path,
            metrics_path=config.metrics_path
        )
        
        self.executor = TradeExecutor(
            client=self.client,
            path_finder=self.path_finder,
            allocation_engine=self.allocation_engine,
            audit_logger=self.audit,
            financial_tracker=self.tracker,
            trading_mode=config.trading_mode,
            max_daily_loss_pct=config.max_daily_loss_percent,
            circuit_breaker_threshold=config.circuit_breaker_threshold
        )
        
        # State
        self._running = False
        self._start_time: Optional[datetime] = None
        self._rounds_executed = 0
        self._current_capital = Decimal('0')
    
    async def initialize(self) -> bool:
        """
        Initialize strategy components.
        
        Returns:
            True if initialization successful
        """
        logger.info("🔧 Initializing Minimal Pretrain Strategy...")
        
        try:
            # Connect to Coinbase
            if not self.client.connect():
                raise Exception("Failed to connect to Coinbase")
            
            # Initialize path finder
            await self.path_finder.initialize()
            
            # Get current balance
            balance = await self.client.get_balance(self.config.base_currency)
            self._current_capital = min(balance, self.config.max_account_usage)
            
            if self._current_capital < self.config.min_group_allocation:
                raise Exception(f"Insufficient balance: ${balance}")
            
            # Set up tracking
            self.tracker.starting_balance = self._current_capital
            self.tracker.current_balance = self._current_capital
            self.executor.reset_daily_tracking(self._current_capital)
            
            # Log initialization
            await self.audit.log_system_start({
                'trading_mode': self.config.trading_mode,
                'max_capital': str(self.config.max_account_usage),
                'current_balance': str(self._current_capital),
                'num_groups': self.config.num_trade_groups,
                'chain_length': f"{self.config.min_chain_length}-{self.config.max_chain_length}"
            })
            
            self._start_time = datetime.now()
            self.state = StrategyState.IDLE
            
            logger.info(f"✅ Strategy initialized with ${self._current_capital} capital")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.state = StrategyState.STOPPED
            return False
    
    async def run(
        self,
        max_rounds: Optional[int] = None,
        duration_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run the trading strategy.
        
        Args:
            max_rounds: Maximum rounds to execute (None for unlimited)
            duration_hours: Maximum duration in hours (None for unlimited)
            
        Returns:
            Final performance summary
        """
        if self.state == StrategyState.STOPPED:
            logger.error("Strategy is stopped. Call initialize() first.")
            return {}
        
        self._running = True
        start_time = datetime.now()
        
        logger.info("🚀 Starting Minimal Pretrain Strategy...")
        logger.info(f"   Mode: {self.config.trading_mode.upper()}")
        logger.info(f"   Capital: ${self._current_capital}")
        logger.info(f"   Groups: {self.config.num_trade_groups}")
        logger.info(f"   Chain Length: {self.config.min_chain_length}-{self.config.max_chain_length}")
        
        while self._running:
            try:
                # Check time bounds
                if duration_hours:
                    elapsed = (datetime.now() - start_time).total_seconds() / 3600
                    if elapsed >= duration_hours:
                        logger.info(f"Duration limit reached ({duration_hours}h)")
                        break
                
                # Check round bounds
                if max_rounds and self._rounds_executed >= max_rounds:
                    logger.info(f"Round limit reached ({max_rounds})")
                    break
                
                # Check trading hours
                if not self._is_trading_time():
                    logger.debug("Outside trading hours, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                # Execute round
                self.state = StrategyState.SCANNING
                
                result = await self.executor.execute_round(
                    available_capital=self._current_capital,
                    num_groups=self.config.num_trade_groups
                )
                
                self._rounds_executed += 1
                
                # Update capital
                if result.net_profit != 0:
                    self._current_capital += result.net_profit
                    self.tracker.current_balance = self._current_capital
                
                # Learning phase
                self.state = StrategyState.LEARNING
                await self._analyze_and_learn(result)
                
                # Wait for next round
                self.state = StrategyState.IDLE
                await asyncio.sleep(self.config.round_interval)
                
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(10)
        
        self._running = False
        self.state = StrategyState.STOPPED
        
        return await self._finalize()
    
    async def _analyze_and_learn(self, result: RoundExecutionResult) -> None:
        """Analyze round results and update learning."""
        if not self.config.enable_learning:
            return
        
        # Update daily summary
        self.tracker.update_daily_summary()
        
        # Log significant events
        if result.net_profit > 0:
            logger.info(f"📈 Profitable round: +${result.net_profit:.2f}")
        elif result.net_profit < 0:
            logger.info(f"📉 Loss round: ${result.net_profit:.2f}")
        
        # Check for learning opportunities
        for group_result in result.group_results:
            # Record path outcome for future probability calculations
            actual_pct = float(group_result.net_profit / group_result.start_amount * 100) if group_result.start_amount > 0 else 0
            expected_pct = float(group_result.expected_profit / group_result.start_amount * 100) if group_result.start_amount > 0 else 0
            
            # Log path result for learning
            await self.audit.log_path_result(
                path_str=group_result.decision.path.currency_path_str,
                success=group_result.net_profit > 0,
                expected_profit=str(group_result.expected_profit),
                actual_profit=str(group_result.net_profit),
                currencies=group_result.decision.path.currencies
            )
            
            # Track significant deviations
            if abs(actual_pct - expected_pct) > 0.5:
                logger.debug(
                    f"Deviation detected: expected {expected_pct:.2f}%, "
                    f"got {actual_pct:.2f}% on {group_result.decision.path.currency_path_str}"
                )
    
    def _is_trading_time(self) -> bool:
        """Check if current time is within trading hours."""
        now = datetime.now().time()
        
        start_parts = self.config.trading_start_time.split(':')
        end_parts = self.config.trading_end_time.split(':')
        
        start = time(int(start_parts[0]), int(start_parts[1]))
        end = time(int(end_parts[0]), int(end_parts[1]))
        
        return start <= now <= end
    
    async def _finalize(self) -> Dict[str, Any]:
        """Finalize strategy and generate reports."""
        logger.info("📊 Generating final reports...")
        
        # Update analysis sheets
        self.tracker.update_analysis_sheets()
        
        # Export metrics
        self.tracker.export_metrics_json()
        
        # Generate audit report
        await self.audit.generate_audit_report(
            f"{self.config.audit_log_path}/final_audit_report.json"
        )
        
        # Get summary
        summary = self.tracker.get_performance_summary()
        summary.update({
            'rounds_executed': self._rounds_executed,
            'uptime_hours': (datetime.now() - self._start_time).total_seconds() / 3600 if self._start_time else 0,
            'path_statistics': self.path_finder.get_path_statistics(),
            'what_worked': self.tracker.analyze_what_worked()[:5],
            'what_failed': self.tracker.analyze_what_failed()[:5]
        })
        
        self._print_summary(summary)
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print final summary to console."""
        logger.info("=" * 60)
        logger.info("TRADING SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Rounds Executed: {summary.get('rounds_executed', 0)}")
        logger.info(f"Total Trades: {summary.get('total_trades', 0)}")
        logger.info(f"Win Rate: {summary.get('win_rate', 0):.1f}%")
        logger.info(f"Total Profit: ${summary.get('total_profit', 0):.2f}")
        logger.info(f"Total Fees: ${summary.get('total_fees', 0):.2f}")
        logger.info(f"Net Profit: ${summary.get('net_profit', 0):.2f}")
        logger.info(f"ROI: {summary.get('roi', 0):.2f}%")
        logger.info(f"Current Balance: ${summary.get('current_balance', 0):.2f}")
        logger.info("=" * 60)
        
        if summary.get('what_worked'):
            logger.info("\n✅ WHAT WORKED:")
            for item in summary['what_worked'][:3]:
                logger.info(f"  - {item['category']}: {item['description']}")
        
        if summary.get('what_failed'):
            logger.info("\n❌ WHAT FAILED:")
            for item in summary['what_failed'][:3]:
                logger.info(f"  - {item['category']}: {item['description']}")
        
        logger.info("=" * 60)
    
    def stop(self) -> None:
        """Stop the strategy gracefully."""
        logger.info("Stopping strategy...")
        self._running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current strategy status."""
        return {
            'state': self.state.value,
            'running': self._running,
            'rounds_executed': self._rounds_executed,
            'current_capital': float(self._current_capital),
            'uptime_hours': (datetime.now() - self._start_time).total_seconds() / 3600 if self._start_time else 0,
            'client_health': self.client.health_status,
            'executor_stats': self.executor.get_execution_stats(),
            'performance': self.tracker.get_performance_summary()
        }
