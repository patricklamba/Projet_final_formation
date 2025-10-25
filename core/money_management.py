"""
Module indépendant de gestion du risque et position sizing
"""
from typing import Dict, Tuple
import numpy as np
from config.strategy_config import STRATEGY_CONFIG

class MoneyManagement:
    def __init__(self, capital: float = None):
        self.config = STRATEGY_CONFIG['risk_management']
        self.capital = capital or self.config['initial_capital']
        self.current_capital = self.capital
        
    def update_capital(self, new_capital: float):
        """Met à jour le capital courant"""
        self.current_capital = new_capital
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, symbol: str) -> Dict[str, float]:
        """Calcule la taille de position avec risk management strict"""
        risk_amount = self.current_capital * self.config['risk_per_trade']
        
        # Calcul de la distance en pips selon le symbole
        if "XAU" in symbol.upper():  # Or
            pip_value = 10.0  # 1 pip XAUUSD = 10$ par lot
            pip_distance = abs(entry_price - stop_loss) / 0.01
            lot_multiplier = 100  # 1 lot = 100 onces
        else:  # Forex (EURUSD, etc.)
            pip_value = 10.0  # 1 pip EURUSD = 10$ par lot
            pip_distance = abs(entry_price - stop_loss) / 0.0001
            lot_multiplier = 100000  # 1 lot = 100,000 unités
        
        if pip_distance == 0:
            return {"lots": 0, "risk_amount": 0, "units": 0, "risk_percent": 0}
        
        # Calcul des lots
        lots = risk_amount / (pip_distance * pip_value)
        lots = round(max(0.01, min(lots, 1.0)), 2)  # Limite entre 0.01 et 1.0 lots
        
        # Risk réel
        actual_risk = pip_distance * pip_value * lots
        risk_percent = (actual_risk / self.current_capital) * 100
        units = lots * lot_multiplier  
        
        return {
            "lots": lots,
            "units": int(units),
            "risk_amount": round(actual_risk, 2),
            "risk_percent": round(risk_percent, 2)
        }
    
    def calculate_stop_loss_take_profit(self, entry_price: float, direction: str, 
                                      atr: float = None, symbol: str = None) -> Tuple[float, float]:
        """Calcule SL et TP basés sur ATR ou pourcentage fixe"""
        
        if atr and symbol and "XAU" in symbol.upper():
            # Pour l'or: SL basé sur ATR
            if direction == "LONG":
                stop_loss = entry_price - (atr * 2.0)
                take_profit = entry_price + (atr * 2.0 * self.config['risk_reward_ratio'])
            else:  # SHORT
                stop_loss = entry_price + (atr * 2.0)
                take_profit = entry_price - (atr * 2.0 * self.config['risk_reward_ratio'])
        else:
            # Méthode par pourcentage
            risk_percent = 0.02  # 2%
            if direction == "LONG":
                stop_loss = entry_price * (1 - risk_percent)
                take_profit = entry_price * (1 + risk_percent * self.config['risk_reward_ratio'])
            else:  # SHORT
                stop_loss = entry_price * (1 + risk_percent)
                take_profit = entry_price * (1 - risk_percent * self.config['risk_reward_ratio'])
        
        return round(stop_loss, 5), round(take_profit, 5)
    
    def validate_trade(self, risk_amount: float, risk_percent: float) -> bool:
        """Valide si le trade respecte les règles de risque"""
        max_risk_percent = self.config['risk_per_trade'] * 100 * 1.5  # 50% de tolérance
        
        return (risk_percent <= max_risk_percent and 
                risk_amount <= self.current_capital * self.config['risk_per_trade'] * 1.5)