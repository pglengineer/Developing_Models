import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

class UniversalFeaturePipe:
    """
    增強型美股特徵流水線：包含市值、產業、成交量排名等
    """
    @staticmethod
    def calculate_features(df, market_cap=None, sector=None, windows=[5, 20, 60]):
        df = df.copy()
        
        # 1. 趨勢連續性 (核心三因子)
        # DC, SL, PE 邏輯
        log_ret = np.log(df['Close'] / df['Close'].shift(1))
        df['dc_5d'] = (log_ret > 0).rolling(5).mean() # 方向一致性
        # 連續長度 (簡化版)
        df['sl_3d'] = (np.sign(log_ret) == np.sign(log_ret.shift(1))).astype(int).rolling(3).sum() / 3.0
        # 路徑效率
        df['pe_5d'] = df['Close'].diff(5).abs() / df['Close'].diff().abs().rolling(5).sum()
        
        # 2. 市值與產業 (靜態/外部特徵)
        if market_cap is not None:
            df['mkt_cap_log'] = np.log(market_cap)
        if sector is not None:
            df['sector_code'] = sector # 建議傳入類別編碼
            
        # 3. 波動度變化
        for d in [5, 20]:
            df[f'vol_{d}d'] = df['Close'].pct_change().rolling(d).std() * np.sqrt(252)
        df['vol_change'] = df['vol_5d'] / df['vol_20d'] # 近期波動變化
            
        # 4. 成交量多維度
        df['vol_ma_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        # 注意：成交量排名 (Volume Rank) 需要在 Cross-Sectional 級別計算，此處預留欄位
        
        # 5. 常用技術指標
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi_14'] = 100 - (100 / (1 + gain/loss.replace(0, np.nan)))
        
        # 布林帶寬度
        df['bb_width'] = (df['Close'].rolling(20).std() * 4) / df['Close'].rolling(20).mean()
        
        return df.dropna()

    @staticmethod
    def calculate_cross_sectional_rank(master_df):
        """
        在所有股票池中計算橫截面排名 (成交量占比、量能排名等)
        master_df: 包含多隻股票數據的 Long-format DataFrame
        """
        # 成交量占比 (與昨日全市場總成交量比)
        total_market_vol = master_df.groupby(level=0)['Volume'].transform('sum')
        master_df['vol_market_share'] = master_df['Volume'] / total_market_vol
        
        # 成交量百分位排名
        master_df['vol_rank'] = master_df.groupby(level=0)['Volume'].rank(pct=True)
        
        return master_df

class MarketStateEncoder(nn.Module):
    """
    時序自編碼器 (保持結構，輸入維度隨特徵增加而變)
    """
    def __init__(self, input_dim, seq_len, hidden_dim=128, embedding_dim=32):
        super(MarketStateEncoder, self).__init__()
        self.seq_len = seq_len
        self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True, num_layers=2)
        self.encoder_fc = nn.Linear(hidden_dim, embedding_dim)
        
        self.decoder_fc = nn.Linear(embedding_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(hidden_dim, input_dim, batch_first=True, num_layers=2)

    def encode(self, x):
        _, (hidden, _) = self.encoder_lstm(x)
        return self.encoder_fc(hidden[-1])

    def forward(self, x):
        z = self.encode(x)
        h_seq = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        hidden = self.decoder_fc(h_seq)
        out, _ = self.decoder_lstm(hidden)
        return out, z
