"""
Keltner Channel Indicator
-------------------------
Calcule le canal de Keltner basé sur :
- EMA du prix typique (close)
- ATR (Average True Range)
"""

import pandas as pd
import numpy as np

class KeltnerChannel:
    def __init__(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 1.5):
        """
        Initialise les paramètres du canal de Keltner.
        :param ema_period: période de l'EMA (par défaut 20)
        :param atr_period: période du calcul de l'ATR (par défaut 10)
        :param atr_multiplier: multiplicateur de l'ATR (par défaut 1.5)
        """
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule le canal de Keltner sur une DataFrame avec colonnes ['high', 'low', 'close'].
        Retourne une DataFrame avec colonnes ['KC_Middle', 'KC_Upper', 'KC_Lower'].
        """
        required_cols = {'high', 'low', 'close'}
        if not required_cols.issubset(data.columns):
            raise ValueError(f"La DataFrame doit contenir les colonnes {required_cols}.")

        df = data.copy()
        df['TP'] = (df['high'] + df['low'] + df['close']) / 3
        df['KC_Middle'] = df['TP'].ewm(span=self.ema_period, adjust=False).mean()

        # Calcul de l’ATR
        df['H-L'] = df['high'] - df['low']
        df['H-PC'] = np.abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = np.abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=self.atr_period).mean()

        # Bornes du canal
        df['KC_Upper'] = df['KC_Middle'] + (df['ATR'] * self.atr_multiplier)
        df['KC_Lower'] = df['KC_Middle'] - (df['ATR'] * self.atr_multiplier)

        df.drop(columns=['TP', 'H-L', 'H-PC', 'L-PC', 'TR', 'ATR'], inplace=True)
        return df
