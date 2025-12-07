"""
Probability-Based Allocation Engine
Dynamically allocates capital based on path confidence scores.
"""

from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from src.core.path_finder import TradePath


@dataclass
class AllocationDecision:
    """Allocation decision for a trade group."""
    group_id: int
    path: TradePath
    allocation: Decimal
    probability: float
    confidence_level: str  # 'high', 'medium', 'low'
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'group_id': self.group_id,
            'path': self.path.currency_path_str,
            'allocation': str(self.allocation),
            'probability': self.probability,
            'confidence': self.confidence_level,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AllocationPlan:
    """Complete allocation plan for a trading round."""
    round_id: str
    total_capital: Decimal
    allocated_capital: Decimal
    reserved_capital: Decimal
    decisions: List[AllocationDecision]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def num_groups(self) -> int:
        return len(self.decisions)
    
    @property
    def allocation_efficiency(self) -> float:
        if self.total_capital == 0:
            return 0
        return float(self.allocated_capital / self.total_capital * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'round_id': self.round_id,
            'total_capital': str(self.total_capital),
            'allocated_capital': str(self.allocated_capital),
            'reserved_capital': str(self.reserved_capital),
            'num_groups': self.num_groups,
            'allocation_efficiency': self.allocation_efficiency,
            'decisions': [d.to_dict() for d in self.decisions],
            'timestamp': self.timestamp.isoformat()
        }


class AllocationEngine:
    """
    Dynamic capital allocation based on probability scores.
    
    Allocates between $100-$300 per group based on:
    - Path probability score
    - Historical performance
    - Current market conditions
    - Risk management constraints
    """
    
    def __init__(
        self,
        min_allocation: Decimal = Decimal('100'),
        max_allocation: Decimal = Decimal('300'),
        default_allocation: Decimal = Decimal('200'),
        high_confidence_threshold: float = 0.85,
        low_confidence_threshold: float = 0.50,
        max_total_capital: Decimal = Decimal('1000')
    ):
        self.min_allocation = min_allocation
        self.max_allocation = max_allocation
        self.default_allocation = default_allocation
        self.high_threshold = high_confidence_threshold
        self.low_threshold = low_confidence_threshold
        self.max_total = max_total_capital
        
        # Track allocation history for analysis
        self.allocation_history: List[AllocationPlan] = []
        
    def calculate_allocation(
        self,
        probability: float,
        historical_success_rate: float = 0.5
    ) -> Tuple[Decimal, str, str]:
        """
        Calculate allocation amount based on probability.
        
        Args:
            probability: Path probability score (0-1)
            historical_success_rate: Historical success rate for similar paths
            
        Returns:
            Tuple of (allocation_amount, confidence_level, reasoning)
        """
        # Combine probability with historical data
        combined_score = probability * 0.6 + historical_success_rate * 0.4
        
        if combined_score >= self.high_threshold:
            allocation = self.max_allocation
            confidence = 'high'
            reasoning = f"High confidence ({combined_score:.2f}): Max allocation"
            
        elif combined_score <= self.low_threshold:
            allocation = self.min_allocation
            confidence = 'low'
            reasoning = f"Low confidence ({combined_score:.2f}): Min allocation"
            
        else:
            # Linear interpolation
            range_size = float(self.max_allocation - self.min_allocation)
            score_range = self.high_threshold - self.low_threshold
            normalized = (combined_score - self.low_threshold) / score_range
            
            allocation = self.min_allocation + Decimal(str(normalized * range_size))
            allocation = allocation.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            
            confidence = 'medium'
            reasoning = f"Medium confidence ({combined_score:.2f}): Scaled allocation"
        
        return allocation, confidence, reasoning
    
    def create_allocation_plan(
        self,
        paths: List[TradePath],
        available_capital: Decimal,
        num_groups: int = 5,
        path_history: Dict[str, Dict] = None
    ) -> AllocationPlan:
        """
        Create a complete allocation plan for a trading round.
        
        Args:
            paths: Candidate paths (should be non-overlapping)
            available_capital: Total capital available
            num_groups: Target number of trade groups
            path_history: Historical path performance data
            
        Returns:
            AllocationPlan with decisions for each group
        """
        round_id = f"round_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        path_history = path_history or {}
        
        decisions = []
        total_allocated = Decimal('0')
        
        # Limit to available paths
        paths_to_allocate = paths[:num_groups]
        
        for i, path in enumerate(paths_to_allocate):
            # Get historical success rate for this path
            path_str = path.currency_path_str
            hist = path_history.get(path_str, {})
            hist_success = 0.5  # Default neutral
            
            if hist.get('executions', 0) >= 5:
                total = hist.get('successes', 0) + hist.get('failures', 0)
                if total > 0:
                    hist_success = hist.get('successes', 0) / total
            
            # Calculate allocation
            allocation, confidence, reasoning = self.calculate_allocation(
                path.probability_score,
                hist_success
            )
            
            # Check capital constraints
            remaining = available_capital - total_allocated
            if allocation > remaining:
                allocation = remaining.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                reasoning += f" (capped to remaining ${allocation})"
            
            if allocation < self.min_allocation:
                # Skip if can't meet minimum
                continue
            
            decision = AllocationDecision(
                group_id=i + 1,
                path=path,
                allocation=allocation,
                probability=path.probability_score,
                confidence_level=confidence,
                reasoning=reasoning
            )
            
            decisions.append(decision)
            total_allocated += allocation
            
            if total_allocated >= self.max_total:
                break
        
        plan = AllocationPlan(
            round_id=round_id,
            total_capital=available_capital,
            allocated_capital=total_allocated,
            reserved_capital=available_capital - total_allocated,
            decisions=decisions
        )
        
        self.allocation_history.append(plan)
        
        logger.info(
            f"Allocation plan created: {len(decisions)} groups, "
            f"${total_allocated} allocated ({plan.allocation_efficiency:.1f}% efficiency)"
        )
        
        return plan
    
    def analyze_allocation_performance(self) -> Dict[str, Any]:
        """Analyze historical allocation performance."""
        if not self.allocation_history:
            return {'plans_analyzed': 0}
        
        total_plans = len(self.allocation_history)
        total_decisions = sum(len(p.decisions) for p in self.allocation_history)
        
        high_conf_count = sum(
            1 for p in self.allocation_history 
            for d in p.decisions 
            if d.confidence_level == 'high'
        )
        
        avg_efficiency = sum(p.allocation_efficiency for p in self.allocation_history) / total_plans
        
        avg_allocation = Decimal('0')
        if total_decisions > 0:
            avg_allocation = sum(
                d.allocation for p in self.allocation_history for d in p.decisions
            ) / total_decisions
        
        return {
            'plans_analyzed': total_plans,
            'total_decisions': total_decisions,
            'high_confidence_rate': high_conf_count / total_decisions if total_decisions > 0 else 0,
            'avg_allocation_efficiency': avg_efficiency,
            'avg_allocation_per_group': float(avg_allocation)
        }
    
    def get_recommended_adjustments(self) -> List[str]:
        """Get recommendations for allocation parameter adjustments."""
        analysis = self.analyze_allocation_performance()
        recommendations = []
        
        if analysis.get('high_confidence_rate', 0) > 0.7:
            recommendations.append(
                "High confidence rate is very high - consider raising high_threshold"
            )
        elif analysis.get('high_confidence_rate', 0) < 0.2:
            recommendations.append(
                "High confidence rate is low - consider lowering high_threshold"
            )
        
        if analysis.get('avg_allocation_efficiency', 0) < 70:
            recommendations.append(
                "Allocation efficiency is low - consider expanding path search"
            )
        
        return recommendations
