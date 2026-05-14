import pandas as pd
import numpy as np

def calculate_continuity_score(df_daily, n_days=5):
    """
    計算趨勢延續性強度評分 (Continuity Strength Score)
    
    1. DC (Direction Consistency): 同向日佔比 (0.4)
    2. SL (Streak Length): 連續段長度 (0.3)
    3. PE (Path Efficiency): 路徑效率 (0.3)
    """
    # 1. DC: Direction Consistency
    net_return = df_daily['Close'].diff(n_days)
    direction = np.sign(net_return)
    
    daily_diff = df_daily['Close'].diff()
    dc = []
    for i in range(len(df_daily)):
        if i < n_days:
            dc.append(0)
            continue
        window = daily_diff.iloc[i-n_days+1:i+1]
        d = direction.iloc[i]
        if d > 0:
            count = (window > 0).sum()
        elif d < 0:
            count = (window < 0).sum()
        else:
            count = 0
        dc.append(count / n_days)
    
    # 2. SL: Streak Length
    sl = []
    current_streak = 0
    prev_dir = 0
    for d in daily_diff:
        curr_dir = np.sign(d)
        if curr_dir == prev_dir and curr_dir != 0:
            current_streak += 1
        else:
            current_streak = 1 if curr_dir != 0 else 0
        prev_dir = curr_dir
        sl.append(min(current_streak / 3.0, 1.0))
        
    # 3. PE: Path Efficiency (Kaufman Efficiency Ratio)
    abs_net_change = df_daily['Close'].diff(n_days).abs()
    sum_abs_daily_changes = df_daily['Close'].diff().abs().rolling(n_days).sum()
    pe = abs_net_change / sum_abs_daily_changes
    
    cs_score = pd.Series(dc) * 0.4 + pd.Series(sl) * 0.3 + pe.reset_index(drop=True) * 0.3
    return cs_score

def calculate_l1_breakout(df_15m, n_bars=480, entry_param=0.8):
    """
    計算 L1 通道突破觸發價
    """
    rolling_max = df_15m['High'].rolling(window=n_bars).max()
    rolling_min = df_15m['Low'].rolling(window=n_bars).min()
    
    long_trigger = rolling_min + entry_param * (rolling_max - rolling_min)
    short_trigger = rolling_max - entry_param * (rolling_max - rolling_min)
    
    return long_trigger, short_trigger

def check_trailing_stop(pos_type, current_high, current_low, entry_price, peak_valley_price, stop_loss_pct, trailing_stop_pct):
    """
    動態追蹤停損停利邏輯
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
