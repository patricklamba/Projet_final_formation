"""
Test spécifique pour vérifier la correction de Keltner Channel
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_keltner_fixed():
    """Test que Keltner Channel retourne bien un DataFrame"""
    print("🧪 TEST CORRECTION KELTNER CHANNEL")
    print("=" * 50)
    
    try:
        from indicators.keltner_channel import KeltnerChannel
        
        # Créer des données de test
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        df = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        print("📊 Données de test créées")
        
        # Test Keltner Channel
        kc = KeltnerChannel()
        result = kc.calculate(df)
        
        # Vérifier que c'est un DataFrame
        if isinstance(result, pd.DataFrame):
            print("✅ KeltnerChannel retourne un DataFrame")
            
            # Vérifier les colonnes ajoutées
            kc_columns = [col for col in result.columns if 'kc_' in col]
            print(f"✅ Colonnes Keltner: {kc_columns}")
            
            # Vérifier les signaux
            signals = []
            for i in range(20, min(50, len(result))):
                signal = kc.get_signal(result, i)
                if signal != 0:
                    signals.append((i, signal))
            
            print(f"✅ Signaux générés: {len(signals)}")
            
            if signals:
                print("\n📊 Exemples de signaux:")
                for i, (idx, signal) in enumerate(signals[:3]):
                    direction = "HAUSSIER" if signal > 0 else "BAISSIER"
                    strength = "FORT" if abs(signal) == 1 else "FAIBLE"
                    print(f"   Bougie {idx}: {direction} ({strength})")
            
            # Test d'intégration avec Bollinger
            from indicators.bollinger_bands import BollingerBands
            bb = BollingerBands()
            df_with_bb = bb.calculate(df)
            df_with_both = kc.calculate(df_with_bb)
            
            print(f"\n🔗 Intégration BB + KC réussie!")
            print(f"   Colonnes totales: {len(df_with_both.columns)}")
            print(f"   Forme du DataFrame: {df_with_both.shape}")
            
        else:
            print(f"❌ KeltnerChannel retourne {type(result)} au lieu de DataFrame")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keltner_fixed()