"""
Bollinger Bands Indicator
-------------------------
Calcule les bandes de Bollinger pour une série de prix.
"""

import pandas as pd

class BollingerBands:
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev

    def calculate(self, data: pd.DataFrame):
        """
        Calcule les bandes de Bollinger.
        Retourne 3 séries: (middle_band, upper_band, lower_band)
        """
        if 'close' not in data.columns:
            raise ValueError("La DataFrame doit contenir une colonne 'close'.")

        df = data.copy()
        middle_band = df['close'].rolling(window=self.period).mean()
        bb_std = df['close'].rolling(window=self.period).std(ddof=0)
        upper_band = middle_band + (self.std_dev * bb_std)
        lower_band = middle_band - (self.std_dev * bb_std)
        
        return middle_band, upper_band, lower_band