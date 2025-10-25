"""
Bollinger Bands - Version modulaire
"""
import pandas as pd
from .base_indicator import BaseIndicator

class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les bandes de Bollinger"""
        df = df.copy()
        
        # Moyenne mobile
        df['bb_middle'] = df['close'].rolling(window=self.period).mean()
        
        # Écart-type
        bb_std = df['close'].rolling(window=self.period).std(ddof=0)
        
        # Bandes supérieure et inférieure
        df['bb_upper'] = df['bb_middle'] + (self.std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (self.std_dev * bb_std)
        
        # Bandwidth et position
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur la position par rapport aux bandes"""
        if current_index < self.period:
            return 0
            
        current_row = df.iloc[current_index]
        prev_row = df.iloc[current_index - 1]
        
        # Signal d'achat: prix touche la bande inférieure + momentum
        if (current_row['close'] <= current_row['bb_lower'] and 
            current_row['close'] > prev_row['close']):
            return 1
            
        # Signal de vente: prix touche la bande supérieure + momentum  
        elif (current_row['close'] >= current_row['bb_upper'] and 
              current_row['close'] < prev_row['close']):
            return -1
            
        return 0