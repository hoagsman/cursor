#!/bin/bash
# Setup script for creating the private GitHub repository
# Run this after configuring your GitHub CLI (gh auth login)

# Create private repository on GitHub
gh repo create tjhoags/nimble-trading-algo --private --source=. --remote=origin

# Push code to repository
git add .
git commit -m "Initial commit: Nimble Trading Algorithm

- Multi-token arbitrage path finder (2-7 token chains)
- Concurrent trade groups (4-8 non-overlapping)
- Coinbase Advanced Trade API integration
- Paper trading and live trading modes
- Backtesting engine for pre-training
- Excel logging with comprehensive analytics
- CLI interface for all operations"

git push -u origin main

echo ""
echo "Repository created at: https://github.com/tjhoags/nimble-trading-algo"
echo "Don't forget to add your .env file with Coinbase API credentials!"
