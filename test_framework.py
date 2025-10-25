"""
Script de test du framework modulaire
"""
import pandas as pd
import numpy as np
from core.strategy import MultiSignalStrategy

def test_framework():
    """Test complet du framework modulaire"""
    print("🧪 TEST DU FRAMEWORK MODULAIRE")
    print("=" * 50)
    
    # Créer des données de test
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1H')
    np.random.seed(42)
    
    # Générer des prix avec tendance
    prices = [100.0]
    for i in range(1, 1000):
        trend = 0.001 if i < 500 else -0.001
        volatility = 0.5 + 0.3 * np.sin(i / 100)  # Volatilité cyclique
        change = trend + volatility * np.random.randn()
        prices.append(prices[-1] + change)
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p + abs(np.random.randn() * 0.5) for p in prices],
        'low': [p - abs(np.random.randn() * 0.5) for p in prices], 
        'close': prices,
        'volume': [1000000 + np.random.randn() * 100000 for _ in prices]
    }, index=dates)
    
    # Initialiser la stratégie
    strategy = MultiSignalStrategy(initial_capital=50000)
    
    print("📈 Application des indicateurs...")
    df_with_indicators = strategy.apply_indicators(df)
    
    print("🔍 Analyse des signaux de convergence...")
    for i in range(100, min(200, len(df_with_indicators))):
        score, signals = strategy.signal_convergence.compute_convergence_score(df_with_indicators, i)
        if abs(score) >= 1.0:
            direction = "📈 HAUSSIER" if score > 0 else "📉 BAISSIER"
            strength = strategy.signal_convergence.get_signal_strength(score)
            print(f"   {direction} | Score: {score:.2f} | Force: {strength}")
            print(f"   Détails: {signals}")
    
    print("🎯 Exécution de la stratégie complète...")
    trades = strategy.execute_strategy(df, "XAUUSD")
    
    print(f"\n✅ TEST TERMINÉ: {len(trades)} trades générés")
    print("=" * 50)
    
    if trades:
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        print(f"📊 Performance:")
        print(f"   Trades gagnants: {len(winning_trades)}")
        print(f"   Trades perdants: {len(losing_trades)}")
        print(f"   Win Rate: {len(winning_trades)/len(trades)*100:.1f}%")
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        print(f"   P&L Total: {total_pnl:+.2f}€")

if __name__ == "__main__":
    test_framework()