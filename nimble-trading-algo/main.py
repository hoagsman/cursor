#!/usr/bin/env python3
"""
Nimble Trading Algorithm - Main Entry Point
Cryptocurrency arbitrage trading system for Coinbase.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import click
from loguru import logger
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import load_config, TradingConfig
from src.strategies.nimble_strategy import NimbleStrategy
from backtesting.backtester import Backtester, BacktestConfig, run_parameter_optimization


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/trading_{time}.log",
        rotation="1 day",
        retention="30 days",
        level=log_level
    )


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug: bool):
    """Nimble Trading Algorithm - Crypto Arbitrage System"""
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level)


@cli.command()
@click.option('--rounds', '-r', default=None, type=int, help='Number of rounds to execute')
@click.option('--paper', is_flag=True, default=True, help='Use paper trading mode')
@click.option('--live', is_flag=True, help='Use live trading mode (CAUTION: Real money)')
def run(rounds: int, paper: bool, live: bool):
    """Run the trading algorithm."""
    load_dotenv()
    
    try:
        config = load_config()
        
        # Override trading mode from CLI
        if live:
            config.trading_mode = 'live'
            logger.warning("⚠️  LIVE TRADING MODE - Real money will be used!")
            click.confirm('Are you sure you want to trade with real money?', abort=True)
        else:
            config.trading_mode = 'paper'
            logger.info("📝 Paper trading mode - No real money involved")
        
        strategy = NimbleStrategy(config)
        
        async def main():
            await strategy.initialize()
            await strategy.run(max_rounds=rounds)
        
        asyncio.run(main())
        
    except Exception as e:
        logger.error(f"Failed to run strategy: {e}")
        sys.exit(1)


@cli.command()
@click.option('--days', '-d', default=30, help='Number of days to backtest')
@click.option('--capital', '-c', default=1000, help='Initial capital for backtest')
@click.option('--groups', '-g', default=4, help='Number of trade groups')
@click.option('--output', '-o', default='./data/backtest', help='Output directory')
def backtest(days: int, capital: float, groups: int, output: str):
    """Run backtesting simulation."""
    logger.info(f"Running {days}-day backtest with ${capital} capital...")
    
    config = BacktestConfig(
        start_date=datetime.now() - timedelta(days=days),
        end_date=datetime.now(),
        initial_capital=Decimal(str(capital)),
        num_trade_groups=groups,
        max_chain_length=7,
        min_profit_threshold=0.5,
        fee_percent=0.60,
        slippage_percent=0.1,
        price_volatility=2.0
    )
    
    backtester = Backtester(config)
    result = backtester.run_backtest()
    
    # Print results
    click.echo("\n" + "=" * 60)
    click.echo("BACKTEST RESULTS")
    click.echo("=" * 60)
    click.echo(f"Period: {days} days")
    click.echo(f"Initial Capital: ${capital:,.2f}")
    click.echo(f"Final Capital: ${float(config.initial_capital) + float(result.net_profit):,.2f}")
    click.echo(f"Net Profit: ${float(result.net_profit):,.2f}")
    click.echo(f"ROI: {result.roi_percent:.2f}%")
    click.echo(f"Win Rate: {result.win_rate:.1f}%")
    click.echo(f"Max Drawdown: {result.max_drawdown:.2f}%")
    click.echo(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    click.echo(f"Total Trades: {len(result.trades)}")
    click.echo(f"Best Path: {result.best_path}")
    click.echo("=" * 60)
    
    # Export results
    backtester.export_results(output)
    click.echo(f"\nResults exported to {output}/")


@cli.command()
@click.option('--capital', '-c', default=1000, help='Initial capital')
@click.option('--days', '-d', default=14, help='Days to test')
def optimize(capital: float, days: int):
    """Run parameter optimization."""
    logger.info("Running parameter optimization...")
    
    best_params = run_parameter_optimization(
        initial_capital=Decimal(str(capital)),
        start_date=datetime.now() - timedelta(days=days),
        end_date=datetime.now()
    )
    
    click.echo("\n" + "=" * 60)
    click.echo("OPTIMAL PARAMETERS")
    click.echo("=" * 60)
    for key, value in best_params.items():
        click.echo(f"{key}: {value}")
    click.echo("=" * 60)


@cli.command()
def status():
    """Check API connection and account status."""
    load_dotenv()
    
    try:
        config = load_config()
        
        from src.api.coinbase_client import CoinbaseClient
        client = CoinbaseClient(config.coinbase_api_key, config.coinbase_api_secret)
        
        async def check_status():
            client.connect()
            
            # Get balances
            balances = await client.get_all_balances()
            
            click.echo("\n" + "=" * 40)
            click.echo("ACCOUNT STATUS")
            click.echo("=" * 40)
            click.echo("\nBalances:")
            for currency, balance in balances.items():
                click.echo(f"  {currency}: {balance}")
            
            # Get product count
            products = await client.get_all_products()
            click.echo(f"\nAvailable Trading Pairs: {len(products)}")
            click.echo("=" * 40)
        
        asyncio.run(check_status())
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        click.echo(f"❌ Connection failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--amount', '-a', default=250, help='Amount per path')
@click.option('--min-profit', '-p', default=0.5, help='Minimum profit threshold')
def scan(amount: float, min_profit: float):
    """Scan for profitable trading paths."""
    load_dotenv()
    
    try:
        config = load_config()
        
        from src.api.coinbase_client import CoinbaseClient
        from src.core.path_finder import PathFinder
        
        client = CoinbaseClient(config.coinbase_api_key, config.coinbase_api_secret)
        path_finder = PathFinder(
            client=client,
            fee_percent=config.coinbase_fee_percent,
            max_chain_length=config.max_chain_length,
            min_profit_threshold=min_profit
        )
        
        async def do_scan():
            client.connect()
            await path_finder.build_token_graph()
            await path_finder.update_prices()
            
            paths = path_finder.find_profitable_paths(
                start_token='USDC',
                start_amount=Decimal(str(amount)),
                max_paths=20
            )
            
            click.echo("\n" + "=" * 70)
            click.echo(f"PROFITABLE PATHS (min {min_profit}% profit)")
            click.echo("=" * 70)
            
            if not paths:
                click.echo("No profitable paths found at current prices.")
            else:
                for i, path in enumerate(paths, 1):
                    click.echo(f"\n{i}. {path}")
                    click.echo(f"   Chain Length: {path.chain_length}")
                    click.echo(f"   Expected: ${path.start_amount} -> ${path.end_amount:.4f}")
                    click.echo(f"   Profit: {path.profit_percent:.4f}%")
            
            click.echo("\n" + "=" * 70)
        
        asyncio.run(do_scan())
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
