"""
Analytics module for trade analysis and data export
"""

import pandas as pd
import streamlit as st
from io import StringIO
from datetime import datetime

class Analytics:
    def export_trades_to_csv(self):
        """Export all trade data to CSV for analysis"""
        if not st.session_state.trades:
            return None
        
        df = pd.DataFrame(st.session_state.trades)
        
        # Add calculated fields
        df['profit_margin'] = df['pnl'] / (df['position_size'] + 0.01) * 100
        df['score_per_dollar'] = df['score'] / (df['position_size'] + 0.01)
        df['volume_to_mcap_ratio'] = df['volume_24h'] / (df['market_cap'] + 1)
        df['liquidity_ratio'] = df['liquidity'] / (df['market_cap'] + 1)
        df['momentum_score'] = (
            df['price_change_5m_at_entry'] + 
            df['price_change_1h_at_entry'] + 
            (df['price_change_24h_at_entry'] / 4)
        )
        
        # Categorize trades
        df['trade_category'] = df['pnl'].apply(
            lambda x: 'Big Win' if x > 5 else 'Win' if x > 0 else 'Loss' if x > -3 else 'Big Loss'
        )
        df['hold_category'] = df['duration_minutes'].apply(
            lambda x: 'Quick' if x < 5 else 'Medium' if x < 15 else 'Long'
        )
        df['score_category'] = df['score'].apply(
            lambda x: 'High' if x >= 60 else 'Medium' if x >= 40 else 'Low'
        )
        
        return df
    
    def generate_analysis_report(self):
        """Generate detailed analysis of trading patterns"""
        if not st.session_state.trades or len(st.session_state.trades) < 10:
            return "Need at least 10 trades for meaningful analysis"
        
        df = self.export_trades_to_csv()
        analysis = []
        
        analysis.append("📊 TRADING PATTERN ANALYSIS\n")
        analysis.append(f"Total Trades: {len(df)}\n")
        analysis.append(f"Time Period: {df['timestamp'].min()} to {df['timestamp'].max()}\n\n")
        
        # Profitability by Score
        analysis.append("🎯 Profitability by Token Score:\n")
        score_analysis = df.groupby('score_category')['pnl'].agg(['mean', 'sum', 'count'])
        analysis.append(score_analysis.to_string() + "\n\n")
        
        # Winning trade characteristics
        analysis.append("✅ Characteristics of Winning Trades:\n")
        winners = df[df['pnl'] > 0]
        if len(winners) > 0:
            analysis.append(f"- Avg Score: {winners['score'].mean():.1f}\n")
            analysis.append(f"- Avg Market Cap: ${winners['market_cap'].mean():,.0f}\n")
            analysis.append(f"- Avg Liquidity: ${winners['liquidity'].mean():,.0f}\n")
            analysis.append(f"- Avg Volume: ${winners['volume_24h'].mean():,.0f}\n")
            analysis.append(f"- Avg 1h Price Change: {winners['price_change_1h_at_entry'].mean():.1f}%\n\n")
        
        # Losing trade characteristics
        analysis.append("❌ Characteristics of Losing Trades:\n")
        losers = df[df['pnl'] < 0]
        if len(losers) > 0:
            analysis.append(f"- Avg Score: {losers['score'].mean():.1f}\n")
            analysis.append(f"- Avg Market Cap: ${losers['market_cap'].mean():,.0f}\n")
            analysis.append(f"- Avg Liquidity: ${losers['liquidity'].mean():,.0f}\n")
            analysis.append(f"- Avg Volume: ${losers['volume_24h'].mean():,.0f}\n")
            analysis.append(f"- Avg 1h Price Change: {losers['price_change_1h_at_entry'].mean():.1f}%\n\n")
        
        # Exit reason analysis
        analysis.append("🚪 Exit Reason Performance:\n")
        exit_analysis = df.groupby('exit_reason')['pnl'].agg(['mean', 'sum', 'count'])
        analysis.append(exit_analysis.to_string() + "\n\n")
        
        # Time-based patterns
        analysis.append("⏰ Performance by Hour:\n")
        hourly_analysis = df.groupby('hour_of_day')['pnl'].agg(['mean', 'sum', 'count'])
        best_hours = hourly_analysis.nlargest(3, 'mean')
        analysis.append(f"Best Hours: {best_hours.index.tolist()}\n\n")
        
        # Key insights
        analysis.append("💡 KEY INSIGHTS:\n")
        
        # Find optimal score range
        score_ranges = [(0, 30), (30, 50), (50, 70), (70, 100)]
        best_score_range = None
        best_score_profit = -999
        
        for low, high in score_ranges:
            range_df = df[(df['score'] >= low) & (df['score'] < high)]
            if len(range_df) > 0:
                avg_profit = range_df['pnl'].mean()
                if avg_profit > best_score_profit:
                    best_score_profit = avg_profit
                    best_score_range = (low, high)
        
        if best_score_range:
            analysis.append(f"- Optimal Score Range: {best_score_range[0]}-{best_score_range[1]} (Avg P&L: ${best_score_profit:.2f})\n")
        
        # Find optimal market cap range
        if len(df) > 0:
            mcap_ranges = [(0, 50000), (50000, 200000), (200000, 1000000), (1000000, 10000000)]
            best_mcap_range = None
            best_mcap_profit = -999
            
            for low, high in mcap_ranges:
                range_df = df[(df['market_cap'] >= low) & (df['market_cap'] < high)]
                if len(range_df) > 0:
                    avg_profit = range_df['pnl'].mean()
                    if avg_profit > best_mcap_profit:
                        best_mcap_profit = avg_profit
                        best_mcap_range = (low, high)
            
            if best_mcap_range:
                analysis.append(f"- Optimal Market Cap: ${best_mcap_range[0]:,}-${best_mcap_range[1]:,} (Avg P&L: ${best_mcap_profit:.2f})\n")
        
        # Correlations
        if len(df) > 5:
            volume_correlation = df['volume_24h'].corr(df['pnl'])
            analysis.append(f"- Volume-Profit Correlation: {volume_correlation:.3f}\n")
            
            liquidity_correlation = df['liquidity'].corr(df['pnl'])
            analysis.append(f"- Liquidity-Profit Correlation: {liquidity_correlation:.3f}\n")
        
        return ''.join(analysis)
    
    def get_performance_metrics(self):
        """Calculate key performance metrics"""
        if not st.session_state.trades:
            return None
        
        df = pd.DataFrame(st.session_state.trades)
        
        metrics = {
            'total_trades': len(df),
            'winning_trades': len(df[df['pnl'] > 0]),
            'losing_trades': len(df[df['pnl'] < 0]),
            'win_rate': len(df[df['pnl'] > 0]) / len(df) * 100 if len(df) > 0 else 0,
            'avg_win': df[df['pnl'] > 0]['pnl'].mean() if len(df[df['pnl'] > 0]) > 0 else 0,
            'avg_loss': df[df['pnl'] < 0]['pnl'].mean() if len(df[df['pnl'] < 0]) > 0 else 0,
            'total_pnl': df['pnl'].sum(),
            'avg_pnl': df['pnl'].mean(),
            'best_trade': df['pnl'].max(),
            'worst_trade': df['pnl'].min(),
            'avg_duration': df['duration_seconds'].mean() if 'duration_seconds' in df else 0
        }
        
        # Profit factor
        if metrics['avg_loss'] != 0:
            metrics['profit_factor'] = abs(metrics['avg_win'] / metrics['avg_loss'])
        else:
            metrics['profit_factor'] = 0
        
        return metrics
    
    def get_exit_reason_breakdown(self):
        """Get breakdown by exit reason"""
        if not st.session_state.trades:
            return {}
        
        df = pd.DataFrame(st.session_state.trades)
        return df['exit_reason'].value_counts().to_dict()
    
    def get_source_performance(self):
        """Get performance by data source"""
        if not st.session_state.trades:
            return {}
        
        df = pd.DataFrame(st.session_state.trades)
        source_perf = {}
        
        for source in df['source'].unique():
            source_df = df[df['source'] == source]
            source_perf[source] = {
                'count': len(source_df),
                'total_pnl': source_df['pnl'].sum(),
                'avg_pnl': source_df['pnl'].mean()
            }
        
        return source_perf