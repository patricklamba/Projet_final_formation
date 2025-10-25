"""
Japanese Candlestick Patterns - Version Modulaire
"""
import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class CandlestickPatterns(BaseIndicator):
    def __init__(self):
        self.patterns = []
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Détecte les patterns de chandeliers japonais"""
        df = df.copy()
        
        # Initialiser les colonnes de patterns
        df['candle_pattern'] = 'NONE'
        df['candle_signal'] = 0
        
        # Détecter les patterns pour chaque bougie
        for i in range(1, len(df)):
            patterns = self._detect_all_patterns(df, i)
            if patterns:
                df.loc[df.index[i], 'candle_pattern'] = ','.join(patterns)
                df.loc[df.index[i], 'candle_signal'] = self._patterns_to_signal(patterns)
        
        return df
    
    def _detect_all_patterns(self, df: pd.DataFrame, i: int) -> list:
        """Détecte tous les patterns pour une bougie donnée"""
        patterns = []
        
        open_price = df['open'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        close = df['close'].iloc[i]
        
        # Doji
        if self._is_doji(open_price, high, low, close):
            patterns.append("DOJI")
        
        # Hammer / Hanging Man
        hammer_signal = self._is_hammer(open_price, high, low, close)
        if hammer_signal:
            patterns.append(hammer_signal)
        
        # Engulfing
        engulfing_signal = self._is_engulfing(df, i)
        if engulfing_signal != "NONE":
            patterns.append(engulfing_signal)
            
        # Morning/Evening Star (simplifié)
        star_signal = self._is_star_pattern(df, i)
        if star_signal != "NONE":
            patterns.append(star_signal)
            
        return patterns
    
    def _is_doji(self, open_price: float, high: float, low: float, close: float, threshold: float = 0.1) -> bool:
        """Détecte un Doji"""
        body_size = abs(close - open_price)
        total_range = high - low
        return body_size <= (total_range * threshold) if total_range > 0 else False
    
    def _is_hammer(self, open_price: float, high: float, low: float, close: float) -> str:
        """Détecte Hammer ou Hanging Man"""
        body_size = abs(close - open_price)
        lower_shadow = min(open_price, close) - low
        upper_shadow = high - max(open_price, close)
        
        # Hammer (marteau) - signal haussier
        if (lower_shadow >= 2 * body_size and 
            upper_shadow <= body_size * 0.5):
            return "HAMMER"
            
        # Shooting Star - signal baissier
        elif (upper_shadow >= 2 * body_size and 
              lower_shadow <= body_size * 0.5):
            return "SHOOTING_STAR"
            
        return ""
    
    def _is_engulfing(self, df: pd.DataFrame, i: int) -> str:
        """Détecte un pattern Engulfing"""
        if i < 1:
            return "NONE"
            
        prev_open, prev_close = df['open'].iloc[i-1], df['close'].iloc[i-1]
        curr_open, curr_close = df['open'].iloc[i], df['close'].iloc[i]
        
        prev_body = abs(prev_close - prev_open)
        curr_body = abs(curr_close - curr_open)
        
        # Bullish Engulfing
        if (prev_close < prev_open and curr_close > curr_open and
            curr_body > prev_body and curr_open < prev_close and curr_close > prev_open):
            return "BULLISH_ENGULFING"
        
        # Bearish Engulfing  
        elif (prev_close > prev_open and curr_close < curr_open and
              curr_body > prev_body and curr_open > prev_close and curr_close < prev_open):
            return "BEARISH_ENGULFING"
            
        return "NONE"
    
    def _is_star_pattern(self, df: pd.DataFrame, i: int) -> str:
        """Détecte les patterns Morning/Evening Star (simplifié)"""
        if i < 2:
            return "NONE"
            
        # Morning Star (haussier)
        if (df['close'].iloc[i-2] < df['open'].iloc[i-2] and  # Première bougie baissière
            self._is_doji(df['open'].iloc[i-1], df['high'].iloc[i-1], 
                         df['low'].iloc[i-1], df['close'].iloc[i-1]) and  # Doji
            df['close'].iloc[i] > df['open'].iloc[i] and  # Bougie haussière
            df['close'].iloc[i] > df['close'].iloc[i-2]):  # Dépassement
            return "MORNING_STAR"
            
        # Evening Star (baissier)
        elif (df['close'].iloc[i-2] > df['open'].iloc[i-2] and  # Première bougie haussière
              self._is_doji(df['open'].iloc[i-1], df['high'].iloc[i-1], 
                           df['low'].iloc[i-1], df['close'].iloc[i-1]) and  # Doji
              df['close'].iloc[i] < df['open'].iloc[i] and  # Bougie baissière
              df['close'].iloc[i] < df['close'].iloc[i-2]):  # Dépassement
            return "EVENING_STAR"
            
        return "NONE"
    
    def _patterns_to_signal(self, patterns: list) -> int:
        """Convertit les patterns en signal numérique"""
        bullish_patterns = ["HAMMER", "BULLISH_ENGULFING", "MORNING_STAR"]
        bearish_patterns = ["SHOOTING_STAR", "BEARISH_ENGULFING", "EVENING_STAR"]
        
        bull_count = sum(1 for p in patterns if p in bullish_patterns)
        bear_count = sum(1 for p in patterns if p in bearish_patterns)
        
        if bull_count > bear_count:
            return 1
        elif bear_count > bull_count:
            return -1
        else:
            return 0
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur les patterns de chandeliers"""
        if current_index < 2:
            return 0
            
        return df['candle_signal'].iloc[current_index]