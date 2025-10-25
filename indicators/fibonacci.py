"""
Fibonacci Retracement & Extension - Version Modulaire
"""
import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class Fibonacci(BaseIndicator):
    def __init__(self):
        self.retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.extension_levels = [1.272, 1.414, 1.618, 2.0, 2.618]
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les niveaux Fibonacci basés sur les derniers swing points"""
        df = df.copy()
        
        # Trouver les swing points récents
        df = self._find_swing_points(df)
        
        # Calculer les niveaux Fibonacci
        df = self._calculate_fibonacci_levels(df)
        
        return df
    
    def _find_swing_points(self, df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
        """Trouve les points de swing highs et lows"""
        df['swing_high'] = df['high'].rolling(window=window, center=True).max()
        df['swing_low'] = df['low'].rolling(window=window, center=True).min()
        
        # Identifier les swing points exacts
        df['is_swing_high'] = (df['high'] == df['swing_high'])
        df['is_swing_low'] = (df['low'] == df['swing_low'])
        
        return df
    
    def _calculate_fibonacci_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les niveaux de retracement Fibonacci"""
        
        # Trouver le dernier swing high et low significatif
        swing_highs = df[df['is_swing_high']]
        swing_lows = df[df['is_swing_low']]
        
        if len(swing_highs) > 0 and len(swing_lows) > 0:
            recent_high = swing_highs['high'].iloc[-1]
            recent_low = swing_lows['low'].iloc[-1]
            
            diff = recent_high - recent_low
            
            # Calcul des niveaux de retracement
            for level in self.retracement_levels:
                df[f'fib_r_{level}'] = recent_high - (diff * level)
            
            # Niveaux d'extension
            for level in self.extension_levels:
                df[f'fib_e_{level}'] = recent_low + (diff * level)
        
        return df
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur les réactions aux niveaux Fibonacci"""
        if current_index < 20:  # Besoin de suffisamment de données
            return 0
            
        current_price = df['close'].iloc[current_index]
        current_high = df['high'].iloc[current_index]
        current_low = df['low'].iloc[current_index]
        
        # Vérifier les réactions aux niveaux Fibonacci
        for level in self.retracement_levels:
            fib_level = df[f'fib_r_{level}'].iloc[current_index]
            
            # Tolérance de 0.1% autour du niveau
            tolerance = fib_level * 0.001
            
            # Rebond sur support Fibonacci
            if (abs(current_low - fib_level) <= tolerance and 
                current_price > current_low):
                return 1  # Signal haussier
                
            # Rejet sur résistance Fibonacci  
            elif (abs(current_high - fib_level) <= tolerance and 
                  current_price < current_high):
                return -1  # Signal baissier
                
        return 0