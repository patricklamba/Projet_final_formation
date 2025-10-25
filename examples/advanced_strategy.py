"""
Exemple d'utilisation avancée du framework
"""
import pandas as pd
from core.strategy import MultiSignalStrategy
from config.strategy_config import INDICATOR_CONFIG, STRATEGY_CONFIG

def create_custom_strategy():
    """Crée une stratégie personnalisée avec configuration avancée"""
    
    # Configuration personnalisée
    custom_config = {
        "bollinger_bands": {
            "enabled": True,
            "weight": 1.5,
            "params": {"period": 20, "std_dev": 2.0}
        },
        "keltner_channel": {
            "enabled": True, 
            "weight": 1.5,
            "params": {"ema_period": 20, "atr_period": 10, "atr_multiplier": 1.5}
        },
        "ema": {
            "enabled": True,
            "weight": 1.2,
            "params": {"fast_period": 10, "slow_period": 30}  # EMA plus réactifs
        },
        "rsi": {
            "enabled": True,
            "weight": 0.8, 
            "params": {"period": 14, "overbought": 75, "oversold": 25}  # Seuils plus stricts
        },
        "candlestick_patterns": {
            "enabled": True,
            "weight": 0.7,
            "params": {}
        }
    }
    
    # Mise à jour de la configuration
    INDICATOR_CONFIG.update(custom_config)
    STRATEGY_CONFIG['signal_convergence']['min_convergence_score'] = 2.5  # Score plus strict
    
    # Création de la stratégie
    strategy = MultiSignalStrategy(initial_capital=100000)
    
    return strategy

def optimize_strategy_parameters():
    """Exemple d'optimisation des paramètres"""
    
    strategies = []
    
    # Tester différentes configurations
    for bb_std in [1.5, 2.0, 2.5]:
        for kc_mult in [1.0, 1.5, 2.0]:
            
            # Mettre à jour la configuration
            INDICATOR_CONFIG['bollinger_bands']['params']['std_dev'] = bb_std
            INDICATOR_CONFIG['keltner_channel']['params']['atr_multiplier'] = kc_mult
            
            strategy = MultiSignalStrategy(initial_capital=50000)
            strategies.append({
                'strategy': strategy,
                'params': f"BB_std={bb_std}, KC_mult={kc_mult}",
                'bb_std': bb_std,
                'kc_mult': kc_mult
            })
    
    return strategies

if __name__ == "__main__":
    # Stratégie personnalisée
    custom_strategy = create_custom_strategy()
    print("🎯 Stratégie personnalisée créée avec succès!")
    
    # Optimisation de paramètres
    strategies = optimize_strategy_parameters()
    print(f"🔧 {len(strategies)} configurations créées pour optimisation")