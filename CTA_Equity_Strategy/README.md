# 🚀 美股多商品橫截面趨勢延續性策略藍圖 (Cross-Sectional CTA)

## 📌 核心想法
將原本針對單一指數期貨的 **CTA 趨勢延續性邏輯**，擴展至美股股票池（如 S&P 500 或 Nasdaq 100）。核心在於從「時間序列的絕對強度」轉向「橫截面的相對強度排名」。

## 🛠 策略組件

### 1. 因子計算 (Ranking Factor)
- **核心指標**: 趨勢延續性得分 (Continuity Strength Score, CS)。
- **計算維度**:
    - **方向一致性 (DC)**: 衡量趨勢是否受雜訊干擾。
    - **連續段長度 (SL)**: 衡量當前動能的純度。
    - **路徑效率 (PE)**: 衡量價格運動的「直達度」(Efficiency Ratio)。
- **操作**: 每日或每週計算股票池中所有股票的 CS 得分。

### 2. 橫截面篩選 (Selection)
- **多頭組合 (Long Basket)**: 選取 CS 得分最高的前 10% (Top Decile) 股票。
- **空頭組合 (Short Basket)**: 選取 CS 得分最低的前 10% (Bottom Decile) 股票，或選擇不持倉。
- **權重分配**: 採等權重或波動率倒數加權 (Risk Parity)。

### 3. 進場過濾 (Timing Filter)
- 雖然股票被選入 Top Decile，但進場仍需滿足 **L1 通道突破** 條件。
- 確保在「相對強勢」且「即時突破」的雙重確認下進場。

### 4. 風控與出場 (Risk Management)
- **動態追蹤停損 (Trailing Stop)**: 沿用原策略的動態最高點回撤機制。
- **組合再平衡 (Rebalancing)**: 定期（如每週五）更新排名，汰弱留強。

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

### `calculate_continuity_score(df_daily, n_days=5)`
- **功能**: 計算個股的趨勢延續性複合得分，用於橫截面排名。
- **輸入**:
    - `df_daily` (DataFrame): 包含 'Close' 欄位的日線數據。
    - `n_days` (int): 回看天數，預設為 5。
- **輸出**:
    - `cs_score` (Series): 每日的 CS 得分 (0~1 區間)。

### `calculate_l1_breakout(df_15m, n_bars=480, entry_param=0.8)`
- **功能**: 計算基於通道的進場觸發價。
- **輸入**:
    - `df_15m` (DataFrame): 包含 'High', 'Low' 欄位的 15 分鐘 K 線。
    - `n_bars` (int): 通道視窗大小（如 5 天約 480 根 K 線）。
    - `entry_param` (float): 通道係數 $k$ (0~1)。
- **輸出**:
    - `long_trigger`, `short_trigger` (float): 多/空進場價。

### `check_trailing_stop(pos_type, current_high, current_low, entry_price, peak_valley_price, stop_loss_pct, trailing_stop_pct)`
- **功能**: 執行進場後的動態追蹤停損邏輯。
- **輸入**:
    - `pos_type` (str): 'long' 或 'short'。
    - `current_high`/`current_low`: 當前 K 線最高/最低價。
    - `entry_price`: 進場成本價。
    - `peak_valley_price`: 進場後達到的最高點 (或最低點)。
    - `stop_loss_pct`: 初始硬停損比例。
    - `trailing_stop_pct`: 追蹤停損比例。
- **輸出**:
    - `is_exit` (bool): 是否觸發出場。
    - `new_peak_valley`: 更新後的極值。
    - `exit_trigger`: 當前的實際出場臨界價。

## 📊 視覺化展示邏輯 (Visualization)
為了有效監控策略表現，建議實作以下圖表：
1.  **分組回測曲線 (Group NAV)**: 將股票按 CS 得分分為 5 或 10 組，畫出每組的累積收益曲線，驗證因子單調性。
2.  **因子分佈熱力圖 (Factor Heatmap)**: 展示標的池中 CS 得分隨時間的分佈變化，識別市場整體的趨勢強度。
3.  **個股進場標記圖**: 在 K 線圖上標註 L1 突破點位與動態追蹤停損線的即時變化。

---
**核心函數參考**: [core_logic.py](./core_logic.py)
