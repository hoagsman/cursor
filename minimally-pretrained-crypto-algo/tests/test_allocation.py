"""Tests for the allocation engine."""

import pytest
from decimal import Decimal

from src.core.allocation_engine import AllocationEngine


class TestAllocationEngine:
    """Test allocation calculations."""
    
    @pytest.fixture
    def engine(self):
        return AllocationEngine(
            min_allocation=Decimal('100'),
            max_allocation=Decimal('300'),
            default_allocation=Decimal('200'),
            high_confidence_threshold=0.85,
            low_confidence_threshold=0.50
        )
    
    def test_high_confidence_allocation(self, engine):
        """High probability should get max allocation."""
        allocation, confidence, _ = engine.calculate_allocation(0.90, 0.80)
        assert allocation == Decimal('300')
        assert confidence == 'high'
    
    def test_low_confidence_allocation(self, engine):
        """Low probability should get min allocation."""
        allocation, confidence, _ = engine.calculate_allocation(0.40, 0.45)
        assert allocation == Decimal('100')
        assert confidence == 'low'
    
    def test_medium_confidence_allocation(self, engine):
        """Medium probability should get scaled allocation."""
        allocation, confidence, _ = engine.calculate_allocation(0.65, 0.70)
        assert Decimal('100') < allocation < Decimal('300')
        assert confidence == 'medium'
    
    def test_allocation_bounds(self, engine):
        """Allocation should never exceed bounds."""
        for prob in [0.0, 0.25, 0.5, 0.75, 1.0]:
            allocation, _, _ = engine.calculate_allocation(prob, prob)
            assert Decimal('100') <= allocation <= Decimal('300')
