import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

class UniversalFeaturePipe:
    """
    通用特徵流水線：將原始數據轉化為「跨股票可比」的形態特徵
    """
    @staticmethod
    def calculate_features(df, windows=[5, 20, 60]):
        df = df.copy()
        # 1. 價格結構 (使用百分比/對數，確保 Apple 與 Tesla 可比)
        for d in windows:
            df[f'log_ret_{d}d'] = np.log(df['Close'] / df['Close'].shift(d))
            roll_high = df['High'].rolling(d).max()
            roll_low = df['Low'].rolling(d).min()
            df[f'dist_high_{d}d'] = (df['Close'] - roll_high) / roll_high
            df[f'dist_low_{d}d'] = (df['Close'] - roll_low) / roll_low
            
        # 2. 波動率 (年化波動)
        df['vol_20d'] = df['Close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        # 3. 相對成交量 (當前量 / 均量)
        df['rel_vol'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # 4. 技術指標 (RSI 等)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['rsi_14d'] = 100 - (100 / (1 + rs))
        
        return df.dropna()

class MarketStateEncoder(nn.Module):
    """
    時序自編碼器：將 N 天的走勢壓縮為一個 Embedding 向量 (z_t)
    """
    def __init__(self, input_dim, seq_len, hidden_dim=64, embedding_dim=16):
        super(MarketStateEncoder, self).__init__()
        self.seq_len = seq_len
        self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.encoder_fc = nn.Linear(hidden_dim, embedding_dim)
        
        self.decoder_fc = nn.Linear(embedding_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(hidden_dim, input_dim, batch_first=True)

    def encode(self, x):
        _, (hidden, _) = self.encoder_lstm(x)
        z = self.encoder_fc(hidden[-1])
        return z

    def forward(self, x):
        z = self.encode(x)
        # Decoder 邏輯用於無監督訓練
        h_seq = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        hidden = self.decoder_fc(h_seq)
        out, _ = self.decoder_lstm(hidden)
        return out, z

class CrossStockSearchEngine:
    """
    跨股票相似性檢索引擎
    """
    def __init__(self, embedding_dim=16):
        self.index = None # 建議使用 faiss.IndexFlatL2
        self.metadata = [] # 儲存 (Ticker, Date) 對應關係

    def add_to_index(self, embeddings, tickers, dates):
        """
        將多隻股票的歷史 Embedding 全部打入全局索引
        embeddings: np.array (Total_Days, Embedding_Dim)
        """
        if self.index is None:
            import faiss
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        
        self.index.add(embeddings.astype('float32'))
        for t, d in zip(tickers, dates):
            self.metadata.append({'ticker': t, 'date': d})

    def search_analogies(self, query_embedding, k=10, target_date=None):
        """
        在全局歷史中尋找最相似的 K 個瞬間
        """
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx in indices[0]:
            match = self.metadata[idx]
            # 嚴格過濾：相似時刻必須發生在目標日期之前 (避免未來函數)
            if target_date is None or match['date'] < target_date:
                results.append(match)
        
        return results
