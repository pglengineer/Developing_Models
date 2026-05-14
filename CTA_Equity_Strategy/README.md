# 🚀 美股多商品橫截面趨勢延續性策略藍圖 (Cross-Sectional CTA)

## 📌 核心想法
將原本針對單一指數期貨的 **CTA 趨勢延續性邏輯**，擴展至美股股票池。核心在於從「時間序列的絕對強度」轉向「橫截面的相對強度排名」，並加入市值與產業中性化過濾。

## 🛠 增強型特徵 (Enhanced Features)
1.  **趨勢連續性核心三因子**: 
    - **DC (Directional Consistency)**: 方向一致性。
    - **SL (Streak Length)**: 連續同向天數。
    - **PE (Path Efficiency)**: 價格路徑效率 (Efficiency Ratio)。
2.  **基本面與結構特徵**:
    - **市值 (Market Cap)**: 用於區分大型股與中小盤股走勢特性。
    - **產業區塊 (Sector)**: 用於執行產業中性化 (Sector Neutral) 配置。
3.  **動態特徵**:
    - **近期波動度變化**: 比較 5 日與 20 日波動率，識別波動爆發。
    - **量能多維度**: 包含成交量相對於均線的放大倍數。

## 🔢 核心公式 (Core Formulas)

### 1. 趨勢延續性得分 (Continuity Strength Score)
$$CS_t = DC_t \times 0.4 + SL_t \times 0.3 + PE_t \times 0.3$$
其中：
- **$DC_t$ (Directional Consistency)**: 過去 $N$ 日中與總趨勢同向的天數比例。
- **$SL_t$ (Streak Length)**: 當前連續上漲或下跌的天數 $K$，標準化為 $\min(K/3, 1)$。
- **$PE_t$ (Path Efficiency)**: 價格位移與總路徑之比 $\frac{|P_t - P_{t-N}|}{\sum |P_i - P_{i-1}|}$。

### 2. L1 通道突破觸發價
$$Trigger_{Long} = RollingMin + k \times (RollingMax - RollingMin)$$
$$Trigger_{Short} = RollingMax - k \times (RollingMax - RollingMin)$$

## 📖 核心函數說明 (API Reference)

### `calculate_advanced_features(df_daily, market_cap=None, sector=None)`
- **功能**: 計算個股的趨勢延續性複合得分與市值、產業特徵。
- **輸入**:
    - `df_daily`: 包含 'Close', 'Volume' 欄位的日線數據。
    - `market_cap`: 該股目前市值。
- **輸出**: 包含新特徵欄位的 DataFrame。

### `calculate_l1_breakout(df_15m, n_bars=480, entry_param=0.8)`
- **功能**: 計算基於通道的進場觸發價。
- **輸入**:
    - `df_15m`: 15 分鐘 K 線。
    - `n_bars`: 通道視窗大小。
- **輸出**: `long_trigger`, `short_trigger` (float)。

### `check_trailing_stop(pos_type, ...)`
- **功能**: 執行進場後的動態追蹤停損邏輯。
- **輸入**: 持倉類型、當前高低價、進場價、最高點、停損比例。
- **輸出**: `is_exit`, `new_peak`, `exit_trigger`。

## 📝 詳細回測規則與進出場設定 (Backtesting Rules)

### 1. 進場設定 (Entry Rules)
- **選股頻率**: 每週五收盤前執行橫截面排名。
- **篩選門檻**: 取 CS 得分最高的前 10% 股票進入「觀察籃子」。
- **進場觸發**: 觀察籃子中的股票，需在下週一出現 **L1 通道向上突破**（價格 > Trigger）時即時買入。
- **初始倉位**: 等權重分配，單一股票最大權重不超過 5%。

### 2. 出場與風控 (Exit Rules)
- **硬停損 (Stop Loss)**: 進場價格 - 2.0%。
- **動態追蹤停損 (Trailing Stop)**: 多頭進場後最高價回撤 1.0% 時出場。
- **定期汰換**: 每週末重新排名，若持倉股掉出 Top 30% 則主動換股。

## 📊 視覺化展示邏輯 (Visualization)
1.  **分組回測曲線 (Group NAV)**: 驗證因子單調性。
2.  **因子分佈熱力圖 (Factor Heatmap)**: 監控全市場趨勢強度。
3.  **個股進場標記圖**: 在 K 線圖上標註 L1 突破點與停損線。

---
**核心函數參考**: [core_logic.py](./core_logic.py)
