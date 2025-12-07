"""Tests for the path finding algorithm."""

import pytest
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock
import asyncio

from src.core.path_finder import PathFinder, TradePath, ConversionStep


class TestPathFinder:
    """Test cases for PathFinder class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Coinbase client."""
        client = MagicMock()
        client.get_all_products = AsyncMock(return_value=[
            {
                'product_id': 'BTC-USDC',
                'base_currency_id': 'BTC',
                'quote_currency_id': 'USDC',
                'status': 'online',
                'base_min_size': '0.0001',
                'base_max_size': '10000',
                'quote_increment': '0.01',
                'base_increment': '0.00000001'
            },
            {
                'product_id': 'ETH-USDC',
                'base_currency_id': 'ETH',
                'quote_currency_id': 'USDC',
                'status': 'online',
                'base_min_size': '0.001',
                'base_max_size': '10000',
                'quote_increment': '0.01',
                'base_increment': '0.0000001'
            },
            {
                'product_id': 'ETH-BTC',
                'base_currency_id': 'ETH',
                'quote_currency_id': 'BTC',
                'status': 'online',
                'base_min_size': '0.001',
                'base_max_size': '10000',
                'quote_increment': '0.00001',
                'base_increment': '0.0000001'
            }
        ])
        return client
    
    @pytest.fixture
    def path_finder(self, mock_client):
        """Create a PathFinder instance."""
        return PathFinder(
            client=mock_client,
            fee_percent=0.60,
            max_chain_length=5,
            min_profit_threshold=0.5
        )
    
    def test_conversion_step_str(self):
        """Test ConversionStep string representation."""
        step = ConversionStep(
            from_token='USDC',
            to_token='BTC',
            product_id='BTC-USDC',
            side='buy',
            rate=Decimal('0.00001'),
            fee_adjusted_rate=Decimal('0.0000099')
        )
        assert str(step) == "USDC -> BTC (BTC-USDC)"
    
    def test_trade_path_properties(self):
        """Test TradePath properties."""
        steps = [
            ConversionStep('USDC', 'BTC', 'BTC-USDC', 'buy', Decimal('0.00001'), Decimal('0.0000099')),
            ConversionStep('BTC', 'USDC', 'BTC-USDC', 'sell', Decimal('100000'), Decimal('99400'))
        ]
        
        path = TradePath(
            steps=steps,
            start_amount=Decimal('250'),
            end_amount=Decimal('251.25'),
            profit_percent=Decimal('0.5'),
            tokens_used={'USDC', 'BTC'}
        )
        
        assert path.is_profitable
        assert path.chain_length == 2
    
    def test_non_overlapping_selection(self, path_finder):
        """Test selection of non-overlapping paths."""
        # Create mock paths with different token sets
        path1 = TradePath(
            steps=[],
            start_amount=Decimal('250'),
            end_amount=Decimal('252'),
            profit_percent=Decimal('0.8'),
            tokens_used={'USDC', 'BTC', 'ETH'}
        )
        
        path2 = TradePath(
            steps=[],
            start_amount=Decimal('250'),
            end_amount=Decimal('251.5'),
            profit_percent=Decimal('0.6'),
            tokens_used={'USDC', 'SOL', 'AVAX'}
        )
        
        path3 = TradePath(
            steps=[],
            start_amount=Decimal('250'),
            end_amount=Decimal('251'),
            profit_percent=Decimal('0.4'),
            tokens_used={'USDC', 'BTC', 'LINK'}  # Overlaps with path1
        )
        
        selected = path_finder.get_non_overlapping_paths([path1, path2, path3], num_groups=3)
        
        # Should select path1 and path2, but not path3 (overlaps with path1)
        assert len(selected) == 2
        assert path1 in selected
        assert path2 in selected
        assert path3 not in selected


class TestConversionStep:
    """Test ConversionStep dataclass."""
    
    def test_creation(self):
        """Test creating a conversion step."""
        step = ConversionStep(
            from_token='USDC',
            to_token='BTC',
            product_id='BTC-USDC',
            side='buy',
            rate=Decimal('0.0000105'),
            fee_adjusted_rate=Decimal('0.00001044')
        )
        
        assert step.from_token == 'USDC'
        assert step.to_token == 'BTC'
        assert step.side == 'buy'


class TestTradePath:
    """Test TradePath dataclass."""
    
    def test_profitable_path(self):
        """Test a profitable trade path."""
        path = TradePath(
            steps=[],
            start_amount=Decimal('1000'),
            end_amount=Decimal('1010'),
            profit_percent=Decimal('1.0'),
            tokens_used={'USDC', 'BTC'}
        )
        
        assert path.is_profitable
        assert path.profit_percent == Decimal('1.0')
    
    def test_unprofitable_path(self):
        """Test an unprofitable trade path."""
        path = TradePath(
            steps=[],
            start_amount=Decimal('1000'),
            end_amount=Decimal('995'),
            profit_percent=Decimal('-0.5'),
            tokens_used={'USDC', 'ETH'}
        )
        
        assert not path.is_profitable
