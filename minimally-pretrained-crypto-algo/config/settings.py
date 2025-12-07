"""
Institutional Grade Configuration Management
Comprehensive settings with validation for the trading algorithm.
"""

from decimal import Decimal
from typing import Literal, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator


class AlgoConfig(BaseSettings):
    """
    Master configuration for the Minimally Pretrained Crypto Algorithm.
    All settings are validated and type-checked.
    """
    
    # ==========================================================================
    # COINBASE API
    # ==========================================================================
    coinbase_api_key: str = Field(..., description="Coinbase API Key")
    coinbase_api_secret: str = Field(..., description="Coinbase API Secret")
    
    # ==========================================================================
    # ACCOUNT LIMITS
    # ==========================================================================
    max_account_usage: Decimal = Field(
        default=Decimal('1000.00'),
        ge=Decimal('100'),
        le=Decimal('100000'),
        description="Maximum account usage cap"
    )
    base_currency: str = Field(default='USDC', description="Base currency for profits")
    
    # ==========================================================================
    # TRADE GROUPS
    # ==========================================================================
    num_trade_groups: int = Field(default=5, ge=4, le=8, description="Number of trade groups")
    min_group_allocation: Decimal = Field(default=Decimal('100.00'), ge=Decimal('50'))
    max_group_allocation: Decimal = Field(default=Decimal('300.00'), le=Decimal('500'))
    default_group_allocation: Decimal = Field(default=Decimal('200.00'))
    
    # ==========================================================================
    # PATH CONFIGURATION
    # ==========================================================================
    min_chain_length: int = Field(default=5, ge=3, le=10)
    max_chain_length: int = Field(default=10, ge=5, le=15)
    min_profit_threshold: float = Field(default=0.3, ge=0.1, le=5.0)
    coinbase_fee_percent: float = Field(default=0.60, ge=0, le=2.0)
    
    # ==========================================================================
    # PROBABILITY ENGINE
    # ==========================================================================
    high_confidence_threshold: float = Field(default=0.85, ge=0.5, le=1.0)
    low_confidence_threshold: float = Field(default=0.50, ge=0.3, le=0.8)
    chain_length_decay: float = Field(default=0.02, ge=0, le=0.1)
    historical_weight: float = Field(default=0.40, ge=0, le=1.0)
    
    # ==========================================================================
    # RISK MANAGEMENT
    # ==========================================================================
    max_single_loss_percent: float = Field(default=3.0, ge=1.0, le=10.0)
    max_daily_loss_percent: float = Field(default=5.0, ge=1.0, le=20.0)
    circuit_breaker_threshold: int = Field(default=5, ge=2, le=20)
    circuit_breaker_cooldown: int = Field(default=300, ge=60, le=3600)
    
    # ==========================================================================
    # EXECUTION
    # ==========================================================================
    trading_mode: Literal['paper', 'live'] = Field(default='live')
    order_timeout: int = Field(default=30, ge=5, le=120)
    slippage_tolerance: float = Field(default=0.15, ge=0.01, le=1.0)
    max_retry_attempts: int = Field(default=3, ge=1, le=10)
    inter_trade_delay_ms: int = Field(default=100, ge=0, le=1000)
    
    # ==========================================================================
    # AUDIT & LOGGING
    # ==========================================================================
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field(default='INFO')
    audit_log_path: str = Field(default='./logs/audit')
    excel_log_path: str = Field(default='./logs/trading_log.xlsx')
    metrics_path: str = Field(default='./logs/metrics')
    detailed_logging: bool = Field(default=True)
    audit_retention_days: int = Field(default=365)
    
    # ==========================================================================
    # LEARNING
    # ==========================================================================
    enable_learning: bool = Field(default=True)
    learning_rate: float = Field(default=0.05, ge=0.001, le=0.5)
    min_trades_for_learning: int = Field(default=10, ge=5, le=100)
    path_memory_size: int = Field(default=100, ge=10, le=1000)
    
    # ==========================================================================
    # SCHEDULING
    # ==========================================================================
    trading_start_time: str = Field(default='01:00')
    trading_end_time: str = Field(default='23:00')
    round_interval: int = Field(default=30, ge=5, le=300)
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    @model_validator(mode='after')
    def validate_allocations(self):
        """Ensure allocation ranges are valid."""
        if self.min_group_allocation > self.max_group_allocation:
            raise ValueError("min_group_allocation cannot exceed max_group_allocation")
        if self.default_group_allocation < self.min_group_allocation:
            raise ValueError("default_group_allocation cannot be less than min_group_allocation")
        if self.default_group_allocation > self.max_group_allocation:
            raise ValueError("default_group_allocation cannot exceed max_group_allocation")
        if self.min_chain_length > self.max_chain_length:
            raise ValueError("min_chain_length cannot exceed max_chain_length")
        return self
    
    @field_validator('audit_log_path', 'metrics_path')
    @classmethod
    def ensure_directory(cls, v: str) -> str:
        """Create directory if it doesn't exist."""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator('excel_log_path')
    @classmethod
    def ensure_excel_directory(cls, v: str) -> str:
        """Create parent directory for Excel file."""
        Path(v).parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @property
    def fee_rate(self) -> Decimal:
        """Get fee as decimal."""
        return Decimal(str(self.coinbase_fee_percent)) / Decimal('100')
    
    @property
    def allocation_range(self) -> tuple:
        """Get allocation range as tuple."""
        return (self.min_group_allocation, self.max_group_allocation)
    
    def calculate_allocation(self, probability: float) -> Decimal:
        """
        Calculate allocation based on profit probability.
        
        Args:
            probability: Estimated probability of profit (0-1)
            
        Returns:
            Allocation amount between min and max
        """
        if probability >= self.high_confidence_threshold:
            return self.max_group_allocation
        elif probability <= self.low_confidence_threshold:
            return self.min_group_allocation
        else:
            # Linear interpolation
            range_size = float(self.max_group_allocation - self.min_group_allocation)
            prob_range = self.high_confidence_threshold - self.low_confidence_threshold
            normalized = (probability - self.low_confidence_threshold) / prob_range
            allocation = float(self.min_group_allocation) + (normalized * range_size)
            return Decimal(str(round(allocation, 2)))


def load_config() -> AlgoConfig:
    """Load and validate configuration from environment."""
    return AlgoConfig()
