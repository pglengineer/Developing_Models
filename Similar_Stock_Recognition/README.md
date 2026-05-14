# 🌌 美股全市場相似性識別與類比交易藍圖 (Cross-Stock Analogous Search)

## 📌 核心想法
利用 LSTM Autoencoder 提取美股走勢的「數字指紋」，在全市場歷史中尋找相似形態，並根據類比對象的後續走勢進行概率預測。

## 🛠 增強型特徵 (Enhanced Features)
1.  **全市場相似維度**:
    - **趨勢連續性三因子 (DC, SL, PE)**: 確保類比的走勢具備相似的「乾淨度」。
    - **近期波動度變化**: 相似的波動爆發特徵。
    - **成交量百分位排名 (Volume Rank)**: 確保類比標的具備相似的市場熱度。
2.  **屬性對齊**:
    - **市值區間**: 大型股類比大型股。
    - **產業區塊 (Sector)**: 觀察跨產業形態的關聯性。

## 🔢 核心公式 (Core Formulas)

### 1. 歐式空間相似度 (Similarity Metric)
在 Embedding 空間中，兩次市場狀態 $z_A$ 與 $z_B$ 的距離計算為：
$$d(z_A, z_B) = \sqrt{\sum_{i=1}^{16} (z_{A,i} - z_{B,i})^2}$$

### 2. 類比勝率預測 (Expectation)
$$WinRate = \frac{Count(Return_{K, t+1} > 0)}{K}$$

## 📖 核心函數說明 (API Reference)

### `UniversalFeaturePipe.calculate_features(...)`
- **功能**: 轉化為去量綱的形態特徵，包含 DC, SL, PE, 波動變化等。
- **輸入**: 原始 OHLCV、市值、產業。
- **輸出**: 歸一化特徵 DataFrame。

### `MarketStateEncoder.encode(x)`
- **功能**: 將時序序列壓縮為 32 維的 Embedding。
- **輸出**: 狀態向量 (Tensor)。

### `CrossStockSearchEngine.search_analogies(...)`
- **功能**: 在全局向量資料庫中尋找相似瞬間，並過濾未來數據。
- **輸出**: 相似對象列表 `[{ticker, date}, ...]`。

## 📝 詳細回測規則與進出場設定 (Backtesting Rules)

### 1. 進場設定 (Entry Rules)
- **回看視窗**: 過去 20 個交易日。
- **搜索數量 (K)**: 100 個鄰居。
- **勝率門檻**: 5 日勝率 > 70% 且預期收益 > 1.5% 時買入。

### 2. 出場與風控 (Exit Rules)
- **固定持有期**: 5 個交易日強制平倉。
- **異常退出**: 2 日內虧損超過 3% 代表類比失效。
- **動態更新**: 每日重新搜索，方向反轉時主動出場。

## 📊 視覺化展示邏輯 (Visualization)
1.  **Embedding 降維散點圖 (TSNE/UMAP)**: 觀察市場狀態聚類。
2.  **形態類比疊加圖 (Overlay Plot)**: 將當前標的與歷史最相似走勢重疊。
3.  **預期收益分佈圖**: 100 個鄰居未來收益的分布直方圖。

---
**核心函數參考**: [core_similarity.py](./core_similarity.py)
