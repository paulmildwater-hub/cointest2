"""
High-Volume Trading Engine - Optimized for frequent trades while maintaining quality
"""

import streamlit as st
import time
import random
from datetime import datetime
from config import *

class HighVolumeTradingEngine:
    def __init__(self):
        self.config = NORMAL_SETTINGS.copy()
        self.price_history = {}
        self.quick_scalp_targets = {}  # Track quick scalp opportunities
        
    def apply_turbo_mode(self, enabled):
        """Apply turbo mode settings for maximum volume"""
        if enabled:
            self.config = TURBO_SETTINGS.copy()
            for key, value in TURBO_SETTINGS.items():
                globals()[key] = value
        else:
            self.config = NORMAL_SETTINGS.copy()
            for key, value in NORMAL_SETTINGS.items():
                globals()[key] = value
    
"""
High-Volume Trading Engine - Optimized for frequent trades while maintaining quality
"""

import streamlit as st
import time
import random
from datetime import datetime
from config import *

class HighVolumeTradingEngine:
    def __init__(self):
        self.config = NORMAL_SETTINGS.copy()
        self.price_history = {}
        self.quick_scalp_targets = {}  # Track quick scalp opportunities
        
    def apply_turbo_mode(self, enabled):
        """Apply turbo mode settings for maximum volume"""
        if enabled:
            self.config = TURBO_SETTINGS.copy()
            for key, value in TURBO_SETTINGS.items():
                globals()[key] = value
        else:
            self.config = NORMAL_SETTINGS.copy()
            for key, value in NORMAL_SETTINGS.items():
                globals()[key] = value
    
    def should_buy_token(self, token):
        """More permissive token selection for higher volume"""
        mint = token.get('mint', '')
        
        # Skip if already seen or owned
        if mint in st.session_state.seen_tokens or mint in st.session_state.active_positions:
            return False
        
        # Check daily loss limit
        if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
            return False
        
        # More permissive score requirement for volume
        score = token.get('score', 0)
        min_score = self.config.get('MIN_TOKEN_SCORE', MIN_TOKEN_SCORE)
        if score < min_score:
            return False
        
        # More permissive momentum requirements
        price_change_1h = token.get('price_change_1h', 0)
        price_change_5m = token.get('price_change_5m', 0)
        
        # Accept if either timeframe shows momentum
        min_increase = self.config.get('MIN_PRICE_INCREASE', MIN_PRICE_INCREASE) * 100
        if price_change_1h < min_increase and price_change_5m < (min_increase * 0.5):
            return False
        
        # Expanded market cap range
        market_cap = token.get('market_cap', 0)
        if not (MIN_MARKET_CAP <= market_cap <= MAX_MARKET_CAP):
            return False
        
        # More permissive liquidity
        liquidity = token.get('liquidity', 0)
        if liquidity < MIN_LIQUIDITY:
            return False
        
        # Volume activity check
        volume_24h = token.get('volume_24h', 0)
        volume_to_mcap = volume_24h / market_cap if market_cap > 0 else 0
        if volume_to_mcap < QUALITY_FILTERS['MIN_VOLUME_TO_MCAP_RATIO']:
            return False
        
        st.session_state.seen_tokens.add(mint)
        return True
    
    def calculate_position_size(self, token):
        """Dynamic position sizing for volume optimization"""
        score = token.get('score', 0)
        volume_24h = token.get('volume_24h', 0)
        
        # Base size on score and volume
        if score >= 75 and volume_24h > 500000:
            return min(BASE_POSITION_SIZE * 2, MAX_POSITION_SIZE)
        elif score >= 60 and volume_24h > 100000:
            return BASE_POSITION_SIZE * 1.5
        elif score >= 50:
            return BASE_POSITION_SIZE * 1.2
        else:
            return BASE_POSITION_SIZE
    
    def enter_position(self, token):
        """Enter position with quick scalp detection"""
        try:
            entry_price = token.get('price_usd', 0)
            if entry_price <= 0:
                return None
            
            position_size = self.calculate_position_size(token)
            entry_price = entry_price * (1 + SLIPPAGE)
            mint = token.get('mint', '')
            
            # Initialize price history
            self.price_history[mint] = {
                'prices': [entry_price],
                'timestamps': [datetime.now()],
                'last_significant_change': datetime.now()
            }
            
            # Detect quick scalp opportunity
            is_quick_scalp = self._is_quick_scalp_candidate(token)
            
            position = {
                'token': token,
                'entry_price': entry_price,
                'entry_time': datetime.now(),
                'current_price': entry_price,
                'position_size': position_size,
                'tokens_bought': (position_size - TRANSACTION_FEE) / entry_price,
                'take_profit_1': entry_price * (1 + TAKE_PROFIT_1),
                'take_profit_2': entry_price * (1 + TAKE_PROFIT_2),
                'stop_loss': entry_price * (1 - STOP_LOSS),
                'highest_price': entry_price,
                'partial_sold': False,
                'last_price_check': datetime.now(),
                'consecutive_no_change_periods': 0,
                'score': token.get('score', 0),
                'trailing_stop': None,
                'is_quick_scalp': is_quick_scalp,
                'scalp_target': entry_price * 1.05 if is_quick_scalp else None  # 5% quick target
            }
            
            st.session_state.active_positions[mint] = position
            st.session_state.equity -= position_size
            st.session_state.tokens_bought += 1
            
            if is_quick_scalp:
                self.quick_scalp_targets[mint] = datetime.now()
            
            return position
        except Exception as e:
            print(f"Error entering position: {e}")
            return None
    
    def _is_quick_scalp_candidate(self, token):
        """Identify tokens suitable for quick scalping"""
        volume_24h = token.get('volume_24h', 0)
        price_change_5m = token.get('price_change_5m', 0)
        liquidity = token.get('liquidity', 0)
        
        # High volume, recent momentum, good liquidity
        return (volume_24h > 200000 and 
                price_change_5m > 1.0 and 
                liquidity > 30000)
    
    def check_exit_conditions(self, position, current_price):
        """Enhanced exit logic for high volume trading"""
        mint = position['token'].get('mint', '')
        position['current_price'] = current_price
        
        # Update price history
        if mint in self.price_history:
            history = self.price_history[mint]
            history['prices'].append(current_price)
            history['timestamps'].append(datetime.now())
            
            # Keep recent history
            if len(history['prices']) > 20:
                history['prices'] = history['prices'][-20:]
                history['timestamps'] = history['timestamps'][-20:]
        
        # Update highest price
        if current_price > position['highest_price']:
            position['highest_price'] = current_price
            
            # Dynamic trailing stop
            gain_percent = ((current_price - position['entry_price']) / position['entry_price']) * 100
            if gain_percent > 20:
                position['trailing_stop'] = current_price * 0.92  # 8% trailing stop
            elif gain_percent > 15:
                position['trailing_stop'] = current_price * 0.95  # 5% trailing stop
        
        time_held = (datetime.now() - position['entry_time']).total_seconds()
        percent_change = ((current_price - position['entry_price']) / position['entry_price']) * 100
        
        # Calculate P&L
        position_size = position.get('position_size', BASE_POSITION_SIZE)
        if position.get('partial_sold', False):
            position_size = position_size / 2
        
        exit_price = current_price * (1 - SLIPPAGE)
        gross_value = position['tokens_bought'] * exit_price
        if position.get('partial_sold', False):
            gross_value = gross_value / 2
        
        net_value = gross_value - TRANSACTION_FEE
        pnl = net_value - position_size
        
        # QUICK SCALP EXIT - Priority for fast turnover
        if position.get('is_quick_scalp', False) and mint in self.quick_scalp_targets:
            scalp_time = (datetime.now() - self.quick_scalp_targets[mint]).total_seconds()
            
            # Quick 3-5% scalp exits
            if percent_change >= 5 or scalp_time >= PROFIT_OPTIMIZATION.get('scalp_exit_time', 120):
                if percent_change >= 2:  # At least 2% profit for scalp
                    return True, 'QUICK_SCALP', pnl
                elif scalp_time >= 120:  # Exit after 2 minutes regardless
                    return True, 'SCALP_TIMEOUT', pnl
        
        # MULTI-LEVEL PROFIT TAKING for volume
        if not position.get('partial_sold', False):
            if percent_change >= 8:  # First level at 8%
                position['partial_sold'] = True
                partial_pnl = (position_size * 0.4) * 0.08  # Take 40% at 8%
                st.session_state.equity += (position_size * 0.4) + partial_pnl
                st.session_state.daily_pnl += partial_pnl
                position['tokens_bought'] = position['tokens_bought'] * 0.6
                return False, 'PARTIAL_8%', partial_pnl
        
        # IMPROVED NO-CHANGE DETECTION
        if mint in self.price_history:
            history = self.price_history[mint]
            recent_prices = history['prices'][-5:] if len(history['prices']) >= 5 else history['prices']
            
            if len(recent_prices) > 1:
                price_variance = max(recent_prices) - min(recent_prices)
                relative_variance = price_variance / current_price
                
                # Faster exit for no movement
                if relative_variance < 0.003:  # Less than 0.3% variance
                    position['consecutive_no_change_periods'] += 1
                    
                    no_change_threshold = 2 if st.session_state.turbo_mode else 3
                    if position['consecutive_no_change_periods'] >= no_change_threshold:
                        return True, 'NO_CHANGE', pnl
                else:
                    position['consecutive_no_change_periods'] = 0
        
        # TRAILING STOP
        if position.get('trailing_stop') and current_price <= position['trailing_stop']:
            return True, 'TRAILING_STOP', pnl
        
        # STANDARD EXITS - Faster for volume
        if percent_change >= 20:  # Take profit at 20%
            return True, 'TAKE_PROFIT_20%', pnl
        elif percent_change <= -8:  # Stop loss at 8%
            return True, 'STOP_LOSS_8%', pnl
        elif time_held >= MAX_TRADE_DURATION:  # Max hold time
            return True, 'TIMEOUT', pnl
        
        # MOMENTUM REVERSAL - Quick exit on trend change
        if percent_change > 3 and mint in self.price_history:
            recent_prices = self.price_history[mint]['prices'][-4:]
            if len(recent_prices) >= 4:
                # Check for 3 consecutive drops
                if (recent_prices[-1] < recent_prices[-2] < 
                    recent_prices[-3] < recent_prices[-4]):
                    return True, 'MOMENTUM_REVERSAL', pnl
        
        # VOLUME DECAY EXIT - If volume drops significantly
        current_volume = position['token'].get('volume_24h', 0)
        if current_volume > 0 and time_held > 300:  # After 5 minutes
            volume_decay = current_volume / position['token'].get('volume_24h', 1)
            if volume_decay < 0.5:  # Volume dropped by 50%+
                return True, 'VOLUME_DECAY', pnl
        
        return False, 'HOLDING', pnl
    
    def close_position(self, mint, reason, pnl):
        """Close position with volume tracking"""
        position = st.session_state.active_positions[mint]
        position_size = position.get('position_size', BASE_POSITION_SIZE)
        
        if position.get('partial_sold', False):
            position_size = position_size * 0.6  # Remaining 60%
        
        # Record trade
        trade = self._create_trade_record(position, reason, pnl, position_size)
        st.session_state.trades.append(trade)
        
        # Update equity and P&L
        st.session_state.equity += position_size + pnl
        st.session_state.daily_pnl += pnl
        
        # Update streaks
        if pnl > 0:
            st.session_state.win_streak += 1
            st.session_state.loss_streak = 0
            if pnl > st.session_state.best_trade:
                st.session_state.best_trade = pnl
        else:
            st.session_state.loss_streak += 1
            st.session_state.win_streak = 0
            if pnl < st.session_state.worst_trade:
                st.session_state.worst_trade = pnl
        
        # Track P&L history
        current_total_pnl = sum(t['pnl'] for t in st.session_state.trades)
        st.session_state.pnl_history.append(current_total_pnl)
        st.session_state.time_history.append(datetime.now())
        
        # Clean up
        del st.session_state.active_positions[mint]
        if mint in self.price_history:
            del self.price_history[mint]
        if mint in self.quick_scalp_targets:
            del self.quick_scalp_targets[mint]
    
    def _create_trade_record(self, position, reason, pnl, position_size):
        """Create detailed trade record"""
        percent_change = ((position['current_price'] - position['entry_price']) / position['entry_price']) * 100
        duration_seconds = (datetime.now() - position['entry_time']).total_seconds()
        
        return {
            'timestamp': datetime.now(),
            'symbol': position['token']['symbol'],
            'mint_address': position['token'].get('mint', ''),
            'entry_price': position['entry_price'],
            'exit_price': position['current_price'],
            'exit_reason': reason,
            'pnl': pnl,
            'pnl_percent': (pnl / position_size) * 100 if position_size > 0 else 0,
            'duration_seconds': duration_seconds,
            'duration_minutes': duration_seconds / 60,
            'percent_change': percent_change,
            'position_size': position_size,
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
            'highest_price_reached': position.get('highest_price', position['entry_price']),
            'max_profit_potential': ((position.get('highest_price', position['entry_price']) - position['entry_price']) / position['entry_price']) * 100,
            'turbo_mode': st.session_state.turbo_mode,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'is_quick_scalp': position.get('is_quick_scalp', False)
        }
    
    def update_all_prices(self, data_fetcher):
        """Fast price updates for high volume trading"""
        if not st.session_state.active_positions:
            return
        
        updated_count = 0
        for mint, position in st.session_state.active_positions.items():
            try:
                new_price = data_fetcher.get_current_price(position['token'])
                if new_price > 0:
                    current_price = position.get('current_price', position['entry_price'])
                    price_change_ratio = abs(new_price - current_price) / current_price
                    
                    # Accept larger price movements for high volume trading
                    if price_change_ratio < 0.7:  # Accept up to 70% moves
                        position['current_price'] = new_price
                        if new_price > position.get('highest_price', position['entry_price']):
                            position['highest_price'] = new_price
                        updated_count += 1
            except Exception as e:
                continue
    
    def run_trading_cycle(self, data_fetcher):
        """High-frequency trading cycle"""
        if not st.session_state.bot_running:
            return
        
        # Check daily loss limit
        if st.session_state.daily_pnl <= MAX_DAILY_LOSS:
            st.session_state.bot_running = False
            return
        
        current_time = time.time()
        if current_time - st.session_state.last_update < CYCLE_DELAY:
            return
        
        st.session_state.last_update = current_time
        
        # More frequent price updates for volume trading
        if current_time - st.session_state.last_price_update >= PRICE_UPDATE_INTERVAL:
            st.session_state.last_price_update = current_time
            self.update_all_prices(data_fetcher)
        
        # Check exits more frequently
        positions_to_close = []
        for mint, position in list(st.session_state.active_positions.items()):
            try:
                current_price = data_fetcher.get_current_price(position['token'])
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
        
        # More frequent token scanning for volume
        scan_interval = self.config.get('SCAN_INTERVAL', SCAN_INTERVAL)
        if current_time - st.session_state.last_token_check >= scan_interval:
            st.session_state.last_token_check = current_time
            
            if st.session_state.equity >= BASE_POSITION_SIZE:
                try:
                    tokens = data_fetcher.fetch_all_tokens()
                    
                    bought_this_cycle = 0
                    max_positions = self.config.get('MAX_CONCURRENT_POSITIONS', MAX_CONCURRENT_POSITIONS)
                    
                    # Take more tokens per cycle for volume
                    for token in tokens[:20]:  # Consider top 20 tokens
                        if len(st.session_state.active_positions) >= max_positions:
                            break
                        
                        position_size = self.calculate_position_size(token)
                        if st.session_state.equity < position_size:
                            continue
                        
                        if bought_this_cycle >= 8:  # Increased from 3 to 8
                            break
                        
                        if self.should_buy_token(token):
                            if self.enter_position(token):
                                bought_this_cycle += 1
                except Exception as e:
                    print(f"Error in token scanning: {e}")
                
                # Clean seen tokens more frequently
                if len(st.session_state.seen_tokens) > 800:
                    st.session_state.seen_tokens = set(list(st.session_state.seen_tokens)[-400:])

# Create alias for backward compatibility  
TradingEngine = HighVolumeTradingEngine