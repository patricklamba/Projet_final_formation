"""
Keltner Channel Indicator - VERSION MODULAIRE CORRIGÉE
"""

import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class KeltnerChannel(BaseIndicator):
    def __init__(self, ema_period: int = 20, atr_period: int = 10, atr_multiplier: float = 1.5):
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule le canal de Keltner et retourne le DataFrame modifié
        """
        required_cols = {'high', 'low', 'close'}
        if not required_cols.issubset(data.columns):
            raise ValueError(f"La DataFrame doit contenir les colonnes {required_cols}.")

        df = data.copy()
        
        # Ligne centrale (EMA du prix typique)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        df['kc_middle'] = typical_price.ewm(span=self.ema_period, adjust=False).mean()

        # Calcul ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        true_range = np.maximum(np.maximum(high_low, high_close), low_close)
        atr = true_range.rolling(window=self.atr_period).mean()

        # Bandes
        df['kc_upper'] = df['kc_middle'] + (atr * self.atr_multiplier)
        df['kc_lower'] = df['kc_middle'] - (atr * self.atr_multiplier)
        
        # Position relative du prix dans le canal
        df['kc_position'] = (df['close'] - df['kc_lower']) / (df['kc_upper'] - df['kc_lower'])
        df['kc_width'] = (df['kc_upper'] - df['kc_lower']) / df['kc_middle'] * 100
        
        return df  # ← IMPORTANT: Retourner le DataFrame, pas un tuple !

    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """
        Retourne le signal de trading basé sur le Keltner Channel
        Returns: 1 (ACHAT), -1 (VENTE), 0 (NEUTRE)
        """
        if current_index < max(self.ema_period, self.atr_period):
            return 0

        current_row = df.iloc[current_index]
        prev_row = df.iloc[current_index - 1] if current_index > 0 else None

        # Signal d'achat: Prix touche la bande inférieure + rebond
        if (current_row['close'] <= current_row['kc_lower'] and 
            prev_row is not None and current_row['close'] > prev_row['close']):
            return 1
            
        # Signal de vente: Prix touche la bande supérieure + rejet
        elif (current_row['close'] >= current_row['kc_upper'] and 
              prev_row is not None and current_row['close'] < prev_row['close']):
            return -1
            
        # Signal faible: Prix proche des bandes
        elif current_row['kc_position'] <= 0.1:  # Proche de la bande inférieure
            return 0.5
        elif current_row['kc_position'] >= 0.9:  # Proche de la bande supérieure
            return -0.5
            
        return 0