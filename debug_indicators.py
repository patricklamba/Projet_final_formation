"""
Script de débogage pour identifier les problèmes d'indicateurs
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_indicator_individual():
    """Test chaque indicateur individuellement"""
    from indicators.bollinger_bands import BollingerBands
    from indicators.keltner_channel import KeltnerChannel
    from indicators.ema import EMA
    from indicators.rsi import RSI
    
    # Créer des données de test simples
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    print("🧪 TEST INDIVIDUEL DES INDICATEURS")
    print("=" * 50)
    
    # Test Bollinger Bands
    try:
        bb = BollingerBands()
        result_bb = bb.calculate(df)
        print("✅ BollingerBands: OK")
        print(f"   Colonnes ajoutées: {[col for col in result_bb.columns if 'bb_' in col]}")
    except Exception as e:
        print(f"❌ BollingerBands: ERREUR - {e}")
    
    # Test Keltner Channel
    try:
        kc = KeltnerChannel()
        result_kc = kc.calculate(df)
        print("✅ KeltnerChannel: OK")
        print(f"   Colonnes ajoutées: {[col for col in result_kc.columns if 'kc_' in col]}")
    except Exception as e:
        print(f"❌ KeltnerChannel: ERREUR - {e}")
    
    # Test EMA
    try:
        ema = EMA()
        result_ema = ema.calculate(df)
        print("✅ EMA: OK")
        print(f"   Colonnes ajoutées: {[col for col in result_ema.columns if 'ema_' in col]}")
    except Exception as e:
        print(f"❌ EMA: ERREUR - {e}")
    
    # Test RSI
    try:
        rsi = RSI()
        result_rsi = rsi.calculate(df)
        print("✅ RSI: OK")
        print(f"   Colonnes ajoutées: {[col for col in result_rsi.columns if 'rsi_' in col]}")
    except Exception as e:
        print(f"❌ RSI: ERREUR - {e}")

if __name__ == "__main__":
    test_indicator_individual()