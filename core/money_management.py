"""
Module indépendant de gestion du risque et position sizing - VERSION CORRIGÉE
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
    
    def add_pnl(self, pnl: float):
        """Ajoute le résultat du trade au capital courant - NOUVEAU"""
        self.current_capital += pnl
        print(f"💰 Capital mis à jour : {self.current_capital:.2f}€")
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, symbol: str) -> Dict[str, float]:
        risk_amount = self.current_capital * self.config['risk_per_trade']
        
        if "XAU" in symbol.upper():
            pip_value = 1.0
            pip_distance = abs(entry_price - stop_loss) / 0.01
            lot_multiplier = 10  # ⚠️ CORRECTION : 10 au lieu de 100 !
        else:
            pip_value = 10.0
            pip_distance = abs(entry_price - stop_loss) / 0.0001
            lot_multiplier = 10000  # Ajusté aussi pour Forex
        
        if pip_distance == 0:
            return {"lots": 0, "risk_amount": 0, "units": 0, "risk_percent": 0}
        
        lots = risk_amount / (pip_distance * pip_value)
        lots = round(max(0.01, min(lots, 0.3)), 2)  # Max 0.3 lots
        
        units = lots * lot_multiplier  # ← MAINTENANT CORRECT
        
        actual_risk = pip_distance * pip_value * lots
        risk_percent = (actual_risk / self.current_capital) * 100
        
        return {
            "lots": lots,
            "units": int(units),
            "risk_amount": round(actual_risk, 2),
            "risk_percent": round(risk_percent, 2)
        }
    
    def calculate_stop_loss_take_profit(self, entry_price: float, direction: str, 
                                      atr: float = None, symbol: str = None) -> Tuple[float, float]:
        """Calcule SL et TP basés sur ATR ou pourcentage fixe - VERSION AMÉLIORÉE"""
        
        # PRIORITÉ à l'ATR si disponible
        if atr:
            if direction == "LONG":
                stop_loss = entry_price - (atr * 2.0)  # 1.5 ATR pour SL
                take_profit = entry_price + (atr * 2.0 * self.config['risk_reward_ratio'])
            else:  # SHORT
                stop_loss = entry_price + (atr * 2.0)
                take_profit = entry_price - (atr * 2.0 * self.config['risk_reward_ratio'])
        else:
            # Méthode par pourcentage fixe
            risk_percent = 0.015  # 1.5% plus conservateur
            if direction == "LONG":
                stop_loss = entry_price * (1 - risk_percent)
                take_profit = entry_price * (1 + risk_percent * self.config['risk_reward_ratio'])
            else:  # SHORT
                stop_loss = entry_price * (1 + risk_percent)
                take_profit = entry_price * (1 - risk_percent * self.config['risk_reward_ratio'])
        
        return round(stop_loss, 5), round(take_profit, 5)
    
    def validate_trade(self, risk_amount: float, risk_percent: float) -> bool:
        """Valide si le trade respecte les règles de risque - VERSION CORRIGÉE"""
        max_risk_percent = self.config['risk_per_trade'] * 100 * 1.5  # 50% de tolérance
        max_risk_amount = self.current_capital * self.config['risk_per_trade'] * 1.5
        
        # CORRECTION : utilisation de 'and' au lieu de 'et'
        return (risk_percent <= max_risk_percent and 
                risk_amount <= max_risk_amount)
    
    def is_in_drawdown(self) -> bool:
        """Vérifie si on est en drawdown excessif - NOUVEAU"""
        drawdown_limit = self.config.get('max_drawdown', 0.10)  # 10% par défaut
        current_drawdown = (self.capital - self.current_capital) / self.capital
        return current_drawdown > drawdown_limit
    
    def get_risk_summary(self) -> Dict[str, float]:
        """Retourne un résumé du risque actuel - NOUVEAU"""
        return {
            "current_capital": self.current_capital,
            "initial_capital": self.capital,
            "drawdown_percent": ((self.capital - self.current_capital) / self.capital) * 100,
            "max_risk_per_trade": self.current_capital * self.config['risk_per_trade']
        }