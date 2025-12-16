# ============================================================================
# NYZTrade Professional GEX/DEX Dashboard
# Real-time Options Greeks Analysis with Time Machine
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.stats import norm
from datetime import datetime, timedelta
import requests
import time
import json
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="NYZTrade GEX/DEX Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --bg-card-hover: #232f42;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-yellow: #f59e0b;
        --accent-cyan: #06b6d4;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #2d3748;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, var(--bg-primary) 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .sub-title {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card.positive { border-left: 4px solid var(--accent-green); }
    .metric-card.negative { border-left: 4px solid var(--accent-red); }
    .metric-card.neutral { border-left: 4px solid var(--accent-yellow); }
    
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    .metric-value.neutral { color: var(--accent-yellow); }
    
    .metric-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        margin-top: 8px;
        color: var(--text-secondary);
    }
    
    .signal-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .signal-badge.bullish {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .signal-badge.bearish {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .signal-badge.volatile {
        background: rgba(245, 158, 11, 0.15);
        color: var(--accent-yellow);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 20px;
        animation: pulse-live 2s infinite;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-red);
        border-radius: 50%;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    @keyframes pulse-live {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
    }
    
    .countdown-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
    }
    
    .countdown-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-cyan);
    }
    
    .countdown-label {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .strategy-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    
    .strategy-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--accent-cyan);
        margin-bottom: 12px;
    }
    
    .strategy-detail {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .gamma-flip-zone {
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
        border: 2px dashed var(--accent-yellow);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .flip-label {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--accent-yellow);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stSlider > div > div > div > div {
        background: var(--accent-purple);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-card);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-blue);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class DhanConfig:
    client_id: str = "1100480354"
    access_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY1OTYzMzk2LCJhcHBfaWQiOiJjOTNkM2UwOSIsImlhdCI6MTc2NTg3Njk5NiwidG9rZW5Db25zdW1lclR5cGUiOiJBUFAiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDQ4MDM1NCJ9.K93qVFYO2XrMJ-Jn4rY2autNZ444tc-AzYtaxVUsjRfsjW7NhfQom58vzuSMVI6nRMMB_sa7fCtWE5JIvk75yw"
    expiry_time: str = "2026-12-17T14:53:17"

DHAN_SECURITY_IDS = {
    "NIFTY": 13, "BANKNIFTY": 25, "FINNIFTY": 27, "MIDCPNIFTY": 442, "SENSEX": 51
}

EXCHANGE_SEGMENTS = {
    "NIFTY": "IDX_I", "BANKNIFTY": "IDX_I", "FINNIFTY": "IDX_I", 
    "MIDCPNIFTY": "IDX_I", "SENSEX": "BSE_IDX"
}

SYMBOL_CONFIG = {
    "NIFTY": {"contract_size": 25, "strike_interval": 50, "lot_size": 25},
    "BANKNIFTY": {"contract_size": 15, "strike_interval": 100, "lot_size": 15},
    "FINNIFTY": {"contract_size": 40, "strike_interval": 50, "lot_size": 40},
    "MIDCPNIFTY": {"contract_size": 75, "strike_interval": 25, "lot_size": 75},
}

# ============================================================================
# BLACK-SCHOLES CALCULATOR
# ============================================================================

class BlackScholesCalculator:
    @staticmethod
    def calculate_d1(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0:
            return 0
        return (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def calculate_d2(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0:
            return 0
        d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
        return d1 - sigma * np.sqrt(T)
    
    @staticmethod
    def calculate_gamma(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            n_prime_d1 = norm.pdf(d1)
            return n_prime_d1 / (S * sigma * np.sqrt(T))
        except:
            return 0
    
    @staticmethod
    def calculate_call_delta(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1)
        except:
            return 0
    
    @staticmethod
    def calculate_put_delta(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1) - 1
        except:
            return 0
    
    @staticmethod
    def calculate_vega(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return S * norm.pdf(d1) * np.sqrt(T) / 100
        except:
            return 0
    
    @staticmethod
    def calculate_theta_call(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            term1 = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
            return (term1 + term2) / 365
        except:
            return 0
    
    @staticmethod
    def calculate_vanna(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            vanna = -norm.pdf(d1) * d2 / sigma
            return vanna
        except:
            return 0
    
    @staticmethod
    def calculate_charm(S, K, T, r, sigma):
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            charm = -norm.pdf(d1) * (2 * r * T - d2 * sigma * np.sqrt(T)) / (2 * T * sigma * np.sqrt(T))
            return charm / 365
        except:
            return 0

# ============================================================================
# DHAN API DATA FETCHER
# ============================================================================

class DhanAPIFetcher:
    def __init__(self, config: DhanConfig):
        self.config = config
        self.headers = {
            'access-token': config.access_token,
            'client-id': config.client_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.base_url = "https://api.dhan.co/v2"
        self.bs_calc = BlackScholesCalculator()
        self.risk_free_rate = 0.07
    
    def get_expiry_list(self, symbol: str) -> List[str]:
        try:
            security_id = DHAN_SECURITY_IDS.get(symbol, 13)
            segment = EXCHANGE_SEGMENTS.get(symbol, "IDX_I")
            payload = {"UnderlyingScrip": security_id, "UnderlyingSeg": segment}
            response = requests.post(
                f"{self.base_url}/optionchain/expirylist",
                headers=self.headers, json=payload, timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('data', [])
            return []
        except Exception as e:
            return []
    
    def fetch_option_chain(self, symbol: str, expiry_date: str = None) -> Optional[Dict]:
        try:
            security_id = DHAN_SECURITY_IDS.get(symbol, 13)
            segment = EXCHANGE_SEGMENTS.get(symbol, "IDX_I")
            payload = {"UnderlyingScrip": security_id, "UnderlyingSeg": segment}
            if expiry_date:
                payload["Expiry"] = expiry_date
            response = requests.post(
                f"{self.base_url}/optionchain",
                headers=self.headers, json=payload, timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return data['data']
            return None
        except:
            return None
    
    def calculate_futures_price(self, spot_price: float, days_to_expiry: int) -> float:
        T = days_to_expiry / 365.0
        return spot_price * np.exp(self.risk_free_rate * T)
    
    def process_option_chain(self, symbol: str, expiry_index: int = 0, strikes_range: int = 12):
        expiry_list = self.get_expiry_list(symbol)
        if not expiry_list:
            return None, None
        
        selected_expiry = expiry_list[min(expiry_index, len(expiry_list) - 1)]
        
        try:
            expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d")
            days_to_expiry = max((expiry_date - datetime.now()).days, 1)
            time_to_expiry = days_to_expiry / 365
        except:
            days_to_expiry = 7
            time_to_expiry = 7 / 365
        
        oc_data = self.fetch_option_chain(symbol, selected_expiry)
        if not oc_data:
            return None, None
        
        spot_price = oc_data.get('last_price', 0)
        option_chain = oc_data.get('oc', {})
        futures_price = self.calculate_futures_price(spot_price, days_to_expiry)
        
        config = SYMBOL_CONFIG.get(symbol, SYMBOL_CONFIG["NIFTY"])
        contract_size = config["contract_size"]
        strike_interval = config["strike_interval"]
        
        all_strikes = []
        atm_strike = None
        min_atm_diff = float('inf')
        atm_call_premium = 0
        atm_put_premium = 0
        
        for strike_str, strike_data in option_chain.items():
            try:
                strike = float(strike_str)
            except:
                continue
            
            if strike == 0 or abs(strike - futures_price) / strike_interval > strikes_range:
                continue
            
            ce = strike_data.get('ce', {})
            pe = strike_data.get('pe', {})
            
            call_oi = ce.get('oi', 0) or 0
            put_oi = pe.get('oi', 0) or 0
            call_oi_change = (ce.get('oi', 0) or 0) - (ce.get('previous_oi', 0) or 0)
            put_oi_change = (pe.get('oi', 0) or 0) - (pe.get('previous_oi', 0) or 0)
            call_volume = ce.get('volume', 0) or 0
            put_volume = pe.get('volume', 0) or 0
            call_iv = ce.get('implied_volatility', 0) or 0
            put_iv = pe.get('implied_volatility', 0) or 0
            call_ltp = ce.get('last_price', 0) or 0
            put_ltp = pe.get('last_price', 0) or 0
            
            strike_diff = abs(strike - futures_price)
            if strike_diff < min_atm_diff:
                min_atm_diff = strike_diff
                atm_strike = strike
                atm_call_premium = call_ltp
                atm_put_premium = put_ltp
            
            call_iv_dec = call_iv / 100 if call_iv > 1 else (call_iv if call_iv > 0 else 0.15)
            put_iv_dec = put_iv / 100 if put_iv > 1 else (put_iv if put_iv > 0 else 0.15)
            
            call_gamma = self.bs_calc.calculate_gamma(futures_price, strike, time_to_expiry, self.risk_free_rate, call_iv_dec)
            put_gamma = self.bs_calc.calculate_gamma(futures_price, strike, time_to_expiry, self.risk_free_rate, put_iv_dec)
            call_delta = self.bs_calc.calculate_call_delta(futures_price, strike, time_to_expiry, self.risk_free_rate, call_iv_dec)
            put_delta = self.bs_calc.calculate_put_delta(futures_price, strike, time_to_expiry, self.risk_free_rate, put_iv_dec)
            call_vanna = self.bs_calc.calculate_vanna(futures_price, strike, time_to_expiry, self.risk_free_rate, call_iv_dec)
            put_vanna = self.bs_calc.calculate_vanna(futures_price, strike, time_to_expiry, self.risk_free_rate, put_iv_dec)
            call_charm = self.bs_calc.calculate_charm(futures_price, strike, time_to_expiry, self.risk_free_rate, call_iv_dec)
            put_charm = self.bs_calc.calculate_charm(futures_price, strike, time_to_expiry, self.risk_free_rate, put_iv_dec)
            
            call_gex = (call_oi * call_gamma * futures_price**2 * contract_size) / 1e9
            put_gex = -(put_oi * put_gamma * futures_price**2 * contract_size) / 1e9
            call_dex = (call_oi * call_delta * futures_price * contract_size) / 1e9
            put_dex = (put_oi * put_delta * futures_price * contract_size) / 1e9
            call_vanna_exp = (call_oi * call_vanna * futures_price * contract_size) / 1e9
            put_vanna_exp = (put_oi * put_vanna * futures_price * contract_size) / 1e9
            call_charm_exp = (call_oi * call_charm * futures_price * contract_size) / 1e9
            put_charm_exp = (put_oi * put_charm * futures_price * contract_size) / 1e9
            call_flow_gex = (call_oi_change * call_gamma * futures_price**2 * contract_size) / 1e9
            put_flow_gex = -(put_oi_change * put_gamma * futures_price**2 * contract_size) / 1e9
            call_flow_dex = (call_oi_change * call_delta * futures_price * contract_size) / 1e9
            put_flow_dex = (put_oi_change * put_delta * futures_price * contract_size) / 1e9
            
            all_strikes.append({
                'Strike': strike, 'Call_OI': call_oi, 'Put_OI': put_oi,
                'Call_OI_Change': call_oi_change, 'Put_OI_Change': put_oi_change,
                'Call_Volume': call_volume, 'Put_Volume': put_volume,
                'Total_Volume': call_volume + put_volume,
                'Call_IV': call_iv, 'Put_IV': put_iv,
                'Call_LTP': call_ltp, 'Put_LTP': put_ltp,
                'Call_Delta': call_delta, 'Put_Delta': put_delta,
                'Call_Gamma': call_gamma, 'Put_Gamma': put_gamma,
                'Call_Vanna': call_vanna, 'Put_Vanna': put_vanna,
                'Call_Charm': call_charm, 'Put_Charm': put_charm,
                'Call_GEX': call_gex, 'Put_GEX': put_gex, 'Net_GEX': call_gex + put_gex,
                'Call_DEX': call_dex, 'Put_DEX': put_dex, 'Net_DEX': call_dex + put_dex,
                'Call_Vanna_Exp': call_vanna_exp, 'Put_Vanna_Exp': put_vanna_exp,
                'Net_Vanna': call_vanna_exp + put_vanna_exp,
                'Call_Charm_Exp': call_charm_exp, 'Put_Charm_Exp': put_charm_exp,
                'Net_Charm': call_charm_exp + put_charm_exp,
                'Call_Flow_GEX': call_flow_gex, 'Put_Flow_GEX': put_flow_gex,
                'Net_Flow_GEX': call_flow_gex + put_flow_gex,
                'Call_Flow_DEX': call_flow_dex, 'Put_Flow_DEX': put_flow_dex,
                'Net_Flow_DEX': call_flow_dex + put_flow_dex,
            })
        
        if not all_strikes:
            return None, None
        
        df = pd.DataFrame(all_strikes).sort_values('Strike').reset_index(drop=True)
        max_gex = df['Net_GEX'].abs().max()
        df['Hedging_Pressure'] = (df['Net_GEX'] / max_gex * 100) if max_gex > 0 else 0
        
        meta = {
            'symbol': symbol, 'spot_price': spot_price, 'futures_price': futures_price,
            'expiry': selected_expiry, 'days_to_expiry': days_to_expiry,
            'atm_strike': atm_strike, 'atm_call_premium': atm_call_premium,
            'atm_put_premium': atm_put_premium, 'atm_straddle': atm_call_premium + atm_put_premium,
            'expiry_list': expiry_list, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return df, meta

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_flow_metrics(df: pd.DataFrame, futures_price: float) -> Dict:
    df_unique = df.drop_duplicates(subset=['Strike']).sort_values('Strike').reset_index(drop=True)
    
    positive_gex_df = df_unique[df_unique['Net_GEX'] > 0].copy()
    positive_gex_df['Distance'] = abs(positive_gex_df['Strike'] - futures_price)
    positive_gex_df = positive_gex_df.nsmallest(5, 'Distance')
    
    negative_gex_df = df_unique[df_unique['Net_GEX'] < 0].copy()
    negative_gex_df['Distance'] = abs(negative_gex_df['Strike'] - futures_price)
    negative_gex_df = negative_gex_df.nsmallest(5, 'Distance')
    
    gex_near_positive = positive_gex_df['Net_GEX'].sum() if len(positive_gex_df) > 0 else 0
    gex_near_negative = negative_gex_df['Net_GEX'].sum() if len(negative_gex_df) > 0 else 0
    gex_near_total = gex_near_positive + gex_near_negative
    gex_total_all = df_unique['Net_GEX'].sum()
    
    above_futures = df_unique[df_unique['Strike'] > futures_price].head(5)
    below_futures = df_unique[df_unique['Strike'] < futures_price].tail(5)
    
    dex_near_above = above_futures['Net_DEX'].sum() if len(above_futures) > 0 else 0
    dex_near_below = below_futures['Net_DEX'].sum() if len(below_futures) > 0 else 0
    dex_near_total = dex_near_above + dex_near_below
    dex_total_all = df_unique['Net_DEX'].sum()
    
    vanna_total = df_unique['Net_Vanna'].sum()
    charm_total = df_unique['Net_Charm'].sum()
    flow_gex_total = df_unique['Net_Flow_GEX'].sum()
    flow_dex_total = df_unique['Net_Flow_DEX'].sum()
    
    def get_gex_bias(v):
        if v > 50: return "🟢 STRONG SUPPRESSION", "green", "Bullish - Low Vol Expected"
        elif v > 0: return "🟢 SUPPRESSION", "lightgreen", "Mild Bullish"
        elif v < -50: return "🔴 HIGH AMPLIFICATION", "red", "High Volatility Expected"
        elif v < 0: return "🔴 AMPLIFICATION", "lightcoral", "Volatile"
        return "⚖️ NEUTRAL", "orange", "Balanced"
    
    def get_dex_bias(v):
        if v > 50: return "🟢 BULLISH", "green", "Strong Upward Pressure"
        elif v < -50: return "🔴 BEARISH", "red", "Strong Downward Pressure"
        elif v > 0: return "🟢 Mild Bullish", "lightgreen", "Slight Upward Bias"
        elif v < 0: return "🔴 Mild Bearish", "lightcoral", "Slight Downward Bias"
        return "⚖️ NEUTRAL", "orange", "No Clear Direction"
    
    gex_bias, gex_color, gex_desc = get_gex_bias(gex_near_total)
    dex_bias, dex_color, dex_desc = get_dex_bias(dex_near_total)
    combined_signal = (gex_near_total + dex_near_total) / 2
    combined_bias, combined_color, combined_desc = get_gex_bias(combined_signal)
    
    return {
        'gex_near_positive': gex_near_positive, 'gex_near_negative': gex_near_negative,
        'gex_near_total': gex_near_total, 'gex_total': gex_total_all,
        'gex_bias': gex_bias, 'gex_color': gex_color, 'gex_desc': gex_desc,
        'dex_near_above': dex_near_above, 'dex_near_below': dex_near_below,
        'dex_near_total': dex_near_total, 'dex_total': dex_total_all,
        'dex_bias': dex_bias, 'dex_color': dex_color, 'dex_desc': dex_desc,
        'vanna_total': vanna_total, 'charm_total': charm_total,
        'flow_gex_total': flow_gex_total, 'flow_dex_total': flow_dex_total,
        'combined_signal': combined_signal, 'combined_bias': combined_bias,
        'combined_color': combined_color, 'combined_desc': combined_desc,
    }

def detect_gamma_flip_zones(df: pd.DataFrame) -> List[Dict]:
    gamma_flip_zones = []
    df_sorted = df.sort_values('Strike').reset_index(drop=True)
    
    for i in range(len(df_sorted) - 1):
        current_gex = df_sorted.iloc[i]['Net_GEX']
        next_gex = df_sorted.iloc[i + 1]['Net_GEX']
        
        if (current_gex > 0 and next_gex < 0) or (current_gex < 0 and next_gex > 0):
            lower = df_sorted.iloc[i]['Strike']
            upper = df_sorted.iloc[i + 1]['Strike']
            weight = abs(current_gex) / (abs(current_gex) + abs(next_gex)) if (abs(current_gex) + abs(next_gex)) > 0 else 0.5
            flip_strike = lower + (upper - lower) * weight
            
            gamma_flip_zones.append({
                'flip_strike': flip_strike, 'lower_strike': lower, 'upper_strike': upper,
                'flip_type': "Positive → Negative" if current_gex > 0 else "Negative → Positive",
                'lower_gex': current_gex, 'upper_gex': next_gex,
                'impact': "Resistance" if current_gex > 0 else "Support"
            })
    
    return gamma_flip_zones

def calculate_key_levels(df: pd.DataFrame, futures_price: float) -> Dict:
    df_sorted = df.sort_values('Strike').reset_index(drop=True)
    max_pain_strike = df_sorted.loc[df_sorted['Call_OI'].idxmax(), 'Strike']
    highest_call_oi_strike = df_sorted.loc[df_sorted['Call_OI'].idxmax(), 'Strike']
    highest_put_oi_strike = df_sorted.loc[df_sorted['Put_OI'].idxmax(), 'Strike']
    max_positive_gex_strike = df_sorted.loc[df_sorted['Net_GEX'].idxmax(), 'Strike']
    max_negative_gex_strike = df_sorted.loc[df_sorted['Net_GEX'].idxmin(), 'Strike']
    
    total_put_oi = df_sorted['Put_OI'].sum()
    total_call_oi = df_sorted['Call_OI'].sum()
    pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1
    
    return {
        'max_pain': max_pain_strike, 'highest_call_oi': highest_call_oi_strike,
        'highest_put_oi': highest_put_oi_strike, 'max_positive_gex': max_positive_gex_strike,
        'max_negative_gex': max_negative_gex_strike, 'pcr': pcr,
        'total_call_oi': total_call_oi, 'total_put_oi': total_put_oi,
    }

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_gex_chart(df: pd.DataFrame, futures_price: float, gamma_flips: List[Dict]) -> go.Figure:
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Net_GEX']]
    fig = go.Figure()
    
    max_gex = df['Net_GEX'].abs().max()
    max_vol = df['Total_Volume'].max()
    if max_vol > 0:
        scaled_vol = df['Total_Volume'] * (max_gex * 0.3) / max_vol
        fig.add_trace(go.Scatter(
            y=df['Strike'], x=scaled_vol, fill='tozerox',
            fillcolor='rgba(59, 130, 246, 0.2)',
            line=dict(color='#3b82f6', width=1), name='Volume',
            hovertemplate='Strike: %{y}<br>Volume: %{customdata:,.0f}<extra></extra>',
            customdata=df['Total_Volume']
        ))
    
    fig.add_trace(go.Bar(
        y=df['Strike'], x=df['Net_GEX'], orientation='h',
        marker_color=colors, name='Net GEX',
        hovertemplate='Strike: %{y}<br>Net GEX: %{x:.4f}B<extra></extra>'
    ))
    
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Futures: {futures_price:,.2f}", annotation_position="top right")
    
    for zone in gamma_flips:
        fig.add_hrect(y0=zone['lower_strike'], y1=zone['upper_strike'],
                     fillcolor="rgba(245, 158, 11, 0.2)", line_width=0, layer="below")
        fig.add_annotation(y=zone['flip_strike'], x=0, text=f"🔄 Γ-Flip ({zone['impact']})",
                          showarrow=True, arrowcolor="#f59e0b", font=dict(size=10, color="#f59e0b"))
    
    fig.update_layout(
        title=dict(text="<b>Net GEX Profile</b>", font=dict(size=16, color='white')),
        xaxis_title="GEX (₹ Billions)", yaxis_title="Strike Price",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=500, showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    return fig

def create_dex_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Net_DEX']]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df['Strike'], x=df['Net_DEX'], orientation='h',
        marker_color=colors, name='Net DEX',
        hovertemplate='Strike: %{y}<br>Net DEX: %{x:.4f}B<extra></extra>'
    ))
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=3,
                  annotation_text=f"Futures: {futures_price:,.2f}", annotation_position="top right")
    fig.update_layout(
        title=dict(text="<b>Net DEX Profile</b>", font=dict(size=16, color='white')),
        xaxis_title="DEX (₹ Billions)", yaxis_title="Strike Price",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=500,
    )
    return fig

def create_hedging_pressure_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df['Strike'], x=df['Hedging_Pressure'], orientation='h',
        marker=dict(color=df['Hedging_Pressure'], colorscale='RdYlGn', showscale=True,
                   colorbar=dict(title='Pressure %')),
        hovertemplate='Strike: %{y}<br>Pressure: %{x:.1f}%<extra></extra>'
    ))
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=3)
    fig.update_layout(
        title=dict(text="<b>Hedging Pressure Distribution</b>", font=dict(size=16, color='white')),
        xaxis_title="Hedging Pressure (%)", yaxis_title="Strike Price",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=500,
    )
    return fig

def create_vanna_charm_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Vanna Exposure", "Charm Exposure"))
    
    vanna_colors = ['#8b5cf6' if x > 0 else '#f59e0b' for x in df['Net_Vanna']]
    fig.add_trace(go.Bar(y=df['Strike'], x=df['Net_Vanna'], orientation='h',
                        marker_color=vanna_colors, name='Net Vanna'), row=1, col=1)
    
    charm_colors = ['#06b6d4' if x > 0 else '#ec4899' for x in df['Net_Charm']]
    fig.add_trace(go.Bar(y=df['Strike'], x=df['Net_Charm'], orientation='h',
                        marker_color=charm_colors, name='Net Charm'), row=1, col=2)
    
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2, row=1, col=1)
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2, row=1, col=2)
    
    fig.update_layout(
        title=dict(text="<b>Vanna & Charm Exposure</b>", font=dict(size=16, color='white')),
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=450, showlegend=False
    )
    return fig

def create_flow_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("GEX Flow (OI Change)", "DEX Flow (OI Change)"))
    
    gex_flow_colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Net_Flow_GEX']]
    fig.add_trace(go.Bar(y=df['Strike'], x=df['Net_Flow_GEX'], orientation='h',
                        marker_color=gex_flow_colors, name='GEX Flow'), row=1, col=1)
    
    dex_flow_colors = ['#10b981' if x > 0 else '#ef4444' for x in df['Net_Flow_DEX']]
    fig.add_trace(go.Bar(y=df['Strike'], x=df['Net_Flow_DEX'], orientation='h',
                        marker_color=dex_flow_colors, name='DEX Flow'), row=1, col=2)
    
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2, row=1, col=1)
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2, row=1, col=2)
    
    fig.update_layout(
        title=dict(text="<b>Today's Flow Analysis (OI Change Impact)</b>", font=dict(size=16, color='white')),
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=450, showlegend=False
    )
    return fig

def create_straddle_payoff_chart(meta: Dict) -> go.Figure:
    atm_strike = meta['atm_strike']
    call_premium = meta['atm_call_premium']
    put_premium = meta['atm_put_premium']
    straddle_premium = meta['atm_straddle']
    futures = meta['futures_price']
    
    strike_range = np.linspace(atm_strike * 0.9, atm_strike * 1.1, 100)
    call_payoff = np.maximum(strike_range - atm_strike, 0) - call_premium
    put_payoff = np.maximum(atm_strike - strike_range, 0) - put_premium
    straddle_payoff = call_payoff + put_payoff
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strike_range, y=straddle_payoff, name='Straddle P&L',
                            line=dict(color='#8b5cf6', width=3), fill='tozeroy',
                            fillcolor='rgba(139, 92, 246, 0.2)'))
    fig.add_trace(go.Scatter(x=strike_range, y=call_payoff, name='Call P&L',
                            line=dict(color='#10b981', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=strike_range, y=put_payoff, name='Put P&L',
                            line=dict(color='#ef4444', width=2, dash='dot')))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.add_vline(x=atm_strike, line_color="#3b82f6", line_width=2, annotation_text=f"ATM: {atm_strike:,.0f}")
    fig.add_vline(x=atm_strike + straddle_premium, line_dash="dash", line_color="#f59e0b",
                  annotation_text=f"Upper BE: {atm_strike + straddle_premium:,.0f}")
    fig.add_vline(x=atm_strike - straddle_premium, line_dash="dash", line_color="#f59e0b",
                  annotation_text=f"Lower BE: {atm_strike - straddle_premium:,.0f}")
    fig.add_vline(x=futures, line_color="#ef4444", line_width=2, annotation_text=f"Current: {futures:,.0f}")
    
    fig.update_layout(
        title=dict(text=f"<b>ATM Straddle Payoff | Premium: ₹{straddle_premium:,.2f}</b>",
                  font=dict(size=16, color='white')),
        xaxis_title="Underlying Price", yaxis_title="Profit/Loss (₹)",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    return fig

def create_oi_distribution_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(y=df['Strike'], x=df['Call_OI'], orientation='h',
                        name='Call OI', marker_color='#10b981', opacity=0.7))
    fig.add_trace(go.Bar(y=df['Strike'], x=-df['Put_OI'], orientation='h',
                        name='Put OI', marker_color='#ef4444', opacity=0.7))
    fig.add_hline(y=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2)
    fig.update_layout(
        title=dict(text="<b>Open Interest Distribution</b>", font=dict(size=16, color='white')),
        xaxis_title="Open Interest (Calls +ve | Puts -ve)", yaxis_title="Strike Price",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=450, barmode='overlay',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    return fig

def create_iv_smile_chart(df: pd.DataFrame, futures_price: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Call_IV'], name='Call IV',
                            mode='lines+markers', line=dict(color='#10b981', width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=df['Strike'], y=df['Put_IV'], name='Put IV',
                            mode='lines+markers', line=dict(color='#ef4444', width=2), marker=dict(size=6)))
    fig.add_vline(x=futures_price, line_dash="dash", line_color="#06b6d4", line_width=2, annotation_text="ATM")
    fig.update_layout(
        title=dict(text="<b>Implied Volatility Smile</b>", font=dict(size=16, color='white')),
        xaxis_title="Strike Price", yaxis_title="Implied Volatility (%)",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26,35,50,0.8)', height=350,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    return fig

def create_combined_gauge(metrics: Dict) -> go.Figure:
    combined_signal = metrics['combined_signal']
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=combined_signal,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Combined GEX+DEX Signal", 'font': {'size': 16, 'color': 'white'}},
        delta={'reference': 0, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
        gauge={
            'axis': {'range': [-100, 100], 'tickcolor': 'white'},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "rgba(26,35,50,0.8)",
            'borderwidth': 2, 'bordercolor': "gray",
            'steps': [
                {'range': [-100, -50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [-50, 0], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [0, 50], 'color': 'rgba(16, 185, 129, 0.3)'},
                {'range': [50, 100], 'color': 'rgba(16, 185, 129, 0.5)'}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': combined_signal}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
    return fig

def simulate_time_decay(df: pd.DataFrame, meta: Dict, hours_forward: float):
    df_sim = df.copy()
    current_days = meta['days_to_expiry']
    new_days = max(current_days - (hours_forward / 24), 0.1)
    time_factor = new_days / current_days if current_days > 0 else 1
    gamma_decay = np.sqrt(time_factor)
    df_sim['Net_GEX'] = df_sim['Net_GEX'] * gamma_decay
    df_sim['Hedging_Pressure'] = df_sim['Hedging_Pressure'] * gamma_decay
    return df_sim, new_days

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 180
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False
    
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="main-title">📊 NYZTrade GEX/DEX Dashboard</h1>
                <p class="sub-title">Professional Options Greeks Analysis | Real-time Market Intelligence</p>
            </div>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <span style="color: #ef4444; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">LIVE</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        symbol = st.selectbox("📈 Select Index", options=list(DHAN_SECURITY_IDS.keys()), index=0)
        strikes_range = st.slider("📏 Strikes Range", min_value=5, max_value=20, value=12)
        expiry_index = st.number_input("📅 Expiry Index", min_value=0, max_value=5, value=0)
        
        st.markdown("---")
        st.markdown("### 🔄 Auto Refresh")
        auto_refresh = st.checkbox("Enable Auto Refresh", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
        refresh_interval = st.slider("Refresh Interval (sec)", min_value=60, max_value=600, value=180, step=30)
        st.session_state.refresh_interval = refresh_interval
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔑 API Status")
        config = DhanConfig()
        try:
            expiry_time = datetime.strptime(config.expiry_time, "%Y-%m-%dT%H:%M:%S")
            remaining = expiry_time - datetime.now()
            if remaining.total_seconds() > 0:
                st.success(f"✅ Token Valid: {remaining.days}d {remaining.seconds//3600}h")
            else:
                st.error("❌ Token Expired")
        except:
            st.warning("⚠️ Token status unknown")
        
        st.markdown("---")
        st.markdown("### 📊 Time Machine")
        time_offset = st.slider("⏰ Simulate Time Forward (hours)", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
    
    if st.session_state.auto_refresh:
        elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
        remaining = max(0, st.session_state.refresh_interval - elapsed)
        progress = 1 - (remaining / st.session_state.refresh_interval)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="countdown-container">
                <div class="countdown-label">Next Refresh In</div>
                <div class="countdown-value">{int(remaining // 60):02d}:{int(remaining % 60):02d}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if remaining <= 0:
            st.session_state.last_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()
    
    @st.cache_data(ttl=180)
    def fetch_data(symbol, strikes_range, expiry_index):
        fetcher = DhanAPIFetcher(DhanConfig())
        return fetcher.process_option_chain(symbol, expiry_index, strikes_range)
    
    with st.spinner(f"🔄 Fetching {symbol} data from Dhan API..."):
        df, meta = fetch_data(symbol, strikes_range, expiry_index)
    
    if df is None or meta is None:
        st.error("❌ Failed to fetch data. Please check API credentials or try again.")
        return
    
    if time_offset > 0:
        df, sim_days = simulate_time_decay(df, meta, time_offset)
        st.info(f"⏰ Time Machine Active: Simulating {time_offset}h forward | Days to expiry: {sim_days:.1f}")
    
    metrics = calculate_flow_metrics(df, meta['futures_price'])
    gamma_flips = detect_gamma_flip_zones(df)
    key_levels = calculate_key_levels(df, meta['futures_price'])
    
    st.markdown("### 📊 Market Overview")
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""<div class="metric-card neutral"><div class="metric-label">Spot Price</div>
            <div class="metric-value">₹{meta['spot_price']:,.2f}</div></div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""<div class="metric-card neutral"><div class="metric-label">Futures</div>
            <div class="metric-value">₹{meta['futures_price']:,.2f}</div></div>""", unsafe_allow_html=True)
    with cols[2]:
        gex_class = "positive" if metrics['gex_near_total'] > 0 else "negative"
        st.markdown(f"""<div class="metric-card {gex_class}"><div class="metric-label">Net GEX (Near)</div>
            <div class="metric-value {gex_class}">{metrics['gex_near_total']:.4f}B</div>
            <div class="metric-delta">{metrics['gex_desc']}</div></div>""", unsafe_allow_html=True)
    with cols[3]:
        dex_class = "positive" if metrics['dex_near_total'] > 0 else "negative"
        st.markdown(f"""<div class="metric-card {dex_class}"><div class="metric-label">Net DEX (Near)</div>
            <div class="metric-value {dex_class}">{metrics['dex_near_total']:.4f}B</div>
            <div class="metric-delta">{metrics['dex_desc']}</div></div>""", unsafe_allow_html=True)
    with cols[4]:
        pcr_class = "positive" if key_levels['pcr'] > 1 else "negative"
        st.markdown(f"""<div class="metric-card {pcr_class}"><div class="metric-label">Put/Call Ratio</div>
            <div class="metric-value {pcr_class}">{key_levels['pcr']:.2f}</div>
            <div class="metric-delta">{'Bearish' if key_levels['pcr'] > 1.2 else 'Bullish' if key_levels['pcr'] < 0.8 else 'Neutral'}</div></div>""", unsafe_allow_html=True)
    with cols[5]:
        st.markdown(f"""<div class="metric-card neutral"><div class="metric-label">ATM Straddle</div>
            <div class="metric-value">₹{meta['atm_straddle']:.2f}</div>
            <div class="metric-delta">Strike: {meta['atm_strike']:,.0f}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        badge_class = "bullish" if "SUPPRESSION" in metrics['gex_bias'] else "bearish" if "HIGH" in metrics['gex_bias'] else "volatile"
        st.markdown(f'<div class="signal-badge {badge_class}">{metrics["gex_bias"]}</div>', unsafe_allow_html=True)
    with cols[1]:
        badge_class = "bullish" if "BULLISH" in metrics['dex_bias'] else "bearish" if "BEARISH" in metrics['dex_bias'] else "volatile"
        st.markdown(f'<div class="signal-badge {badge_class}">{metrics["dex_bias"]}</div>', unsafe_allow_html=True)
    with cols[2]:
        badge_class = "bullish" if metrics['combined_signal'] > 0 else "bearish"
        st.markdown(f'<div class="signal-badge {badge_class}">{metrics["combined_bias"]}</div>', unsafe_allow_html=True)
    with cols[3]:
        flip_badge = f"🔄 {len(gamma_flips)} Gamma Flip Zone(s)" if gamma_flips else "✅ No Gamma Flips"
        st.markdown(f'<div class="signal-badge volatile">{flip_badge}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    tabs = st.tabs(["📊 GEX/DEX", "🎯 Hedging Pressure", "📈 Vanna & Charm", "🔄 Flow", "📋 Data", "💡 Strategies"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_gex_chart(df, meta['futures_price'], gamma_flips), use_container_width=True)
        with col2:
            st.plotly_chart(create_dex_chart(df, meta['futures_price']), use_container_width=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.plotly_chart(create_combined_gauge(metrics), use_container_width=True)
        st.plotly_chart(create_straddle_payoff_chart(meta), use_container_width=True)
    
    with tabs[1]:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_hedging_pressure_chart(df, meta['futures_price']), use_container_width=True)
        with col2:
            st.plotly_chart(create_oi_distribution_chart(df, meta['futures_price']), use_container_width=True)
        
        st.markdown("### 🎯 Key Levels")
        cols = st.columns(5)
        levels = [("Max Pain", key_levels['max_pain'], "#f59e0b"),
                 ("Highest Call OI", key_levels['highest_call_oi'], "#10b981"),
                 ("Highest Put OI", key_levels['highest_put_oi'], "#ef4444"),
                 ("Max +GEX", key_levels['max_positive_gex'], "#8b5cf6"),
                 ("Max -GEX", key_levels['max_negative_gex'], "#ec4899")]
        for col, (label, value, color) in zip(cols, levels):
            with col:
                st.markdown(f"""<div class="metric-card" style="border-left-color: {color};">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color: {color};">{value:,.0f}</div></div>""", unsafe_allow_html=True)
        
        if gamma_flips:
            st.markdown("### 🔄 Gamma Flip Zones")
            for i, zone in enumerate(gamma_flips, 1):
                st.markdown(f"""<div class="gamma-flip-zone"><div class="flip-label">Zone #{i}: {zone['flip_type']}</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <div><span style="color: #64748b;">Flip Strike:</span><span style="font-weight: 600; color: #f59e0b;"> {zone['flip_strike']:,.2f}</span></div>
                    <div><span style="color: #64748b;">Range:</span><span style="font-weight: 600;"> {zone['lower_strike']:,.0f} - {zone['upper_strike']:,.0f}</span></div>
                    <div><span style="color: #64748b;">Impact:</span><span style="font-weight: 600; color: {'#10b981' if zone['impact'] == 'Support' else '#ef4444'};"> {zone['impact']}</span></div></div></div>""", unsafe_allow_html=True)
    
    with tabs[2]:
        st.plotly_chart(create_vanna_charm_chart(df, meta['futures_price']), use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Vanna Exposure")
            vanna_df = df[['Strike', 'Net_Vanna', 'Call_Vanna', 'Put_Vanna']].sort_values('Net_Vanna', ascending=False).head(10)
            st.dataframe(vanna_df, use_container_width=True, hide_index=True)
            st.markdown(f"**Total Vanna:** {metrics['vanna_total']:.4f}B")
        with col2:
            st.markdown("### 📊 Charm Exposure")
            charm_df = df[['Strike', 'Net_Charm', 'Call_Charm', 'Put_Charm']].sort_values('Net_Charm', ascending=False).head(10)
            st.dataframe(charm_df, use_container_width=True, hide_index=True)
            st.markdown(f"**Total Charm:** {metrics['charm_total']:.6f}B/day")
        st.plotly_chart(create_iv_smile_chart(df, meta['futures_price']), use_container_width=True)
    
    with tabs[3]:
        st.plotly_chart(create_flow_chart(df, meta['futures_price']), use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 GEX Flow")
            gex_class = 'positive' if metrics['flow_gex_total'] > 0 else 'negative'
            st.markdown(f"""<div class="metric-card {gex_class}"><div class="metric-label">Total GEX Flow</div>
                <div class="metric-value">{'+'if metrics['flow_gex_total'] > 0 else ''}{metrics['flow_gex_total']:.4f}B</div></div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("### 📊 DEX Flow")
            dex_class = 'positive' if metrics['flow_dex_total'] > 0 else 'negative'
            st.markdown(f"""<div class="metric-card {dex_class}"><div class="metric-label">Total DEX Flow</div>
                <div class="metric-value">{'+'if metrics['flow_dex_total'] > 0 else ''}{metrics['flow_dex_total']:.4f}B</div></div>""", unsafe_allow_html=True)
    
    with tabs[4]:
        st.markdown("### 📋 Complete Option Chain Data")
        display_cols = ['Strike', 'Call_OI', 'Put_OI', 'Call_OI_Change', 'Put_OI_Change',
                       'Call_IV', 'Put_IV', 'Call_LTP', 'Put_LTP', 'Net_GEX', 'Net_DEX', 'Net_Vanna', 'Hedging_Pressure']
        display_df = df[display_cols].copy()
        display_df['Net_GEX'] = display_df['Net_GEX'].apply(lambda x: f"{x:.4f}B")
        display_df['Net_DEX'] = display_df['Net_DEX'].apply(lambda x: f"{x:.4f}B")
        display_df['Net_Vanna'] = display_df['Net_Vanna'].apply(lambda x: f"{x:.4f}B")
        display_df['Hedging_Pressure'] = display_df['Hedging_Pressure'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Full Data (CSV)", data=csv,
                          file_name=f"NYZTrade_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
    
    with tabs[5]:
        st.markdown("### 💼 Trading Strategy Recommendations")
        gex_bias = metrics['gex_near_total']
        dex_bias = metrics['dex_near_total']
        atm_strike = meta['atm_strike']
        straddle = meta['atm_straddle']
        
        if gex_bias > 50:
            regime, regime_color = "Low Volatility / Mean Reversion", "#10b981"
        elif gex_bias < -50:
            regime, regime_color = "High Volatility / Trending", "#ef4444"
        else:
            regime, regime_color = "Transitional / Mixed", "#f59e0b"
        
        st.markdown(f"""<div class="strategy-card" style="border-left: 4px solid {regime_color};">
            <div class="strategy-title">🎯 Market Regime: {regime}</div>
            <div class="strategy-detail">GEX: {gex_bias:.2f} | DEX: {dex_bias:.2f} | ATM: {atm_strike:,.0f} | Straddle: ₹{straddle:.2f}</div></div>""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 Recommended Strategies")
            if gex_bias > 50:
                st.markdown("""<div class="strategy-card"><div class="strategy-title">🎯 Iron Condor / Short Straddle</div>
                    <div class="strategy-detail">Positive GEX = Market makers suppress moves. Sell premium strategies work well.</div></div>""", unsafe_allow_html=True)
            elif gex_bias < -50:
                st.markdown("""<div class="strategy-card"><div class="strategy-title">🎯 Long Straddle / Directional</div>
                    <div class="strategy-detail">Negative GEX = Volatility amplification. Buy premium or trade breakouts.</div></div>""", unsafe_allow_html=True)
                if dex_bias > 20:
                    st.markdown("""<div class="strategy-card"><div class="strategy-title">🎯 Bull Call Spread</div>
                        <div class="strategy-detail">DEX bullish + High volatility = Upside momentum likely.</div></div>""", unsafe_allow_html=True)
                elif dex_bias < -20:
                    st.markdown("""<div class="strategy-card"><div class="strategy-title">🎯 Bear Put Spread</div>
                        <div class="strategy-detail">DEX bearish + High volatility = Downside momentum likely.</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div class="strategy-card"><div class="strategy-title">⏳ Wait for Clarity</div>
                    <div class="strategy-detail">Mixed signals. Wait for clearer GEX/DEX alignment.</div></div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚠️ Risk Management")
            st.markdown(f"""<div class="strategy-card" style="border-left: 4px solid #ef4444;"><div class="strategy-title">🛡️ Position Sizing</div>
                <div class="strategy-detail">• Max position: 2% of capital<br>• Max daily loss: 5%<br>• Scale into positions</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="strategy-card" style="border-left: 4px solid #f59e0b;"><div class="strategy-title">⏰ Time Rules</div>
                <div class="strategy-detail">• Avoid 9:15-9:30 AM<br>• Best: 10:00-11:30 AM<br>• Days to Expiry: {meta['days_to_expiry']}</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="strategy-card" style="border-left: 4px solid #8b5cf6;"><div class="strategy-title">🎯 Key Levels</div>
                <div class="strategy-detail">• ATM: {atm_strike:,.0f}<br>• Upper BE: {atm_strike + straddle:,.0f}<br>• Lower BE: {atm_strike - straddle:,.0f}<br>• Max Pain: {key_levels['max_pain']:,.0f}</div></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""<div style="text-align: center; padding: 20px; color: #64748b;">
        <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
        NYZTrade GEX/DEX Dashboard | Data: Dhan API | Last Update: {meta['timestamp']}<br>
        Expiry: {meta['expiry']} | Symbol: {symbol} | Strikes: {len(df)}</p>
        <p style="font-size: 0.75rem;">⚠️ Educational purposes only. Options trading involves substantial risk.</p></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
