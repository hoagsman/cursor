"""
Configuration settings for the Nimble Trading Algorithm.
Uses pydantic-settings for validation and environment variable loading.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Literal
from pathlib import Path


class TradingConfig(BaseSettings):
    """Main configuration for trading operations."""
    
    # Coinbase API
    coinbase_api_key: str = Field(..., description="Coinbase API Key")
    coinbase_api_secret: str = Field(..., description="Coinbase API Secret")
    
    # Trading Parameters
    initial_capital: float = Field(default=1000.0, ge=100, description="Initial capital in USDC")
    num_trade_groups: int = Field(default=4, ge=1, le=8, description="Number of trade groups")
    max_chain_length: int = Field(default=7, ge=2, le=7, description="Max tokens in conversion chain")
    min_profit_threshold: float = Field(default=0.5, ge=0.1, description="Min profit % after fees")
    coinbase_fee_percent: float = Field(default=0.60, ge=0, description="Coinbase fee percentage")
    
    # Risk Management
    max_group_allocation: float = Field(default=25.0, ge=10, le=50)
    stop_loss_percent: float = Field(default=2.0, ge=0.5, le=10)
    max_daily_loss_percent: float = Field(default=5.0, ge=1, le=20)
    
    # Execution
    trading_mode: Literal['paper', 'live'] = Field(default='paper')
    order_timeout: int = Field(default=30, ge=5, le=120)
    slippage_tolerance: float = Field(default=0.1, ge=0.01, le=1.0)
    max_retry_attempts: int = Field(default=3, ge=1, le=5)
    
    # Logging
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(default='INFO')
    excel_log_path: str = Field(default='./logs/trading_log.xlsx')
    detailed_logging: bool = Field(default=True)
    
    # Backtesting
    backtest_period_days: int = Field(default=30, ge=1)
    backtest_start_date: str = Field(default='2024-11-01')
    backtest_end_date: str = Field(default='2024-12-01')
    
    # Performance
    price_update_interval: int = Field(default=1, ge=1, le=60)
    path_recalc_interval: int = Field(default=5, ge=1, le=60)
    max_concurrent_requests: int = Field(default=10, ge=1, le=50)
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    @field_validator('excel_log_path')
    @classmethod
    def validate_excel_path(cls, v: str) -> str:
        """Ensure Excel path has .xlsx extension."""
        if not v.endswith('.xlsx'):
            v += '.xlsx'
        # Create directory if needed
        Path(v).parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @property
    def allocation_per_group(self) -> float:
        """Calculate allocation per trade group."""
        return self.initial_capital / self.num_trade_groups
    
    @property
    def effective_fee_rate(self) -> float:
        """Calculate effective fee rate as decimal."""
        return self.coinbase_fee_percent / 100


def load_config() -> TradingConfig:
    """Load configuration from environment."""
    return TradingConfig()
