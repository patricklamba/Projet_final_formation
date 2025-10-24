import pandas as pd
import numpy as np
from datetime import time
from typing import List, Dict, Any
from enum import Enum

# IMPORT CORRIGÉ - Ajouter ces lignes
from indicators.bollinger_bands import BollingerBands
from indicators.keltner_channel import KeltnerChannel

class TradeStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class BBKeltnerStrategy:
    """
    Stratégie de trading avec money management professionnel
    Capital: 100,000 € - Risk: 1% par trade
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.01,  # 1% du capital
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_ema_period: int = 20,
        kc_atr_period: int = 10,
        kc_mult: float = 1.5,
        killzone_start: str = "03:00",
        killzone_end: str = "06:30",
        risk_reward_ratio: float = 1.5
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        
        # CORRECTION: Maintenant les classes sont bien importées
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
        
        # Suivi des trades et performance
        self.trades = []
        self.portfolio_history = []
        self.closed_trades = []

    def in_killzone(self, dt: pd.Timestamp) -> bool:
        t = dt.time()
        return self.killzone_start <= t <= self.killzone_end

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> Dict[str, float]:
        """
        Calcule la taille de position selon les règles de money management
        Risk: 1% du capital actuel par trade
        """
        risk_amount = self.current_capital * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return {"lots": 0, "risk_amount": 0, "units": 0}
        
        # Pour Forex: 1 lot = 100,000 units
        # Risk en pips * valeur pip par lot = risk_amount
        lots = risk_amount / (price_risk * 100000)  # Simplification pour démo
        
        # Ajustement réaliste (min 0.01 lot, max 5 lots)
        lots = max(0.01, min(lots, 5.0))
        units = lots * 100000
        
        actual_risk = price_risk * units
        
        return {
            "lots": round(lots, 2),
            "units": int(units),
            "risk_amount": round(actual_risk, 2),
            "risk_percent": round((actual_risk / self.current_capital) * 100, 2)
        }

    def simulate_trade_execution(self, trade: Dict, df: pd.DataFrame) -> Dict:
        """
        Simule l'exécution réelle du trade avec gestion de la position
        """
        entry_idx = df.index.get_loc(trade["entry_time"])
        entry_price = trade["entry_price"]
        stop_loss = trade["stop_loss"]
        take_profit = trade["take_profit"]
        direction = trade["direction"]
        units = trade["units"]
        
        # Analyser les bougies suivantes pour voir si SL ou TP est touché
        for i in range(entry_idx + 1, min(entry_idx + 100, len(df))):  # Max 100 bougies
            current_candle = df.iloc[i]
            high, low, close = current_candle["high"], current_candle["low"], current_candle["close"]
            
            # CHECK STOP LOSS
            if direction == "LONG" and low <= stop_loss:
                pnl = (stop_loss - entry_price) * units
                return {
                    **trade,
                    "exit_time": df.index[i],
                    "exit_price": stop_loss,
                    "exit_reason": "STOP_LOSS",
                    "pnl": round(pnl, 2),
                    "pnl_percent": round((pnl / self.current_capital) * 100, 2),
                    "status": TradeStatus.STOP_LOSS.value
                }
            elif direction == "SHORT" and high >= stop_loss:
                pnl = (entry_price - stop_loss) * units
                return {
                    **trade,
                    "exit_time": df.index[i],
                    "exit_price": stop_loss,
                    "exit_reason": "STOP_LOSS",
                    "pnl": round(pnl, 2),
                    "pnl_percent": round((pnl / self.current_capital) * 100, 2),
                    "status": TradeStatus.STOP_LOSS.value
                }
            
            # CHECK TAKE PROFIT
            if direction == "LONG" and high >= take_profit:
                pnl = (take_profit - entry_price) * units
                return {
                    **trade,
                    "exit_time": df.index[i],
                    "exit_price": take_profit,
                    "exit_reason": "TAKE_PROFIT",
                    "pnl": round(pnl, 2),
                    "pnl_percent": round((pnl / self.current_capital) * 100, 2),
                    "status": TradeStatus.TAKE_PROFIT.value
                }
            elif direction == "SHORT" and low <= take_profit:
                pnl = (entry_price - take_profit) * units
                return {
                    **trade,
                    "exit_time": df.index[i],
                    "exit_price": take_profit,
                    "exit_reason": "TAKE_PROFIT",
                    "pnl": round(pnl, 2),
                    "pnl_percent": round((pnl / self.current_capital) * 100, 2),
                    "status": TradeStatus.TAKE_PROFIT.value
                }
        
        # Si ni SL ni TP touché, fermer à la dernière bougie analysée
        last_candle = df.iloc[min(entry_idx + 100, len(df) - 1)]
        exit_price = last_candle["close"]
        
        if direction == "LONG":
            pnl = (exit_price - entry_price) * units
        else:
            pnl = (entry_price - exit_price) * units
            
        return {
            **trade,
            "exit_time": last_candle.name,
            "exit_price": exit_price,
            "exit_reason": "TIME_EXIT",
            "pnl": round(pnl, 2),
            "pnl_percent": round((pnl / self.current_capital) * 100, 2),
            "status": TradeStatus.CLOSED.value
        }

    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Génère les signaux de trading avec money management
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
        df.loc[df["close"] > df["bb_upper"], "raw_signal"] = 1
        df.loc[df["close"] < df["bb_lower"], "raw_signal"] = -1

        # Filtrage Killzone
        df["in_killzone"] = df.index.map(self.in_killzone)
        df["signal"] = df["raw_signal"].where(df["in_killzone"], 0)

        return df

    def execute_trading_strategy(self, df: pd.DataFrame) -> List[Dict]:
        """
        Exécute la stratégie complète avec money management
        """
        self.current_capital = self.initial_capital
        self.trades = []
        self.closed_trades = []
        self.portfolio_history = []
        
        open_trades = []
        
        for i, (index, row) in enumerate(df.iterrows()):
            # Mettre à jour l'historique du portefeuille
            self.portfolio_history.append({
                "timestamp": index,
                "capital": self.current_capital,
                "open_trades": len(open_trades)
            })
            
            # Vérifier les trades ouverts
            for trade in open_trades[:]:
                # Simulation simplifiée de gestion des positions
                if trade["direction"] == "LONG":
                    if row["low"] <= trade["stop_loss"]:
                        # STOP LOSS touché
                        pnl = (trade["stop_loss"] - trade["entry_price"]) * trade["units"]
                        self.close_trade(trade, trade["stop_loss"], "STOP_LOSS", pnl, index)
                        open_trades.remove(trade)
                    elif row["high"] >= trade["take_profit"]:
                        # TAKE PROFIT touché
                        pnl = (trade["take_profit"] - trade["entry_price"]) * trade["units"]
                        self.close_trade(trade, trade["take_profit"], "TAKE_PROFIT", pnl, index)
                        open_trades.remove(trade)
                else:  # SHORT
                    if row["high"] >= trade["stop_loss"]:
                        pnl = (trade["entry_price"] - trade["stop_loss"]) * trade["units"]
                        self.close_trade(trade, trade["stop_loss"], "STOP_LOSS", pnl, index)
                        open_trades.remove(trade)
                    elif row["low"] <= trade["take_profit"]:
                        pnl = (trade["entry_price"] - trade["take_profit"]) * trade["units"]
                        self.close_trade(trade, trade["take_profit"], "TAKE_PROFIT", pnl, index)
                        open_trades.remove(trade)
            
            # SIGNAL LONG - Ouvrir nouvelle position
            if row["signal"] == 1 and len(open_trades) < 3:  # Max 3 trades simultanés
                entry_price = row["close"]
                stop_loss = row["bb_middle"]
                take_profit = entry_price + ((entry_price - stop_loss) * self.risk_reward_ratio)
                
                # Calcul position size avec money management
                position_info = self.calculate_position_size(entry_price, stop_loss)
                
                if position_info["lots"] > 0:
                    trade = {
                        "entry_time": index,
                        "entry_price": entry_price,
                        "direction": "LONG",
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "risk_amount": position_info["risk_amount"],
                        "units": position_info["units"],
                        "lots": position_info["lots"],
                        "risk_percent": position_info["risk_percent"],
                        "phase": row["phase"],
                        "status": "OPEN"
                    }
                    
                    self.trades.append(trade)
                    open_trades.append(trade)
                    
                    print(f"📈 OPEN LONG | {index} | Prix: {entry_price:.2f} | Lots: {position_info['lots']} | Risk: {position_info['risk_amount']}€ ({position_info['risk_percent']}%)")
            
            # SIGNAL SHORT - Ouvrir nouvelle position
            elif row["signal"] == -1 and len(open_trades) < 3:
                entry_price = row["close"]
                stop_loss = row["bb_middle"]
                take_profit = entry_price - ((stop_loss - entry_price) * self.risk_reward_ratio)
                
                position_info = self.calculate_position_size(entry_price, stop_loss)
                
                if position_info["lots"] > 0:
                    trade = {
                        "entry_time": index,
                        "entry_price": entry_price,
                        "direction": "SHORT",
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "risk_amount": position_info["risk_amount"],
                        "units": position_info["units"],
                        "lots": position_info["lots"],
                        "risk_percent": position_info["risk_percent"],
                        "phase": row["phase"],
                        "status": "OPEN"
                    }
                    
                    self.trades.append(trade)
                    open_trades.append(trade)
                    
                    print(f"📉 OPEN SHORT | {index} | Prix: {entry_price:.2f} | Lots: {position_info['lots']} | Risk: {position_info['risk_amount']}€ ({position_info['risk_percent']}%)")
        
        # Fermer les positions restantes à la fin
        for trade in open_trades:
            last_price = df.iloc[-1]["close"]
            if trade["direction"] == "LONG":
                pnl = (last_price - trade["entry_price"]) * trade["units"]
            else:
                pnl = (trade["entry_price"] - last_price) * trade["units"]
                
            self.close_trade(trade, last_price, "END_OF_DATA", pnl, df.index[-1])
        
        return self.closed_trades

    def close_trade(self, trade: Dict, exit_price: float, reason: str, pnl: float, exit_time: pd.Timestamp):
        """Ferme un trade et met à jour le capital"""
        closed_trade = {
            **trade,
            "exit_time": exit_time,
            "exit_price": exit_price,
            "exit_reason": reason,
            "pnl": round(pnl, 2),
            "pnl_percent": round((pnl / self.initial_capital) * 100, 4),
            "status": "CLOSED"
        }
        
        self.closed_trades.append(closed_trade)
        self.current_capital += pnl
        
        result = "🟢 PROFIT" if pnl > 0 else "🔴 PERTE"
        print(f"{result} | CLOSE {trade['direction']} | P&L: {pnl:+.2f}€ | Capital: {self.current_capital:.2f}€")

    def generate_money_management_report(self, symbol: str) -> Dict[str, Any]:
        """
        Génère un rapport détaillé de money management
        """
        if not self.closed_trades:
            return {"message": "Aucun trade exécuté"}
        
        # Métriques de performance
        total_trades = len(self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t["pnl"] > 0])
        losing_trades = len([t for t in self.closed_trades if t["pnl"] < 0])
        win_rate = (winning_trades / total_trades) * 100
        
        total_pnl = sum(t["pnl"] for t in self.closed_trades)
        avg_win = np.mean([t["pnl"] for t in self.closed_trades if t["pnl"] > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([t["pnl"] for t in self.closed_trades if t["pnl"] < 0]) if losing_trades > 0 else 0
        
        # Drawdown
        capital_history = [self.initial_capital]
        for trade in self.closed_trades:
            capital_history.append(capital_history[-1] + trade["pnl"])
        
        peak = capital_history[0]
        max_drawdown = 0
        for capital in capital_history:
            if capital > peak:
                peak = capital
            drawdown = (peak - capital) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Risk analysis
        total_risk = sum(t["risk_amount"] for t in self.closed_trades)
        avg_risk = total_risk / total_trades
        
        report = {
            "money_management": {
                "initial_capital": self.initial_capital,
                "final_capital": round(self.current_capital, 2),
                "net_profit": round(total_pnl, 2),
                "return_percent": round((total_pnl / self.initial_capital) * 100, 2),
                "max_drawdown": round(max_drawdown, 2),
                "sharpe_ratio": round((total_pnl / total_trades) / (np.std([t["pnl"] for t in self.closed_trades]) or 1), 2)
            },
            "performance": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 1),
                "avg_profit_per_trade": round(total_pnl / total_trades, 2),
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "profit_factor": round(abs(avg_win * winning_trades) / (abs(avg_loss) * losing_trades), 2) if losing_trades > 0 else float('inf')
            },
            "risk_analysis": {
                "risk_per_trade_percent": self.risk_per_trade * 100,
                "total_risk_taken": round(total_risk, 2),
                "avg_risk_per_trade": round(avg_risk, 2),
                "risk_reward_ratio": self.risk_reward_ratio
            },
            "trades_detailed": self.closed_trades
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