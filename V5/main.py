"""
Micro-Profit High-Frequency Trading Bot - Main Application
Updated for $50/hour target with fixed P&L calculations
"""

import streamlit as st
import time
from datetime import datetime
from collections import deque

# Import updated bot modules
from config import *
from data_fetcher import DataFetcher
from trading_engine import TradingEngine
from analytics import Analytics
from ui_components import UIComponents

# Page configuration
st.set_page_config(
    page_title="Micro-Profit Trading Bot - $50/Hour Target",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with micro-profit defaults
def init_session_state():
    """Initialize all session state variables for micro-profit trading"""
    defaults = {
        'equity': 1000.0,
        'starting_equity': 1000.0,
        'trades': [],
        'active_positions': {},
        'seen_tokens': set(),
        'bot_running': False,
        'turbo_mode': False,
        'debug_info': deque(maxlen=100),
        'last_update': time.time(),
        'api_calls_count': 0,
        'tokens_bought': 0,
        'tokens_found': 0,
        'last_token_check': time.time(),
        'pnl_history': [0],
        'time_history': [datetime.now()],
        'last_price_update': time.time(),
        'daily_pnl': 0,
        'win_streak': 0,
        'loss_streak': 0,
        'best_trade': 0,
        'worst_trade': 0,
        'trades_per_hour': 0,
        'last_hour_check': datetime.now(),
        'micro_profit_target': 50,  # $50/hour target
        'session_start_time': datetime.now()
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize components
init_session_state()
data_fetcher = DataFetcher()
trading_engine = TradingEngine()
analytics = Analytics()
ui = UIComponents()

# Main UI
st.title("Micro-Profit High-Frequency Trading Bot")
st.markdown("**Target: $50/hour | Strategy: 150+ trades/hour at $0.33 avg profit | Fixed P&L Calculations**")

# Micro-profit target progress bar
if st.session_state.trades:
    session_duration = (datetime.now() - st.session_state.session_start_time).total_seconds() / 3600
    current_rate = st.session_state.daily_pnl / session_duration if session_duration > 0 else 0
    progress = min(current_rate / 50, 1.0) if current_rate > 0 else 0
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.progress(progress)
        st.caption(f"Progress to $50/hour: {progress*100:.1f}% (Currently: ${current_rate:.2f}/hr)")
    with col2:
        st.metric("Session Duration", f"{session_duration:.1f}h")
    with col3:
        st.metric("Target Gap", f"${50-current_rate:.2f}/hr")

# Performance metrics
ui.render_performance_metrics()

# Control buttons
ui.render_control_buttons(trading_engine)

# Strategy info boxes
ui.render_strategy_info()

# Micro-profit system status
with st.sidebar:
    st.header("Micro-Profit System Status")
    
    # System parameters
    st.subheader("Current Settings")
    if st.session_state.turbo_mode:
        st.info(f"""
        **TURBO MICRO MODE:**
        - Position Size: ${BASE_POSITION_SIZE * 1.3:.0f} max
        - Profit Targets: {TURBO_SETTINGS['TAKE_PROFIT_1']*100:.0f}%, {TURBO_SETTINGS['TAKE_PROFIT_2']*100:.0f}%
        - Stop Loss: {TURBO_SETTINGS['STOP_LOSS']*100:.1f}%
        - Scan Interval: {TURBO_SETTINGS['SCAN_INTERVAL']*1000:.0f}ms
        - Score Threshold: {TURBO_SETTINGS['MIN_TOKEN_SCORE']}
        """)
    else:
        st.info(f"""
        **NORMAL MICRO MODE:**
        - Position Size: ${BASE_POSITION_SIZE}-{MAX_POSITION_SIZE}
        - Profit Targets: {TAKE_PROFIT_1*100:.0f}%, {TAKE_PROFIT_2*100:.0f}%
        - Stop Loss: {STOP_LOSS*100:.1f}%
        - Scan Interval: {SCAN_INTERVAL*1000:.0f}ms
        - Score Threshold: {MIN_TOKEN_SCORE}
        """)
    
    # Real-time frequency tracking
    st.subheader("Frequency Tracking")
    trades_last_hour = st.session_state.trades_per_hour
    target_trades = TARGET_TRADES_PER_HOUR
    frequency_progress = min(trades_last_hour / target_trades, 1.0)
    
    st.progress(frequency_progress)
    st.caption(f"Trade Frequency: {trades_last_hour}/{target_trades} trades/hour")
    
    # P&L accuracy verification
    if st.session_state.trades:
        recent_trades = st.session_state.trades[-5:]
        profitable_moves = len([t for t in recent_trades if t.get('percent_change', 0) > 0])
        profitable_pnl = len([t for t in recent_trades if t.get('pnl', 0) > 0])
        
        st.subheader("P&L Calculation Health")
        if profitable_moves == profitable_pnl:
            st.success(f"P&L Accurate: {profitable_pnl}/{profitable_moves} matches")
        else:
            st.error(f"P&L Error: {profitable_pnl}/{profitable_moves} profitable")
    
    # Network status
    st.subheader("Network Status")
    st.metric("API Calls", st.session_state.api_calls_count)
    st.metric("Tokens Found", st.session_state.tokens_found)
    
    # Seen tokens management
    seen_count = len(st.session_state.seen_tokens)
    st.metric("Seen Tokens", seen_count)
    if seen_count > 500:
        st.warning("High seen token count - resets every 10min")

# Active positions
if st.session_state.active_positions:
    ui.render_active_positions()

# P&L Chart
if len(st.session_state.pnl_history) > 1:
    ui.render_pnl_chart()

# Trading tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Live Activity", 
    "Trade History", 
    "Statistics", 
    "Analysis & Export"
])

