"""
Relative Strength Index (RSI) Indicator
"""
import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class RSI(BaseIndicator):
    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule le RSI"""
        df = df.copy()
        
        # Calcul du RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Signaux de surachat/survente
        df['rsi_overbought'] = (df['rsi'] >= self.overbought).astype(int)
        df['rsi_oversold'] = (df['rsi'] <= self.oversold).astype(int)
        
        # Divergences (simplifié)
        df['rsi_high'] = df['rsi'].rolling(window=5).max()
        df['rsi_low'] = df['rsi'].rolling(window=5).min()
        
        return df
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur le RSI"""
        if current_index < self.period:
            return 0
            
        current_rsi = df['rsi'].iloc[current_index]
        prev_rsi = df['rsi'].iloc[current_index - 1] if current_index > 0 else current_rsi
        
        # Signal d'achat: RSI sort de la zone de survente
        if (prev_rsi <= self.oversold and current_rsi > self.oversold and
            current_rsi > prev_rsi):
            return 1
            
        # Signal de vente: RSI sort de la zone de surachat
        elif (prev_rsi >= self.overbought and current_rsi < self.overbought and
              current_rsi < prev_rsi):
            return -1
            
        # Signal faible: RSI en zone extrême mais pas encore de sortie
        elif current_rsi <= self.oversold:
            return 0.5  # Préparation achat
            
        elif current_rsi >= self.overbought:
            return -0.5  # Préparation vente
            
        return 0