"""
Module de convergence des signaux techniques avec pondération et filtres avancés
"""
from typing import Dict, Tuple
import pandas as pd
import numpy as np
from config.strategy_config import INDICATOR_CONFIG, STRATEGY_CONFIG


class SignalConvergence:
    def __init__(self, indicators: Dict):
        self.indicators = indicators
        self.weights = self._calculate_weights()

    # ==========================================================
    # 1️⃣  Initialisation et pondération
    # ==========================================================
    def _calculate_weights(self) -> Dict[str, float]:
        """Calcule les poids des indicateurs selon la config"""
        weights = {}
        for name, cfg in INDICATOR_CONFIG.items():
            if cfg.get('enabled', False):
                weight = cfg.get('weight', 1.0)
                # Bonus pour indicateurs "requis"
                if name in STRATEGY_CONFIG['signal_convergence'].get('required_indicators', []):
                    weight += 0.3
                weights[name] = weight
        return weights

    # ==========================================================
    # 2️⃣  Calcul du score de convergence
    # ==========================================================
    def compute_convergence_score(self, df: pd.DataFrame, current_index: int) -> Tuple[float, Dict]:
        """Calcule le score de convergence pondéré des signaux"""
        signals = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for name, indicator in self.indicators.items():
            cfg = INDICATOR_CONFIG.get(name, {})
            if not cfg.get('enabled', False):
                continue

            try:
                signal = indicator.get_signal(df, current_index)
                # force les signaux dans [-1, 0, 1]
                signal = max(-1, min(1, float(signal)))
                signals[name] = signal

                w = self.weights.get(name, 1.0)
                weighted_sum += signal * w
                total_weight += w

            except Exception as e:
                print(f"⚠️ Erreur dans {name}: {e}")
                signals[name] = 0.0

        if total_weight == 0:
            return 0.0, signals

        score = weighted_sum / total_weight

        # Optionnel : normalisation selon nb d’indicateurs actifs
        if STRATEGY_CONFIG['signal_convergence'].get('weighted_scoring', True):
            enabled_count = len([v for v in INDICATOR_CONFIG.values() if v.get('enabled', False)])
            score *= enabled_count  # garde cohérence avec ancienne logique

        return round(score, 3), signals

    # ==========================================================
    # 3️⃣  Validation d'entrée
    # ==========================================================
    def is_valid_entry(self, score: float, signals: Dict, df: pd.DataFrame, current_index: int) -> bool:
        """Vérifie si les conditions d'entrée sont remplies"""
        min_score = STRATEGY_CONFIG['signal_convergence'].get('min_convergence_score', 1.0)

        # A. Score minimal
        if abs(score) < min_score:
            return False

        # B. Indicateurs requis
        for req in STRATEGY_CONFIG['signal_convergence'].get('required_indicators', []):
            sig = signals.get(req, 0)
            if sig == 0 or (score > 0 and sig < 0) or (score < 0 and sig > 0):
                return False

        # C. Cohérence des signaux
        vals = [s for s in signals.values() if s != 0]
        if not vals:
            return False
        bullish = sum(1 for s in vals if s > 0)
        bearish = sum(1 for s in vals if s < 0)
        ratio = bullish / len(vals) if score > 0 else bearish / len(vals)
        if ratio < 0.6:
            return False

        # D. Filtres avancés
        if not self._check_advanced_filters(df, current_index, score > 0):
            return False

        # E. Confirmation bougies
        if not self._check_confirmation(df, current_index, score > 0):
            return False

        return True

    # ==========================================================
    # 4️⃣  Filtres avancés
    # ==========================================================
    def _check_advanced_filters(self, df: pd.DataFrame, idx: int, is_bullish: bool) -> bool:
        """Applique les filtres squeeze + volatilité + tendance + momentum"""
        return (
            self._check_squeeze_condition(df, idx)
            and self._check_volatility_filter(df, idx)
            and self._check_trend_alignment(df, idx, is_bullish)
            and self._check_momentum_confirmation(df, idx, is_bullish)
        )

    # --- 4.1 Squeeze ---
    def _check_squeeze_condition(self, df, idx) -> bool:
        """Version corrigée pour détecter l'expansion"""
        if idx < 20:
            return False
            
        row = df.iloc[idx]
        
        if not all(col in df.columns for col in ['bb_upper', 'bb_lower', 'kc_upper', 'kc_lower']):
            return True
        
        bb_width = row['bb_upper'] - row['bb_lower']
        kc_width = row['kc_upper'] - row['kc_lower']
        
        if kc_width <= 0:
            return True
            
        ratio = bb_width / kc_width
        
        # CORRECTION : On veut BB > KC (expansion)
        return ratio > 1.0  # BB plus large que KC = expansion volatilité

    # --- 4.2 Volatilité ---
    def _check_volatility_filter(self, df, idx) -> bool:
        if idx < 20:
            return False
        row = df.iloc[idx]

        # Bollinger bandwidth
        bb_bw = row.get('bb_bandwidth', np.nan)
        if not np.isnan(bb_bw):
            if bb_bw < 0.002 or bb_bw > 0.015:
                return False

        # Keltner width (%)
        kc_width = None
        if 'kc_width' in df.columns:
            kc_width = row['kc_width'] / 100
            if kc_width < 0.0015 or kc_width > 0.012:
                return False

        return True

    # --- 4.3 Tendance ---
    def _check_trend_alignment(self, df, idx, is_bullish: bool) -> bool:
        if idx < 25 or 'bb_middle' not in df.columns:
            return False
        slope = self._calculate_slope(df, 'bb_middle', idx, 5)
        return slope > -0.0005 if is_bullish else slope < 0.0005

    # --- 4.4 Momentum ---
    def _check_momentum_confirmation(self, df, idx, is_bullish: bool) -> bool:
        if idx < 3:
            return False
        closes = df['close'].iloc[max(0, idx - 3): idx + 1].values
        diffs = np.sign(np.diff(closes))
        momentum = diffs.sum()  # ∈ [-3, 3]
        if is_bullish:
            return momentum >= -1
        else:
            return momentum <= 1

    # ==========================================================
    # 5️⃣  Outils internes
    # ==========================================================
    def _calculate_slope(self, df, column: str, idx: int, lookback: int = 5) -> float:
        """Calcule la pente normalisée sur N périodes"""
        if idx < lookback or column not in df.columns:
            return 0.0
        y = df[column].iloc[idx - lookback + 1: idx + 1].values
        x = np.arange(lookback)
        if len(y) < lookback:
            return 0.0
        slope = np.polyfit(x, y, 1)[0]
        mean_y = np.mean(y)
        return slope / mean_y if mean_y != 0 else 0.0

    # ==========================================================
    # 6️⃣  Confirmation post-signal
    # ==========================================================
    def _check_confirmation(self, df, idx, is_bullish: bool) -> bool:
        n = STRATEGY_CONFIG['signal_convergence'].get('confirmation_candles', 0)
        if n == 0:
            return True
        if idx + n >= len(df):
            return False
        cur_close = df['close'].iloc[idx]
        closes = df['close'].iloc[idx + 1: idx + n + 1]
        if is_bullish:
            return all(c >= cur_close for c in closes)
        else:
            return all(c <= cur_close for c in closes)

    # ==========================================================
    # 7️⃣  Informations supplémentaires
    # ==========================================================
    def get_signal_strength(self, score: float) -> str:
        """Retourne une interprétation textuelle du score"""
        s = abs(score)
        if s >= 3.0:
            return "TRÈS FORT"
        elif s >= 2.0:
            return "FORT"
        elif s >= 1.0:
            return "MOYEN"
        return "FAIBLE"

    def get_filter_details(self, df, idx) -> Dict:
        """Retourne les détails des filtres (debugging visuel)"""
        if idx < 20:
            return {"error": "données insuffisantes"}

        details = {}
        row = df.iloc[idx]

        if all(c in df.columns for c in ['bb_upper', 'bb_lower', 'kc_upper', 'kc_lower']):
            bb_w = row['bb_upper'] - row['bb_lower']
            kc_w = row['kc_upper'] - row['kc_lower']
            ratio = bb_w / kc_w if kc_w != 0 else 0
            details['squeeze_ratio'] = ratio
            details['squeeze_condition'] = 0.8 <= ratio <= 0.95

        if 'bb_bandwidth' in df.columns:
            details['bb_bandwidth'] = row['bb_bandwidth']
            details['volatility_ok'] = 0.002 <= row['bb_bandwidth'] <= 0.015

        if 'bb_middle' in df.columns and idx >= 25:
            details['bb_trend_slope'] = self._calculate_slope(df, 'bb_middle', idx, 5)

        return details
