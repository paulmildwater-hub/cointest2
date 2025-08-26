"""
Updated User interface components for micro-profit high-frequency system
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
        """Render performance metrics for micro-profit trading"""
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        
        with col1:
            if st.session_state.turbo_mode:
                status = "TURBO MICRO"
            elif st.session_state.bot_running:
                status = "MICRO TRADING"
            else:
                status = "STOPPED"
                
            if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
                status = "LIMIT HIT"
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
            # Calculate trades per hour for micro-profit tracking
            if st.session_state.trades:
                current_hour = datetime.now()
                hour_ago = (current_hour.timestamp() - 3600)
                recent_trades = [t for t in st.session_state.trades 
                               if t['timestamp'].timestamp() > hour_ago]
                st.session_state.trades_per_hour = len(recent_trades)
            st.metric("Trades/Hour", st.session_state.trades_per_hour)
        
        with col8:
            # Micro-profit hourly rate estimate
            if st.session_state.trades_per_hour > 0 and st.session_state.trades:
                recent_trades = st.session_state.trades[-50:] if len(st.session_state.trades) > 50 else st.session_state.trades
                avg_pnl = sum(t['pnl'] for t in recent_trades) / len(recent_trades)
                projected_hourly = avg_pnl * st.session_state.trades_per_hour
                
                # Color code based on $50 target
                if projected_hourly >= 45:
                    st.success(f"${projected_hourly:.2f}/hr")
                elif projected_hourly >= 25:
                    st.warning(f"${projected_hourly:.2f}/hr")
                else:
                    st.error(f"${projected_hourly:.2f}/hr")
            else:
                st.metric("$/Hour Est", "$0.00")
    
    def render_control_buttons(self, trading_engine):
        """Updated control buttons for micro-profit system"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("START MICRO TRADING" if not st.session_state.bot_running else "PAUSE", 
                        type="primary", use_container_width=True):
                st.session_state.bot_running = not st.session_state.bot_running
                if st.session_state.bot_running:
                    self.log_debug("Micro-profit system started - targeting $50/hour", "success")
        
        with col2:
            if st.button("TURBO MICRO" if not st.session_state.turbo_mode else "NORMAL MICRO", 
                        type="primary" if not st.session_state.turbo_mode else "secondary",
                        use_container_width=True):
                st.session_state.turbo_mode = not st.session_state.turbo_mode
                trading_engine.apply_turbo_mode(st.session_state.turbo_mode)
                
                if st.session_state.turbo_mode:
                    self.log_debug("TURBO MICRO: 300 positions, 2% targets, 300ms scans", "warning")
                else:
                    self.log_debug("NORMAL MICRO: 200 positions, 3% targets, 500ms scans", "info")
        
        with col3:
            if st.button("RESET BOT", use_container_width=True):
                # Reset for micro-profit system
                st.session_state.equity = 1000.0
                st.session_state.starting_equity = 1000.0
                st.session_state.trades = []
                st.session_state.active_positions = {}
                st.session_state.seen_tokens = set()
                st.session_state.debug_info = deque(maxlen=100)
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
                self.log_debug("Reset for micro-profit trading", "info")
        
        with col4:
            if st.button("SPEED SCAN", use_container_width=True):
                st.info("High-frequency scanning active...")
        
        with col5:
            if st.button("CLEAR SEEN", use_container_width=True):
                st.session_state.seen_tokens = set()
                st.success("Cleared seen tokens - micro-opportunities available!")
    
    def render_strategy_info(self):
        """Updated strategy information for micro-profit system"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.turbo_mode:
                st.warning("""
                **TURBO MICRO-PROFIT MODE:**
                - 300 concurrent micro-positions
                - 2% and 4% profit targets
                - 2% stop loss, 3min max hold
                - Score threshold: 15 (ultra-low)
                - 300ms scan interval
                - $2k min market cap
                - Reset tokens every 10min
                """)
            else:
                st.info("""
                **MICRO-PROFIT MODE:**
                - 200 concurrent positions
                - 3% and 5% profit targets  
                - 2.5% stop loss, 3min max hold
                - Score threshold: 25 (very low)
                - 500ms scan interval
                - $5k min market cap
                - High-frequency re-trading
                """)
        
        with col2:
            # Calculate current performance vs $50/hour target
            trades_per_hour = st.session_state.trades_per_hour
            target_trades = TARGET_TRADES_PER_HOUR
            target_profit = TARGET_AVG_PROFIT
            
            if trades_per_hour >= target_trades * 0.8:
                st.success(f"""
                **TARGET: $50/HOUR**
                - Need: {target_trades} trades/hour
                - Current: {trades_per_hour} trades/hour
                - Target profit: ${target_profit:.2f}/trade
                - Status: ON TRACK
                - Small positions, fast exits
                """)
            else:
                st.warning(f"""
                **TARGET: $50/HOUR**
                - Need: {target_trades} trades/hour
                - Current: {trades_per_hour} trades/hour
                - Target profit: ${target_profit:.2f}/trade
                - Status: RAMPING UP
                - Frequency increasing...
                """)
        
        with col3:
            # Real-time micro-profit metrics
            if st.session_state.trades:
                recent_trades = st.session_state.trades[-20:] if len(st.session_state.trades) > 20 else st.session_state.trades
                avg_duration = sum(t.get('duration_minutes', 0) for t in recent_trades) / len(recent_trades)
                quick_exits = len([t for t in recent_trades if t.get('duration_minutes', 0) < 5])
                micro_profits = len([t for t in recent_trades if 0 < t.get('pnl', 0) < 1])
                
                st.success(f"""
                **MICRO-PROFIT METRICS:**
                - Trades: {len(recent_trades)}
                - Avg duration: {avg_duration:.1f}min
                - Quick exits (<5min): {quick_exits}
                - Micro-profits ($0-1): {micro_profits}
                - Daily P&L: ${st.session_state.daily_pnl:.2f}
                """)
            else:
                st.info("""
                **MICRO-PROFIT SYSTEM:**
                - Position size: $12-20
                - Profit targets: 3%, 5%
                - Stop loss: 2.5%
                - Max hold: 3 minutes
                - Solana fees: ~$0.05/trade
                """)
    
    def render_active_positions(self):
        """Updated active positions for micro-profit display"""
        st.subheader(f"Micro-Positions ({len(st.session_state.active_positions)})")
        
        positions_data = []
        for mint, pos in st.session_state.active_positions.items():
            current_price = pos.get('current_price', pos.get('base_price', 0))
            base_price = pos.get('base_price', pos.get('entry_price', 0))
            
            if base_price > 0:
                pnl_percent = ((current_price - base_price) / base_price) * 100
            else:
                pnl_percent = 0
            
            position_size = pos.get('position_size', BASE_POSITION_SIZE)
            if pos.get('partial_sold', False):
                position_size = position_size * 0.5
            
            # Calculate micro-profit P&L
            tokens_owned = pos.get('tokens_bought', 0)
            if pos.get('partial_sold', False):
                tokens_owned = tokens_owned * 0.5
            
            if tokens_owned > 0:
                exit_price = current_price * (1 - SLIPPAGE)
                gross_proceeds = tokens_owned * exit_price
                net_proceeds = gross_proceeds - TRANSACTION_FEE
                current_pnl = net_proceeds - position_size
            else:
                current_pnl = 0
            
            # Progress to micro-profit targets
            target_1 = TURBO_SETTINGS['TAKE_PROFIT_1'] if st.session_state.turbo_mode else TAKE_PROFIT_1
            target_2 = TURBO_SETTINGS['TAKE_PROFIT_2'] if st.session_state.turbo_mode else TAKE_PROFIT_2
            
            tp1_progress = (pnl_percent / (target_1 * 100)) * 100
            tp2_progress = (pnl_percent / (target_2 * 100)) * 100
            
            display_address = f"{mint[:4]}...{mint[-4:]}" if len(mint) > 10 else mint
            
            # Status with micro-profit context
            if pnl_percent >= (target_2 * 100):
                status = f"EXIT {pos.get('score', 0)}"
            elif pnl_percent >= (target_1 * 100):
                status = f"PROFIT {pos.get('score', 0)}"
            elif pnl_percent >= 1:
                status = f"MICRO {pos.get('score', 0)}"
            elif pnl_percent >= 0:
                status = f"HOLD {pos.get('score', 0)}"
            else:
                status = f"LOSS {pos.get('score', 0)}"
            
            # Time held
            time_held = (datetime.now() - pos.get('entry_time', datetime.now())).total_seconds()
            time_display = f"{int(time_held)}s" if time_held < 300 else f"{int(time_held/60)}m"
            
            positions_data.append({
                'Status': status,
                'Symbol': pos['token']['symbol'],
                'Size': f"${position_size:.0f}",
                'Entry': f"${base_price:.6f}",
                'Current': f"${current_price:.6f}",
                'Change': f"{pnl_percent:+.2f}%",
                'P&L': f"${current_pnl:.3f}",  # Show more precision for micro-profits
                'TP1%': f"{tp1_progress:.0f}%",
                'TP2%': f"{tp2_progress:.0f}%",
                'Time': time_display,
                'Partial': "Y" if pos.get('partial_sold', False) else "N",
                'Source': pos['token'].get('source', 'Unknown')
            })
        
        if positions_data:
            df_positions = pd.DataFrame(positions_data)
            st.dataframe(df_positions, use_container_width=True)
            
            # Micro-profit summary
            total_current_pnl = sum(float(p['P&L'].replace('$', '')) for p in positions_data)
            profitable_positions = len([p for p in positions_data if float(p['P&L'].replace('$', '')) > 0])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Open P&L", f"${total_current_pnl:.2f}")
            with col2:
                st.metric("Profitable Positions", f"{profitable_positions}/{len(positions_data)}")
            with col3:
                avg_time = sum(int(p['Time'].replace('s', '').replace('m', '')) for p in positions_data) / len(positions_data) if positions_data else 0
                st.metric("Avg Hold Time", f"{avg_time:.0f}s")
            with col4:
                micro_profits = len([p for p in positions_data if 0 < float(p['P&L'].replace('$', '')) < 1])
                st.metric("Micro-Profits", micro_profits)
    
    def render_pnl_chart(self):
        """Enhanced P&L chart for micro-profit tracking"""
        st.subheader("Micro-Profit Performance Analytics")
        
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
            st.metric("Best Micro-Trade", f"${st.session_state.best_trade:.3f}")
            st.metric("Worst Trade", f"${st.session_state.worst_trade:.3f}")
            
            # Micro-profit specific metrics
            if st.session_state.trades:
                micro_trades = [t for t in st.session_state.trades if 0 < t.get('pnl', 0) < 1]
                st.metric("Micro-Profit Trades", len(micro_trades))
            
            if st.session_state.win_streak > 0:
                st.metric("Win Streak", f"{st.session_state.win_streak}")
            else:
                st.metric("Loss Streak", f"{st.session_state.loss_streak}")
        
        with col2:
            if len(chart_data) > 1:
                st.line_chart(chart_data.set_index('Time')['Total P&L'], use_container_width=True, height=400)
                
                # Add target line annotation
                if len(st.session_state.trades) > 0:
                    trading_hours = (datetime.now() - st.session_state.trades[0]['timestamp']).total_seconds() / 3600
                    target_pnl = trading_hours * 50  # $50/hour target
                    st.caption(f"Target P&L for {trading_hours:.1f} hours: ${target_pnl:.2f}")
    
    def render_live_activity(self):
        """Enhanced live activity for micro-profit system"""
        st.subheader("Micro-Profit Live Activity")
        if st.session_state.debug_info:
            for msg, msg_type in list(st.session_state.debug_info)[-30:]:
                if msg_type == "success":
                    st.success(msg)
                elif msg_type == "error":
                    st.error(msg)
                elif msg_type == "warning":
                    st.warning(msg)
                else:
                    st.info(msg)
        else:
            st.info("Click START MICRO TRADING to begin high-frequency micro-profit system...")
    
    def render_trade_history(self):
        """Enhanced trade history for micro-profit analysis"""
        if st.session_state.trades:
            st.subheader("Micro-Profit Trade History")
            
            trades_data = []
            for trade in st.session_state.trades[-50:]:  # Show more recent trades
                display_address = f"{trade['mint_address'][:4]}...{trade['mint_address'][-4:]}" if len(trade.get('mint_address', '')) > 10 else 'N/A'
                
                # Color code micro-profits
                pnl = trade.get('pnl', 0)
                if 0 < pnl < 0.5:
                    pnl_display = f"${pnl:.3f} 🔸"  # Micro profit
                elif 0.5 <= pnl < 1:
                    pnl_display = f"${pnl:.3f} ⭐"  # Good micro profit
                elif pnl >= 1:
                    pnl_display = f"${pnl:.2f} 💰"  # Excellent profit
                else:
                    pnl_display = f"${pnl:.3f}"
                
                trades_data.append({
                    'Time': trade['timestamp'].strftime('%H:%M:%S'),
                    'Symbol': trade['symbol'],
                    'Score': trade.get('score', 0),
                    'Size': f"${trade.get('position_size', BASE_POSITION_SIZE):.0f}",
                    'Entry': f"${trade['entry_price']:.6f}",
                    'Exit': f"${trade['exit_price']:.6f}",
                    'Change': f"{trade['percent_change']:+.2f}%",
                    'P&L': pnl_display,
                    'Reason': trade['exit_reason'],
                    'Duration': f"{int(trade.get('duration_seconds', 0))}s",
                    'Source': trade.get('source', 'Unknown')
                })
            
            df_trades = pd.DataFrame(trades_data)
            st.dataframe(df_trades, use_container_width=True)
            
            # Micro-profit analysis
            if len(st.session_state.trades) >= 10:
                col1, col2, col3, col4 = st.columns(4)
                
                recent_trades = st.session_state.trades[-20:]
                micro_profits = [t for t in recent_trades if 0 < t.get('pnl', 0) < 1]
                avg_duration = sum(t.get('duration_seconds', 0) for t in recent_trades) / len(recent_trades)
                quick_trades = len([t for t in recent_trades if t.get('duration_seconds', 0) < 180])  # Under 3 minutes
                
                with col1:
                    st.metric("Micro-Profits", f"{len(micro_profits)}/{len(recent_trades)}")
                with col2:
                    st.metric("Avg Duration", f"{avg_duration:.0f}s")
                with col3:
                    st.metric("Quick Exits (<3min)", quick_trades)
                with col4:
                    total_pnl = sum(t.get('pnl', 0) for t in recent_trades)
                    st.metric("Recent 20 P&L", f"${total_pnl:.2f}")
    
    def render_statistics(self):
        """Updated statistics for micro-profit system"""
        if not st.session_state.trades:
            st.info("No trades yet")
            return
        
        from analytics import Analytics
        analytics = Analytics()
        metrics = analytics.get_performance_metrics()
        
        if metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Trades", metrics['total_trades'])
                st.metric("Winning Trades", metrics['winning_trades'])
                st.metric("Losing Trades", metrics['losing_trades'])
                
                # Micro-profit specific metrics
                micro_profits = len([t for t in st.session_state.trades if 0 < t.get('pnl', 0) < 1])
                st.metric("Micro-Profits", micro_profits)
            
            with col2:
                st.metric("Average Win", f"${metrics['avg_win']:.3f}")
                st.metric("Average Loss", f"${metrics['avg_loss']:.3f}")
                st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
                
                # Speed metrics
                avg_duration = metrics.get('avg_duration', 0)
                st.metric("Avg Duration", f"{avg_duration:.0f}s")
            
            with col3:
                st.metric("Total P&L", f"${metrics['total_pnl']:.2f}")
                st.metric("Average P&L", f"${metrics['avg_pnl']:.3f}")
                st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
                
                # Target progress
                trades_per_hour = st.session_state.trades_per_hour
                target_progress = (trades_per_hour / TARGET_TRADES_PER_HOUR) * 100
                st.metric("Target Progress", f"{target_progress:.0f}%")
    
    def render_analysis_export(self, analytics):
        """Enhanced analysis export for micro-profit data"""
        st.subheader("Micro-Profit Analysis & Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Export Micro-Profit Data")
            if st.session_state.trades:
                df = analytics.export_trades_to_csv()
                
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="Download Micro-Profit Data (CSV)",
                    data=csv_data,
                    file_name=f"micro_profit_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                # Micro-profit summary
                micro_trades = len([t for t in st.session_state.trades if 0 < t.get('pnl', 0) < 1])
                st.info(f"Dataset: {len(df)} trades, {micro_trades} micro-profits")
            else:
                st.warning("No trades to export yet")
        
        with col2:
            st.markdown("### Micro-Profit Analysis")
            if st.button("Analyze Micro-Profit Patterns", use_container_width=True):
                if len(st.session_state.trades) >= 20:
                    analysis = analytics.generate_analysis_report()
                    
                    st.download_button(
                        label="Download Micro-Profit Analysis",
                        data=analysis,
                        file_name=f"micro_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    with st.expander("View Micro-Profit Analysis", expanded=True):
                        st.text(analysis)
                else:
                    st.warning("Need at least 20 trades for micro-profit analysis")
    
    def render_footer(self):
        """Updated footer for micro-profit system"""
        st.markdown("---")
        st.caption("**MICRO-PROFIT SYSTEM**: High-frequency trading optimized for $50/hour on Solana")
        st.caption("**TARGETS**: 3% and 5% profits with 2.5% stop loss in under 3 minutes")
        st.caption("**SOLANA OPTIMIZED**: ~$0.05 transaction costs enable micro-profit scalping")
        st.caption("**HIGH FREQUENCY**: 150+ trades/hour target with automatic token reset")
        st.caption("**RISK MANAGED**: Small positions ($12-20), tight stops, fast exits")
        st.caption("**FIXED P&L**: Accurate profit calculations with slippage and fee accounting")
