import pandas as pd
import numpy as np
from datetime import time
from typing import List, Dict, Any
from enum import Enum

from indicators.bollinger_bands import BollingerBands
from indicators.keltner_channel import KeltnerChannel

class TradeStatus(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class BBKeltnerStrategy:
    """
    STRATÉGIE OPTIMISÉE : Convergence BB/Keltner avec conditions équilibrées
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.01,
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_ema_period: int = 20,
        kc_atr_period: int = 10,
        kc_mult: float = 1.5,
        killzone_start: str = "03:00",
        killzone_end: str = "06:30",
        risk_reward_ratio: float = 1.8,
        ema_filter_period: int = 50,
        confirmation_candles: int = 1  # Réduit de 2 à 1
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        
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
        self.ema_period = ema_filter_period
        self.confirmation_candles = confirmation_candles
        
        # Suivi des trades
        self.trades = []
        self.portfolio_history = []
        self.closed_trades = []
        self.last_trade_time = None

    def in_killzone(self, dt: pd.Timestamp) -> bool:
        t = dt.time()
        return self.killzone_start <= t <= self.killzone_end

    def calculate_position_size(self, entry_price: float, stop_loss: float, symbol: str) -> Dict[str, float]:
        """Calcul des lots avec risk management strict"""
        risk_amount = self.current_capital * self.risk_per_trade
        
        if "XAU" in symbol:
            pip_value = 1.0
            pip_distance = abs(entry_price - stop_loss) / 0.01
        else:  # EURUSD
            pip_value = 1.0
            pip_distance = abs(entry_price - stop_loss) / 0.0001
        
        if pip_distance == 0:
            return {"lots": 0, "risk_amount": 0, "units": 0, "risk_percent": 0}
        
        lots = risk_amount / (pip_distance * pip_value)
        lots = round(max(0.01, min(lots, 1.0)), 2)
        
        actual_risk = pip_distance * pip_value * lots
        risk_percent = (actual_risk / self.current_capital) * 100
        units = lots * 10000
        
        return {
            "lots": lots,
            "units": int(units),
            "risk_amount": round(actual_risk, 2),
            "risk_percent": round(risk_percent, 2)
        }

    def is_bb_outside_kc(self, bb_upper: float, bb_lower: float, kc_upper: float, kc_lower: float) -> bool:
        """Vérifie si BB est SORTI du KC"""
        return (bb_upper > kc_upper) or (bb_lower < kc_lower)

    def is_bb_inside_kc(self, bb_upper: float, bb_lower: float, kc_upper: float, kc_lower: float, tolerance: float = 0.03) -> bool:
        """Vérifie si BB est RENTRÉ dans le KC (tolérance 3%)"""
        return (bb_upper <= kc_upper * (1 + tolerance)) and (bb_lower >= kc_lower * (1 - tolerance))

    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        return df['close'].ewm(span=period, adjust=False).mean()

    def should_enter_trade(self, df: pd.DataFrame, current_index: int, symbol: str) -> bool:
        """
        CONDITIONS OPTIMISÉES - Moins restrictives mais toujours sélectives
        """
        if current_index < max(self.ema_period, 10):
            return False

        current_time = df.index[current_index]
        
        # 1. Killzone uniquement
        if not self.in_killzone(current_time):
            return False

        # FILTRE TENDANCE - Évite les trades contre-tendance
        if not self.check_trend_filter(df, current_index):
            return False   
        # 2. Temps entre trades réduit à 15 minutes
        if self.last_trade_time is not None:
            time_diff = (current_time - self.last_trade_time).total_seconds()
            if time_diff < 900:  # 15 minutes au lieu de 60
                return False
        
        # 3. Séquence BB sort → BB rentre (version optimisée)
        if not self.check_breakout_conditions(df, current_index):
            return False
            
        # 4. Filtre EMA assoupli
        if not self.check_ema_filter_optimized(df, current_index):
            return False
            
        # 5. Momentum simplifié
        if not self.check_momentum_simple(df, current_index):
            return False
            
        # 6. Un seul trade maximum
        open_trades = [t for t in self.trades if t.get('status') == 'OPEN']
        if len(open_trades) >= 1:
            return False
            
        return True


    def check_breakout_conditions(self, df: pd.DataFrame, i: int) -> bool:
        """Vérifie les conditions de cassure avec tendance"""
        # Pour LONG: Cassure BB supérieure + tendance haussière
        if df['signal'].iloc[i] == 1:
            return (df['close'].iloc[i] > df['bb_upper'].iloc[i] and 
                df['ema_20'].iloc[i] > df['ema_50'].iloc[i])
    
        # Pour SHORT: Cassure BB inférieure + tendance baissière
        elif df['signal'].iloc[i] == -1:
            return (df['close'].iloc[i] < df['bb_lower'].iloc[i] and 
                df['ema_20'].iloc[i] < df['ema_50'].iloc[i])
    
        return False

    def check_trend_filter(self, df: pd.DataFrame, i: int) -> bool:
        """Filtre les trades contre-tendance - VERSION CORRIGÉE"""
        if i < 50:  # Besoin de EMA50 donc i >= 50
            return False
        
        # CALCUL CORRECT EMA20
        ema_20 = df['ema_20'].iloc[i]
        ema_50 = df['ema_50'].iloc[i]
    
        current_signal = df['signal'].iloc[i]
    
        print(f"🎯 Trend Check: Signal={current_signal}, EMA20={ema_20:.2f}, EMA50={ema_50:.2f}, Trend_OK={ema_20 > ema_50 if current_signal == 1 else ema_20 < ema_50}")
    
        # Pour LONG: EMA20 > EMA50 (tendance haussière)
        if current_signal == 1:
            return ema_20 > ema_50
        # Pour SHORT: EMA20 < EMA50 (tendance baissière)  
        elif current_signal == -1:
            return ema_20 < ema_50
        
        return False
    
    

    def check_ema_filter_optimized(self, df: pd.DataFrame, i: int) -> bool:
        """
        FILTRE EMA ASSOULI - Prix dans ±3% de l'EMA 50
        """
        current_price = df['close'].iloc[i]
        ema_50 = df['ema_50'].iloc[i]
        
        price_deviation = abs(current_price - ema_50) / ema_50
        return price_deviation <= 0.03  # 3% au lieu de 2%

    def check_momentum_simple(self, df: pd.DataFrame, i: int) -> bool:
        """
        MOMENTUM SIMPLIFIÉ - Une seule bougie de confirmation
        """
        if i < 2:
            return False
            
        current_close = df['close'].iloc[i]
        prev_close = df['close'].iloc[i-1]
        current_signal = df['signal'].iloc[i]
        
        # Pour LONG: bougie actuelle >= précédente
        if current_signal == 1:
            return current_close >= prev_close * 0.998  # Tolérance 0.2%
        # Pour SHORT: bougie actuelle <= précédente  
        elif current_signal == -1:
            return current_close <= prev_close * 1.002  # Tolérance 0.2%
            
        return False

    def calculate_stop_loss_optimized(self, df: pd.DataFrame, i: int, direction: str) -> float:
        """
        STOP LOSS OPTIMISÉ - Basé sur ATR pour plus de robustesse
        """
        # Calcul ATR simplifié
        true_ranges = []
        for j in range(max(0, i-13), i+1):
            tr1 = df['high'].iloc[j] - df['low'].iloc[j]
            tr2 = abs(df['high'].iloc[j] - df['close'].iloc[j-1]) if j > 0 else 0
            tr3 = abs(df['low'].iloc[j] - df['close'].iloc[j-1]) if j > 0 else 0
            true_ranges.append(max(tr1, tr2, tr3))
        atr = np.mean(true_ranges) if true_ranges else (df['high'].iloc[i] - df['low'].iloc[i])
        
        current_price = df['close'].iloc[i]
        
        if direction == "LONG":
            # Stop Loss: prix - 1.5 ATR
            stop_loss = current_price - (atr * 2.5)
            # Mais pas en dessous du plus bas récent
            recent_low = min([df['low'].iloc[i-j] for j in range(min(3, i+1))])
            stop_loss = max(stop_loss, recent_low * 0.999)
        else:  # SHORT
            # Stop Loss: prix + 1.5 ATR
            stop_loss = current_price + (atr * 2.5)
            # Mais pas au dessus du plus haut récent
            recent_high = max([df['high'].iloc[i-j] for j in range(min(3, i+1))])
            stop_loss = min(stop_loss, recent_high * 1.001)
            
        return round(stop_loss, 5)

    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Génération des signaux avec logique améliorée"""
        df = df.copy()

        required_cols = ["high", "low", "close", "open"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante: {col}")

        print("📈 Calcul des indicateurs avancés...")
        
        # Indicateurs de base
        bb_mid, bb_up, bb_low = self.bb.calculate(df[["close"]])
        kc_mid, kc_up, kc_low = self.kc.calculate(df)

        df["bb_middle"] = bb_mid
        df["bb_upper"] = bb_up
        df["bb_lower"] = bb_low
        df["kc_middle"] = kc_mid
        df["kc_upper"] = kc_up
        df["kc_lower"] = kc_low
        df["ema_50"] = self.calculate_ema(df, self.ema_period)

        # Après le calcul EMA50, AJOUTE :
        df["ema_20"] = df['close'].ewm(span=20, adjust=False).mean()

        # Phase de volatilité
        df["phase"] = "EXPANSION"
        for i in range(len(df)):
            if self.is_bb_inside_kc(df['bb_upper'].iloc[i], df['bb_lower'].iloc[i], 
                                  df['kc_upper'].iloc[i], df['kc_lower'].iloc[i]):
                df.iloc[i, df.columns.get_loc('phase')] = "CONTRACTION"

        # Signaux bruts
       # Signaux basés sur CASSURE + TENDANCE
        df["raw_signal"] = 0
        for i in range(50, len(df)):  # Besoin de EMA50
        # SCÉNARIO HAUSSIER : Prix > BB supérieure + EMA20 > EMA50
            if (df["close"].iloc[i] > df["bb_upper"].iloc[i] and 
                df["ema_20"].iloc[i] > df["ema_50"].iloc[i]):
                df.iloc[i, df.columns.get_loc('raw_signal')] = 1
    
        # SCÉNARIO BAISSIER : Prix < BB inférieure + EMA20 < EMA50  
            elif (df["close"].iloc[i] < df["bb_lower"].iloc[i] and 
                df["ema_20"].iloc[i] < df["ema_50"].iloc[i]):
                df.iloc[i, df.columns.get_loc('raw_signal')] = -1

        # Filtrage Killzone
        df["in_killzone"] = df.index.map(self.in_killzone)
        df["signal"] = 0
        for i in range(len(df)):
            if df["in_killzone"].iloc[i]:
                df.iloc[i, df.columns.get_loc('signal')] = df["raw_signal"].iloc[i]

        return df

    def execute_trading_strategy(self, df: pd.DataFrame) -> List[Dict]:
        """Exécution de la stratégie optimisée"""
        self.current_capital = self.initial_capital
        self.trades = []
        self.closed_trades = []
        self.portfolio_history = []
        self.last_trade_time = None
        
        open_trades = []
        
        print(f"🔍 Analyse de {len(df)} bougies pour signaux optimisés...")
        
        for i, (index, row) in enumerate(df.iterrows()):
            # Gestion des trades ouverts
            for trade in open_trades[:]:
                if trade["direction"] == "LONG":
                    if row["low"] <= trade["stop_loss"]:
                        pnl = (trade["stop_loss"] - trade["entry_price"]) * trade["units"]
                        self.close_trade(trade, trade["stop_loss"], "STOP_LOSS", pnl, index)
                        open_trades.remove(trade)
                    elif row["high"] >= trade["take_profit"]:
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
            
            symbol = "XAUUSD" if "XAU" in str(df.index.name) else "EURUSD"
            current_signal = row["signal"]
            
            # OUVERTURE DE TRADE
            if current_signal != 0 and self.should_enter_trade(df, i, symbol):
                entry_price = row["close"]
                direction = "LONG" if current_signal == 1 else "SHORT"
                
                stop_loss = self.calculate_stop_loss_optimized(df, i, direction)
                
                if direction == "LONG":
                    take_profit = entry_price + ((entry_price - stop_loss) * self.risk_reward_ratio)
                else:
                    take_profit = entry_price - ((stop_loss - entry_price) * self.risk_reward_ratio)
                
                position_info = self.calculate_position_size(entry_price, stop_loss, symbol)
                
                if (position_info["lots"] > 0 and 
                    position_info["risk_percent"] <= 1.5 and
                    position_info["risk_percent"] >= 0.3):
                    
                    trade = {
                        "entry_time": index,
                        "entry_price": round(entry_price, 5),
                        "direction": direction,
                        "stop_loss": round(stop_loss, 5),
                        "take_profit": round(take_profit, 5),
                        "risk_amount": position_info["risk_amount"],
                        "units": position_info["units"],
                        "lots": position_info["lots"],
                        "risk_percent": position_info["risk_percent"],
                        "phase": row["phase"],
                        "status": "OPEN"
                    }
                    
                    self.trades.append(trade)
                    open_trades.append(trade)
                    self.last_trade_time = index
                    
                    print(f"🎯 {'📈' if direction == 'LONG' else '📉'} OPEN {direction} | {index} | Prix: {entry_price:.2f} | Lots: {position_info['lots']} | Risk: {position_info['risk_percent']}%")
                    print(f"   🛑 SL: {stop_loss:.2f} | 🎯 TP: {take_profit:.2f} | 📊 R/R: {self.risk_reward_ratio}")
        
        # Fermeture des trades restants
        if open_trades:
            last_price = df.iloc[-1]["close"]
            for trade in open_trades:
                if trade["direction"] == "LONG":
                    pnl = (last_price - trade["entry_price"]) * trade["units"]
                else:
                    pnl = (trade["entry_price"] - last_price) * trade["units"]
                self.close_trade(trade, last_price, "END_OF_DATA", pnl, df.index[-1])
        
        print(f"\n✅ STRATÉGIE OPTIMISÉE TERMINÉE: {len(self.closed_trades)} trades exécutés")
        return self.closed_trades

    def close_trade(self, trade: Dict, exit_price: float, reason: str, pnl: float, exit_time: pd.Timestamp):
        """Fermeture de trade"""
        closed_trade = {
            **trade,
            "exit_time": exit_time,
            "exit_price": round(exit_price, 5),
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
        """Génération du rapport"""
        if not self.closed_trades:
            return {"error": "Aucun trade exécuté", "symbol": symbol}
        
        total_trades = len(self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t["pnl"] > 0])
        losing_trades = len([t for t in self.closed_trades if t["pnl"] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
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
        
        total_risk = sum(t["risk_amount"] for t in self.closed_trades)
        avg_risk = total_risk / total_trades if total_trades > 0 else 0
        
        report = {
            "money_management": {
                "initial_capital": self.initial_capital,
                "final_capital": round(self.current_capital, 2),
                "net_profit": round(total_pnl, 2),
                "return_percent": round((total_pnl / self.initial_capital) * 100, 2),
                "max_drawdown": round(max_drawdown, 2),
                "sharpe_ratio": round((total_pnl / total_trades) / (np.std([t["pnl"] for t in self.closed_trades]) or 1), 2) if total_trades > 1 else 0
            },
            "performance": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 1),
                "avg_profit_per_trade": round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
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
            "trades_detailed": self.closed_trades,
            "symbol": symbol
        }
        
        return report

    def summary(self, df: pd.DataFrame) -> dict:
        long_signals = (df["signal"] == 1).sum()
        short_signals = (df["signal"] == -1).sum()
        total = long_signals + short_signals
        
        return {
            "total_signaux": total,
            "longs": long_signals,
            "shorts": short_signals,
            "periode": f"{self.killzone_start.strftime('%H:%M')}–{self.killzone_end.strftime('%H:%M')}",
        }