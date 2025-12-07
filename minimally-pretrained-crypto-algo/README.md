# Minimally Pretrained Crypto Algorithm

An institutional-grade cryptocurrency arbitrage trading system that learns from real money trades to discover unique patterns that heavily pretrained models miss.

## Philosophy

> "Learn from the market, not from history."

This algorithm uses minimal pretraining to discover trading opportunities through actual execution. While heavily pretrained models often overfit to historical patterns, this system adapts in real-time based on what actually works.

## Features

### Trading Engine
- **Multi-Currency Paths**: 5-10 currency conversion chains
- **Dynamic Allocation**: $100-$300 per group based on probability
- **4-8 Concurrent Groups**: Non-overlapping trades for maximum efficiency
- **$1,000 Max Capital**: Hard cap for risk management

### Audit & Logging
- **Blockchain-style Audit Trail**: Tamper-proof hash chain
- **Comprehensive Excel Reports**: Every trade logged with full details
- **What Worked/What Failed Analysis**: Automatic pattern detection
- **Financial Tracking**: Real-time P&L, fees, and ROI

### Risk Management
- **Circuit Breakers**: Automatic halt on consecutive failures
- **Daily Loss Limits**: Stop trading if losses exceed threshold
- **Probability Scoring**: Allocate more to higher confidence trades

## Quick Start

### 1. Installation

```bash
git clone https://github.com/tjhoags/minimally-pretrained-crypto-algo.git
cd minimally-pretrained-crypto-algo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your Coinbase credentials
nano .env
```

**Required Settings:**
```env
COINBASE_API_KEY=your_api_key
COINBASE_API_SECRET=your_api_secret
TRADING_MODE=live  # or 'paper' for testing
```

### 3. Check Connection

```bash
python main.py status
```

### 4. Scan for Opportunities

```bash
python main.py scan --amount 200 --min-profit 0.3
```

### 5. Run Trading

```bash
# Paper trading (no real money)
python main.py run --paper --rounds 10

# Live trading
python main.py run --rounds 50 --hours 4
```

## Trading Logic

### Path Discovery
```
USDC → BTC → ETH → SOL → AVAX → MATIC → DOT → USDC
```
The algorithm finds circular paths through 5-10 currencies where the final USDC amount exceeds the starting amount after fees.

### Group Allocation

| Probability | Allocation | Confidence |
|-------------|------------|------------|
| ≥85% | $300 | High |
| 50-85% | $100-$300 (scaled) | Medium |
| ≤50% | $100 | Low |

### Concurrent Execution
- 4-8 groups execute simultaneously
- No shared currencies between groups
- Each group follows its own path

## Logging & Analysis

### Excel Report (`logs/trading_log.xlsx`)
- **Trade Log**: Every individual trade
- **Daily Summary**: Daily P&L and metrics
- **Path Performance**: Success rates by path
- **What Worked**: Successful patterns
- **What Failed**: Failure analysis
- **Fee Analysis**: Fee breakdown

### Audit Trail (`logs/audit/`)
- Tamper-proof JSON logs
- Every action recorded
- Integrity verification

### Metrics (`logs/metrics/`)
- JSON performance exports
- Machine-readable analysis

## CLI Commands

```bash
# Run trading
python main.py run [--rounds N] [--hours H] [--paper]

# Check status
python main.py status

# Scan for paths
python main.py scan [--amount A] [--min-profit P]

# View report
python main.py report

# Debug mode
python main.py --debug run
```

## Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_ACCOUNT_USAGE` | 1000 | Maximum capital to use |
| `NUM_TRADE_GROUPS` | 5 | Concurrent trade groups |
| `MIN_GROUP_ALLOCATION` | 100 | Minimum per group |
| `MAX_GROUP_ALLOCATION` | 300 | Maximum per group |
| `MIN_CHAIN_LENGTH` | 5 | Minimum currencies in path |
| `MAX_CHAIN_LENGTH` | 10 | Maximum currencies in path |
| `MIN_PROFIT_THRESHOLD` | 0.3 | Minimum profit % after fees |
| `MAX_DAILY_LOSS_PERCENT` | 5.0 | Daily loss limit |
| `CIRCUIT_BREAKER_THRESHOLD` | 5 | Failures before pause |

## Architecture

```
minimally-pretrained-crypto-algo/
├── main.py                      # CLI entry point
├── config/
│   └── settings.py              # Configuration management
├── src/
│   ├── api/
│   │   └── coinbase_client.py   # Coinbase API integration
│   ├── core/
│   │   ├── path_finder.py       # Path discovery (5-10 currencies)
│   │   ├── allocation_engine.py # Dynamic allocation ($100-$300)
│   │   └── trade_executor.py    # Execution engine
│   ├── strategies/
│   │   └── minimal_pretrain.py  # Main trading strategy
│   └── audit/
│       ├── audit_logger.py      # Tamper-proof logging
│       └── financial_tracker.py # P&L and Excel reports
├── logs/                        # Trade logs and audit trail
└── data/                        # Generated data
```

## Learning System

The algorithm learns from every trade:

1. **Path Success Tracking**: Records win/loss for each path
2. **Probability Updates**: Adjusts confidence based on actual results
3. **Allocation Optimization**: Higher allocation to proven paths
4. **Pattern Detection**: Identifies what works and what doesn't

## Risk Disclaimer

⚠️ **IMPORTANT**: Cryptocurrency trading involves substantial risk.

- This software trades with REAL MONEY in live mode
- Past performance does not guarantee future results
- Never trade more than you can afford to lose
- Use paper trading mode extensively before going live
- The algorithm can and will lose money

## Creating Private GitHub Repository

```bash
# Authenticate with GitHub
gh auth login

# Create private repository
gh repo create tjhoags/minimally-pretrained-crypto-algo --private --source=. --push

# Or manually:
git init
git add .
git commit -m "Initial commit: Minimally Pretrained Crypto Algorithm"
git remote add origin https://github.com/tjhoags/minimally-pretrained-crypto-algo.git
git push -u origin main
```

## Support

For questions or issues, contact the repository owner.

---

**Built for institutional-grade execution with real-time learning.**
