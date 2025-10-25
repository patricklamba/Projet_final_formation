"""
CONFIGURATION CENTRALE COMPLÈTE
"""

# Indicateurs activés/désactivés avec paramètres
# Dans INDICATOR_CONFIG - MODIFIER COMME ÇA :
INDICATOR_CONFIG = {
    "bollinger_bands": {
        "enabled": True,        # ✅ ACTIVÉ
        "weight": 1.2,
        "params": {"period": 20, "std_dev": 2.0}
    },
    "keltner_channel": {
        "enabled": True,        # ✅ ACTIVÉ  
        "weight": 1.2,
        "params": {"ema_period": 20, "atr_period": 10, "atr_multiplier": 1.5}
    },
    "ema": {
        "enabled": False,       # ❌ DÉSACTIVÉ
        "weight": 1.0,
        "params": {"fast_period": 20, "slow_period": 50}
    },
    "rsi": {
        "enabled": False,       # ❌ DÉSACTIVÉ
        "weight": 0.8,
        "params": {"period": 14, "overbought": 70, "oversold": 30}
    },
    "ichimoku": {
        "enabled": False,       # ❌ DÉSACTIVÉ
        "weight": 1.5,
        "params": {"tenkan_period": 9, "kijun_period": 26, "senkou_period": 52}
    },
    "fibonacci": {
        "enabled": False,       # ❌ DÉSACTIVÉ
        "weight": 0.7,
        "params": {}
    },
    "candlestick_patterns": {
        "enabled": False,       # ❌ DÉSACTIVÉ
        "weight": 0.6,
        "params": {}
    }
}


# Configuration de la stratégie
STRATEGY_CONFIG = {
    "risk_management": {
        "initial_capital": 100000.0,
        "risk_per_trade": 0.01,  # 1% du capital
        "risk_reward_ratio": 1.5,
        "max_open_trades": 3,
        "max_drawdown": 0.10,  # 10% max
        "min_risk_percent": 0.3,
        "max_risk_percent": 1.5
    },
    "trading_hours": {
        "killzone_start": "00:00",
        "killzone_end": "23:59",
        "timeframe": "1H",
        "min_trade_interval": 15  # minutes
    },
    "signal_convergence": {
        "min_convergence_score": 1.5,  # Score minimal pour déclencher
        "weighted_scoring": True,
        "required_indicators": ["bollinger_bands", "keltner_channel"],
        "confirmation_candles": 1
    },
    "filters": {
        "trend_filter": True,
        "volatility_filter": True,
        "volume_filter": False
    },
    "execution": {
        "demo_mode": False,
        "max_concurrent_symbols": 5,
        "log_level": "INFO"
    }
}

# Symboles et instruments
SYMBOL_CONFIG = {
    "XAUUSD": {
        "pip_value": 1.0,
        "pip_size": 0.01,
        "lot_size": 100,
        "spread": 0.3,
        "volatility_adjustment": 1.5
    },
    "EURUSD": {
        "pip_value": 1.0, 
        "pip_size": 0.0001,
        "lot_size": 1000,
        "spread": 0.0001,
        "volatility_adjustment": 1.0
    }
}