"""
Micro-Profit High-Frequency Configuration - Optimized for $50/hour on Solana
"""

# High-Frequency Micro-Profit Parameters
BASE_POSITION_SIZE = 12   # Reduced from 20 to 12 for higher frequency
MAX_POSITION_SIZE = 20    # Reduced from 40 to 20
TAKE_PROFIT_1 = 0.03      # 3% first target (was 8%)
TAKE_PROFIT_2 = 0.05      # 5% second target (was 20%)
STOP_LOSS = 0.025         # 2.5% stop loss (was 8%)
MAX_TRADE_DURATION = 180  # 3 minutes max (was 10 minutes)

# Accurate Solana Network Fees
SOLANA_BASE_FEE = 0.000005    # ~$0.0001
SOLANA_PRIORITY_FEE = 0.001   # ~$0.02 for fast execution
SOLANA_SWAP_FEE_RATE = 0.003  # 0.3% average DEX fee
SLIPPAGE = 0.002              # 0.2% slippage (tighter)
TRANSACTION_FEE = 0.05        # Total ~$0.05 per trade (much lower)

# High-Frequency Settings
MAX_CONCURRENT_POSITIONS = 200  # High volume
MIN_PRICE_INCREASE = 0.005      # 0.5% minimum (very low)
STAGNANT_SELL_TIME = 30         # 30 seconds
NO_CHANGE_SELL_TIME = 15        # 15 seconds
MAX_DAILY_LOSS = -100           # Tight daily control
MIN_TOKEN_SCORE = 25            # Very low threshold

# Expanded Market Parameters
MIN_MARKET_CAP = 5000          # Much lower
MIN_LIQUIDITY = 5000           # Much lower  
MAX_MARKET_CAP = 5000000       # Higher ceiling

# Ultra-Fast Timing
SCAN_INTERVAL = 0.5            # Scan every 500ms
PRICE_UPDATE_INTERVAL = 0.5    # Update every 500ms
CYCLE_DELAY = 0.1              # 100ms cycles
SEEN_TOKENS_RESET_TIME = 600   # Reset seen tokens every 10 minutes

# Turbo mode for maximum aggression
TURBO_SETTINGS = {
    'MIN_TOKEN_SCORE': 15,           # Extremely low
    'MIN_PRICE_INCREASE': 0.002,     # 0.2% minimum
    'MIN_MARKET_CAP': 2000,          # Very low
    'MIN_LIQUIDITY': 2000,           # Very low
    'MAX_CONCURRENT_POSITIONS': 300,
    'SCAN_INTERVAL': 0.3,            # 300ms
    'NO_CHANGE_SELL_TIME': 10,       # 10 seconds
    'TAKE_PROFIT_1': 0.02,           # 2% 
    'TAKE_PROFIT_2': 0.04,           # 4%
    'STOP_LOSS': 0.02                # 2%
}

# Normal mode - still aggressive
NORMAL_SETTINGS = {
    'MIN_TOKEN_SCORE': 25,
    'MIN_PRICE_INCREASE': 0.005,
    'MIN_MARKET_CAP': 5000,
    'MIN_LIQUIDITY': 5000,
    'MAX_CONCURRENT_POSITIONS': 200,
    'SCAN_INTERVAL': 0.5,
    'NO_CHANGE_SELL_TIME': 15,
    'TAKE_PROFIT_1': 0.03,
    'TAKE_PROFIT_2': 0.05,
    'STOP_LOSS': 0.025
}

# API Configuration
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

# Massively expanded search for maximum discovery
SEARCH_QUERIES = [
    # Core Solana
    "SOL", "pump", "bonk", "wif", "jupiter", "orca", "raydium",
    # Meme coins (high activity)
    "pepe", "doge", "shib", "wojak", "chad", "frog", "cat", "dog",
    "ape", "moon", "rocket", "gem", "100x", "1000x", "diamond",
    # New/trending
    "new", "fresh", "launch", "fair", "stealth", "based", "alpha",
    "beta", "gamma", "sigma", "chad", "wagmi", "gm", "ngmi",
    # Pump.fun ecosystem
    "pumpfun", "pump.fun", "bonding", "curve", "graduation",
    # DeFi/utility
    "defi", "yield", "farm", "stake", "swap", "dex", "nft", "dao",
    # Trending topics
    "ai", "trump", "elon", "meta", "tiktok", "x", "twitter",
    # Random discovery
    "a", "b", "c", "1", "2", "3", "test", "coin", "token",
    # Time-based
    "today", "2025", "jan", "winter", "monday", "week"
]

# Extremely permissive quality filters
QUALITY_FILTERS = {
    'MIN_VOLUME_TO_MCAP_RATIO': 1.0,    # Very low
    'MIN_MOMENTUM_SCORE': 0.0,          # Accept any momentum
    'MAX_AGE_HOURS': 720,               # 30 days
    'MIN_HOLDER_COUNT': 10,             # Very low
    'MAX_TOP_HOLDER_PERCENT': 60,       # Very permissive
}

# Aggressive risk settings
RISK_SETTINGS = {
    'MAX_DAILY_TRADES': 500,            # Very high
    'MAX_EQUITY_PER_TRADE': 0.15,       # 15% max
    'STOP_TRADING_WIN_STREAK': False,
    'STOP_TRADING_LOSS_STREAK': 15,     # High tolerance
    'DAILY_PROFIT_TARGET': 50,
    'TAKE_BREAK_AFTER_TARGET': False,
}

# Network optimized for Solana speed
NETWORK_PRIORITY = {
    'solana': 1,      # Highest priority
    'base': 2,        # Secondary
    'arbitrum': 3,    # Tertiary
    'polygon': 4,     # Quaternary
    'ethereum': 5     # Lowest (too expensive)
}

# Profit target calculation for $50/hour
# At $0.50 avg profit per trade, need 100 trades/hour
# At $0.30 avg profit per trade, need 167 trades/hour
# At $0.20 avg profit per trade, need 250 trades/hour
TARGET_TRADES_PER_HOUR = 150
TARGET_AVG_PROFIT = 0.33  # $0.33 per trade for $50/hour
