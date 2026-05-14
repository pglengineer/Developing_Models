# 🚀 美股多商品橫截面趨勢延續性策略藍圖 (Cross-Sectional CTA)

## 📌 核心想法
將原本針對單一指數期貨的 **CTA 趨勢延續性邏輯**，擴展至美股股票池（如 S&P 500 或 Nasdaq 100）。核心在於從「時間序列的絕對強度」轉向「橫截面的相對強度排名」。

## 🛠 策略組件 (Original Framework)

### 1. 因子計算 (Ranking Factor)
- **核心指標**: 趨勢延續性得分 (Continuity Strength Score, CS)。
- **操作**: 每日或每週計算股票池中所有股票的 CS 得分。

### 2. 橫截面篩選 (Selection)
- **多頭組合 (Long Basket)**: 選取 CS 得分最高的前 10% (Top Decile) 股票。
- **權重分配**: 採等權重或波動率倒數加權 (Risk Parity)。

### 3. 進場過濾 (Timing Filter)
- 即使入選 Top Decile，進場仍需滿足 **L1 通道突破** 條件。

### 4. 風控與出場 (Risk Management)
- **動態追蹤停損 (Trailing Stop)**: 沿用原策略的動態最高點回撤機制。
- **組合再平衡 (Rebalancing)**: 定期（如每週五）更新排名。

## 🌟 增強型特徵 (Enhanced Features)
1.  **趨勢連續性三因子 (DC, SL, PE)**:
    - **DC (Directional Consistency)**: 方向一致性。
    - **SL (Streak Length)**: 連續同向天數。
    - **PE (Path Efficiency)**: 價格路徑效率。
2.  **屬性與結構**:
    - **市值 (Market Cap)**: 用於規模因子篩選。
    - **產業區塊 (Sector)**: 用於執行產業中性化配置。
3.  **動態特徵**:
    - **近期波動度變化**: 比較 5 日與 20 日波動率，識別波動爆發。
    - **量能多維度**: 包含成交量相對於均線的放大倍數。

## 🔢 核心公式 (Core Formulas)

### 1. 趨勢延續性得分 (Continuity Strength Score)
$$CS_t = DC_t \times 0.4 + SL_t \times 0.3 + PE_t \times 0.3$$
其中：
- **$DC_t$**: 過去 $N$ 日中與總趨勢同向的天數比例。
- **$SL_t$**: 當前連續上漲或下跌天數 $K$，標準化為 $\min(K/3, 1)$。
- **$PE_t$**: 價格位移與總路徑之比 $\frac{|P_t - P_{t-N}|}{\sum |P_i - P_{i-1}|}$。

### 2. L1 通道突破觸發價
$$Trigger_{Long} = RollingMin + k \times (RollingMax - RollingMin)$$

## 📖 核心函數說明 (API Reference)

### `calculate_advanced_features(df_daily, market_cap, sector)`
- **功能**: 計算個股的趨勢延續性複合得分與多維特徵。
- **輸入/輸出**: DataFrame 進，擴展特徵後 DataFrame 出。

### `calculate_l1_breakout(df_15m, n_bars, entry_param)`
- **功能**: 計算 L1 通道進場價格。
- **輸出**: `long_trigger`, `short_trigger`。

## 📝 詳細回測規則與進出場設定 (Backtesting Rules)

### 1. 進場設定
- **選股頻率**: 每週五收盤排名。
- **篩選門檻**: 取 CS 得分最高的前 10% 進入觀察籃。
- **進場觸發**: 下週一出現 **L1 通道向上突破** 時即時買入。

### 2. 出場與風控
- **硬停損**: 進場價 - 2.0%。
- **動態追蹤停損**: 多頭進場後最高價回撤 1.0% 時出場。
- **定期汰換**: 每週末重新排名，若持倉股掉出 Top 30% 則主動換股。

## 📊 視覺化展示邏輯 (Visualization)
1.  **分組回測曲線 (Group NAV)**: 驗證因子單調性。
2.  **因子分佈熱力圖 (Factor Heatmap)**: 監控全市場趨勢強度。

---
**核心函數參考**: [core_logic.py](./core_logic.py)
