#!/usr/bin/env python3
"""
Minimally Pretrained Crypto Algorithm
Main entry point for the trading system.
"""

import asyncio
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import click
from loguru import logger
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import load_config, AlgoConfig
from src.strategies.minimal_pretrain import MinimalPretrainStrategy

console = Console()


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging."""
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    # File logging
    logger.add(
        "logs/algo_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug: bool):
    """Minimally Pretrained Crypto Algorithm - Institutional Grade Trading"""
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level)


@cli.command()
@click.option('--rounds', '-r', type=int, help='Maximum rounds to execute')
@click.option('--hours', '-h', type=float, help='Maximum hours to run')
@click.option('--paper', is_flag=True, help='Force paper trading mode')
def run(rounds: int, hours: float, paper: bool):
    """Run the trading algorithm."""
    load_dotenv()
    
    try:
        config = load_config()
        
        if paper:
            config.trading_mode = 'paper'
        
        # Display startup info
        console.print(Panel.fit(
            f"[bold green]MINIMALLY PRETRAINED CRYPTO ALGORITHM[/bold green]\n\n"
            f"Mode: [yellow]{config.trading_mode.upper()}[/yellow]\n"
            f"Capital: [cyan]${config.max_account_usage}[/cyan]\n"
            f"Groups: [cyan]{config.num_trade_groups}[/cyan]\n"
            f"Chain Length: [cyan]{config.min_chain_length}-{config.max_chain_length}[/cyan]\n"
            f"Allocation: [cyan]${config.min_group_allocation}-${config.max_group_allocation}[/cyan]",
            title="Configuration"
        ))
        
        if config.trading_mode == 'live':
            console.print("[bold red]⚠️  LIVE TRADING MODE - REAL MONEY AT RISK[/bold red]")
            if not click.confirm('Continue with live trading?'):
                return
        
        strategy = MinimalPretrainStrategy(config)
        
        async def main():
            if not await strategy.initialize():
                console.print("[red]Failed to initialize strategy[/red]")
                return
            
            summary = await strategy.run(max_rounds=rounds, duration_hours=hours)
            
            # Display final results
            display_results(summary)
        
        asyncio.run(main())
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Fatal error")
        sys.exit(1)


@cli.command()
def status():
    """Check API connection and account status."""
    load_dotenv()
    
    try:
        config = load_config()
        
        from src.api.coinbase_client import CoinbaseClient
        client = CoinbaseClient(config.coinbase_api_key, config.coinbase_api_secret)
        
        async def check():
            if not client.connect():
                console.print("[red]❌ Failed to connect to Coinbase[/red]")
                return
            
            console.print("[green]✅ Connected to Coinbase[/green]")
            
            # Get balances
            balances = await client.get_all_balances()
            
            table = Table(title="Account Balances")
            table.add_column("Currency", style="cyan")
            table.add_column("Balance", style="green")
            
            for currency, balance in sorted(balances.items()):
                table.add_row(currency, f"{balance:.8f}")
            
            console.print(table)
            
            # Get products
            products = await client.get_all_products()
            console.print(f"\n[cyan]Tradeable Products:[/cyan] {len(products)}")
            
            # Health status
            health = client.health_status
            console.print(f"[cyan]Client Health:[/cyan] {health['success_rate']:.1f}% success rate")
        
        asyncio.run(check())
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--amount', '-a', default=200, help='Amount per path')
@click.option('--min-profit', '-p', default=0.3, help='Minimum profit threshold')
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
            min_chain_length=config.min_chain_length,
            max_chain_length=config.max_chain_length,
            min_profit_threshold=min_profit
        )
        
        async def do_scan():
            if not client.connect():
                console.print("[red]Failed to connect[/red]")
                return
            
            console.print(f"[cyan]Scanning for paths with >{min_profit}% profit...[/cyan]")
            
            await path_finder.initialize()
            await path_finder.update_prices()
            
            paths = path_finder.find_profitable_paths(
                start_currency='USDC',
                amount=Decimal(str(amount)),
                max_paths=20
            )
            
            if not paths:
                console.print("[yellow]No profitable paths found[/yellow]")
                return
            
            table = Table(title=f"Profitable Paths (${amount} each)")
            table.add_column("#", style="dim")
            table.add_column("Path", style="cyan")
            table.add_column("Length", style="white")
            table.add_column("Profit %", style="green")
            table.add_column("Expected", style="green")
            table.add_column("Probability", style="yellow")
            
            for i, path in enumerate(paths[:15], 1):
                table.add_row(
                    str(i),
                    path.currency_path_str,
                    str(path.chain_length),
                    f"{path.profit_percent:.3f}%",
                    f"${path.expected_output:.4f}",
                    f"{path.probability_score:.2f}"
                )
            
            console.print(table)
        
        asyncio.run(do_scan())
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def report():
    """Generate and display performance report."""
    load_dotenv()
    
    try:
        config = load_config()
        
        from src.audit.financial_tracker import FinancialTracker
        
        tracker = FinancialTracker(
            excel_path=config.excel_log_path,
            metrics_path=config.metrics_path
        )
        
        summary = tracker.get_performance_summary()
        
        if summary.get('total_trades', 0) == 0:
            console.print("[yellow]No trades recorded yet[/yellow]")
            return
        
        display_results(summary)
        
        # Show what worked/failed
        worked = tracker.analyze_what_worked()
        failed = tracker.analyze_what_failed()
        
        if worked:
            console.print("\n[bold green]✅ WHAT WORKED[/bold green]")
            for item in worked[:5]:
                console.print(f"  • {item['category']}: {item['description']}")
                console.print(f"    Impact: {item['impact']}")
        
        if failed:
            console.print("\n[bold red]❌ WHAT FAILED[/bold red]")
            for item in failed[:5]:
                console.print(f"  • {item['category']}: {item['description']}")
                console.print(f"    Loss: {item['loss_amount']}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def display_results(summary: dict) -> None:
    """Display trading results in a formatted table."""
    table = Table(title="Trading Performance")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    metrics = [
        ("Total Trades", str(summary.get('total_trades', 0))),
        ("Winning Trades", str(summary.get('winning_trades', 0))),
        ("Losing Trades", str(summary.get('losing_trades', 0))),
        ("Win Rate", f"{summary.get('win_rate', 0):.1f}%"),
        ("Total Profit", f"${summary.get('total_profit', 0):.2f}"),
        ("Total Fees", f"${summary.get('total_fees', 0):.2f}"),
        ("Net Profit", f"${summary.get('net_profit', 0):.2f}"),
        ("ROI", f"{summary.get('roi', 0):.2f}%"),
        ("Best Trade", f"${summary.get('best_trade', 0):.2f}"),
        ("Worst Trade", f"${summary.get('worst_trade', 0):.2f}"),
        ("Current Balance", f"${summary.get('current_balance', 0):.2f}"),
    ]
    
    for metric, value in metrics:
        table.add_row(metric, value)
    
    console.print(table)


if __name__ == '__main__':
    cli()
