# indicators/keltner_channel.py
import numpy as np
import pandas as pd
from .base_indicator import BaseIndicator

class KeltnerChannel(BaseIndicator):
    def __init__(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 1.5):
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        typical = (df['high'] + df['low'] + df['close']) / 3.0
        df['kc_middle'] = typical.ewm(span=self.ema_period, adjust=False).mean()

        # True Range
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift(1)).abs()
        low_close = (df['low'] - df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Wilder ATR (EMA with alpha=1/n)
        atr = tr.ewm(alpha=1.0/self.atr_period, adjust=False).mean()
        df['kc_atr'] = atr

        df['kc_upper'] = df['kc_middle'] + atr * self.atr_multiplier
        df['kc_lower'] = df['kc_middle'] - atr * self.atr_multiplier

        width = df['kc_upper'] - df['kc_lower']
        df['kc_position'] = np.where(width != 0, (df['close'] - df['kc_lower']) / width, 0.5)
        df['kc_width_pct'] = np.where(df['kc_middle'] != 0, width / df['kc_middle'] * 100, np.nan)

        return df

    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        if current_index < max(self.ema_period, self.atr_period):
            return 0

        cur = df.iloc[current_index]
        prev = df.iloc[current_index - 1]

        if (cur['close'] > cur['kc_upper']) and (prev['close'] <= prev['kc_upper']):
            return 1
        if (cur['close'] < cur['kc_lower']) and (prev['close'] >= prev['kc_lower']):
            return -1
        return 0
