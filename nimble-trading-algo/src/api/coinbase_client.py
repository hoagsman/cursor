"""
Coinbase Advanced Trade API Client
Handles all interactions with Coinbase for market data and order execution.
"""

import asyncio
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

from coinbase.rest import RESTClient
from loguru import logger


@dataclass
class TokenPair:
    """Represents a trading pair on Coinbase."""
    product_id: str  # e.g., "BTC-USDC"
    base_currency: str  # e.g., "BTC"
    quote_currency: str  # e.g., "USDC"
    base_min_size: Decimal
    base_max_size: Decimal
    quote_increment: Decimal
    base_increment: Decimal
    status: str
    

@dataclass
class OrderBook:
    """Snapshot of order book for a trading pair."""
    product_id: str
    bids: List[tuple]  # [(price, size), ...]
    asks: List[tuple]  # [(price, size), ...]
    timestamp: datetime
    
    @property
    def best_bid(self) -> Optional[Decimal]:
        return Decimal(self.bids[0][0]) if self.bids else None
    
    @property
    def best_ask(self) -> Optional[Decimal]:
        return Decimal(self.asks[0][0]) if self.asks else None
    
    @property
    def spread(self) -> Optional[Decimal]:
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None


@dataclass
class Trade:
    """Represents a completed or pending trade."""
    order_id: str
    product_id: str
    side: str  # 'buy' or 'sell'
    size: Decimal
    price: Decimal
    fee: Decimal
    status: str
    timestamp: datetime
    
    @property
    def total_cost(self) -> Decimal:
        """Total cost including fees."""
        if self.side == 'buy':
            return (self.size * self.price) + self.fee
        return (self.size * self.price) - self.fee


class CoinbaseClient:
    """
    Async client for Coinbase Advanced Trade API.
    Handles market data fetching and order execution.
    """
    
    def __init__(self, api_key: str, api_secret: str, sandbox: bool = False):
        """
        Initialize the Coinbase client.
        
        Args:
            api_key: Coinbase API key
            api_secret: Coinbase API secret
            sandbox: Use sandbox environment for testing
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        self._client: Optional[RESTClient] = None
        self._products_cache: Dict[str, TokenPair] = {}
        self._price_cache: Dict[str, Dict] = {}
        
    def connect(self) -> None:
        """Initialize the REST client connection."""
        try:
            self._client = RESTClient(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            logger.info("Connected to Coinbase Advanced Trade API")
        except Exception as e:
            logger.error(f"Failed to connect to Coinbase: {e}")
            raise
    
    async def get_all_products(self) -> List[TokenPair]:
        """
        Fetch all available trading pairs from Coinbase.
        
        Returns:
            List of TokenPair objects for active trading pairs.
        """
        if not self._client:
            self.connect()
            
        try:
            response = self._client.get_products()
            products = []
            
            for product in response.get('products', []):
                # Only include active trading pairs
                if product.get('status') == 'online':
                    pair = TokenPair(
                        product_id=product['product_id'],
                        base_currency=product['base_currency_id'],
                        quote_currency=product['quote_currency_id'],
                        base_min_size=Decimal(product.get('base_min_size', '0')),
                        base_max_size=Decimal(product.get('base_max_size', '999999999')),
                        quote_increment=Decimal(product.get('quote_increment', '0.01')),
                        base_increment=Decimal(product.get('base_increment', '0.00000001')),
                        status=product['status']
                    )
                    products.append(pair)
                    self._products_cache[pair.product_id] = pair
                    
            logger.info(f"Loaded {len(products)} active trading pairs")
            return products
            
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            raise
    
    async def get_product_price(self, product_id: str) -> Dict[str, Decimal]:
        """
        Get current price data for a trading pair.
        
        Args:
            product_id: Trading pair ID (e.g., "BTC-USDC")
            
        Returns:
            Dictionary with bid, ask, and last prices.
        """
        if not self._client:
            self.connect()
            
        try:
            ticker = self._client.get_product(product_id)
            
            price_data = {
                'bid': Decimal(ticker.get('bid', '0')),
                'ask': Decimal(ticker.get('ask', '0')),
                'price': Decimal(ticker.get('price', '0')),
                'volume_24h': Decimal(ticker.get('volume_24h', '0'))
            }
            
            self._price_cache[product_id] = {
                **price_data,
                'timestamp': datetime.now()
            }
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error fetching price for {product_id}: {e}")
            raise
    
    async def get_order_book(self, product_id: str, level: int = 2) -> OrderBook:
        """
        Get order book for a trading pair.
        
        Args:
            product_id: Trading pair ID
            level: Order book depth (1=best, 2=top 50, 3=full)
            
        Returns:
            OrderBook object with current bids and asks.
        """
        if not self._client:
            self.connect()
            
        try:
            book = self._client.get_product_book(product_id, level=level)
            
            return OrderBook(
                product_id=product_id,
                bids=[(b['price'], b['size']) for b in book.get('bids', [])],
                asks=[(a['price'], a['size']) for a in book.get('asks', [])],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching order book for {product_id}: {e}")
            raise
    
    async def get_account_balance(self, currency: str = 'USDC') -> Decimal:
        """
        Get account balance for a specific currency.
        
        Args:
            currency: Currency code (e.g., 'USDC', 'BTC')
            
        Returns:
            Available balance as Decimal.
        """
        if not self._client:
            self.connect()
            
        try:
            accounts = self._client.get_accounts()
            
            for account in accounts.get('accounts', []):
                if account['currency'] == currency:
                    return Decimal(account['available_balance']['value'])
            
            return Decimal('0')
            
        except Exception as e:
            logger.error(f"Error fetching balance for {currency}: {e}")
            raise
    
    async def place_market_order(
        self,
        product_id: str,
        side: str,
        size: Optional[Decimal] = None,
        quote_size: Optional[Decimal] = None
    ) -> Trade:
        """
        Place a market order.
        
        Args:
            product_id: Trading pair ID
            side: 'buy' or 'sell'
            size: Amount of base currency (for sells)
            quote_size: Amount of quote currency (for buys)
            
        Returns:
            Trade object with order details.
        """
        if not self._client:
            self.connect()
            
        try:
            order_config = {
                'market_market_ioc': {}
            }
            
            if size:
                order_config['market_market_ioc']['base_size'] = str(size)
            elif quote_size:
                order_config['market_market_ioc']['quote_size'] = str(quote_size)
            else:
                raise ValueError("Must specify either size or quote_size")
            
            response = self._client.create_order(
                client_order_id=f"nimble_{datetime.now().timestamp()}",
                product_id=product_id,
                side=side.upper(),
                order_configuration=order_config
            )
            
            order_id = response.get('order_id', '')
            
            # Get order details
            order = self._client.get_order(order_id)
            
            return Trade(
                order_id=order_id,
                product_id=product_id,
                side=side,
                size=Decimal(order.get('filled_size', '0')),
                price=Decimal(order.get('average_filled_price', '0')),
                fee=Decimal(order.get('total_fees', '0')),
                status=order.get('status', 'unknown'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise
    
    async def get_all_balances(self) -> Dict[str, Decimal]:
        """
        Get all non-zero account balances.
        
        Returns:
            Dictionary of currency -> balance.
        """
        if not self._client:
            self.connect()
            
        try:
            accounts = self._client.get_accounts()
            balances = {}
            
            for account in accounts.get('accounts', []):
                balance = Decimal(account['available_balance']['value'])
                if balance > 0:
                    balances[account['currency']] = balance
            
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching balances: {e}")
            raise
    
    def close(self) -> None:
        """Close the client connection."""
        self._client = None
        logger.info("Coinbase client closed")
