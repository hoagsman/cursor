"""
Institutional Grade Coinbase Client
Production-ready API integration with comprehensive error handling.
"""

import asyncio
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json

from coinbase.rest import RESTClient
from loguru import logger
from aiolimiter import AsyncLimiter


class OrderStatus(Enum):
    """Order execution status."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class Product:
    """Trading pair information."""
    product_id: str
    base_currency: str
    quote_currency: str
    base_min_size: Decimal
    base_max_size: Decimal
    quote_increment: Decimal
    base_increment: Decimal
    min_market_funds: Decimal
    max_market_funds: Decimal
    status: str
    trading_disabled: bool
    
    @property
    def is_tradeable(self) -> bool:
        return self.status == 'online' and not self.trading_disabled


@dataclass
class PriceData:
    """Real-time price information."""
    product_id: str
    bid: Decimal
    ask: Decimal
    price: Decimal
    volume_24h: Decimal
    spread: Decimal
    spread_percent: float
    timestamp: datetime
    
    @property
    def mid_price(self) -> Decimal:
        return (self.bid + self.ask) / 2


@dataclass
class OrderResult:
    """Result of an order execution."""
    order_id: str
    product_id: str
    side: str
    order_type: str
    size: Decimal
    filled_size: Decimal
    price: Decimal
    average_price: Decimal
    fee: Decimal
    status: OrderStatus
    created_at: datetime
    completed_at: Optional[datetime]
    execution_time_ms: float
    slippage_percent: float
    
    # Audit fields
    request_hash: str
    response_hash: str
    
    def to_audit_dict(self) -> Dict[str, Any]:
        """Convert to audit-ready dictionary."""
        return {
            'order_id': self.order_id,
            'product_id': self.product_id,
            'side': self.side,
            'order_type': self.order_type,
            'size': str(self.size),
            'filled_size': str(self.filled_size),
            'price': str(self.price),
            'average_price': str(self.average_price),
            'fee': str(self.fee),
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time_ms': self.execution_time_ms,
            'slippage_percent': self.slippage_percent,
            'request_hash': self.request_hash,
            'response_hash': self.response_hash
        }


class CoinbaseClient:
    """
    Production-grade Coinbase Advanced Trade API client.
    
    Features:
    - Rate limiting
    - Automatic retries with exponential backoff
    - Comprehensive error handling
    - Audit trail for all operations
    - Connection health monitoring
    """
    
    # Rate limits: 10 requests per second for private endpoints
    RATE_LIMIT = 10
    RATE_PERIOD = 1.0
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_retries = max_retries
        self.timeout = timeout
        
        self._client: Optional[RESTClient] = None
        self._rate_limiter = AsyncLimiter(self.RATE_LIMIT, self.RATE_PERIOD)
        
        # Caches
        self._products_cache: Dict[str, Product] = {}
        self._price_cache: Dict[str, PriceData] = {}
        self._last_products_refresh: Optional[datetime] = None
        
        # Health tracking
        self._consecutive_errors = 0
        self._total_requests = 0
        self._failed_requests = 0
        
    def connect(self) -> bool:
        """
        Establish connection to Coinbase API.
        
        Returns:
            True if connection successful
        """
        try:
            self._client = RESTClient(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            # Test connection
            self._client.get_accounts()
            
            self._consecutive_errors = 0
            logger.info("✅ Connected to Coinbase Advanced Trade API")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Coinbase: {e}")
            return False
    
    async def get_all_products(self, force_refresh: bool = False) -> List[Product]:
        """
        Fetch all available trading pairs.
        
        Args:
            force_refresh: Force cache refresh
            
        Returns:
            List of tradeable products
        """
        if (
            not force_refresh 
            and self._products_cache 
            and self._last_products_refresh
            and (datetime.now() - self._last_products_refresh).seconds < 300
        ):
            return list(self._products_cache.values())
        
        await self._rate_limiter.acquire()
        
        try:
            response = self._client.get_products()
            products = []
            
            for p in response.get('products', []):
                product = Product(
                    product_id=p['product_id'],
                    base_currency=p['base_currency_id'],
                    quote_currency=p['quote_currency_id'],
                    base_min_size=Decimal(p.get('base_min_size', '0')),
                    base_max_size=Decimal(p.get('base_max_size', '999999999')),
                    quote_increment=Decimal(p.get('quote_increment', '0.01')),
                    base_increment=Decimal(p.get('base_increment', '0.00000001')),
                    min_market_funds=Decimal(p.get('min_market_funds', '1')),
                    max_market_funds=Decimal(p.get('max_market_funds', '1000000')),
                    status=p.get('status', 'offline'),
                    trading_disabled=p.get('trading_disabled', True)
                )
                
                if product.is_tradeable:
                    products.append(product)
                    self._products_cache[product.product_id] = product
            
            self._last_products_refresh = datetime.now()
            self._consecutive_errors = 0
            
            logger.info(f"Loaded {len(products)} tradeable products")
            return products
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def get_price(self, product_id: str) -> PriceData:
        """
        Get current price data for a product.
        
        Args:
            product_id: Trading pair ID
            
        Returns:
            PriceData with current bid/ask/price
        """
        await self._rate_limiter.acquire()
        
        try:
            ticker = self._client.get_product(product_id)
            
            bid = Decimal(ticker.get('bid', '0'))
            ask = Decimal(ticker.get('ask', '0'))
            
            spread = ask - bid if bid > 0 and ask > 0 else Decimal('0')
            spread_pct = float(spread / bid * 100) if bid > 0 else 0
            
            price_data = PriceData(
                product_id=product_id,
                bid=bid,
                ask=ask,
                price=Decimal(ticker.get('price', '0')),
                volume_24h=Decimal(ticker.get('volume_24h', '0')),
                spread=spread,
                spread_percent=spread_pct,
                timestamp=datetime.now()
            )
            
            self._price_cache[product_id] = price_data
            self._consecutive_errors = 0
            
            return price_data
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def get_balance(self, currency: str) -> Decimal:
        """Get available balance for a currency."""
        await self._rate_limiter.acquire()
        
        try:
            accounts = self._client.get_accounts()
            
            for account in accounts.get('accounts', []):
                if account['currency'] == currency:
                    return Decimal(account['available_balance']['value'])
            
            return Decimal('0')
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def get_all_balances(self) -> Dict[str, Decimal]:
        """Get all non-zero balances."""
        await self._rate_limiter.acquire()
        
        try:
            accounts = self._client.get_accounts()
            balances = {}
            
            for account in accounts.get('accounts', []):
                balance = Decimal(account['available_balance']['value'])
                if balance > 0:
                    balances[account['currency']] = balance
            
            return balances
            
        except Exception as e:
            self._handle_error(e)
            raise
    
    async def execute_market_order(
        self,
        product_id: str,
        side: str,
        size: Optional[Decimal] = None,
        quote_size: Optional[Decimal] = None,
        expected_price: Optional[Decimal] = None
    ) -> OrderResult:
        """
        Execute a market order with full audit trail.
        
        Args:
            product_id: Trading pair
            side: 'buy' or 'sell'
            size: Base currency amount (for sells)
            quote_size: Quote currency amount (for buys)
            expected_price: Expected execution price (for slippage calc)
            
        Returns:
            OrderResult with complete execution details
        """
        start_time = datetime.now()
        
        # Build request
        request_data = {
            'product_id': product_id,
            'side': side.upper(),
            'timestamp': start_time.isoformat()
        }
        
        order_config = {'market_market_ioc': {}}
        
        if size:
            order_config['market_market_ioc']['base_size'] = str(size)
            request_data['base_size'] = str(size)
        elif quote_size:
            order_config['market_market_ioc']['quote_size'] = str(quote_size)
            request_data['quote_size'] = str(quote_size)
        else:
            raise ValueError("Must specify either size or quote_size")
        
        request_hash = hashlib.sha256(json.dumps(request_data).encode()).hexdigest()[:16]
        
        await self._rate_limiter.acquire()
        self._total_requests += 1
        
        for attempt in range(self.max_retries):
            try:
                client_order_id = f"mpc_{start_time.timestamp()}_{request_hash}"
                
                response = self._client.create_order(
                    client_order_id=client_order_id,
                    product_id=product_id,
                    side=side.upper(),
                    order_configuration=order_config
                )
                
                order_id = response.get('order_id', '')
                
                # Get full order details
                await asyncio.sleep(0.1)  # Brief delay for order to settle
                order_details = self._client.get_order(order_id)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                average_price = Decimal(order_details.get('average_filled_price', '0'))
                slippage = 0.0
                if expected_price and expected_price > 0:
                    slippage = float((average_price - expected_price) / expected_price * 100)
                
                response_hash = hashlib.sha256(
                    json.dumps(order_details, default=str).encode()
                ).hexdigest()[:16]
                
                result = OrderResult(
                    order_id=order_id,
                    product_id=product_id,
                    side=side,
                    order_type='market',
                    size=size or Decimal('0'),
                    filled_size=Decimal(order_details.get('filled_size', '0')),
                    price=expected_price or Decimal('0'),
                    average_price=average_price,
                    fee=Decimal(order_details.get('total_fees', '0')),
                    status=OrderStatus.FILLED if order_details.get('status') == 'FILLED' else OrderStatus.FAILED,
                    created_at=start_time,
                    completed_at=end_time,
                    execution_time_ms=execution_time,
                    slippage_percent=slippage,
                    request_hash=request_hash,
                    response_hash=response_hash
                )
                
                self._consecutive_errors = 0
                logger.debug(f"Order executed: {product_id} {side} - {execution_time:.0f}ms")
                
                return result
                
            except Exception as e:
                self._failed_requests += 1
                logger.warning(f"Order attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self._handle_error(e)
                    
                    # Return failed result
                    return OrderResult(
                        order_id='',
                        product_id=product_id,
                        side=side,
                        order_type='market',
                        size=size or Decimal('0'),
                        filled_size=Decimal('0'),
                        price=expected_price or Decimal('0'),
                        average_price=Decimal('0'),
                        fee=Decimal('0'),
                        status=OrderStatus.FAILED,
                        created_at=start_time,
                        completed_at=datetime.now(),
                        execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        slippage_percent=0,
                        request_hash=request_hash,
                        response_hash='FAILED'
                    )
    
    def _handle_error(self, error: Exception) -> None:
        """Handle and track errors."""
        self._consecutive_errors += 1
        logger.error(f"Coinbase API error ({self._consecutive_errors} consecutive): {error}")
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Get client health metrics."""
        success_rate = 0
        if self._total_requests > 0:
            success_rate = (self._total_requests - self._failed_requests) / self._total_requests * 100
        
        return {
            'connected': self._client is not None,
            'consecutive_errors': self._consecutive_errors,
            'total_requests': self._total_requests,
            'failed_requests': self._failed_requests,
            'success_rate': success_rate,
            'products_cached': len(self._products_cache),
            'prices_cached': len(self._price_cache)
        }
    
    def close(self) -> None:
        """Close client connection."""
        self._client = None
        logger.info("Coinbase client closed")
