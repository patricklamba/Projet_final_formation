# test_bollinger_fixed.py
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from indicators.bollinger_bands import BollingerBands
from utils.file_manager import FileManager

def test_bollinger_fixed():
    """Test corrigé de Bollinger Bands"""
    print("🧪 TEST BOLLINGER BANDS CORRIGÉ")
    print("=" * 50)
    
    try:
        # Charger les données
        fm = FileManager(data_dir="data")
        df = fm.load_csv("XAUUSD")
        
        print(f"📊 Données chargées: {len(df)} bougies")
        
        # Initialiser Bollinger Bands
        bb = BollingerBands(period=20, std_dev=2.0)
        
        # Calculer les indicateurs
        df_with_bb = bb.calculate(df)
        print(f"✅ Calcul Bollinger Bands réussi")
        print(f"📈 Colonnes: {[col for col in df_with_bb.columns if 'bb_' in col]}")
        
        # Tester quelques signaux
        test_indices = [50, 100, 150]  # Indices entiers
        for idx in test_indices:
            if idx < len(df_with_bb):
                signal = bb.get_signal(df_with_bb, idx)
                detailed = bb.get_detailed_signal(df_with_bb, idx)
                direction = "ACHAT 🟢" if signal == 1 else "VENTE 🔴" if signal == -1 else "NEUTRE ⚪"
                print(f"   Index {idx}: {direction} | Confiance: {detailed['confidence']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bollinger_fixed()