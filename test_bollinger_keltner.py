"""
TEST SPÉCIFIQUE CORRIGÉ - Seulement Bollinger Bands + Keltner Channel
"""
import pandas as pd
import numpy as np
import asyncio
import sys
import os

# Ajouter le chemin au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """Crée des données de test réalistes"""
    dates = pd.date_range(start='2024-01-01', periods=500, freq='1H')
    np.random.seed(42)
    
    # Générer des prix avec tendance et volatilité
    prices = [1800.0]  # Prix initial pour XAUUSD
    for i in range(1, 500):
        # Tendances alternées
        if i < 100:
            trend = 0.08  # Légère hausse
        elif i < 300:
            trend = -0.05  # Légère baisse  
        else:
            trend = 0.12  # Hausse
        
        # Volatilité variable
        volatility = 2.0 + 1.0 * np.sin(i / 50)
        change = trend + volatility * np.random.randn()
        new_price = prices[-1] + change
        prices.append(max(new_price, 100))  # Éviter les prix négatifs
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p + abs(np.random.randn() * 3) for p in prices],
        'low': [p - abs(np.random.randn() * 3) for p in prices],
        'close': prices,
        'volume': [1000000 + np.random.randn() * 100000 for _ in prices]
    }, index=dates)
    
    return df

def test_bollinger_keltner_simple():
    """Test SIMPLIFIÉ avec seulement Bollinger Bands et Keltner Channel"""
    print("🧪 TEST BOLLINGER + KELTNER UNIQUEMENT (SIMPLIFIÉ)")
    print("=" * 50)
    
    try:
        from indicators.bollinger_bands import BollingerBands
        from indicators.keltner_channel import KeltnerChannel
        
        # Créer les données de test
        df = create_test_data()
        print(f"📊 Données créées: {len(df)} bougies")
        
        # 1. Appliquer Bollinger Bands
        print("📈 Application de Bollinger Bands...")
        bb = BollingerBands(period=20, std_dev=2.0)
        df_with_bb = bb.calculate(df)
        bb_columns = [col for col in df_with_bb.columns if 'bb_' in col]
        print(f"   ✅ Colonnes BB: {bb_columns}")
        
        # 2. Appliquer Keltner Channel
        print("📈 Application de Keltner Channel...")
        kc = KeltnerChannel(ema_period=20, atr_period=10, atr_multiplier=1.5)
        df_with_both = kc.calculate(df_with_bb)
        kc_columns = [col for col in df_with_both.columns if 'kc_' in col]
        print(f"   ✅ Colonnes KC: {kc_columns}")
        
        # 3. Tester les signaux
        print("🔍 Test des signaux individuels...")
        signals_bb = []
        signals_kc = []
        
        for i in range(50, min(100, len(df_with_both))):
            signal_bb = bb.get_signal(df_with_both, i)
            signal_kc = kc.get_signal(df_with_both, i)
            
            if signal_bb != 0:
                signals_bb.append((i, signal_bb))
            if signal_kc != 0:
                signals_kc.append((i, signal_kc))
        
        print(f"   Signaux Bollinger: {len(signals_bb)}")
        print(f"   Signaux Keltner: {len(signals_kc)}")
        
        # 4. Afficher quelques signaux
        if signals_bb:
            print("\n📊 Exemples de signaux Bollinger:")
            for i, (idx, signal) in enumerate(signals_bb[:3]):
                direction = "HAUSSIER" if signal > 0 else "BAISSIER"
                print(f"   #{i+1}: Bougie {idx} → {direction} ({signal})")
        
        if signals_kc:
            print("\n📊 Exemples de signaux Keltner:")
            for i, (idx, signal) in enumerate(signals_kc[:3]):
                direction = "HAUSSIER" if signal > 0 else "BAISSIER"
                print(f"   #{i+1}: Bougie {idx} → {direction} ({signal})")
                
        # 5. Test de convergence simple
        print("\n🎯 Test de convergence simple:")
        convergence_signals = []
        for i in range(50, min(100, len(df_with_both))):
            signal_bb = bb.get_signal(df_with_both, i)
            signal_kc = kc.get_signal(df_with_both, i)
            
            # Convergence: les deux signaux dans le même sens
            if signal_bb != 0 and signal_kc != 0 and (signal_bb * signal_kc) > 0:
                convergence_signals.append((i, signal_bb, signal_kc))
        
        print(f"   Signaux de convergence: {len(convergence_signals)}")
        
        if convergence_signals:
            print("\n📈 Exemples de convergence:")
            for i, (idx, bb_sig, kc_sig) in enumerate(convergence_signals[:3]):
                direction = "HAUSSIER" if bb_sig > 0 else "BAISSIER"
                print(f"   #{i+1}: Bougie {idx} → {direction} (BB: {bb_sig}, KC: {kc_sig})")
        
        print(f"\n✅ TEST RÉUSSI!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bollinger_keltner_simple()