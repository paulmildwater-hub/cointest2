"""
Volume-Boosted Configuration - Increase trade frequency while maintaining quality
"""

# Trading Parameters - Optimized for higher volume
BASE_POSITION_SIZE = 20  # Increased from $15 to $20 for better profit per trade
MAX_POSITION_SIZE = 40  # Increased from $25 to $40 for high conviction
TAKE_PROFIT_1 = 0.12   # Reduced from 15% to 12% for faster exits
TAKE_PROFIT_2 = 0.20   # Reduced from 25% to 20% for quicker full exits
STOP_LOSS = 0.08       # Keep tight at 8%
MAX_TRADE_DURATION = 600  # Reduced from 900s (15min) to 600s (10min) for faster turnover
SLIPPAGE = 0.005
TRANSACTION_FEE = 0.25
MAX_CONCURRENT_POSITIONS = 100  # Increased from 50 to 100
MIN_PRICE_INCREASE = 0.015  # Slightly reduced from 2% to 1.5%
STAGNANT_SELL_TIME = 90   # Reduced from 120s to 90s
NO_CHANGE_SELL_TIME = 30  # Reduced from 45s to 30s
MAX_DAILY_LOSS = -150     # Increased from -100 to -150 to allow more trades
MIN_TOKEN_SCORE = 50      # Reduced from 70 to 50 for more opportunities

# Market parameters - Expanded ranges for more opportunities
MIN_MARKET_CAP = 15000    # Reduced from 30k to 15k
MIN_LIQUIDITY = 15000     # Reduced from 25k to 15k  
MAX_MARKET_CAP = 2000000  # Increased from 1M to 2M

# Timing parameters - Faster scanning
SCAN_INTERVAL = 1         # Reduced from 2s to 1s for faster discovery
PRICE_UPDATE_INTERVAL = 1 # Update prices every second
CYCLE_DELAY = 0.2         # Faster cycles

# Turbo mode settings - Even more aggressive
TURBO_SETTINGS = {
    'MIN_TOKEN_SCORE': 35,           # Reduced from 50 to 35
    'MIN_PRICE_INCREASE': 0.01,      # Reduced from 0.015 to 0.01
    'MIN_MARKET_CAP': 10000,         # Reduced from 20k to 10k
    'MIN_LIQUIDITY': 10000,          # Reduced from 15k to 10k
    'MAX_CONCURRENT_POSITIONS': 150, # Increased from 75 to 150
    'SCAN_INTERVAL': 0.5,            # Scan every 500ms
    'NO_CHANGE_SELL_TIME': 20        # Exit faster at 20s
}

# Normal mode settings - More permissive than before
NORMAL_SETTINGS = {
    'MIN_TOKEN_SCORE': 50,           # Reduced from 70 to 50
    'MIN_PRICE_INCREASE': 0.015,     # Reduced from 0.02 to 0.015
    'MIN_MARKET_CAP': 15000,         # Reduced from 30k to 15k
    'MIN_LIQUIDITY': 15000,          # Reduced from 25k to 15k
    'MAX_CONCURRENT_POSITIONS': 100, # Increased from 50 to 100
    'SCAN_INTERVAL': 1,              # Faster from 2s
    'NO_CHANGE_SELL_TIME': 30        # Faster from 45s
}

# API Configuration
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
}

# EXPANDED Search queries for more token discovery
SEARCH_QUERIES = [
    # Original high-volume searches
    "SOL", "pump", "moon", "rocket", "new", "gem", "100x",
    # Meme categories
    "pepe", "bonk", "wif", "doge", "shib", "floki", "inu", "cat",
    "frog", "wojak", "chad", "based", "wagmi", "gm",
    # Trending/popular terms
    "ai", "trump", "elon", "bitcoin", "eth", "defi", "nft",
    "meta", "web3", "dao", "yield", "stake", "farm",
    # Additional discovery terms
    "alpha", "beta", "gamma", "token", "coin", "crypto",
    "trade", "swap", "dex", "pool", "pair", "launch"
]

# New: Multiple data sources for broader coverage
DATA_SOURCES = {
    'dexscreener': {
        'enabled': True,
        'weight': 0.6,  # 60% of tokens from DexScreener
        'queries': SEARCH_QUERIES[:20]
    },
    'birdeye': {
        'enabled': True,  # Enable Birdeye as secondary source
        'weight': 0.3,    # 30% from Birdeye
        'base_url': 'https://public-api.birdeye.so/public'
    },
    'jupiter': {
        'enabled': True,  # Enable Jupiter token list
        'weight': 0.1,    # 10% from Jupiter
        'base_url': 'https://token.jup.ag'
    }
}

# Quality filters - More permissive for higher volume
QUALITY_FILTERS = {
    'MIN_VOLUME_TO_MCAP_RATIO': 3.0,     # Reduced from 5.0 to 3.0
    'MIN_MOMENTUM_SCORE': 7.0,           # Reduced from 10.0 to 7.0
    'MAX_AGE_HOURS': 168,                # Increased from 48 to 168 (1 week)
    'MIN_HOLDER_COUNT': 50,              # Reduced from 100 to 50
    'MAX_TOP_HOLDER_PERCENT': 40,        # Increased from 30% to 40%
}

# Risk management settings - Adjusted for higher volume
RISK_SETTINGS = {
    'MAX_DAILY_TRADES': 100,             # Increased from 50 to 100
    'MAX_EQUITY_PER_TRADE': 0.08,        # Increased from 5% to 8%
    'STOP_TRADING_WIN_STREAK': False,    
    'STOP_TRADING_LOSS_STREAK': 8,       # Increased tolerance from 5 to 8
    'DAILY_PROFIT_TARGET': 40,           
    'TAKE_BREAK_AFTER_TARGET': False,    
}

# New: Additional blockchain networks for diversification
SUPPORTED_NETWORKS = {
    'solana': {
        'enabled': True,
        'dex_sources': ['raydium', 'orca', 'jupiter', 'pumpfun'],
        'min_liquidity': 10000
    },
    'ethereum': {
        'enabled': False,  # Can enable for ETH tokens
        'dex_sources': ['uniswap', 'sushiswap'],
        'min_liquidity': 50000  # Higher due to gas costs
    },
    'base': {
        'enabled': False,  # Can enable for Base network
        'dex_sources': ['uniswap'],
        'min_liquidity': 25000
    }
}

# Volume boost strategies
VOLUME_STRATEGIES = {
    'multi_timeframe_scanning': True,    # Scan multiple timeframes
    'cross_dex_arbitrage': False,        # Look for price differences
    'momentum_following': True,          # Follow momentum trends
    'mean_reversion': False,             # Counter-trend strategy
    'breakout_detection': True,          # Detect price breakouts
}

# Profit optimization
PROFIT_OPTIMIZATION = {
    'dynamic_position_sizing': True,     # Adjust size based on confidence
    'partial_profit_levels': [0.08, 0.12, 0.20],  # Multiple take profit levels
    'trailing_stop_activation': 0.15,   # Start trailing at 15%
    'trailing_stop_distance': 0.05,     # 5% trailing distance
    'quick_scalp_mode': True,           # Enable quick 3-5% scalps
    'scalp_exit_time': 120,             # Exit scalps after 2 minutes
}