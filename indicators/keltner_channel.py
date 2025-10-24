"""
Keltner Channel Indicator
-------------------------
Calcule le canal de Keltner
"""

import pandas as pd
import numpy as np

class KeltnerChannel:
    def __init__(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 1.5):
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def calculate(self, data: pd.DataFrame):
        """
        Calcule le canal de Keltner.
        Retourne 3 séries: (middle_line, upper_band, lower_band)
        """
        required_cols = {'high', 'low', 'close'}
        if not required_cols.issubset(data.columns):
            raise ValueError(f"La DataFrame doit contenir les colonnes {required_cols}.")

        df = data.copy()
        
        # Ligne centrale (EMA du prix typique)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        middle_line = typical_price.ewm(span=self.ema_period, adjust=False).mean()

        # Calcul ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        true_range = np.maximum(np.maximum(high_low, high_close), low_close)
        atr = true_range.rolling(window=self.atr_period).mean()

        # Bandes
        upper_band = middle_line + (atr * self.atr_multiplier)
        lower_band = middle_line - (atr * self.atr_multiplier)
        
        return middle_line, upper_band, lower_band