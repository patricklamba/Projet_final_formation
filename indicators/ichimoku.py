"""
Ichimoku Cloud Indicator - Version Modulaire
"""
import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator

class Ichimoku(BaseIndicator):
    def __init__(self, tenkan_period: int = 9, kijun_period: int = 26, senkou_period: int = 52):
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_period = senkou_period
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule toutes les composantes de l'Ichimoku Cloud"""
        df = df.copy()
        
        # Tenkan-sen (Conversion Line)
        tenkan_high = df['high'].rolling(window=self.tenkan_period).max()
        tenkan_low = df['low'].rolling(window=self.tenkan_period).min()
        df['tenkan_sen'] = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line)
        kijun_high = df['high'].rolling(window=self.kijun_period).max()
        kijun_low = df['low'].rolling(window=self.kijun_period).min()
        df['kijun_sen'] = (kijun_high + kijun_low) / 2
        
        # Senkou Span A (Leading Span A)
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(self.kijun_period)
        
        # Senkou Span B (Leading Span B)
        senkou_b_high = df['high'].rolling(window=self.senkou_period).max()
        senkou_b_low = df['low'].rolling(window=self.senkou_period).min()
        df['senkou_span_b'] = ((senkou_b_high + senkou_b_low) / 2).shift(self.kijun_period)
        
        # Chikou Span (Lagging Span)
        df['chikou_span'] = df['close'].shift(-self.kijun_period)
        
        # Nuage (Kumo)
        df['kumo_top'] = df[['senkou_span_a', 'senkou_span_b']].max(axis=1)
        df['kumo_bottom'] = df[['senkou_span_a', 'senkou_span_b']].min(axis=1)
        df['in_kumo'] = (df['close'] <= df['kumo_top']) & (df['close'] >= df['kumo_bottom'])
        
        return df
    
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Signal basé sur la configuration Ichimoku"""
        if current_index < self.senkou_period:
            return 0
            
        current = df.iloc[current_index]
        price = current['close']
        
        # Position par rapport au nuage
        above_cloud = price > current['kumo_top']
        below_cloud = price < current['kumo_bottom']
        in_cloud = current['in_kumo']
        
        # Configuration Tenkan/Kijun
        tenkan_above_kijun = current['tenkan_sen'] > current['kijun_sen']
        tenkan_below_kijun = current['tenkan_sen'] < current['kijun_sen']
        
        # Signal haussier fort: Prix au-dessus du nuage + Tenkan > Kijun
        if above_cloud and tenkan_above_kijun:
            return 1
            
        # Signal baissier fort: Prix en-dessous du nuage + Tenkan < Kijun
        elif below_cloud and tenkan_below_kijun:
            return -1
            
        # Signal haussier modéré: Dans le nuage mais configuration positive
        elif in_cloud and tenkan_above_kijun:
            return 0.5
            
        # Signal baissier modéré: Dans le nuage mais configuration négative
        elif in_cloud and tenkan_below_kijun:
            return -0.5
            
        return 0