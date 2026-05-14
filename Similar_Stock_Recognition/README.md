# 🌌 美股全市場相似性識別與類比交易藍圖 (Cross-Stock Analogous Search)

## 📌 核心想法
傳統的相似天數信號僅在單一資產的歷史中尋找規律。本策略將其擴展為「全市場類比」：當 Apple 出現某個特定的走勢形態時，我們在美股歷史長河（如 S&P 500 十年數據）中尋找所有表現最像 Apple 當下狀態的時刻（不限於 Apple，可能是 2018 年的 Amazon 或 2021 年的 Tesla），利用這些「類比瞬間」後的群體表現來預測未來。

## 🛠 策略組件

### 1. 跨股票特徵流水線 (Scale-Invariant Features)
為了讓不同價格、不同市值的股票能在一起比較，我們提取以下特徵：
- **收益率結構**: 過去 5, 20, 60 日的對數收益。
- **相對位置**: 當前價相對於週、月、季高低點的百分比位置。
- **能量指標**: 成交量相對於自身均線的放大倍數。
- **波動狀態**: 歸一化的歷史波動率。

### 2. 市場狀態編碼器 (LSTM Autoencoder)
- 將 20 天的高維時序特徵序列壓縮成一個 16 維的 **「Embedding (z_t)」**。
- 這個向量就像是該股票當前走勢的「數字指紋」。

### 3. 全局向量檢索引擎 (Vector Search Engine)
- 使用 **FAISS** 建立一個包含數百萬條歷史狀態的檢索索引。
- 每一條記錄包含 `(Ticker, Date, Embedding_Vector)`。

### 4. 類比推理與信號 (Inference)
- **檢索**: 為目標股票尋找 Top-K 個歐式距離最近的歷史鄰居。
- **過濾**: 剔除所有發生在「當前目標日期」之後的數據，確保回測有效性。
- **預測**: 統計這 K 個鄰居在 1 天、5 天後的平均收益率與勝率。
- **信號**: 若 80% 的類比瞬間在隨後 5 天內都是上漲的，則觸發買入信號。

## 🔢 核心公式 (Core Formulas)

### 1. 歐式空間相似度 (Similarity Metric)
在 Embedding 空間中，兩次市場狀態 $z_A$ 與 $z_B$ 的距離計算為：
$$d(z_A, z_B) = \sqrt{\sum_{i=1}^{16} (z_{A,i} - z_{B,i})^2}$$
距離越小，表示形態越相似。

### 2. 類比勝率預測 (Expectation)
$$WinRate = \frac{Count(Return_{K, t+1} > 0)}{K}$$
其中 $K$ 為最相似的鄰居數量。

## 📖 核心函數說明 (API Reference)

### `UniversalFeaturePipe.calculate_features(df, windows=[5, 20, 60])`
- **功能**: 將原始 OHLCV 數據清洗並轉化為去量綱的形態特徵，確保不同股票可比較。
- **輸入**: 
    - `df`: 包含 Open, High, Low, Close, Volume 的原始數據。
    - `windows`: 計算收益與波動的週期。
- **輸出**: 返回包含歸一化特徵的 DataFrame。

### `MarketStateEncoder.encode(x)`
- **功能**: 將一段時間的時序特徵 (Sequence) 壓縮為 Embedding 向量。
- **輸入**: 
    - `x` (Tensor): 形狀為 `(Batch, Seq_Len, Features)` 的張量。
- **輸出**: 
    - `z` (Tensor): 16 維的狀態 Embedding。

### `CrossStockSearchEngine.add_to_index(embeddings, tickers, dates)`
- **功能**: 將美股池中所有股票的歷史 Embedding 存入向量索引庫。
- **輸入**: 
    - `embeddings` (ndarray): 所有歷史時刻的向量矩陣。
    - `tickers`: 與向量對應的股票代碼清單。
    - `dates`: 與向量對應的日期清單。

### `CrossStockSearchEngine.search_analogies(query_embedding, k=10, target_date=None)`
- **功能**: 在全局資料庫中尋找最像「當前走勢」的 K 個歷史瞬間。
- **輸入**: 
    - `query_embedding`: 當前的狀態向量。
    - `k`: 要找的鄰居數量。
    - `target_date`: 當前日期（用於過濾掉未來的數據）。
- **輸出**: 返回包含 `ticker` 與 `date` 的相似對象列表。

## 📊 視覺化展示邏輯 (Visualization)
1.  ** Embedding 降維散點圖 (TSNE/UMAP)**: 將 16 維狀態降至 2 維，觀察不同市場時期（如牛市、熊盤）是否在空間中形成明顯的聚類。
2.  **形態類比疊加圖 (Overlay Plot)**: 將當前標的的 20 日走勢與檢索出的 Top-5 最相似歷史走勢疊加在一起，直觀驗證「形態相似度」。
3.  **預期收益分佈圖**: 展示 K 個鄰居在未來 1-10 天的收益分佈，幫助判斷預測的置信度。

---
**核心代碼參考**: [core_similarity.py](./core_similarity.py)
