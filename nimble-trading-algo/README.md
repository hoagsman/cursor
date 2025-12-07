# Nimble Trading Algorithm

A cryptocurrency arbitrage trading system for Coinbase that executes quick-turn trades through multi-token conversion paths.

## Features

- **Multi-Token Arbitrage**: Discovers profitable paths through up to 7 tokens before converting back to USDC
- **Concurrent Trade Groups**: Executes 4-8 non-overlapping trade groups simultaneously
- **Fee-Aware Execution**: All profit calculations account for Coinbase trading fees
- **Paper Trading Mode**: Test strategies without risking real money
- **Backtesting Engine**: Pre-train and validate strategies on historical patterns
- **Excel Logging**: Comprehensive trade logs and analytics in Excel format
- **Risk Management**: Daily loss limits, stop-losses, and position sizing

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/tjhoags/nimble-trading-algo.git
cd nimble-trading-algo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your Coinbase API credentials
# Get API keys from: https://www.coinbase.com/settings/api
```

Required environment variables:
- `COINBASE_API_KEY` - Your Coinbase Advanced Trade API key
- `COINBASE_API_SECRET` - Your API secret

### 3. Run Backtesting (Pre-Training)

```bash
# Run 30-day backtest with $1,000 capital
python main.py backtest --days 30 --capital 1000

# Run parameter optimization
python main.py optimize --capital 1000 --days 14
```

### 4. Paper Trading

```bash
# Run in paper trading mode (default)
python main.py run --paper

# Run 10 rounds only
python main.py run --rounds 10
```

### 5. Live Trading (⚠️ CAUTION)

```bash
# ONLY after thorough testing!
python main.py run --live
```

## Trading Strategy

### Algorithm Qualities

1. **Quick Turns**: Targets fast in/out positions through token conversions
2. **Chain Arbitrage**: Finds profit opportunities in conversion chains (2-7 tokens)
3. **Non-Overlapping Groups**: Ensures concurrent trades don't compete for same tokens
4. **Fee Optimization**: Only executes paths with profit > fees + threshold

### Trade Flow

```
USDC → Token1 → Token2 → ... → TokenN → USDC
```

Example 4-token path:
```
$250 USDC → SOL → AVAX → ETH → $251.25 USDC (0.5% profit)
```

### Group Management

With $1,000 initial capital and 4 groups:
- Each group gets $250 allocation
- Groups execute simultaneously but with different tokens
- Profits from each group convert back to USDC

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `INITIAL_CAPITAL` | 1000 | Starting capital in USDC |
| `NUM_TRADE_GROUPS` | 4 | Concurrent trade groups (4-8) |
| `MAX_CHAIN_LENGTH` | 7 | Maximum tokens in path |
| `MIN_PROFIT_THRESHOLD` | 0.5 | Minimum profit % after fees |
| `COINBASE_FEE_PERCENT` | 0.60 | Coinbase trading fee |
| `MAX_DAILY_LOSS_PERCENT` | 5.0 | Stop trading if daily loss exceeds |

## Excel Logging

All trades are logged to `logs/trading_log.xlsx` with sheets:

- **Trade Log**: Individual trade details
- **Round Summary**: Results per trading round
- **Daily Summary**: Daily P&L with charts
- **Path Analysis**: Most profitable paths
- **Fee Analysis**: Fee breakdown by product
- **Performance**: Overall metrics

## CLI Commands

```bash
# Check account status and balances
python main.py status

# Scan for profitable paths without trading
python main.py scan --amount 250 --min-profit 0.5

# Run backtest
python main.py backtest --days 30 --capital 1000 --groups 4

# Run parameter optimization
python main.py optimize --capital 1000 --days 14

# Run trading (paper mode)
python main.py run --paper --rounds 10

# Run trading (live mode - USE CAUTION)
python main.py run --live
```

## Project Structure

```
nimble-trading-algo/
├── main.py                 # CLI entry point
├── config/
│   └── settings.py         # Configuration management
├── src/
│   ├── api/
│   │   └── coinbase_client.py  # Coinbase API integration
│   ├── core/
│   │   ├── path_finder.py      # Arbitrage path discovery
│   │   └── trade_executor.py   # Trade execution engine
│   ├── strategies/
│   │   └── nimble_strategy.py  # Main trading strategy
│   └── utils/
│       └── excel_logger.py     # Excel logging
├── backtesting/
│   └── backtester.py       # Backtesting engine
├── data/                   # Generated data files
├── logs/                   # Log files and Excel reports
└── tests/                  # Test files
```

## Risk Disclaimer

⚠️ **IMPORTANT**: Cryptocurrency trading involves substantial risk of loss. This software is provided as-is for educational purposes. Use at your own risk.

- Always start with paper trading
- Never trade more than you can afford to lose
- Past backtesting results do not guarantee future performance
- Fees and slippage can significantly impact real-world results

## Development

```bash
# Run tests
pytest tests/

# Type checking
mypy src/

# Format code
black src/ tests/
```

## License

Private repository - All rights reserved.

## Support

For questions or issues, contact the repository owner.
