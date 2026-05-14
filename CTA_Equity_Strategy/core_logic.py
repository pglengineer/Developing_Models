import pandas as pd
import numpy as np

def calculate_advanced_features(df_daily, market_cap=None, sector=None):
    """
    計算 CTA 策略所需的進階特徵與因子
    """
    df = df_daily.copy()
    
    # 1. 趨勢連續性核心三因子
    log_ret = np.log(df['Close'] / df['Close'].shift(1))
    df['DC'] = (log_ret > 0).rolling(5).mean()
    df['SL'] = (np.sign(log_ret) == np.sign(log_ret.shift(1))).astype(int).rolling(3).sum() / 3.0
    df['PE'] = df['Close'].diff(5).abs() / df['Close'].diff().abs().rolling(5).sum()
    
    # 2. 波動度變化 (近期 vs 長期)
    df['vol_5d'] = log_ret.rolling(5).std() * np.sqrt(252)
    df['vol_20d'] = log_ret.rolling(20).std() * np.sqrt(252)
    df['vol_ratio'] = df['vol_5d'] / df['vol_20d']
    
    # 3. 成交量占比與量能放大
    df['vol_ma_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    
    # 4. 靜態屬性
    if market_cap is not None:
        df['market_cap'] = market_cap
    if sector is not None:
        df['sector'] = sector
        
    return df

def calculate_l1_breakout(df_15m, n_bars=480, entry_param=0.8):
    """
    計算 L1 通道價格
    """
    rolling_max = df_15m['High'].rolling(window=n_bars).max()
    rolling_min = df_15m['Low'].rolling(window=n_bars).min()
    long_trigger = rolling_min + entry_param * (rolling_max - rolling_min)
    short_trigger = rolling_max - entry_param * (rolling_max - rolling_min)
    return long_trigger, short_trigger

def check_trailing_stop(pos_type, current_high, current_low, entry_price, peak_valley_price, stop_loss_pct, trailing_stop_pct):
    """
    動態追蹤停損
    """
    if pos_type == 'long':
        new_peak = max(peak_valley_price, current_high)
        sl_price = entry_price * (1 - stop_loss_pct)
        ts_price = new_peak * (1 - trailing_stop_pct)
        exit_trigger = max(sl_price, ts_price)
        is_exit = current_low < exit_trigger
        return is_exit, new_peak, exit_trigger
    elif pos_type == 'short':
        new_valley = min(peak_valley_price, current_low)
        sl_price = entry_price * (1 + stop_loss_pct)
        ts_price = new_valley * (1 + trailing_stop_pct)
        exit_trigger = min(sl_price, ts_price)
        is_exit = current_high > exit_trigger
        return is_exit, new_valley, exit_trigger
    return False, peak_valley_price, 0
