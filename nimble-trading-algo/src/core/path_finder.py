"""
Multi-Token Path Finder
Discovers profitable conversion paths between tokens using graph algorithms.
Supports chains of up to 7 tokens before converting back to USDC.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx
from loguru import logger

from src.api.coinbase_client import CoinbaseClient, TokenPair


@dataclass
class ConversionStep:
    """Single step in a conversion path."""
    from_token: str
    to_token: str
    product_id: str
    side: str  # 'buy' or 'sell'
    rate: Decimal  # How much to_token you get per from_token
    fee_adjusted_rate: Decimal  # Rate after Coinbase fees
    
    def __str__(self) -> str:
        return f"{self.from_token} -> {self.to_token} ({self.product_id})"


@dataclass
class TradePath:
    """Complete trading path from USDC through tokens back to USDC."""
    steps: List[ConversionStep]
    start_amount: Decimal
    end_amount: Decimal
    profit_percent: Decimal
    tokens_used: Set[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_profitable(self) -> bool:
        return self.profit_percent > Decimal('0')
    
    @property
    def chain_length(self) -> int:
        return len(self.steps)
    
    def __str__(self) -> str:
        path_str = " -> ".join([self.steps[0].from_token] + [s.to_token for s in self.steps])
        return f"{path_str} | Profit: {self.profit_percent:.4f}%"


class PathFinder:
    """
    Discovers arbitrage opportunities through multi-token conversion paths.
    
    Uses a directed graph where:
    - Nodes are tokens (BTC, ETH, USDC, etc.)
    - Edges are trading pairs with conversion rates
    - Edge weights are negative log of rates (for Bellman-Ford profit finding)
    """
    
    def __init__(
        self,
        client: CoinbaseClient,
        fee_percent: float = 0.60,
        max_chain_length: int = 7,
        min_profit_threshold: float = 0.5
    ):
        """
        Initialize the path finder.
        
        Args:
            client: Coinbase API client
            fee_percent: Trading fee percentage
            max_chain_length: Maximum number of tokens in a path
            min_profit_threshold: Minimum profit % to consider a path viable
        """
        self.client = client
        self.fee_rate = Decimal(str(fee_percent)) / Decimal('100')
        self.max_chain_length = max_chain_length
        self.min_profit_threshold = Decimal(str(min_profit_threshold))
        
        self.graph = nx.DiGraph()
        self.products: Dict[str, TokenPair] = {}
        self.price_cache: Dict[str, Dict] = {}
        
    async def build_token_graph(self) -> None:
        """
        Build the token conversion graph from available trading pairs.
        """
        logger.info("Building token conversion graph...")
        
        # Get all available products
        products = await self.client.get_all_products()
        
        for product in products:
            self.products[product.product_id] = product
            
            base = product.base_currency
            quote = product.quote_currency
            
            # Add nodes for both tokens
            if not self.graph.has_node(base):
                self.graph.add_node(base)
            if not self.graph.has_node(quote):
                self.graph.add_node(quote)
        
        logger.info(f"Graph has {self.graph.number_of_nodes()} tokens")
        
    async def update_prices(self) -> None:
        """
        Update all price data and edge weights in the graph.
        """
        logger.debug("Updating price data...")
        
        # Clear existing edges
        self.graph.clear_edges()
        
        update_tasks = []
        for product_id in self.products:
            update_tasks.append(self._update_pair_prices(product_id))
        
        # Update prices concurrently
        await asyncio.gather(*update_tasks, return_exceptions=True)
        
        logger.debug(f"Updated {self.graph.number_of_edges()} conversion edges")
    
    async def _update_pair_prices(self, product_id: str) -> None:
        """Update prices for a single trading pair."""
        try:
            product = self.products[product_id]
            prices = await self.client.get_product_price(product_id)
            
            self.price_cache[product_id] = {
                **prices,
                'timestamp': datetime.now()
            }
            
            bid = prices['bid']
            ask = prices['ask']
            
            if bid > 0 and ask > 0:
                base = product.base_currency
                quote = product.quote_currency
                
                # Fee-adjusted rates
                # Buying base with quote: pay ask price + fee
                buy_rate = (Decimal('1') / ask) * (Decimal('1') - self.fee_rate)
                
                # Selling base for quote: receive bid price - fee
                sell_rate = bid * (Decimal('1') - self.fee_rate)
                
                # Add edges in both directions
                # quote -> base (buying)
                self.graph.add_edge(
                    quote, base,
                    product_id=product_id,
                    side='buy',
                    rate=Decimal('1') / ask,
                    fee_adjusted_rate=buy_rate,
                    raw_price=ask
                )
                
                # base -> quote (selling)
                self.graph.add_edge(
                    base, quote,
                    product_id=product_id,
                    side='sell',
                    rate=bid,
                    fee_adjusted_rate=sell_rate,
                    raw_price=bid
                )
                
        except Exception as e:
            logger.warning(f"Failed to update prices for {product_id}: {e}")
    
    def find_profitable_paths(
        self,
        start_token: str = 'USDC',
        start_amount: Decimal = Decimal('250'),
        min_paths: int = 4,
        max_paths: int = 8
    ) -> List[TradePath]:
        """
        Find profitable conversion paths starting and ending with the same token.
        
        Args:
            start_token: Starting token (typically USDC)
            start_amount: Amount to start with
            min_paths: Minimum number of paths to find
            max_paths: Maximum number of paths to return
            
        Returns:
            List of profitable TradePath objects, sorted by profit.
        """
        if start_token not in self.graph:
            logger.warning(f"Start token {start_token} not found in graph")
            return []
        
        profitable_paths = []
        
        # Find paths using DFS with depth limit
        for path_length in range(2, self.max_chain_length + 1):
            paths = self._find_paths_of_length(
                start_token,
                start_token,
                path_length,
                start_amount
            )
            profitable_paths.extend(paths)
        
        # Sort by profit and filter
        profitable_paths.sort(key=lambda p: p.profit_percent, reverse=True)
        
        # Filter paths meeting minimum profit threshold
        viable_paths = [
            p for p in profitable_paths 
            if p.profit_percent >= self.min_profit_threshold
        ]
        
        logger.info(f"Found {len(viable_paths)} viable paths with >{self.min_profit_threshold}% profit")
        
        return viable_paths[:max_paths]
    
    def _find_paths_of_length(
        self,
        start: str,
        end: str,
        length: int,
        start_amount: Decimal
    ) -> List[TradePath]:
        """Find all paths of a specific length between start and end tokens."""
        paths = []
        
        def dfs(current: str, target: str, depth: int, visited: Set[str], 
                steps: List[ConversionStep], amount: Decimal):
            """Depth-first search for paths."""
            if depth == 0:
                if current == target and len(steps) > 1:
                    # Found a valid cycle
                    profit = ((amount - start_amount) / start_amount) * Decimal('100')
                    
                    if profit > 0:
                        tokens = set()
                        for step in steps:
                            tokens.add(step.from_token)
                            tokens.add(step.to_token)
                        
                        path = TradePath(
                            steps=steps.copy(),
                            start_amount=start_amount,
                            end_amount=amount,
                            profit_percent=profit,
                            tokens_used=tokens
                        )
                        paths.append(path)
                return
            
            for neighbor in self.graph.neighbors(current):
                # Allow returning to start only on final step
                if neighbor in visited and not (depth == 1 and neighbor == target):
                    continue
                
                edge_data = self.graph.get_edge_data(current, neighbor)
                if not edge_data:
                    continue
                
                # Calculate output amount
                rate = edge_data['fee_adjusted_rate']
                new_amount = (amount * rate).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
                
                if new_amount <= 0:
                    continue
                
                step = ConversionStep(
                    from_token=current,
                    to_token=neighbor,
                    product_id=edge_data['product_id'],
                    side=edge_data['side'],
                    rate=edge_data['rate'],
                    fee_adjusted_rate=rate
                )
                
                new_visited = visited | {neighbor} if neighbor != target else visited
                
                dfs(
                    neighbor,
                    target,
                    depth - 1,
                    new_visited,
                    steps + [step],
                    new_amount
                )
        
        dfs(start, end, length, {start}, [], start_amount)
        return paths
    
    def get_non_overlapping_paths(
        self,
        paths: List[TradePath],
        num_groups: int = 4
    ) -> List[TradePath]:
        """
        Select non-overlapping paths (no shared tokens between concurrent trades).
        
        Args:
            paths: List of candidate paths
            num_groups: Number of paths to select
            
        Returns:
            List of non-overlapping paths.
        """
        if not paths:
            return []
        
        selected: List[TradePath] = []
        used_tokens: Set[str] = set()
        
        # Always exclude USDC from overlap checking (it's our base currency)
        excluded_tokens = {'USDC', 'USD'}
        
        for path in paths:
            # Get tradeable tokens (exclude base currencies)
            path_tokens = path.tokens_used - excluded_tokens
            
            # Check for overlap with already selected paths
            if not path_tokens.intersection(used_tokens):
                selected.append(path)
                used_tokens.update(path_tokens)
                
                if len(selected) >= num_groups:
                    break
        
        logger.info(f"Selected {len(selected)} non-overlapping paths")
        return selected
    
    def estimate_path_execution_time(self, path: TradePath) -> float:
        """
        Estimate execution time for a path in seconds.
        
        Args:
            path: Trading path to estimate
            
        Returns:
            Estimated execution time in seconds.
        """
        # Base time per trade + network latency estimate
        base_time_per_step = 0.5  # seconds
        latency_buffer = 0.2  # seconds
        
        return (path.chain_length * base_time_per_step) + latency_buffer
    
    def validate_path(self, path: TradePath) -> Tuple[bool, str]:
        """
        Validate that a path can still be executed.
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        for step in path.steps:
            product_id = step.product_id
            
            if product_id not in self.products:
                return False, f"Product {product_id} no longer available"
            
            product = self.products[product_id]
            if product.status != 'online':
                return False, f"Product {product_id} is offline"
        
        return True, "Valid"
