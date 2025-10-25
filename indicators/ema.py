"""
Exponential Moving Average (EMA) Indicator - CORRIGÉ
"""
import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class EMA(BaseIndicator):
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les EMA fast et slow - VERSION CORRIGÉE"""
        # S'assurer qu'on travaille sur une copie
        df = df.copy() if hasattr(df, 'copy') else df
        
        # EMA rapide
        df['ema_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        
        # EMA lent
        df['ema_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Croisement des EMA
        df['ema_cross'] = 0
        df.loc[df['ema_fast'] > df['ema_slow'], 'ema_cross'] = 1
        df.loc[df['ema_fast'] < df['ema_slow'], 'ema_cross'] = -1
        
        # Distance relative
        df['ema_distance'] = (df['ema_fast'] - df['ema_slow']) / df['ema_slow'] * 100
        
        return df
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur le croisement des EMA"""
        if current_index < max(self.fast_period, self.slow_period):
            return 0
            
        current_row = df.iloc[current_index]
        prev_row = df.iloc[current_index - 1] if current_index > 0 else None
        
        # Signal haussier: EMA fast croise au-dessus de EMA slow
        if (current_row['ema_cross'] == 1 and 
            prev_row is not None and prev_row['ema_cross'] == -1):
            return 1
            
        # Signal baissier: EMA fast croise en-dessous de EMA slow
        elif (current_row['ema_cross'] == -1 and 
              prev_row is not None and prev_row['ema_cross'] == 1):
            return -1
            
        # Signal de suivi de tendance
        elif current_row['ema_cross'] == 1 and current_row['ema_distance'] > 0.5:
            return 0.5  # Signal faible haussier
            
        elif current_row['ema_cross'] == -1 and current_row['ema_distance'] < -0.5:
            return -0.5  # Signal faible baissier
            
        return 0