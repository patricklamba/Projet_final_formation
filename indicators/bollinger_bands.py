# indicators/bollinger_bands.py
import numpy as np
import pandas as pd
from .base_indicator import BaseIndicator

class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['bb_middle'] = df['close'].rolling(window=self.period).mean()
        bb_std = df['close'].rolling(window=self.period).std(ddof=0)
        df['bb_upper'] = df['bb_middle'] + (self.std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (self.std_dev * bb_std)

        # protections
        width = df['bb_upper'] - df['bb_lower']
        df['bb_bandwidth'] = np.where(df['bb_middle'] != 0, width / df['bb_middle'], np.nan)
        df['bb_position'] = np.where(width != 0, (df['close'] - df['bb_lower']) / width, 0.5)

        return df

    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        if current_index < self.period:
            return 0

        cur = df.iloc[current_index]
        prev = df.iloc[current_index - 1]

        # CONDITIONS ASSOUPLIES :
        # Breakout haut : clôture actuelle AU-DESSUS de BB supérieure
        # ET clôture précédente PROCHE ou EN-DESSOUS
        if (cur['close'] > cur['bb_upper']) and (prev['close'] < cur['bb_upper'] * 1.001):  # 0.1% de tolérance
            return 1

        # Breakout bas : clôture actuelle EN-DESSOUS de BB inférieure  
        # ET clôture précédente PROCHE ou AU-DESSUS
        if (cur['close'] < cur['bb_lower']) and (prev['close'] > cur['bb_lower'] * 0.999):
            return -1

        return 0
