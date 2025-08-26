"""
High-Frequency Data Fetcher - Optimized for maximum token discovery and speed
"""

import requests
import streamlit as st
import time
from datetime import datetime, timedelta
from config import *

class HighFrequencyDataFetcher:
    def __init__(self):
        self.headers = API_HEADERS
        self.last_comprehensive_scan = 0
        self.quick_scan_queries = ["pump", "new", "SOL", "bonk", "pepe"]  # Fast rotation
        
    def fetch_quick_scan_tokens(self):
        """Ultra-fast scan with rotating queries"""
        tokens = []
        current_time = time.time()
        
        # Rotate through quick scan queries every 30 seconds
        query_index = int(current_time / 30) % len(self.quick_scan_queries)
        query = self.quick_scan_queries[query_index]
        
        try:
            url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
            response = requests.get(url, headers=self.headers, timeout=2)  # Very short timeout
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                # Process more pairs quickly
                for pair in pairs[:40]:
                    if pair.get('chainId') != 'solana':
                        continue
                    
                    token_data = self._parse_dexscreener_pair(pair)
                    if token_data and self._passes_quick_filter(token_data):
                        tokens.append(token_data)
                        
        except Exception as e:
            print(f"Quick scan failed for {query}: {str(e)[:30]}")
        
        return tokens
    
    def fetch_comprehensive_scan_tokens(self):
        """Comprehensive scan every 5 minutes"""
        tokens = []
        
        # Use many search queries for maximum discovery
        search_queries = SEARCH_QUERIES[:20]  # Use first 20 for speed
        
        for query in search_queries:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=3)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    for pair in pairs[:25]:  # Take more pairs
                        if pair.get('chainId') != 'solana':
                            continue
                        
                        token_data = self._parse_dexscreener_pair(pair)
                        if token_data and self._passes_volume_filter(token_data):
                            tokens.append(token_data)
                            
            except Exception as e:
                print(f"Comprehensive scan failed for {query}: {str(e)[:30]}")
                continue
        
        return tokens
    
    def fetch_trending_tokens(self):
        """Fetch by volume/activity sorting"""
        tokens = []
        
        try:
            # Try different trending approaches
            trending_queries = ["trending", "volume", "hot", "new"]
            
            for query in trending_queries[:2]:  # Limit for speed
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=2)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    # Sort by volume and take top performers
                    volume_sorted = sorted(
                        [p for p in pairs if p.get('chainId') == 'solana'], 
                        key=lambda x: float(x.get('volume', {}).get('h24', 0) or 0), 
                        reverse=True
                    )
                    
                    for pair in volume_sorted[:20]:
                        token_data = self._parse_dexscreener_pair(pair)
                        if token_data and self._passes_volume_filter(token_data):
                            tokens.append(token_data)
                            
        except Exception as e:
            print(f"Trending fetch failed: {str(e)[:30]}")
        
        return tokens
    
    def fetch_all_tokens(self):
        """Adaptive fetching strategy based on timing"""
        st.session_state.api_calls_count += 1
        current_time = time.time()
        
        all_tokens = []
        
        # Always do quick scan for immediate opportunities
        quick_tokens = self.fetch_quick_scan_tokens()
        all_tokens.extend(quick_tokens)
        
        # Comprehensive scan every 5 minutes
        if current_time - self.last_comprehensive_scan >= 300:  # 5 minutes
            self.last_comprehensive_scan = current_time
            
            comprehensive_tokens = self.fetch_comprehensive_scan_tokens()
            all_tokens.extend(comprehensive_tokens)
            
            trending_tokens = self.fetch_trending_tokens()
            all_tokens.extend(trending_tokens)
        
        # Remove duplicates efficiently
        unique_tokens = {}
        for token in all_tokens:
            mint = token.get('mint', '')
            if mint:
                # Take token with highest volume if duplicate
                if mint not in unique_tokens or token.get('volume_24h', 0) > unique_tokens[mint].get('volume_24h', 0):
                    unique_tokens[mint] = token
        
        # Score and filter with very permissive criteria
        quality_tokens = []
        for token in unique_tokens.values():
            if self.is_high_frequency_tradeable(token):
                score = self.calculate_speed_optimized_score(token)
                token['score'] = score
                
                # Very low score requirements for high frequency
                min_score = 25 if not st.session_state.turbo_mode else 15
                if score >= min_score:
                    quality_tokens.append(token)
        
        # Sort by score and recent activity
        quality_tokens.sort(key=lambda x: (
            x.get('score', 0) + 
            x.get('volume_24h', 0) / 50000 +  # Volume bonus
            x.get('price_change_5m', 0)  # Recent momentum bonus
        ), reverse=True)
        
        # Take many tokens for high frequency
        max_tokens = 100 if not st.session_state.turbo_mode else 150
        final_tokens = quality_tokens[:max_tokens]
        
        st.session_state.tokens_found = len(final_tokens)
        return final_tokens
    
    def _passes_quick_filter(self, token_data):
        """Ultra-permissive quick filter"""
        if not token_data or token_data['price_usd'] <= 0:
            return False
        
        market_cap = token_data.get('market_cap', 0)
        liquidity = token_data.get('liquidity', 0)
        
        # Very basic checks only
        if market_cap < 1000 or market_cap > 10000000:  # Very wide range
            return False
        
        if liquidity < 1000:  # Very low requirement
            return False
        
        return True
    
    def _passes_volume_filter(self, token_data):
        """Slightly more restrictive but still permissive"""
        if not token_data or token_data['price_usd'] <= 0:
            return False
        
        market_cap = token_data.get('market_cap', 0)
        liquidity = token_data.get('liquidity', 0)
        volume_24h = token_data.get('volume_24h', 0)
        
        if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
            return False
        
        if liquidity < MIN_LIQUIDITY:
            return False
        
        if volume_24h < 100:  # Very low volume requirement
            return False
        
        return True
    
    def is_high_frequency_tradeable(self, token):
        """Extremely permissive quality check for high-frequency trading"""
        market_cap = token.get('market_cap', 0)
        liquidity = token.get('liquidity', 0)
        volume = token.get('volume_24h', 0)
        price_change_1h = token.get('price_change_1h', 0)
        
        # Very wide market cap range
        if not (5000 <= market_cap <= 5000000):
            return False
        
        # Low liquidity requirement
        if liquidity < 5000:
            return False
        
        # Accept almost any volume activity
        if volume < 100:
            return False
        
        # Very permissive momentum - only reject extreme negatives
        if price_change_1h < -20:  # Only reject >20% drops in 1h
            return False
        
        # Basic activity check
        if token.get('txns_24h', 0) < 5:  # Very low transaction requirement
            return False
        
        return True
    
    def calculate_speed_optimized_score(self, token):
        """Fast scoring optimized for high-frequency discovery"""
        score = 0
        
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        market_cap = token.get('market_cap', 0)
        price_change_5m = token.get('price_change_5m', 0)
        price_change_1h = token.get('price_change_1h', 0)
        txns_24h = token.get('txns_24h', 0)
        
        # Heavy emphasis on recent activity and volume
        if volume > 200000:
            score += 30
        elif volume > 50000:
            score += 20
        elif volume > 10000:
            score += 15
        elif volume > 1000:
            score += 10
        elif volume > 100:
            score += 5
        
        # Recent momentum scoring (most important for high-frequency)
        if price_change_5m > 5:
            score += 25
        elif price_change_5m > 2:
            score += 20
        elif price_change_5m > 0.5:
            score += 15
        elif price_change_5m > 0:
            score += 10
        elif price_change_5m > -2:  # Small negative OK
            score += 5
        
        # Medium-term momentum
        if price_change_1h > 10:
            score += 20
        elif price_change_1h > 5:
            score += 15
        elif price_change_1h > 0:
            score += 10
        elif price_change_1h > -5:  # Small negative OK
            score += 5
        
        # Liquidity scoring
        if liquidity > 50000:
            score += 20
        elif liquidity > 20000:
            score += 15
        elif liquidity > 10000:
            score += 10
        elif liquidity > 5000:
            score += 5
        
        # Market cap scoring - prefer smaller caps for volatility
        if 10000 <= market_cap <= 200000:
            score += 15  # Sweet spot for micro-cap volatility
        elif 5000 <= market_cap <= 500000:
            score += 12
        elif market_cap <= 1000000:
            score += 8
        
        # Transaction activity
        if txns_24h > 100:
            score += 10
        elif txns_24h > 50:
            score += 8
        elif txns_24h > 10:
            score += 5
        
        # Volatility bonus - high-frequency trading benefits from movement
        if abs(price_change_1h) > 15:  # Any big movement
            score += 10
        elif abs(price_change_1h) > 8:
            score += 5
        
        # Recent activity bonus
        if price_change_5m > 0 and volume > 5000:
            score += 8
        
        return max(0, score)
    
    def _parse_dexscreener_pair(self, pair):
        """Fast parsing with minimal validation"""
        try:
            base_token = pair.get('baseToken', {})
            
            symbol = base_token.get('symbol', 'UNKNOWN').upper()
            
            # Minimal suspicious word filtering for speed
            if any(word in symbol for word in ['TEST', 'FAKE', 'SCAM']):
                return None
            
            token_data = {
                'mint': base_token.get('address', ''),
                'symbol': symbol,
                'name': base_token.get('name', 'Unknown'),
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
        except:
            return None
    
    def _extract_liquidity(self, pair):
        try:
            if 'liquidity' in pair:
                if isinstance(pair['liquidity'], dict):
                    return float(pair['liquidity'].get('usd', 0) or 0)
                else:
                    return float(pair['liquidity'] or 0)
        except:
            return 0
    
    def _extract_volume(self, pair):
        try:
            if 'volume' in pair:
                if isinstance(pair['volume'], dict):
                    return float(pair['volume'].get('h24', 0) or 0)
        except:
            return 0
    
    def _extract_price_change(self, pair, timeframe):
        try:
            if 'priceChange' in pair:
                if isinstance(pair['priceChange'], dict):
                    return float(pair['priceChange'].get(timeframe, 0) or 0)
        except:
            return 0
    
    def _extract_transactions(self, pair):
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
        """Fast price fetching with fallback"""
        try:
            mint = token.get('mint', '')
            if mint and len(mint) > 20:
                url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
                response = requests.get(url, headers=self.headers, timeout=1)  # Very fast timeout
                
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
        
        # Return last known price if API fails
        return token.get('price_usd', 0)

# Create alias
DataFetcher = HighFrequencyDataFetcher
