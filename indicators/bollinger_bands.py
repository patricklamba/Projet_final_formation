# indicators/bollinger_bands.py
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from stock_indicators import indicators
from stock_indicators.indicators.common import Quote
from .base_indicator import BaseIndicator

class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, std_dev: float = 2.0, strategy_type: str = "breakout"):
        self.period = period
        self.std_dev = std_dev
        self.strategy_type = strategy_type
        
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les Bollinger Bands avec StockIndicators - Version robuste"""
        df = df.copy()
        
        # 1️⃣ Nettoyage des données
        required_cols = ["open", "high", "low", "close"]
        df = df.dropna(subset=required_cols)
        
        if len(df) < self.period:
            return df
            
        # 2️⃣ Préparation des quotes pour StockIndicators
        quotes = []
        for i in range(len(df)):
            row = df.iloc[i]  # ✅ Utilisation correcte de iloc
            # Gestion robuste des dates
            if pd.api.types.is_datetime64_any_dtype(df.index):
                date_val = df.index[i]
            elif 'date' in df.columns:
                date_val = row['date']
            else:
                date_val = i
                
            quotes.append(Quote(
                date=date_val,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row.get('volume', 0))
            ))
        
        # 3️⃣ Calcul avec StockIndicators
        try:
            bollinger_results = indicators.get_bollinger_bands(quotes, self.period, self.std_dev)
        except AttributeError:
            bollinger_results = indicators.bollinger_bands(quotes, self.period, self.std_dev)
        
        # 4️⃣ Extraction des résultats
        df['bb_middle'] = [x.sma if x else np.nan for x in bollinger_results]
        df['bb_upper'] = [x.upper_band if x else np.nan for x in bollinger_results]
        df['bb_lower'] = [x.lower_band if x else np.nan for x in bollinger_results]
        
        # 5️⃣ Calculs métier existants
        width = df['bb_upper'] - df['bb_lower']
        df['bb_bandwidth'] = np.where(df['bb_middle'] != 0, width / df['bb_middle'], np.nan)
        df['bb_position'] = np.where(width != 0, (df['close'] - df['bb_lower']) / width, 0.5)

        return df

    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """Retourne le signal selon la stratégie configurée"""
        if current_index < self.period:
            return 0

        # ✅ CORRECTION : Utilisation correcte de iloc avec conversion
        current_index = int(current_index)  # S'assurer que c'est un entier
        cur = df.iloc[current_index]
        prev = df.iloc[current_index - 1]

        # STRATÉGIE BREAKOUT (défaut)
        if (cur['close'] > cur['bb_upper']) and (prev['close'] < cur['bb_upper'] * 1.001):
            return 1   # Cassure haute → Achat
        if (cur['close'] < cur['bb_lower']) and (prev['close'] > cur['bb_lower'] * 0.999):
            return -1  # Cassure basse → Vente

        return 0

    def get_detailed_signal(self, df: pd.DataFrame, current_index: int) -> Dict[str, Any]:
        """Version étendue avec score de confiance"""
        # ✅ CORRECTION : Conversion en entier
        current_index = int(current_index)
        base_signal = self.get_signal(df, current_index)
        
        if current_index < self.period:
            return {"signal": 0, "confidence": 0.0, "position": 0.5}
        
        cur = df.iloc[current_index]  # ✅ Maintenant current_index est un entier
        
        # Score de confiance basé sur la position dans les bandes
        confidence = abs(cur['bb_position'] - 0.5) * 2
        
        return {
            "signal": base_signal,
            "confidence": round(confidence, 3),
            "position": round(cur['bb_position'], 3),
            "bandwidth": round(cur.get('bb_bandwidth', 0), 6)
        }

    def get_name(self) -> str:
        return f"BollingerBands_{self.period}_{self.std_dev}_{self.strategy_type}"