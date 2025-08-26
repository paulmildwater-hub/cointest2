"""
Multi-Marketplace Data Fetcher - Real API calls only, no simulation
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
from config import *

class MultiMarketplaceFetcher:
    def __init__(self):
        self.headers = API_HEADERS
        
    def fetch_dexscreener_tokens(self, network='solana', extended_search=True):
        """Enhanced DexScreener with multi-network support"""
        tokens = []
        
        search_queries = SEARCH_QUERIES if extended_search else SEARCH_QUERIES[:10]
        
        for query in search_queries:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    for pair in pairs[:30]:
                        chain_id = pair.get('chainId', '').lower()
                        if chain_id != network:
                            continue
                        
                        token_data = self._parse_dexscreener_pair(pair, network)
                        if token_data and self._passes_volume_filter(token_data):
                            tokens.append(token_data)
            except Exception as e:
                print(f"Error fetching {query} from {network}: {e}")
                continue
        
        return tokens
    
    def fetch_jupiter_aggregator_tokens(self):
        """Fetch tokens through Jupiter aggregator"""
        tokens = []
        
        try:
            url = "https://price.jup.ag/v4/price?ids=SOL"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                popular_tokens = [
                    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
                    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
                    'So11111111111111111111111111111111111111112',
                    'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
                    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'
                ]
                
                for token_address in popular_tokens:
                    try:
                        dex_data = self._get_token_from_dexscreener(token_address)
                        if dex_data:
                            dex_data['source'] = 'Jupiter'
                            tokens.append(dex_data)
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error fetching Jupiter tokens: {e}")
        
        return tokens
    
    def fetch_orca_tokens(self):
        """Fetch tokens from Orca DEX"""
        tokens = []
        
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=orca"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                for pair in pairs[:25]:
                    if (pair.get('chainId') == 'solana' and 
                        pair.get('dexId') == 'orca'):
                        
                        token_data = self._parse_dexscreener_pair(pair, 'solana')
                        if token_data:
                            token_data['source'] = 'Orca'
                            if self._passes_volume_filter(token_data):
                                tokens.append(token_data)
                                
        except Exception as e:
            print(f"Error fetching Orca tokens: {e}")
        
        return tokens
    
    def fetch_meteora_tokens(self):
        """Fetch tokens from Meteora DEX"""
        tokens = []
        
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=meteora"
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                for pair in pairs[:20]:
                    if (pair.get('chainId') == 'solana' and 
                        'meteora' in pair.get('dexId', '').lower()):
                        
                        token_data = self._parse_dexscreener_pair(pair, 'solana')
                        if token_data:
                            token_data['source'] = 'Meteora'
                            if self._passes_volume_filter(token_data):
                                tokens.append(token_data)
                                
        except Exception as e:
            print(f"Error fetching Meteora tokens: {e}")
        
        return tokens
    
    def fetch_base_network_tokens(self):
        """Fetch tokens from Base network"""
        tokens = []
        
        try:
            searches = ['base', 'uniswap']
            
            for query in searches:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    for pair in pairs[:15]:
                        if pair.get('chainId') == 'base':
                            token_data = self._parse_dexscreener_pair(pair, 'base')
                            if token_data:
                                token_data['source'] = 'Base Network'
                                if (token_data.get('liquidity', 0) >= 50000 and
                                    self._passes_volume_filter(token_data)):
                                    tokens.append(token_data)
                                    
        except Exception as e:
            print(f"Error fetching Base tokens: {e}")
        
        return tokens
    
    def fetch_arbitrum_tokens(self):
        """Fetch tokens from Arbitrum"""
        tokens = []
        
        try:
            searches = ['arbitrum', 'arb']
            
            for query in searches:
                url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
                response = requests.get(url, headers=self.headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    for pair in pairs[:15]:
                        if pair.get('chainId') == 'arbitrum':
                            token_data = self._parse_dexscreener_pair(pair, 'arbitrum')
                            if token_data:
                                token_data['source'] = 'Arbitrum'
                                if (token_data.get('liquidity', 0) >= 25000 and
                                    self._passes_volume_filter(token_data)):
                                    tokens.append(token_data)
                                    
        except Exception as e:
            print(f"Error fetching Arbitrum tokens: {e}")
        
        return tokens
    
    def fetch_all_tokens(self):
        """Fetch from all available marketplaces"""
        st.session_state.api_calls_count += 1
        
        all_tokens = []
        
        # Primary: Solana markets
        solana_tokens = self.fetch_dexscreener_tokens('solana', extended_search=True)
        all_tokens.extend(solana_tokens)
        
        # Additional Solana DEXs
        orca_tokens = self.fetch_orca_tokens()
        all_tokens.extend(orca_tokens)
        
        meteora_tokens = self.fetch_meteora_tokens()
        all_tokens.extend(meteora_tokens)
        
        # Other networks
        base_tokens = self.fetch_base_network_tokens()
        all_tokens.extend(base_tokens)
        
        arbitrum_tokens = self.fetch_arbitrum_tokens()
        all_tokens.extend(arbitrum_tokens)
        
        # Remove duplicates
        unique_tokens = {}
        for token in all_tokens:
            mint = token.get('mint', '') + token.get('network', 'solana')
            if mint and mint not in st.session_state.seen_tokens:
                if mint not in unique_tokens or token.get('volume_24h', 0) > unique_tokens[mint].get('volume_24h', 0):
                    unique_tokens[mint] = token
        
        # Score and filter
        quality_tokens = []
        for token in unique_tokens.values():
            if self.is_tradeable_quality_token(token):
                score = self.calculate_volume_optimized_score(token)
                token['score'] = score
                
                min_score = 50 if not st.session_state.turbo_mode else 35
                if score >= min_score:
                    quality_tokens.append(token)
        
        # Sort by score and volume
        quality_tokens.sort(key=lambda x: (x.get('score', 0) + x.get('volume_24h', 0) / 10000), reverse=True)
        
        max_tokens = 60 if not st.session_state.turbo_mode else 90
        final_tokens = quality_tokens[:max_tokens]
        
        st.session_state.tokens_found = len(final_tokens)
        return final_tokens
    
    def _get_token_from_dexscreener(self, mint_address):
        """Get specific token data"""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
            response = requests.get(url, headers=self.headers, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])
                
                if pairs:
                    best_pair = max(pairs, key=lambda p: float(p.get('liquidity', {}).get('usd', 0) or 0))
                    return self._parse_dexscreener_pair(best_pair, 'solana')
        except:
            pass
        return None
    
    def _parse_dexscreener_pair(self, pair, network='solana'):
        """Parse pair data"""
        try:
            base_token = pair.get('baseToken', {})
            
            symbol = base_token.get('symbol', 'UNKNOWN').upper()
            name = base_token.get('name', 'Unknown')
            
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
                'network': network,
                'pair_created_at': pair.get('pairCreatedAt', 0)
            }
            
            return token_data
        except Exception as e:
            return None
    
    def _passes_volume_filter(self, token_data):
        """Filter tokens by volume criteria"""
        if not token_data or token_data['price_usd'] <= 0:
            return False
        
        market_cap = token_data.get('market_cap', 0)
        liquidity = token_data.get('liquidity', 0)
        volume_24h = token_data.get('volume_24h', 0)
        network = token_data.get('network', 'solana')
        
        # Network-specific requirements
        if network == 'solana':
            min_liquidity = MIN_LIQUIDITY
            min_volume = 500
        else:
            min_liquidity = MIN_LIQUIDITY * 2
            min_volume = 2000
        
        if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
            return False
        
        if liquidity < min_liquidity:
            return False
        
        if volume_24h < min_volume:
            return False
        
        return True
    
    def is_tradeable_quality_token(self, token):
        """Quality assessment for trading"""
        market_cap = token.get('market_cap', 0)
        liquidity = token.get('liquidity', 0)
        volume = token.get('volume_24h', 0)
        price_change_1h = token.get('price_change_1h', 0)
        network = token.get('network', 'solana')
        
        if network == 'solana':
            min_liquidity = 15000
        else:
            min_liquidity = 25000
        
        if not (15000 <= market_cap <= 2000000):
            return False
        
        if liquidity < min_liquidity:
            return False
        
        volume_to_mcap = volume / market_cap if market_cap > 0 else 0
        if volume_to_mcap < 3.0:
            return False
        
        if price_change_1h < -15:
            return False
        
        if token.get('txns_24h', 0) < 20:
            return False
        
        return True
    
    def calculate_volume_optimized_score(self, token):
        """Calculate token score"""
        score = 0
        
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        market_cap = token.get('market_cap', 0)
        price_change_1h = token.get('price_change_1h', 0)
        price_change_5m = token.get('price_change_5m', 0)
        txns_24h = token.get('txns_24h', 0)
        
        # Volume scoring
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
        
        # Momentum scoring
        if price_change_1h > 10:
            score += 20
        elif price_change_1h > 5:
            score += 15
        elif price_change_1h > 0:
            score += 10
        elif price_change_1h > -5:
            score += 5
        
        if price_change_5m > 2:
            score += 15
        elif price_change_5m > 0:
            score += 10
        
        # Liquidity scoring
        if liquidity > 100000:
            score += 25
        elif liquidity > 50000:
            score += 20
        elif liquidity > 25000:
            score += 15
        elif liquidity > 15000:
            score += 10
        
        # Market cap scoring
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
        
        # Consistency bonus
        if price_change_5m > 0 and price_change_1h > 0:
            score += 10
        
        return max(0, score)
    
    def fetch_all_tokens(self):
        """Fetch from all available marketplaces"""
        st.session_state.api_calls_count += 1
        
        all_tokens = []
        
        # Solana markets
        solana_tokens = self.fetch_dexscreener_tokens('solana', extended_search=True)
        all_tokens.extend(solana_tokens)
        
        orca_tokens = self.fetch_orca_tokens()
        all_tokens.extend(orca_tokens)
        
        meteora_tokens = self.fetch_meteora_tokens()
        all_tokens.extend(meteora_tokens)
        
        jupiter_tokens = self.fetch_jupiter_aggregator_tokens()
        all_tokens.extend(jupiter_tokens)
        
        # Other networks (will be skipped if APIs unreachable)
        try:
            base_tokens = self.fetch_dexscreener_tokens('base', extended_search=False)
            all_tokens.extend(base_tokens)
        except:
            pass
        
        try:
            arbitrum_tokens = self.fetch_dexscreener_tokens('arbitrum', extended_search=False)
            all_tokens.extend(arbitrum_tokens)
        except:
            pass
        
        # Remove duplicates
        unique_tokens = {}
        for token in all_tokens:
            mint = token.get('mint', '') + token.get('network', 'solana')
            if mint and mint not in st.session_state.seen_tokens:
                if mint not in unique_tokens or token.get('volume_24h', 0) > unique_tokens[mint].get('volume_24h', 0):
                    unique_tokens[mint] = token
        
        # Score and filter
        quality_tokens = []
        for token in unique_tokens.values():
            if self.is_tradeable_quality_token(token):
                score = self.calculate_volume_optimized_score(token)
                token['score'] = score
                
                min_score = 50 if not st.session_state.turbo_mode else 35
                if score >= min_score:
                    quality_tokens.append(token)
        
        quality_tokens.sort(key=lambda x: (x.get('score', 0) + x.get('volume_24h', 0) / 10000), reverse=True)
        
        max_tokens = 60 if not st.session_state.turbo_mode else 90
        final_tokens = quality_tokens[:max_tokens]
        
        st.session_state.tokens_found = len(final_tokens)
        return final_tokens
    
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
        """Get current price - real API only"""
        try:
            mint = token.get('mint', '')
            if mint and len(mint) > 20:
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
        
        # Return last known price if API fails
        return token.get('price_usd', 0)

# Create alias
DataFetcher = MultiMarketplaceFetcher
