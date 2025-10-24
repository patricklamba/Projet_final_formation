import pandas as pd
import numpy as np
from datetime import time
from typing import List, Dict, Any

from indicators.bollinger_bands import BollingerBands
from indicators.keltner_channel import KeltnerChannel

class BBKeltnerStrategy:
    """
    Stratégie de convergence entre Bollinger Bands et Keltner Channels.
    Génère des signaux de trading concrets avec gestion de position.
    """

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_ema_period: int = 20,
        kc_atr_period: int = 10,
        kc_mult: float = 1.5,
        killzone_start: str = "03:00",
        killzone_end: str = "06:30",
        risk_reward_ratio: float = 1.5
    ):
        self.bb = BollingerBands(period=bb_period, std_dev=bb_std)
        self.kc = KeltnerChannel(
            ema_period=kc_ema_period,
            atr_period=kc_atr_period,
            atr_multiplier=kc_mult
        )

        # Killzone
        h_start, m_start = map(int, killzone_start.split(":"))
        h_end, m_end = map(int, killzone_end.split(":"))
        self.killzone_start = time(h_start, m_start)
        self.killzone_end = time(h_end, m_end)
        self.risk_reward_ratio = risk_reward_ratio
        
        # Suivi des trades
        self.trades = []

    def in_killzone(self, dt: pd.Timestamp) -> bool:
        t = dt.time()
        return self.killzone_start <= t <= self.killzone_end

    def calculate_position_size(self, entry_price: float, stop_loss: float, risk_per_trade: float = 100) -> float:
        """Calcule la taille de position basée sur le risque"""
        risk_amount = abs(entry_price - stop_loss)
        if risk_amount > 0:
            return risk_per_trade / risk_amount
        return 0

    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Génère les signaux de trading avec gestion de position
        """
        df = df.copy()

        # Vérifications
        for col in ["high", "low", "close", "open"]:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante: {col}")

        print("📈 Calcul des indicateurs...")
        
        # Calcul des indicateurs
        bb_mid, bb_up, bb_low = self.bb.calculate(df[["close"]])
        kc_mid, kc_up, kc_low = self.kc.calculate(df)

        # Assignation des résultats
        df["bb_middle"] = bb_mid
        df["bb_upper"] = bb_up
        df["bb_lower"] = bb_low
        df["kc_middle"] = kc_mid
        df["kc_upper"] = kc_up
        df["kc_lower"] = kc_low

        # Détection des phases de volatilité
        df["phase"] = np.where(
            (df["bb_lower"] > df["kc_lower"]) & (df["bb_upper"] < df["kc_upper"]),
            "CONTRACTION",
            "EXPANSION",
        )

        # Génération des signaux bruts
        df["raw_signal"] = 0
        df.loc[df["close"] > df["bb_upper"], "raw_signal"] = 1   # Breakout haussier
        df.loc[df["close"] < df["bb_lower"], "raw_signal"] = -1  # Breakout baissier

        # Filtrage Killzone
        df["in_killzone"] = df.index.map(self.in_killzone)
        df["signal"] = df["raw_signal"].where(df["in_killzone"], 0)

        # Calcul des stops et targets
        df["stop_loss"] = np.nan
        df["take_profit"] = np.nan
        df["position_size"] = np.nan
        
        # LONG signals
        long_mask = (df["signal"] == 1)
        df.loc[long_mask, "stop_loss"] = df.loc[long_mask, "bb_middle"]
        df.loc[long_mask, "take_profit"] = df.loc[long_mask, "close"] + (
            (df.loc[long_mask, "close"] - df.loc[long_mask, "bb_middle"]) * self.risk_reward_ratio
        )
        
        # SHORT signals  
        short_mask = (df["signal"] == -1)
        df.loc[short_mask, "stop_loss"] = df.loc[short_mask, "bb_middle"]
        df.loc[short_mask, "take_profit"] = df.loc[short_mask, "close"] - (
            (df.loc[short_mask, "bb_middle"] - df.loc[short_mask, "close"]) * self.risk_reward_ratio
        )

        # Calcul taille position (risque de 100€ par trade exemple)
        df["position_size"] = df.apply(
            lambda row: self.calculate_position_size(row["close"], row["stop_loss"]) 
            if not pd.isna(row["stop_loss"]) else np.nan, 
            axis=1
        )

        return df

    def analyze_trades(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analyse les trades qui auraient été pris
        """
        trades = []
        current_position = 0
        entry_price = 0
        entry_time = None
        stop_loss = 0
        take_profit = 0
        
        for i, (index, row) in enumerate(df.iterrows()):
            # SIGNAL LONG
            if current_position == 0 and row["signal"] == 1:
                current_position = 1
                entry_price = row["close"]
                entry_time = index
                stop_loss = row["stop_loss"]
                take_profit = row["take_profit"]
                
                trade = {
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "direction": "LONG",
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "risk": abs(entry_price - stop_loss),
                    "reward": abs(take_profit - entry_price),
                    "rr_ratio": round(abs(take_profit - entry_price) / abs(entry_price - stop_loss), 2),
                    "position_size": row["position_size"],
                    "phase": row["phase"]
                }
                trades.append(trade)
                print(f"📈 SIGNAL LONG à {entry_time} | Prix: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f} | R/R: {trade['rr_ratio']}")
            
            # SIGNAL SHORT  
            elif current_position == 0 and row["signal"] == -1:
                current_position = -1
                entry_price = row["close"]
                entry_time = index
                stop_loss = row["stop_loss"]
                take_profit = row["take_profit"]
                
                trade = {
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "direction": "SHORT", 
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "risk": abs(entry_price - stop_loss),
                    "reward": abs(entry_price - take_profit),
                    "rr_ratio": round(abs(entry_price - take_profit) / abs(entry_price - stop_loss), 2),
                    "position_size": row["position_size"],
                    "phase": row["phase"]
                }
                trades.append(trade)
                print(f"📉 SIGNAL SHORT à {entry_time} | Prix: {entry_price:.2f} | SL: {stop_loss:.2f} | TP: {take_profit:.2f} | R/R: {trade['rr_ratio']}")
            
            # Gestion sortie position (simplifiée - sortie au signal opposé)
            elif current_position != 0 and row["signal"] == -current_position:
                # Fermer la position
                current_position = 0
        
        self.trades = trades
        return trades

    def generate_trading_report(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Génère un rapport complet de trading
        """
        trades = self.analyze_trades(df)
        
        if not trades:
            return {"message": "Aucun trade généré pendant la période analysée"}
        
        # Métriques de performance
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t["rr_ratio"] > 1])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_risk = sum(t["risk"] for t in trades)
        total_reward = sum(t["reward"] for t in trades)
        avg_rr = np.mean([t["rr_ratio"] for t in trades])
        
        # Trades par phase
        contraction_trades = len([t for t in trades if t["phase"] == "CONTRACTION"])
        expansion_trades = len([t for t in trades if t["phase"] == "EXPANSION"])
        
        report = {
            "symbol": symbol,
            "periode_analyse": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
            "killzone": f"{self.killzone_start.strftime('%H:%M')}–{self.killzone_end.strftime('%H:%M')}",
            "performance": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 1),
                "avg_risk_reward": round(avg_rr, 2),
                "total_risk": round(total_risk, 2),
                "total_reward": round(total_reward, 2),
            },
            "analyse_phases": {
                "trades_contraction": contraction_trades,
                "trades_expansion": expansion_trades,
                "ratio_contraction_expansion": f"{contraction_trades}:{expansion_trades}"
            },
            "trades_detailed": trades
        }
        
        return report

    def summary(self, df: pd.DataFrame) -> dict:
        """Version simplifiée pour compatibilité"""
        long_signals = (df["signal"] == 1).sum()
        short_signals = (df["signal"] == -1).sum()
        total = long_signals + short_signals
        
        return {
            "total_signaux": total,
            "longs": long_signals,
            "shorts": short_signals,
            "periode": f"{self.killzone_start.strftime('%H:%M')}–{self.killzone_end.strftime('%H:%M')}",
        }