with tab1:
    ui.render_live_activity()

with tab2:
    ui.render_trade_history()

with tab3:
    ui.render_statistics()

with tab4:
    ui.render_analysis_export(analytics)

# Micro-profit performance summary
if st.session_state.trades:
    st.subheader("Micro-Profit Performance Summary")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_pnl = sum(t['pnl'] for t in st.session_state.trades)
    avg_pnl = total_pnl / len(st.session_state.trades) if st.session_state.trades else 0
    
    winning_trades = [t for t in st.session_state.trades if t['pnl'] > 0]
    losing_trades = [t for t in st.session_state.trades if t['pnl'] < 0]
    
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    # Micro-profit specific metrics
    micro_profits = [t for t in st.session_state.trades if 0 < t['pnl'] < 1]
    quick_trades = [t for t in st.session_state.trades if t.get('duration_seconds', 0) < 180]
    
    with col1:
        st.metric("Total P&L", f"${total_pnl:.2f}")
    with col2:
        st.metric("Avg Trade", f"${avg_pnl:.3f}")
    with col3:
        st.metric("Micro-Profits", len(micro_profits))
    with col4:
        st.metric("Quick Trades (<3min)", len(quick_trades))
    with col5:
        st.metric("Avg Win", f"${avg_win:.3f}")
    with col6:
        st.metric("Avg Loss", f"${avg_loss:.3f}")

# Main trading loop with micro-profit optimizations
def run_micro_profit_bot():
    """Enhanced bot execution loop for micro-profit system"""
    if st.session_state.bot_running:
        # Run trading cycle with error handling
        try:
            trading_engine.run_trading_cycle(data_fetcher)
        except Exception as e:
            ui.log_debug(f"Error in micro-profit cycle: {str(e)[:100]}", "error")
            time.sleep(1)
        
        # Ultra-fast refresh for micro-profit system
        time.sleep(CYCLE_DELAY)
        st.rerun()
    else:
        # Slower refresh when not trading
        time.sleep(2)

# Execute micro-profit bot
run_micro_profit_bot()

# Enhanced footer
st.markdown("---")
st.markdown("### MICRO-PROFIT TRADING SYSTEM - OPTIMIZED FOR $50/HOUR")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**SYSTEM IMPROVEMENTS:**")
    st.caption("- Fixed P&L calculations (profit trades now show as profits)")
    st.caption("- Micro-profit targets: 3% and 5% with 2.5% stop loss")
    st.caption("- Ultra-fast cycles: 100ms with 500ms scanning")
    st.caption("- Seen token reset every 10 minutes for re-trading")

with col2:
    st.markdown("**SOLANA OPTIMIZED:**")
    st.caption("- Transaction fees: ~$0.05 per trade (vs $0.25)")
    st.caption("- Position sizes: $12-20 for high frequency")
    st.caption("- Slippage: 0.2% (tighter than 0.5%)")
    st.caption("- Max hold time: 3 minutes for quick turnover")

with col3:
    st.markdown("**TARGET METRICS:**")
    st.caption("- 150 trades/hour target frequency")
    st.caption("- $0.33 average profit per trade")
    st.caption("- Score threshold: 25 (vs 50 previously)")
    st.caption("- Market cap range: $5k-$5M (expanded)")

# Performance warning if needed
if st.session_state.trades and len(st.session_state.trades) >= 10:
    recent_trades = st.session_state.trades[-10:]
    positive_changes = len([t for t in recent_trades if t.get('percent_change', 0) > 0])
    positive_pnl = len([t for t in recent_trades if t.get('pnl', 0) > 0])
    
    if positive_changes > positive_pnl + 2:  # Allow some tolerance
        st.error(f"P&L CALCULATION WARNING: {positive_changes} positive price moves but only {positive_pnl} profitable P&L results. Check calculation accuracy.")
