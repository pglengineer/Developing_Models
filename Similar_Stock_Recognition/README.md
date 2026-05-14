# 🌌 美股全市場相似性識別與類比交易藍圖 (Cross-Stock Analogous Search)

## 📌 核心想法
利用 LSTM Autoencoder 提取美股走勢的「數字指紋」，在全市場歷史中尋找相似形態，並根據類比對象的後續走勢進行概率預測。

## 🛠 策略組件 (Original Framework)

### 1. 跨股票特徵流水線
- 轉化為去量綱、跨股票可比的形態特徵（收益率、相對位置、量能放大）。

### 2. 市場狀態編碼器
- 將時序序列壓縮為低維 Embedding 向量，作為市場狀態的「指紋」。

### 3. 全局向量檢索引擎
- 使用 FAISS 建立海量歷史狀態索引，實現毫秒級類比搜索。

### 4. 類比推理與信號
- 基於相似對象的統計表現（如勝率、期望回報）產生進出場信號。

## 🌟 增強型特徵 (Enhanced Features)
1.  **全市場相似維度**:
    - **趨勢連續性三因子 (DC, SL, PE)**: 確保類比走勢具備相似的「趨勢純度」。
    - **近期波動度變化**: 波動率特徵對齊。
    - **成交量排名與佔比**: 捕捉市場關注度相似的標的。
2.  **屬性對齊**:
    - **市值區間**: 大型股與中小盤股的形態特性區分。
    - **產業區塊 (Sector)**: 跨產業與同產業的類比分析。

## 🔢 核心公式 (Core Formulas)

### 1. 歐式空間相似度 (Similarity Metric)
$$d(z_A, z_B) = \sqrt{\sum_{i=1}^{16} (z_{A,i} - z_{B,i})^2}$$

### 2. 類比勝率預測 (Expectation)
$$WinRate = \frac{Count(Return_{K, t+1} > 0)}{K}$$

## 📖 核心函數說明 (API Reference)

### `UniversalFeaturePipe.calculate_features()`
- **功能**: 清洗並轉化為包含 DC, SL, PE 等多維度去量綱特徵。

### `MarketStateEncoder.encode(x)`
- **功能**: 提取市場狀態 Embedding。

### `CrossStockSearchEngine.search_analogies()`
- **功能**: 在全局資料庫中檢索相似瞬間，並執行「時間過濾」以防止未來函數。

## 📝 詳細回測規則與進出場設定 (Backtesting Rules)

### 1. 進場設定
- **回看視窗**: 20 個交易日。
- **搜索數量 (K)**: 100 個鄰居。
- **買入條件**: 5 日勝率 > 70% 且預期平均收益 > 1.5%。

### 2. 出場與風控
- **固定持有期**: 5 個交易日強制平倉。
- **異常退出**: 2 日內虧損 > 3% 止損。
- **動態更新**: 每日重搜，形態反轉時主動離場。

## 📊 視覺化展示邏輯 (Visualization)
1.  **Embedding 降維散點圖 (TSNE/UMAP)**: 觀察市場狀態聚類。
2.  **形態類比疊加圖 (Overlay Plot)**: 將當前走勢與 Top-5 歷史鄰居重疊展示。
3.  **預期收益分佈圖**: 鄰居未來表現的直方圖。

---
**核心函數參考**: [core_similarity.py](./core_similarity.py)
