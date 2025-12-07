#!/bin/bash
# =============================================================================
# Setup Script for minimally-pretrained-crypto-algo
# Creates private GitHub repository and pushes code
# =============================================================================

set -e

echo "🚀 Setting up minimally-pretrained-crypto-algo repository..."

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    git init
    echo "✅ Initialized git repository"
fi

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env from template - EDIT THIS FILE WITH YOUR CREDENTIALS"
fi

# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Minimally Pretrained Crypto Algorithm

Features:
- Multi-currency arbitrage paths (5-10 currencies)
- Dynamic allocation engine (\$100-\$300 based on probability)
- 4-8 concurrent non-overlapping trade groups
- \$1,000 max capital with risk management
- Comprehensive audit logging (blockchain-style)
- Excel reports with what worked/what failed analysis
- Real-time learning from trade results

Trading Philosophy:
Learn from real money trades to discover unique patterns
that heavily pretrained models miss due to overfitting."

# Create private repository
echo "📦 Creating private repository on GitHub..."
gh repo create tjhoags/minimally-pretrained-crypto-algo \
    --private \
    --source=. \
    --remote=origin \
    --push \
    --description "Institutional grade crypto arbitrage with minimal pretraining"

echo ""
echo "✅ Repository created successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env with your Coinbase API credentials"
echo "   2. Run: python main.py status (to verify connection)"
echo "   3. Run: python main.py scan (to find opportunities)"
echo "   4. Run: python main.py run --paper (paper trading first!)"
echo ""
echo "🔗 Repository: https://github.com/tjhoags/minimally-pretrained-crypto-algo"
