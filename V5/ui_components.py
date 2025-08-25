"""
User interface components module
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO
from collections import deque
from config import *

class UIComponents:
    def log_debug(self, message, msg_type="info"):
        """Add debug message to log"""
        timestamped = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        st.session_state.debug_info.append((timestamped, msg_type))
    
    def render_performance_metrics(self):
        """Render performance metrics row"""
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        
        with col1:
            status = "⚡ TURBO" if st.session_state.turbo_mode else "🟢 TRADING" if st.session_state.bot_running else "🔴 STOPPED"
            if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
                status = "⛔ LIMIT"
            st.metric("Status", status)
        
        with col2:
            st.metric("Equity", f"${st.session_state.equity:.2f}", 
                     f"${st.session_state.equity - 1000:.2f}")
        
        with col3:
            st.metric("Daily P&L", f"${st.session_state.daily_pnl:.2f}")
        
        with col4:
            max_pos = TURBO_SETTINGS['MAX_CONCURRENT_POSITIONS'] if st.session_state.turbo_mode else MAX_CONCURRENT_POSITIONS
            st.metric("Positions", f"{len(st.session_state.active_positions)}/{max_pos}")
        
        with col5:
            total_trades = len(st.session_state.trades)
            wins = len([t for t in st.session_state.trades if t['pnl'] > 0])
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col6:
            st.metric("Tokens Found", st.session_state.tokens_found)
        
        with col7:
            # Calculate trades per hour
            if st.session_state.trades:
                current_hour = datetime.now()
                hour_ago = (current_hour.timestamp() - 3600)
                recent_trades = [t for t in st.session_state.trades 
                               if t['timestamp'].timestamp() > hour_ago]
                st.session_state.trades_per_hour = len(recent_trades)
            st.metric("Trades/Hour", st.session_state.trades_per_hour)
        
        with col8:
            # Profit per hour estimate
            if st.session_state.trades_per_hour > 0 and st.session_state.trades:
                recent_trades = st.session_state.trades[-20:] if len(st.session_state.trades) > 20 else st.session_state.trades
                avg_pnl = sum(t['pnl'] for t in recent_trades) / len(recent_trades)
                projected_hourly = avg_pnl * st.session_state.trades_per_hour
                st.metric("$/Hour Est", f"${projected_hourly:.2f}")
            else:
                st.metric("$/Hour Est", "$0.00")
    
    def render_control_buttons(self, trading_engine):
        """Render control buttons"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🚀 START TRADING" if not st.session_state.bot_running else "⏸️ PAUSE", 
                        type="primary", use_container_width=True):
                st.session_state.bot_running = not st.session_state.bot_running
                if st.session_state.bot_running:
                    self.log_debug("🚀 Bot started - Trading across multiple DEXs", "success")
        
        with col2:
            if st.button("⚡ TURBO MODE" if not st.session_state.turbo_mode else "🔻 NORMAL", 
                        type="primary" if not st.session_state.turbo_mode else "secondary",
                        use_container_width=True):
                st.session_state.turbo_mode = not st.session_state.turbo_mode
                trading_engine.apply_turbo_mode(st.session_state.turbo_mode)
                
                if st.session_state.turbo_mode:
                    self.log_debug("⚡ TURBO MODE ACTIVATED - Maximum aggression!", "warning")
                else:
                    self.log_debug("🔻 Normal mode restored", "info")
        
        with col3:
            if st.button("🔄 RESET BOT", use_container_width=True):
                # Reset all state
                st.session_state.equity = 1000.0
                st.session_state.starting_equity = 1000.0
                st.session_state.trades = []
                st.session_state.active_positions = {}
                st.session_state.seen_tokens = set()
                st.session_state.debug_info = deque(maxlen=50)
                st.session_state.api_calls_count = 0
                st.session_state.tokens_bought = 0
                st.session_state.tokens_found = 0
                st.session_state.pnl_history = []
                st.session_state.time_history = []
                st.session_state.daily_pnl = 0
                st.session_state.win_streak = 0
                st.session_state.loss_streak = 0
                st.session_state.best_trade = 0
                st.session_state.worst_trade = 0
                st.session_state.trades_per_hour = 0
                self.log_debug("🔄 Bot reset - Ready to trade", "info")
        
        with col4:
            if st.button("📊 SCAN NOW", use_container_width=True):
                st.info("Scanning for tokens...")
        
        with col5:
            if st.button("🗑️ CLEAR SEEN", use_container_width=True):
                st.session_state.seen_tokens = set()
                st.success("Cleared seen tokens - will rebuy everything!")
    
    def render_strategy_info(self):
        """Render strategy information boxes"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.turbo_mode:
                st.warning("""
                **⚡ TURBO MODE ACTIVE:**
                - 300 concurrent positions
                - $5k min market cap
                - 0.5% min price increase
                - 10 point min score
                - 1 second scan interval
                - 30 second no-change exit
                """)
            else:
                st.info("""
                **🌐 MULTI-DEX COVERAGE:**
                - DexScreener scanning
                - 200 concurrent positions
                - Dynamic position sizing ($10-30)
                - Smart scoring system
                - 3 second scan interval
                """)
        
        with col2:
            st.success("""
            **📊 VOLUME TARGETS:**
            - Goal: $40 profit/hour
            - Need: ~20-30 trades/hour
            - Target: 60% win rate
            - Avg win: $3-5 per trade
            - Fast exits: 30min max hold
            """)
        
        with col3:
            if st.session_state.daily_pnl > 0:
                st.success(f"""
                **📈 LIVE PERFORMANCE:**
                - Trades Today: {len(st.session_state.trades)}
                - Active Now: {len(st.session_state.active_positions)}
                - Daily P&L: ${st.session_state.daily_pnl:.2f}
                - Equity: ${st.session_state.equity:.2f}
                - API Calls: {st.session_state.api_calls_count}
                """)
            else:
                st.error(f"""
                **📈 LIVE PERFORMANCE:**
                - Trades Today: {len(st.session_state.trades)}
                - Active Now: {len(st.session_state.active_positions)}
                - Daily P&L: ${st.session_state.daily_pnl:.2f}
                - Equity: ${st.session_state.equity:.2f}
                - API Calls: {st.session_state.api_calls_count}
                """)
    
    def render_active_positions(self):
        """Render active positions table"""
        st.subheader(f"📈 Active Positions ({len(st.session_state.active_positions)})")
        
        positions_data = []
        for mint, pos in st.session_state.active_positions.items():
            current_price = pos.get('current_price', pos['entry_price'])
            pnl_percent = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
            
            position_size = pos.get('position_size', BASE_POSITION_SIZE)
            if pos.get('partial_sold', False):
                position_size = position_size / 2
            
            exit_price = current_price * (1 - SLIPPAGE)
            gross_value = pos['tokens_bought'] * exit_price
            net_value = gross_value - TRANSACTION_FEE
            current_pnl = net_value - position_size
            
            # Progress indicators
            if pos.get('partial_sold', False):
                tp_progress = (pnl_percent / 30) * 100
            else:
                tp_progress = (pnl_percent / 15) * 100
            
            sl_progress = (abs(pnl_percent) / 10) * 100 if pnl_percent < 0 else 0
            
            display_address = f"{mint[:4]}...{mint[-4:]}" if len(mint) > 10 else mint
            
            # Status
            if pnl_percent >= 20:
                status = f"🔥 HOT ({pos.get('score', 0)})"
            elif pnl_percent >= 10:
                status = f"📈 Good ({pos.get('score', 0)})"
            elif pnl_percent >= 0:
                status = f"➡️ Hold ({pos.get('score', 0)})"
            else:
                status = f"📉 Down ({pos.get('score', 0)})"
            
            # Stagnant warning
            time_no_change = pos.get('time_no_change', 0)
            stagnant_warning = f"🔴 {int(time_no_change)}s" if time_no_change > 0 else ""
            
            positions_data.append({
                'Status': status,
                'Symbol': pos['token']['symbol'],
                'Size': f"${position_size:.0f}",
                'Entry': f"${pos['entry_price']:.6f}",
                'Current': f"${current_price:.6f}",
                'Change': f"{pnl_percent:+.1f}%",
                'P&L': f"${current_pnl:.2f}",
                'TP%': f"{tp_progress:.0f}%",
                'SL%': f"{sl_progress:.0f}%",
                'Partial': "✅" if pos.get('partial_sold', False) else "❌",
                'Stagnant': stagnant_warning,
                'Source': pos['token'].get('source', 'Unknown')
            })
        
        if positions_data:
            df_positions = pd.DataFrame(positions_data)
            st.dataframe(df_positions, use_container_width=True)
    
    def render_pnl_chart(self):
        """Render P&L performance chart"""
        st.subheader("📊 Performance Analytics")
        
        chart_data = pd.DataFrame({
            'Time': st.session_state.time_history,
            'Total P&L': st.session_state.pnl_history
        })
        
        chart_data['Equity'] = 1000 + chart_data['Total P&L']
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            current_pnl = st.session_state.pnl_history[-1] if st.session_state.pnl_history else 0
            max_pnl = max(st.session_state.pnl_history) if st.session_state.pnl_history else 0
            min_pnl = min(st.session_state.pnl_history) if st.session_state.pnl_history else 0
            
            st.metric("Current P&L", f"${current_pnl:.2f}")
            st.metric("Max P&L", f"${max_pnl:.2f}")
            st.metric("Min P&L", f"${min_pnl:.2f}")
            st.metric("Best Trade", f"${st.session_state.best_trade:.2f}")
            st.metric("Worst Trade", f"${st.session_state.worst_trade:.2f}")
            
            if st.session_state.win_streak > 0:
                st.metric("Win Streak", f"🔥 {st.session_state.win_streak}")
            else:
                st.metric("Loss Streak", f"❄️ {st.session_state.loss_streak}")
        
        with col2:
            st.line_chart(chart_data.set_index('Time')['Total P&L'], use_container_width=True, height=400)
    
    def render_live_activity(self):
        """Render live trading activity"""
        st.subheader("Live Trading Activity")
        if st.session_state.debug_info:
            for msg, msg_type in list(st.session_state.debug_info)[-20:]:
                if msg_type == "success":
                    st.success(msg)
                elif msg_type == "error":
                    st.error(msg)
                elif msg_type == "warning":
                    st.warning(msg)
                else:
                    st.info(msg)
        else:
            st.info("Click START TRADING to begin multi-DEX trading...")
    
    def render_trade_history(self):
        """Render trade history table"""
        if st.session_state.trades:
            st.subheader("Trade History")
            
            trades_data = []
            for trade in st.session_state.trades[-30:]:
                display_address = f"{trade['mint_address'][:4]}...{trade['mint_address'][-4:]}" if len(trade.get('mint_address', '')) > 10 else 'N/A'
                
                trades_data.append({
                    'Time': trade['timestamp'].strftime('%H:%M:%S'),
                    'Symbol': trade['symbol'],
                    'Score': trade.get('score', 0),
                    'Size': f"${trade.get('position_size', BASE_POSITION_SIZE):.0f}",
                    'Entry': f"${trade['entry_price']:.6f}",
                    'Exit': f"${trade['exit_price']:.6f}",
                    'Change': f"{trade['percent_change']:+.1f}%",
                    'P&L': f"${trade['pnl']:.2f}",
                    'Reason': trade['exit_reason'],
                    'Duration': f"{int(trade.get('duration_seconds', 0))}s",
                    'Source': trade.get('source', 'Unknown')
                })
            
            df_trades = pd.DataFrame(trades_data)
            st.dataframe(df_trades, use_container_width=True)
    
    def render_statistics(self):
        """Render trading statistics"""
        if not st.session_state.trades:
            st.info("No trades yet")
            return
        
        # Import Analytics here to avoid circular import
        from analytics import Analytics
        analytics = Analytics()
        metrics = analytics.get_performance_metrics()
        
        if metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Trades", metrics['total_trades'])
                st.metric("Winning Trades", metrics['winning_trades'])
                st.metric("Losing Trades", metrics['losing_trades'])
            
            with col2:
                st.metric("Average Win", f"${metrics['avg_win']:.2f}")
                st.metric("Average Loss", f"${metrics['avg_loss']:.2f}")
                st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
            
            with col3:
                st.metric("Total P&L", f"${metrics['total_pnl']:.2f}")
                st.metric("Average P&L", f"${metrics['avg_pnl']:.2f}")
                st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
    
    def render_analysis_export(self, analytics):
        """Render analysis and export section"""
        st.subheader("🔬 Advanced Analysis & Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Export Trade Data")
            if st.session_state.trades:
                df = analytics.export_trades_to_csv()
                
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Full Trade Data (CSV)",
                    data=csv_data,
                    file_name=f"trading_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.info(f"Dataset: {len(df)} trades with {len(df.columns)} data points")
            else:
                st.warning("No trades to export yet")
        
        with col2:
            st.markdown("### 📊 Generate Analysis Report")
            if st.button("🔍 Analyze Trading Patterns", use_container_width=True):
                if len(st.session_state.trades) >= 10:
                    analysis = analytics.generate_analysis_report()
                    
                    st.download_button(
                        label="📥 Download Analysis Report",
                        data=analysis,
                        file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    with st.expander("View Analysis", expanded=True):
                        st.text(analysis)
                else:
                    st.warning("Need at least 10 trades for analysis")
    
    def render_performance_summary(self):
        """Render performance summary"""
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        total_pnl = sum(t['pnl'] for t in st.session_state.trades)
        avg_pnl = total_pnl / len(st.session_state.trades) if st.session_state.trades else 0
        
        winning_trades = [t for t in st.session_state.trades if t['pnl'] > 0]
        losing_trades = [t for t in st.session_state.trades if t['pnl'] < 0]
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        tp_exits = len([t for t in st.session_state.trades if 'TAKE_PROFIT' in t['exit_reason']])
        sl_exits = len([t for t in st.session_state.trades if 'STOP_LOSS' in t['exit_reason']])
        partial_exits = len([t for t in st.session_state.trades if t.get('partial_sold', False)])
        
        with col1:
            st.metric("Total P&L", f"${total_pnl:.2f}")
        with col2:
            st.metric("Avg Trade", f"${avg_pnl:.2f}")
        with col3:
            st.metric("Avg Win", f"${avg_win:.2f}")
        with col4:
            st.metric("Avg Loss", f"${avg_loss:.2f}")
        with col5:
            st.metric("TP/SL", f"{tp_exits}/{sl_exits}")
        with col6:
            st.metric("Partials", partial_exits)
    
    def render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.caption("🌐 **MULTI-DEX**: Trading across multiple DEXs for maximum opportunities")
        st.caption("💡 **SMART SIZING**: $10-30 positions based on token score")
        st.caption("📊 **PARTIAL PROFITS**: Takes 50% at 15%, lets rest run to 30%")
        st.caption("🛡️ **RISK MANAGEMENT**: 10% stop loss, trailing stops, $200 daily loss limit")
        st.caption("⚡ **TURBO MODE**: 300+ positions, 0.5% min increase, 1-second scanning")
        st.caption("📈 **TARGET**: $40/hour profit with 20-30 trades/hour at 60% win rate")
        st.caption("🔬 **DATA ANALYSIS**: Export comprehensive trade data for optimization")