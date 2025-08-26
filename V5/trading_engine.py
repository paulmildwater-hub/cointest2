"""
Micro-Profit Trading Engine - COMPLETELY FIXED P&L calculations for high-frequency trading
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from config import *

class MicroProfitTradingEngine:
    def __init__(self):
        self.config = NORMAL_SETTINGS.copy()
        self.price_history = {}
        self.seen_tokens_reset_time = time.time()
        
    def apply_turbo_mode(self, enabled):
        """Apply turbo mode settings"""
        if enabled:
            self.config = TURBO_SETTINGS.copy()
            # Update global settings
            for key, value in TURBO_SETTINGS.items():
                if hasattr(st.session_state, f'config_{key.lower()}'):
                    setattr(st.session_state, f'config_{key.lower()}', value)
        else:
            self.config = NORMAL_SETTINGS.copy()
    
    def reset_seen_tokens_periodically(self):
        """Reset seen tokens every 10 minutes for re-trading opportunities"""
        current_time = time.time()
        if current_time - self.seen_tokens_reset_time >= SEEN_TOKENS_RESET_TIME:
            original_count = len(st.session_state.seen_tokens)
            st.session_state.seen_tokens = set()
            self.seen_tokens_reset_time = current_time
            
            if 'debug_info' in st.session_state:
                debug_msg = f"Reset {original_count} seen tokens - allowing re-trades"
                st.session_state.debug_info.append((f"[{datetime.now().strftime('%H:%M:%S')}] {debug_msg}", "info"))
    
    def should_buy_token(self, token):
        """Extremely permissive token selection for high frequency"""
        mint = token.get('mint', '')
        
        # Skip if currently owned (but allow re-trading after reset)
        if mint in st.session_state.active_positions:
            return False
        
        # Check daily loss limit
        if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
            return False
        
        # Very low score threshold
        score = token.get('score', 0)
        min_score = self.config.get('MIN_TOKEN_SCORE', MIN_TOKEN_SCORE)
        if score < min_score:
            return False
        
        # Extremely permissive momentum - accept tiny movements
        price_change_1h = token.get('price_change_1h', 0)
        price_change_5m = token.get('price_change_5m', 0)
        
        min_increase = self.config.get('MIN_PRICE_INCREASE', MIN_PRICE_INCREASE) * 100
        
        # Accept if ANY timeframe shows momentum or even small negative
        if price_change_1h < -10 and price_change_5m < -5:  # Only reject extreme negatives
            return False
        
        # Very permissive market cap range
        market_cap = token.get('market_cap', 0)
        if not (MIN_MARKET_CAP <= market_cap <= MAX_MARKET_CAP):
            return False
        
        # Low liquidity requirement
        liquidity = token.get('liquidity', 0)
        if liquidity < MIN_LIQUIDITY:
            return False
        
        # Mark as seen for current cycle
        st.session_state.seen_tokens.add(mint)
        return True
    
    def calculate_position_size(self, token):
        """Small, consistent position sizes for high frequency"""
        score = token.get('score', 0)
        
        # Keep positions small and consistent
        if score >= 50:
            return BASE_POSITION_SIZE * 1.3  # $15.6
        elif score >= 35:
            return BASE_POSITION_SIZE * 1.1  # $13.2
        else:
            return BASE_POSITION_SIZE  # $12
    
    def enter_position(self, token):
        """Enter position with CORRECT P&L tracking from start"""
        try:
            base_price = token.get('price_usd', 0)
            if base_price <= 0:
                return None
            
            position_size = self.calculate_position_size(token)
            mint = token.get('mint', '')
            
            # STEP 1: Calculate entry with slippage and fees
            entry_price_with_slippage = base_price * (1 + SLIPPAGE)  # Pay 0.2% more
            net_investment = position_size - TRANSACTION_FEE  # Subtract entry fee
            tokens_bought = net_investment / entry_price_with_slippage  # Actual tokens received
            
            # STEP 2: Store all the critical values for P&L calculation
            position = {
                'token': token,
                'base_price': base_price,  # Original market price
                'entry_price': entry_price_with_slippage,  # What we actually paid
                'entry_time': datetime.now(),
                'current_price': base_price,  # Track current market price
                'position_size': position_size,  # Original investment
                'net_investment': net_investment,  # After entry fee
                'tokens_bought': tokens_bought,  # Actual tokens owned
                'take_profit_1': base_price * (1 + self.config.get('TAKE_PROFIT_1', TAKE_PROFIT_1)),
                'take_profit_2': base_price * (1 + self.config.get('TAKE_PROFIT_2', TAKE_PROFIT_2)),
                'stop_loss': base_price * (1 - self.config.get('STOP_LOSS', STOP_LOSS)),
                'highest_price': base_price,
                'partial_sold': False,
                'partial_tokens_sold': 0,
                'partial_proceeds': 0,
                'consecutive_no_change': 0,
                'score': token.get('score', 0)
            }
            
            # Initialize price history
            self.price_history[mint] = {
                'prices': [base_price],
                'timestamps': [datetime.now()]
            }
            
            st.session_state.active_positions[mint] = position
            st.session_state.equity -= position_size
            st.session_state.tokens_bought += 1
            
            return position
            
        except Exception as e:
            print(f"Error entering position: {e}")
            return None
    
    def calculate_current_pnl(self, position, current_market_price):
        """COMPLETELY FIXED P&L calculation"""
        try:
            # Current tokens owned (account for partial sales)
            current_tokens = position['tokens_bought'] - position.get('partial_tokens_sold', 0)
            
            if current_tokens <= 0:
                return 0, 0  # No tokens left
            
            # Calculate exit proceeds with slippage and fees
            exit_price_after_slippage = current_market_price * (1 - SLIPPAGE)  # Get 0.2% less
            gross_proceeds = current_tokens * exit_price_after_slippage
            net_proceeds = gross_proceeds - TRANSACTION_FEE  # Subtract exit fee
            
            # Add any previous partial sale proceeds
            total_proceeds = net_proceeds + position.get('partial_proceeds', 0)
            
            # P&L = Total proceeds - Original investment
            pnl = total_proceeds - position['position_size']
            
            return pnl, net_proceeds
            
        except Exception as e:
            print(f"Error calculating P&L: {e}")
            return 0, 0
    
    def check_exit_conditions(self, position, current_price):
        """Fast exit conditions for micro-profits"""
        mint = position['token'].get('mint', '')
        position['current_price'] = current_price
        
        # Update price history for stagnation detection
        if mint in self.price_history:
            history = self.price_history[mint]
            history['prices'].append(current_price)
            history['timestamps'].append(datetime.now())
            
            # Keep only recent history
            if len(history['prices']) > 10:
                history['prices'] = history['prices'][-10:]
                history['timestamps'] = history['timestamps'][-10:]
        
        # Update highest price
        if current_price > position['highest_price']:
            position['highest_price'] = current_price
        
        # Calculate current P&L and percentage change
        pnl, net_proceeds = self.calculate_current_pnl(position, current_price)
        percent_change = ((current_price - position['base_price']) / position['base_price']) * 100
        time_held = (datetime.now() - position['entry_time']).total_seconds()
        
        # PARTIAL PROFIT TAKING at 3%
        profit_target_1 = self.config.get('TAKE_PROFIT_1', TAKE_PROFIT_1)
        if not position.get('partial_sold', False) and percent_change >= (profit_target_1 * 100):
            # Sell 50% of tokens
            tokens_to_sell = position['tokens_bought'] * 0.5
            partial_exit_price = current_price * (1 - SLIPPAGE)
            partial_gross = tokens_to_sell * partial_exit_price
            partial_net = partial_gross - TRANSACTION_FEE
            
            # Update position tracking
            position['partial_sold'] = True
            position['partial_tokens_sold'] = tokens_to_sell
            position['partial_proceeds'] = partial_net
            
            # Calculate partial P&L
            partial_investment = position['position_size'] * 0.5  # Half of original investment
            partial_pnl = partial_net - partial_investment
            
            # Update equity immediately
            st.session_state.equity += partial_net
            st.session_state.daily_pnl += partial_pnl
            
            return False, 'PARTIAL_3%', partial_pnl
        
        # NO-CHANGE DETECTION (ultra-fast)
        no_change_time = self.config.get('NO_CHANGE_SELL_TIME', NO_CHANGE_SELL_TIME)
        if mint in self.price_history:
            recent_prices = self.price_history[mint]['prices'][-3:]
            if len(recent_prices) >= 3:
                price_range = max(recent_prices) - min(recent_prices)
                relative_range = price_range / current_price
                
                if relative_range < 0.001:  # Less than 0.1% movement
                    position['consecutive_no_change'] += 1
                    if position['consecutive_no_change'] >= 2:  # Very quick exit
                        return True, 'NO_CHANGE', pnl
                else:
                    position['consecutive_no_change'] = 0
        
        # PROFIT TARGETS (micro-profits)
        profit_target_2 = self.config.get('TAKE_PROFIT_2', TAKE_PROFIT_2)
        if percent_change >= (profit_target_2 * 100):  # 5% target
            return True, 'TAKE_PROFIT_5%', pnl
        
        # TIGHT STOP LOSS
        stop_loss_pct = self.config.get('STOP_LOSS', STOP_LOSS)
        if percent_change <= -(stop_loss_pct * 100):  # 2.5% stop loss
            return True, 'STOP_LOSS_2.5%', pnl
        
        # QUICK TIMEOUT (3 minutes)
        if time_held >= MAX_TRADE_DURATION:
            return True, 'TIMEOUT', pnl
        
        # MICRO-PROFIT SCALPING - Exit small wins quickly
        if 1 <= percent_change <= 2 and time_held >= 60:  # 1-2% after 1 minute
            return True, 'MICRO_SCALP', pnl
        
        return False, 'HOLDING', pnl
    
    def close_position(self, mint, reason, pnl):
        """Close position with ACCURATE final P&L recording"""
        position = st.session_state.active_positions[mint]
        current_price = position['current_price']
        
        # Calculate FINAL accurate P&L
        final_pnl, final_proceeds = self.calculate_current_pnl(position, current_price)
        
        # Use calculated P&L, not passed P&L (which might be wrong)
        actual_pnl = final_pnl
        
        # Record trade with correct values
        trade = self._create_trade_record(position, reason, actual_pnl)
        st.session_state.trades.append(trade)
        
        # Update equity correctly
        remaining_tokens = position['tokens_bought'] - position.get('partial_tokens_sold', 0)
        if remaining_tokens > 0:
            # Add final sale proceeds
            st.session_state.equity += final_proceeds
        
        # Update daily P&L (don't double-count partial sales)
        if not position.get('partial_sold', False):
            st.session_state.daily_pnl += actual_pnl
        else:
            # Only add the remaining P&L (partial already added)
            remaining_pnl = actual_pnl - position.get('partial_proceeds', 0) + (position['position_size'] * 0.5)
            st.session_state.daily_pnl += remaining_pnl
        
        # Update streaks
        if actual_pnl > 0:
            st.session_state.win_streak += 1
            st.session_state.loss_streak = 0
            if actual_pnl > st.session_state.best_trade:
                st.session_state.best_trade = actual_pnl
        else:
            st.session_state.loss_streak += 1
            st.session_state.win_streak = 0
            if actual_pnl < st.session_state.worst_trade:
                st.session_state.worst_trade = actual_pnl
        
        # Track P&L history
        current_total_pnl = sum(t['pnl'] for t in st.session_state.trades)
        st.session_state.pnl_history.append(current_total_pnl)
        st.session_state.time_history.append(datetime.now())
        
        # Clean up
        del st.session_state.active_positions[mint]
        if mint in self.price_history:
            del self.price_history[mint]
    
    def _create_trade_record(self, position, reason, pnl):
        """Create trade record with correct values"""
        current_price = position['current_price']
        base_price = position['base_price']
        
        percent_change = ((current_price - base_price) / base_price) * 100
        duration_seconds = (datetime.now() - position['entry_time']).total_seconds()
        
        return {
            'timestamp': datetime.now(),
            'symbol': position['token']['symbol'],
            'mint_address': position['token'].get('mint', ''),
            'entry_price': base_price,  # Use base price for consistency
            'exit_price': current_price,
            'exit_reason': reason,
            'pnl': pnl,  # FIXED: Using correctly calculated P&L
            'pnl_percent': (pnl / position['position_size']) * 100 if position['position_size'] > 0 else 0,
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_seconds / 60,
            'percent_change': percent_change,
            'position_size': position['position_size'],
            'partial_sold': position.get('partial_sold', False),
            'source': position['token'].get('source', 'Unknown'),
            'score': position.get('score', 0),
            'market_cap': position['token'].get('market_cap', 0),
            'liquidity': position['token'].get('liquidity', 0),
            'volume_24h': position['token'].get('volume_24h', 0),
            'price_change_5m_at_entry': position['token'].get('price_change_5m', 0),
            'price_change_1h_at_entry': position['token'].get('price_change_1h', 0),
            'price_change_24h_at_entry': position['token'].get('price_change_24h', 0),
            'txns_24h': position['token'].get('txns_24h', 0),
            'dex': position['token'].get('dex', 'unknown'),
            'highest_price_reached': position.get('highest_price', base_price),
            'max_profit_potential': ((position.get('highest_price', base_price) - base_price) / base_price) * 100,
            'turbo_mode': st.session_state.turbo_mode,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_quick_scalp': reason == 'MICRO_SCALP'
        }
    
    def update_all_prices(self, data_fetcher):
        """Fast price updates"""
        if not st.session_state.active_positions:
            return
        
        for mint, position in st.session_state.active_positions.items():
            try:
                new_price = data_fetcher.get_current_price(position['token'])
                if new_price > 0:
                    # Accept reasonable price movements
                    current_price = position.get('current_price', position['base_price'])
                    price_change_ratio = abs(new_price - current_price) / current_price
                    
                    if price_change_ratio < 0.5:  # 50% sanity check
                        position['current_price'] = new_price
                        if new_price > position.get('highest_price', position['base_price']):
                            position['highest_price'] = new_price
            except Exception as e:
                continue
    
    def run_trading_cycle(self, data_fetcher):
        """Ultra-fast trading cycle"""
        if not st.session_state.bot_running:
            return
        
        # Check daily loss limit
        if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
            st.session_state.bot_running = False
            return
        
        current_time = time.time()
        
        # Very fast cycles
        if current_time - st.session_state.last_update < CYCLE_DELAY:
            return
        
        st.session_state.last_update = current_time
        
        # Reset seen tokens periodically for re-trading
        self.reset_seen_tokens_periodically()
        
        # Fast price updates
        if current_time - st.session_state.last_price_update >= PRICE_UPDATE_INTERVAL:
            st.session_state.last_price_update = current_time
            self.update_all_prices(data_fetcher)
        
        # Check exits frequently
        positions_to_close = []
        for mint, position in list(st.session_state.active_positions.items()):
            try:
                current_price = position.get('current_price', position['base_price'])
                if current_price > 0:
                    should_exit, reason, pnl = self.check_exit_conditions(position, current_price)
                    if should_exit:
                        positions_to_close.append((mint, reason, pnl))
            except Exception as e:
                continue
        
        for mint, reason, pnl in positions_to_close:
            try:
                self.close_position(mint, reason, pnl)
            except Exception as e:
                continue
        
        # Aggressive token scanning
        scan_interval = self.config.get('SCAN_INTERVAL', SCAN_INTERVAL)
        if current_time - st.session_state.last_token_check >= scan_interval:
            st.session_state.last_token_check = current_time
            
            if st.session_state.equity >= BASE_POSITION_SIZE:
                try:
                    tokens = data_fetcher.fetch_all_tokens()
                    
                    bought_this_cycle = 0
                    max_positions = self.config.get('MAX_CONCURRENT_POSITIONS', MAX_CONCURRENT_POSITIONS)
                    
                    # Take many more tokens per cycle
                    for token in tokens[:50]:  # Consider top 50
                        if len(st.session_state.active_positions) >= max_positions:
                            break
                        
                        position_size = self.calculate_position_size(token)
                        if st.session_state.equity < position_size:
                            continue
                        
                        if bought_this_cycle >= 15:  # Up to 15 new positions per cycle
                            break
                        
                        if self.should_buy_token(token):
                            if self.enter_position(token):
                                bought_this_cycle += 1
                                
                except Exception as e:
                    print(f"Error in token scanning: {e}")

# Create alias for backward compatibility  
TradingEngine = MicroProfitTradingEngine
