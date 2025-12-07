"""
Advanced Multi-Currency Path Finder
Discovers profitable conversion paths through 5-10 currencies.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx
from loguru import logger

from src.api.coinbase_client import CoinbaseClient, Product, PriceData


@dataclass
class ConversionStep:
    """Single conversion in a path."""
    step_number: int
    from_currency: str
    to_currency: str
    product_id: str
    side: str  # 'buy' or 'sell'
    rate: Decimal
    fee_adjusted_rate: Decimal
    spread_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step': self.step_number,
            'from': self.from_currency,
            'to': self.to_currency,
            'product': self.product_id,
            'side': self.side,
            'rate': str(self.rate),
            'fee_adj_rate': str(self.fee_adjusted_rate),
            'spread_pct': self.spread_percent
        }


@dataclass
class TradePath:
    """Complete trading path through multiple currencies."""
    path_id: str
    steps: List[ConversionStep]
    currencies: List[str]
    start_currency: str
    end_currency: str
    start_amount: Decimal
    expected_output: Decimal
    profit_amount: Decimal
    profit_percent: Decimal
    total_fees_estimate: Decimal
    probability_score: float
    chain_length: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def currency_path_str(self) -> str:
        """Get human-readable path string."""
        return " → ".join(self.currencies)
    
    @property
    def is_profitable(self) -> bool:
        return self.profit_percent > Decimal('0')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path_id': self.path_id,
            'path': self.currency_path_str,
            'chain_length': self.chain_length,
            'start_amount': str(self.start_amount),
            'expected_output': str(self.expected_output),
            'profit_amount': str(self.profit_amount),
            'profit_percent': str(self.profit_percent),
            'fees_estimate': str(self.total_fees_estimate),
            'probability': self.probability_score,
            'steps': [s.to_dict() for s in self.steps],
            'timestamp': self.timestamp.isoformat()
        }


class PathFinder:
    """
    Advanced path finding engine for multi-currency arbitrage.
    
    Features:
    - Discovers paths through 5-10 currencies
    - Calculates probability scores based on historical performance
    - Filters paths by profitability and liquidity
    - Tracks path success rates for learning
    """
    
    # High-liquidity currencies to prioritize
    PRIORITY_CURRENCIES = {
        'BTC', 'ETH', 'SOL', 'USDC', 'USDT', 'XRP', 'ADA', 
        'DOGE', 'AVAX', 'MATIC', 'LINK', 'DOT'
    }
    
    def __init__(
        self,
        client: CoinbaseClient,
        fee_percent: float = 0.60,
        min_chain_length: int = 5,
        max_chain_length: int = 10,
        min_profit_threshold: float = 0.3
    ):
        self.client = client
        self.fee_rate = Decimal(str(fee_percent)) / Decimal('100')
        self.min_chain_length = min_chain_length
        self.max_chain_length = max_chain_length
        self.min_profit_threshold = Decimal(str(min_profit_threshold))
        
        self.graph = nx.DiGraph()
        self.products: Dict[str, Product] = {}
        self.prices: Dict[str, PriceData] = {}
        
        # Learning: track path success rates
        self.path_history: Dict[str, Dict] = {}  # path_str -> {successes, failures, avg_profit}
        
    async def initialize(self) -> None:
        """Initialize the path finder with current market data."""
        logger.info("Initializing path finder...")
        
        products = await self.client.get_all_products()
        
        for product in products:
            self.products[product.product_id] = product
            
            # Add currency nodes
            self.graph.add_node(product.base_currency)
            self.graph.add_node(product.quote_currency)
        
        logger.info(f"Graph initialized with {self.graph.number_of_nodes()} currencies")
        
    async def update_prices(self) -> int:
        """
        Update all price data.
        
        Returns:
            Number of edges updated
        """
        self.graph.clear_edges()
        updated = 0
        
        tasks = []
        for product_id in self.products:
            tasks.append(self._update_product_price(product_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result is True:
                updated += 1
        
        logger.debug(f"Updated {updated} price edges")
        return updated
    
    async def _update_product_price(self, product_id: str) -> bool:
        """Update price for a single product."""
        try:
            product = self.products[product_id]
            price_data = await self.client.get_price(product_id)
            
            self.prices[product_id] = price_data
            
            if price_data.bid > 0 and price_data.ask > 0:
                base = product.base_currency
                quote = product.quote_currency
                
                # Calculate fee-adjusted rates
                # Buying base with quote: pay ask + fee
                buy_rate = (Decimal('1') / price_data.ask) * (Decimal('1') - self.fee_rate)
                
                # Selling base for quote: receive bid - fee
                sell_rate = price_data.bid * (Decimal('1') - self.fee_rate)
                
                # Add bidirectional edges
                self.graph.add_edge(
                    quote, base,
                    product_id=product_id,
                    side='buy',
                    rate=Decimal('1') / price_data.ask,
                    fee_adjusted_rate=buy_rate,
                    spread_percent=price_data.spread_percent
                )
                
                self.graph.add_edge(
                    base, quote,
                    product_id=product_id,
                    side='sell',
                    rate=price_data.bid,
                    fee_adjusted_rate=sell_rate,
                    spread_percent=price_data.spread_percent
                )
                
                return True
                
        except Exception as e:
            logger.debug(f"Failed to update {product_id}: {e}")
        
        return False
    
    def find_profitable_paths(
        self,
        start_currency: str = 'USDC',
        amount: Decimal = Decimal('200'),
        max_paths: int = 20
    ) -> List[TradePath]:
        """
        Find profitable circular paths starting and ending with the same currency.
        
        Args:
            start_currency: Currency to start and end with
            amount: Amount to trade
            max_paths: Maximum paths to return
            
        Returns:
            List of profitable TradePath objects sorted by expected profit
        """
        if start_currency not in self.graph:
            logger.warning(f"Start currency {start_currency} not in graph")
            return []
        
        all_paths = []
        
        # Search for paths of varying lengths
        for length in range(self.min_chain_length, self.max_chain_length + 1):
            paths = self._find_paths_of_length(
                start_currency,
                length,
                amount
            )
            all_paths.extend(paths)
        
        # Sort by profit and filter
        all_paths.sort(key=lambda p: p.profit_percent, reverse=True)
        
        profitable = [
            p for p in all_paths 
            if p.profit_percent >= self.min_profit_threshold
        ]
        
        logger.info(f"Found {len(profitable)} profitable paths (>{self.min_profit_threshold}%)")
        
        return profitable[:max_paths]
    
    def _find_paths_of_length(
        self,
        start: str,
        length: int,
        amount: Decimal
    ) -> List[TradePath]:
        """Find all circular paths of a specific length."""
        paths = []
        path_counter = 0
        
        def dfs(
            current: str,
            depth: int,
            visited: Set[str],
            currency_path: List[str],
            steps: List[ConversionStep],
            current_amount: Decimal,
            total_spread: float
        ):
            nonlocal path_counter
            
            if depth == 0:
                if current == start and len(currency_path) > 2:
                    # Found a valid circular path
                    profit = current_amount - amount
                    profit_pct = (profit / amount) * Decimal('100')
                    
                    if profit_pct > 0:
                        path_counter += 1
                        path_id = f"path_{start}_{length}_{path_counter}"
                        
                        # Calculate probability score
                        prob = self._calculate_probability(
                            currency_path,
                            profit_pct,
                            total_spread / len(steps) if steps else 0
                        )
                        
                        path = TradePath(
                            path_id=path_id,
                            steps=steps.copy(),
                            currencies=currency_path.copy(),
                            start_currency=start,
                            end_currency=start,
                            start_amount=amount,
                            expected_output=current_amount,
                            profit_amount=profit,
                            profit_percent=profit_pct,
                            total_fees_estimate=amount * self.fee_rate * len(steps),
                            probability_score=prob,
                            chain_length=len(steps)
                        )
                        paths.append(path)
                return
            
            for neighbor in self.graph.neighbors(current):
                # Allow returning to start only on final step
                if neighbor in visited and not (depth == 1 and neighbor == start):
                    continue
                
                edge = self.graph.get_edge_data(current, neighbor)
                if not edge:
                    continue
                
                # Calculate output
                rate = edge['fee_adjusted_rate']
                new_amount = (current_amount * rate).quantize(
                    Decimal('0.00000001'),
                    rounding=ROUND_DOWN
                )
                
                if new_amount <= 0:
                    continue
                
                step = ConversionStep(
                    step_number=len(steps) + 1,
                    from_currency=current,
                    to_currency=neighbor,
                    product_id=edge['product_id'],
                    side=edge['side'],
                    rate=edge['rate'],
                    fee_adjusted_rate=rate,
                    spread_percent=edge['spread_percent']
                )
                
                new_visited = visited | {neighbor} if neighbor != start else visited
                
                dfs(
                    neighbor,
                    depth - 1,
                    new_visited,
                    currency_path + [neighbor],
                    steps + [step],
                    new_amount,
                    total_spread + edge['spread_percent']
                )
        
        dfs(start, length, {start}, [start], [], amount, 0)
        return paths
    
    def _calculate_probability(
        self,
        currency_path: List[str],
        profit_pct: Decimal,
        avg_spread: float
    ) -> float:
        """
        Calculate probability score for a path.
        
        Factors:
        - Historical success rate
        - Profit margin
        - Average spread
        - Number of priority currencies
        """
        path_str = " → ".join(currency_path)
        
        # Base probability from profit margin
        profit_factor = min(float(profit_pct) / 2.0, 1.0)  # Cap at 2% = 1.0
        
        # Spread penalty (high spread = lower probability)
        spread_factor = max(0, 1 - (avg_spread / 1.0))  # 1% spread = 0 factor
        
        # Priority currency bonus
        priority_count = sum(1 for c in currency_path if c in self.PRIORITY_CURRENCIES)
        priority_factor = priority_count / len(currency_path)
        
        # Historical performance
        historical_factor = 0.5  # Default neutral
        if path_str in self.path_history:
            history = self.path_history[path_str]
            total = history.get('successes', 0) + history.get('failures', 0)
            if total >= 5:
                historical_factor = history.get('successes', 0) / total
        
        # Combined probability
        probability = (
            profit_factor * 0.3 +
            spread_factor * 0.2 +
            priority_factor * 0.2 +
            historical_factor * 0.3
        )
        
        return min(max(probability, 0.1), 0.99)  # Clamp between 0.1 and 0.99
    
    def get_non_overlapping_paths(
        self,
        paths: List[TradePath],
        num_groups: int = 5
    ) -> List[TradePath]:
        """
        Select non-overlapping paths for concurrent execution.
        
        Args:
            paths: Candidate paths sorted by preference
            num_groups: Number of groups to select
            
        Returns:
            List of non-overlapping paths
        """
        if not paths:
            return []
        
        selected: List[TradePath] = []
        used_currencies: Set[str] = set()
        
        # Exclude base currencies from overlap check
        excluded = {'USDC', 'USD', 'USDT'}
        
        for path in paths:
            # Get tradeable currencies (exclude base)
            path_currencies = set(path.currencies) - excluded
            
            # Check for overlap
            if not path_currencies.intersection(used_currencies):
                selected.append(path)
                used_currencies.update(path_currencies)
                
                if len(selected) >= num_groups:
                    break
        
        logger.info(f"Selected {len(selected)} non-overlapping paths")
        return selected
    
    def record_path_result(
        self,
        path: TradePath,
        success: bool,
        actual_profit_pct: float
    ) -> None:
        """
        Record path execution result for learning.
        
        Args:
            path: The executed path
            success: Whether the trade was profitable
            actual_profit_pct: Actual profit percentage achieved
        """
        path_str = path.currency_path_str
        
        if path_str not in self.path_history:
            self.path_history[path_str] = {
                'successes': 0,
                'failures': 0,
                'total_profit': 0,
                'executions': 0
            }
        
        history = self.path_history[path_str]
        history['executions'] += 1
        history['total_profit'] += actual_profit_pct
        
        if success:
            history['successes'] += 1
        else:
            history['failures'] += 1
        
        # Update average
        history['avg_profit'] = history['total_profit'] / history['executions']
    
    def get_path_statistics(self) -> Dict[str, Any]:
        """Get statistics on discovered paths."""
        if not self.path_history:
            return {'paths_tracked': 0}
        
        total_paths = len(self.path_history)
        total_executions = sum(h['executions'] for h in self.path_history.values())
        total_successes = sum(h['successes'] for h in self.path_history.values())
        
        best_path = max(
            self.path_history.items(),
            key=lambda x: x[1].get('avg_profit', 0)
        )
        
        return {
            'paths_tracked': total_paths,
            'total_executions': total_executions,
            'overall_success_rate': total_successes / total_executions if total_executions > 0 else 0,
            'best_path': best_path[0],
            'best_path_avg_profit': best_path[1].get('avg_profit', 0)
        }
