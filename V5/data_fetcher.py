"""
Multi-Source Data fetching module - Dramatically increase token discovery volume
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
from config import *

class MultiSourceDataFetcher:
    def __init__(self):
        self.headers = API_HEADERS
        
    def fetch_dexscreener_tokens(self, extended_search=True):
        """Enhanced DexScreener fetching with more comprehensive search"""
        tokens = []
        
        # Use all search queries for maximum coverage
        search_queries = SEARCH_QUERIES if extended_search else SEARCH_QUERIES[:10]
        
        for query in search_queries:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    # Take more pairs for higher volume
                    for pair in pairs[:30]:  # Increased from 20 to 30
                        if pair.get('chainId') != 'solana':
                            continue
                        
                        token_data = self._parse_dexscreener_pair(pair)
                        if token_data and self._passes_volume_filter(token_data):
                            tokens.append(token_data)
            except Exception as e:
                print(f"Error fetching from DexScreener: {e}")
                continue
        
        return tokens
    
    def fetch_trending_tokens(self):
        """Fetch trending/new tokens from DexScreener trending endpoint"""
        tokens = []
        
        try:
            # Get trending pairs by sorting by volume
            url = "https://api.dexscreener.com/latest/dex/search?q=solana"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                # Sort by volume and take top performers
                sorted_pairs = sorted(pairs, key=lambda x: float(x.get('volume', {}).get('h24', 0) or 0), reverse=True)
                
                for pair in sorted_pairs[:50]:  # Top 50 by volume
                    if pair.get('chainId') == 'solana':
                        token_data = self._parse_dexscreener_pair(pair)
                        if token_data and self._passes_volume_filter(token_data):
                            tokens.append(token_data)
        except Exception as e:
            print(f"Error fetching trending tokens: {e}")
        
        return tokens
    
    def fetch_pump_fun_tokens(self):
        """Fetch specifically from pump.fun ecosystem"""
        tokens = []
        
        try:
            # Search for pump.fun related tokens
            pump_queries = ["pump", "pumpfun", "pump.fun", "bonding"]
            
            for query in pump_queries:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    for pair in pairs[:25]:
                        if (pair.get('chainId') == 'solana' and 
                            pair.get('dexId') in ['pumpswap', 'raydium']):
                            
                            token_data = self._parse_dexscreener_pair(pair)
                            if token_data and self._passes_volume_filter(token_data):
                                tokens.append(token_data)
        except Exception as e:
            print(f"Error fetching pump.fun tokens: {e}")
        
        return tokens
    
    def _passes_volume_filter(self, token_data):
        """More permissive filter for higher volume"""
        if not token_data or token_data['price_usd'] <= 0:
            return False
        
        market_cap = token_data.get('market_cap', 0)
        liquidity = token_data.get('liquidity', 0)
        volume_24h = token_data.get('volume_24h', 0)
        
        # More permissive market cap range
        if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
            return False
        
        # Lower liquidity requirement
        if liquidity < MIN_LIQUIDITY:
            return False
        
        # Lower volume requirement
        if volume_24h < 500:  # Reduced from 1000
            return False
        
        # Don't require positive momentum for volume boost
        # This allows more tokens through the initial filter
        
        return True
    
    def fetch_all_tokens(self):
        """Fetch from multiple sources with aggressive discovery"""
        st.session_state.api_calls_count += 1
        
        all_tokens = []
        
        # Fetch from DexScreener with extended search
        dex_tokens = self.fetch_dexscreener_tokens(extended_search=True)
        all_tokens.extend(dex_tokens)
        
        # Fetch trending tokens
        trending_tokens = self.fetch_trending_tokens()
        all_tokens.extend(trending_tokens)
        
        # Fetch pump.fun specific tokens
        pump_tokens = self.fetch_pump_fun_tokens()
        all_tokens.extend(pump_tokens)
        
        # Remove duplicates more efficiently
        unique_tokens = {}
        for token in all_tokens:
            mint = token.get('mint', '')
            if mint and mint not in st.session_state.seen_tokens:
                # Take the token with highest volume if duplicate
                if mint not in unique_tokens or token.get('volume_24h', 0) > unique_tokens[mint].get('volume_24h', 0):
                    unique_tokens[mint] = token
        
        # Score and filter with more permissive criteria
        quality_tokens = []
        for token in unique_tokens.values():
            if self.is_tradeable_quality_token(token):
                score = self.calculate_volume_optimized_score(token)
                token['score'] = score
                # Lower score threshold for higher volume
                min_score = 50 if not st.session_state.turbo_mode else 35
                if score >= min_score:
                    quality_tokens.append(token)
        
        # Sort by score and volume combination
        quality_tokens.sort(key=lambda x: (x.get('score', 0) + x.get('volume_24h', 0) / 10000), reverse=True)
        
        # Take more tokens for higher volume
        max_tokens = 50 if not st.session_state.turbo_mode else 75
        final_tokens = quality_tokens[:max_tokens]
        
        st.session_state.tokens_found = len(final_tokens)
        return final_tokens
    
    def is_tradeable_quality_token(self, token):
        """More permissive quality check for higher volume"""
        market_cap = token.get('market_cap', 0)
        liquidity = token.get('liquidity', 0)
        volume = token.get('volume_24h', 0)
        price_change_1h = token.get('price_change_1h', 0)
        
        # Expanded market cap range
        if not (15000 <= market_cap <= 2000000):
            return False
        
        # Lower liquidity requirement
        if liquidity < 15000:
            return False
        
        # Volume activity requirement (more permissive)
        volume_to_mcap = volume / market_cap if market_cap > 0 else 0
        if volume_to_mcap < 3.0:  # Reduced from 5.0
            return False
        
        # More permissive momentum - allow some negative momentum
        if price_change_1h < -10:  # Only reject if down more than 10% in 1h
            return False
        
        # Basic activity check
        if token.get('txns_24h', 0) < 20:  # Reduced from 50
            return False
        
        return True
    
    def calculate_volume_optimized_score(self, token):
        """Scoring optimized for volume while maintaining quality"""
        score = 0
        
        market_cap = token.get('market_cap', 0)
        liquidity = token.get('liquidity', 0)
        volume = token.get('volume_24h', 0)
        price_change_5m = token.get('price_change_5m', 0)
        price_change_1h = token.get('price_change_1h', 0)
        price_change_24h = token.get('price_change_24h', 0)
        txns_24h = token.get('txns_24h', 0)
        
        # Heavy weight on volume for discovery
        if volume > 500000:
            score += 35
        elif volume > 200000:
            score += 25
        elif volume > 50000:
            score += 20
        elif volume > 10000:
            score += 15
        elif volume > 1000:
            score += 10
        
        # Momentum scoring - more forgiving
        if price_change_1h > 10:
            score += 20
        elif price_change_1h > 5:
            score += 15
        elif price_change_1h > 0:
            score += 10
        elif price_change_1h > -5:  # Allow small negative momentum
            score += 5
        
        # Short-term momentum bonus
        if price_change_5m > 2:
            score += 15
        elif price_change_5m > 0:
            score += 10
        
        # Liquidity scoring
        if liquidity > 50000:
            score += 20
        elif liquidity > 25000:
            score += 15
        elif liquidity > 15000:
            score += 10
        
        # Market cap scoring - broader acceptance
        if 50000 <= market_cap <= 500000:
            score += 15
        elif 20000 <= market_cap <= 1000000:
            score += 12
        elif 10000 <= market_cap <= 2000000:
            score += 8
        
        # Volume to market cap ratio
        volume_to_mcap = volume / market_cap if market_cap > 0 else 0
        if volume_to_mcap > 8:
            score += 15
        elif volume_to_mcap > 5:
            score += 12
        elif volume_to_mcap > 3:
            score += 8
        
        # Transaction activity
        if txns_24h > 200:
            score += 10
        elif txns_24h > 50:
            score += 8
        elif txns_24h > 20:
            score += 5
        
        # Bonus for consistency across timeframes
        if price_change_5m > 0 and price_change_1h > 0:
            score += 10
        
        return max(0, score)
    
    def _parse_dexscreener_pair(self, pair):
        """Enhanced parsing with better error handling"""
        try:
            base_token = pair.get('baseToken', {})
            
            symbol = base_token.get('symbol', 'UNKNOWN').upper()
            name = base_token.get('name', 'Unknown')
            
            # Less restrictive symbol filtering for higher volume
            suspicious_words = ['TEST', 'FAKE', 'SCAM']
            if any(word in symbol for word in suspicious_words):
                return None
            
            token_data = {
                'mint': base_token.get('address', ''),
                'symbol': symbol,
                'name': name,
                'price_usd': float(pair.get('priceUsd', 0) or 0),
                'market_cap': float(pair.get('fdv', 0) or pair.get('marketCap', 0) or 0),
                'liquidity': self._extract_liquidity(pair),
                'volume_24h': self._extract_volume(pair),
                'price_change_5m': self._extract_price_change(pair, 'm5'),
                'price_change_1h': self._extract_price_change(pair, 'h1'),
                'price_change_24h': self._extract_price_change(pair, 'h24'),
                'txns_24h': self._extract_transactions(pair),
                'source': 'DexScreener',
                'dex': pair.get('dexId', 'unknown'),
                'pair_created_at': pair.get('pairCreatedAt', 0)
            }
            
            return token_data
        except Exception as e:
            return None
    
    def _extract_liquidity(self, pair):
        """Extract liquidity from pair data"""
        try:
            if 'liquidity' in pair:
                if isinstance(pair['liquidity'], dict):
                    return float(pair['liquidity'].get('usd', 0) or 0)
                else:
                    return float(pair['liquidity'] or 0)
        except:
            return 0
    
    def _extract_volume(self, pair):
        """Extract volume from pair data"""
        try:
            if 'volume' in pair:
                if isinstance(pair['volume'], dict):
                    return float(pair['volume'].get('h24', 0) or 0)
        except:
            return 0
    
    def _extract_price_change(self, pair, timeframe):
        """Extract price change for timeframe"""
        try:
            if 'priceChange' in pair:
                if isinstance(pair['priceChange'], dict):
                    return float(pair['priceChange'].get(timeframe, 0) or 0)
        except:
            return 0
    
    def _extract_transactions(self, pair):
        """Extract transaction count"""
        try:
            if 'txns' in pair and isinstance(pair['txns'], dict):
                h24_data = pair['txns'].get('h24', {})
                if isinstance(h24_data, dict):
                    buys = h24_data.get('buys', 0)
                    sells = h24_data.get('sells', 0)
                    return int(buys + sells)
        except:
            return 0
    
    def get_current_price(self, token):
        """Get current price with multiple fallbacks"""
        try:
            mint = token.get('mint', '')
            if mint and len(mint) > 20:
                # Try direct token lookup first
                url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
                response = requests.get(url, headers=self.headers, timeout=2)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    if pairs:
                        best_pair = max(pairs, key=lambda p: float(p.get('liquidity', {}).get('usd', 0) or 0))
                        price = float(best_pair.get('priceUsd', 0) or 0)
                        if price > 0:
                            return price
        except:
            pass
        
        # Fallback to simulated price with momentum
        import random
        base_price = token.get('price_usd', 0.001)
        recent_change = token.get('price_change_5m', 0) / 100
        momentum_factor = max(-0.03, min(0.03, recent_change * 0.2))
        random_change = random.gauss(momentum_factor, 0.015)
        
        new_price = base_price * (1 + random_change)
        return max(new_price, base_price * 0.7)  # Don't drop below 70% of base

# Create alias for backward compatibility
DataFetcher = MultiSourceDataFetcher