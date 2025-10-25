"""
Module de convergence des signaux techniques avec pondération
"""
from typing import Dict, List, Tuple
import pandas as pd
from config.strategy_config import INDICATOR_CONFIG, STRATEGY_CONFIG

class SignalConvergence:
    def __init__(self, indicators: Dict):
        self.indicators = indicators
        self.weights = self._calculate_weights()
        
    def _calculate_weights(self) -> Dict[str, float]:
        """Calcule les poids des indicateurs basés sur la configuration"""
        weights = {}
        
        for indicator_name, config in INDICATOR_CONFIG.items():
            if config['enabled']:
                # Utilise le poids spécifié ou 1.0 par défaut
                weight = config.get('weight', 1.0)
                
                # Bonus pour indicateurs requis
                if indicator_name in STRATEGY_CONFIG['signal_convergence']['required_indicators']:
                    weight += 0.3
                    
                weights[indicator_name] = weight
                
        return weights
    
    def compute_convergence_score(self, df: pd.DataFrame, current_index: int) -> Tuple[float, Dict]:
        """
        Calcule le score de convergence pondéré des signaux
        Returns: (score_total, details_des_signaux)
        """
        signals = {}
        weighted_score = 0.0
        total_weight = 0.0
        
        for indicator_name, indicator in self.indicators.items():
            if INDICATOR_CONFIG[indicator_name]['enabled']:
                try:
                    signal = indicator.get_signal(df, current_index)
                    signals[indicator_name] = signal
                    
                    # Score pondéré
                    weight = self.weights.get(indicator_name, 1.0)
                    weighted_score += signal * weight
                    total_weight += weight
                    
                except Exception as e:
                    print(f"❌ Erreur dans {indicator_name}: {e}")
                    signals[indicator_name] = 0
        
        # Normaliser le score si on utilise la pondération
        if STRATEGY_CONFIG['signal_convergence']['weighted_scoring'] and total_weight > 0:
            weighted_score = weighted_score / total_weight * len([ind for ind in INDICATOR_CONFIG.values() if ind['enabled']])
        
        return weighted_score, signals
    
    def is_valid_entry(self, score: float, signals: Dict, df: pd.DataFrame, current_index: int) -> bool:
        """Vérifie si les conditions d'entrée sont remplies"""
        min_score = STRATEGY_CONFIG['signal_convergence']['min_convergence_score']
        
        # 1. Vérifier le score minimum
        if abs(score) < min_score:
            return False
            
        # 2. Vérifier les indicateurs requis
        required_indicators = STRATEGY_CONFIG['signal_convergence']['required_indicators']
        for req_ind in required_indicators:
            if (req_ind not in signals or 
                signals[req_ind] == 0 or
                (score > 0 and signals[req_ind] < 0) or
                (score < 0 and signals[req_ind] > 0)):
                return False
                
        # 3. Vérifier la cohérence des signaux
        bullish_signals = sum(1 for s in signals.values() if s > 0)
        bearish_signals = sum(1 for s in signals.values() if s < 0)
        total_signals = len([s for s in signals.values() if s != 0])
        
        if total_signals == 0:
            return False
            
        # Pour un signal haussier, au moins 60% des signaux doivent être haussiers
        if score > 0 and bearish_signals / total_signals > 0.4:
            return False
            
        # Pour un signal baissier, au moins 60% des signaux doivent être baissiers  
        if score < 0 and bullish_signals / total_signals > 0.4:
            return False
            
        # 4. Vérifier la confirmation des bougies
        if not self._check_confirmation(df, current_index, score > 0):
            return False
            
        return True
    
    def _check_confirmation(self, df: pd.DataFrame, current_index: int, is_bullish: bool) -> bool:
        """Vérifie la confirmation sur les bougies suivantes"""
        confirmation_candles = STRATEGY_CONFIG['signal_convergence']['confirmation_candles']
        
        if confirmation_candles == 0:
            return True
            
        if current_index + confirmation_candles >= len(df):
            return False
            
        # Vérifier que les bougies de confirmation vont dans le sens du signal
        for i in range(1, confirmation_candles + 1):
            if current_index + i < len(df):
                if is_bullish and df['close'].iloc[current_index + i] < df['close'].iloc[current_index]:
                    return False
                elif not is_bullish and df['close'].iloc[current_index + i] > df['close'].iloc[current_index]:
                    return False
                    
        return True
    
    def get_signal_strength(self, score: float) -> str:
        """Retourne la force du signal basée sur le score"""
        abs_score = abs(score)
        
        if abs_score >= 3.0:
            return "TRÈS FORT"
        elif abs_score >= 2.0:
            return "FORT" 
        elif abs_score >= 1.0:
            return "MOYEN"
        else:
            return "FAIBLE"