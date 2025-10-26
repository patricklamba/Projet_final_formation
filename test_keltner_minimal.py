# test_keltner_simple.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_keltner_simple():
    """Test simplifié sans héritage pour debug"""
    
    # Créer une version simplifiée sans héritage
    class SimpleKeltner:
        def __init__(self, ema_period=10, atr_period=5, verbose=True):
            self.ema_period = ema_period
            self.atr_period = atr_period
            self.verbose = verbose
            
        def calculate(self, df):
            print("✅ Méthode calculate appelée avec succès!")
            # Simuler un calcul simple
            df['kc_middle'] = df['close'].rolling(window=self.ema_period).mean()
            df['kc_upper'] = df['kc_middle'] + 2
            df['kc_lower'] = df['kc_middle'] - 2
            return df
    
    # Données de test
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(10)]
    df = pd.DataFrame({
        "open": range(100, 110),
        "high": range(102, 112), 
        "low": range(98, 108),
        "close": range(101, 111),
    }, index=pd.to_datetime(dates))
    
    # Test
    kc = SimpleKeltner()
    result = kc.calculate(df)
    
    print("✅ Test réussi!")
    print(result.tail())
    return True

if __name__ == "__main__":
    test_keltner_simple()