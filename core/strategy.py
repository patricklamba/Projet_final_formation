"""
Stratégie principale basée sur la convergence de signaux
"""
import sys
import os
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

from config.strategy_config import INDICATOR_CONFIG, STRATEGY_CONFIG
from core.signal_convergence import SignalConvergence
from core.money_management import MoneyManagement
# Assurer que le dossier utils est dans le path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class MultiSignalStrategy:
    """
    Stratégie de trading basée sur la convergence de multiples indicateurs techniques
    """
    
    def __init__(self, initial_capital: float = None):
        self.config = STRATEGY_CONFIG
        self.money_management = MoneyManagement(initial_capital)
        
        # Initialisation des indicateurs
        self.indicators = self._initialize_indicators()
        self.signal_convergence = SignalConvergence(self.indicators)
        
        # Suivi des trades
        self.trades = []
        self.closed_trades = []
        self.portfolio_history = []
        
    def _initialize_indicators(self) -> Dict:
        """Initialise les indicateurs activés dans la configuration"""
        indicators = {}
        
        if INDICATOR_CONFIG['bollinger_bands']['enabled']:
            from indicators.bollinger_bands import BollingerBands
            params = INDICATOR_CONFIG['bollinger_bands']['params']
            indicators['bollinger_bands'] = BollingerBands(**params)
            
        if INDICATOR_CONFIG['keltner_channel']['enabled']:
            from indicators.keltner_channel import KeltnerChannel
            params = INDICATOR_CONFIG['keltner_channel']['params']
            indicators['keltner_channel'] = KeltnerChannel(**params)
            
        if INDICATOR_CONFIG['ema']['enabled']:
            from indicators.ema import EMA
            params = INDICATOR_CONFIG['ema']['params']
            indicators['ema'] = EMA(**params)
            
        if INDICATOR_CONFIG['rsi']['enabled']:
            from indicators.rsi import RSI
            params = INDICATOR_CONFIG['rsi']['params']
            indicators['rsi'] = RSI(**params)
            
        # Ajouter d'autres indicateurs selon la configuration...
            
        return indicators
    
    def apply_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applique tous les indicateurs activés sur les données"""
        df_processed = df.copy()
        
        for indicator_name, indicator in self.indicators.items():
            if INDICATOR_CONFIG[indicator_name]['enabled']:
                df_processed = indicator.calculate(df_processed)
                
        return df_processed
    
    def execute_strategy(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """
        Exécute la stratégie complète sur les données
        """
        print(f"🔧 DEBUG: Début execute_strategy pour {symbol}")
        df = self.apply_indicators(df)
        self.trades = []
        self.closed_trades = []
        
        open_trades = []

        print(f"🔧 DEBUG: Données après indicateurs: {len(df)} lignes")
        
        for i in range(50, len(df)):  # Commencer après la période de warmup
            current_time = df.index[i] if hasattr(df.index, 'iloc') else i
            
            # Gérer les trades ouverts
            open_trades = self._manage_open_trades(open_trades, df, i, current_time)
            
            # Vérifier les conditions d'entrée
            if self._should_enter_trade(df, i, symbol, open_trades):
                self._enter_trade(df, i, symbol, open_trades, current_time)
        
        # Fermer les trades restants à la fin
        self._close_remaining_trades(open_trades, df)

        print(f"🔧 DEBUG: {symbol} - Trades fermés: {len(self.closed_trades)}")

        return self.closed_trades
    
    def _should_enter_trade(self, df: pd.DataFrame, current_index: int, 
                          symbol: str, open_trades: List) -> bool:
        """Vérifie si les conditions d'entrée sont remplies"""
        
        # Vérifier le nombre maximum de trades ouverts
        if len(open_trades) >= self.config['risk_management']['max_open_trades']:
            return False
            
        # Calculer le score de convergence
        score, signals = self.signal_convergence.compute_convergence_score(df, current_index)
        
        # Vérifier la validité du signal
        if not self.signal_convergence.is_valid_entry(score, signals, df, current_index):
            return False
            
        # Vérifier la killzone
        if not self._in_killzone(df, current_index):
            return False
            
        return True
    
    def _enter_trade(self, df: pd.DataFrame, current_index: int, symbol: str,
                   open_trades: List, current_time: Any):
        """Ouvre un nouveau trade"""
        score, signals = self.signal_convergence.compute_convergence_score(df, current_index)
        direction = "LONG" if score > 0 else "SHORT"
        entry_price = df['close'].iloc[current_index]
        
        # Calcul SL/TP
        stop_loss, take_profit = self.money_management.calculate_stop_loss_take_profit(
            entry_price, direction, symbol=symbol
        )
        
        # Calcul position sizing
        position_info = self.money_management.calculate_position_size(
            entry_price, stop_loss, symbol
        )
        
        # Validation du trade
        if not self.money_management.validate_trade(
            position_info['risk_amount'], position_info['risk_percent']
        ):
            return
            
        # Création du trade
        trade = {
            'entry_time': current_time,
            'entry_price': round(entry_price, 5),
            'direction': direction,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_amount': position_info['risk_amount'],
            'units': position_info['units'],
            'lots': position_info['lots'],
            'risk_percent': position_info['risk_percent'],
            'convergence_score': score,
            'signals': signals,
            'symbol': symbol,
            'status': 'OPEN'
        }
        
        self.trades.append(trade)
        open_trades.append(trade)
        
        print(f"🎯 {'📈' if direction == 'LONG' else '📉'} OPEN {direction} | "
              f"Prix: {entry_price:.2f} | Lots: {position_info['lots']} | "
              f"Score: {score:.1f}")
    
    def _manage_open_trades(self, open_trades: List, df: pd.DataFrame, 
                          current_index: int, current_time: Any) -> List:
        """Gère les trades ouverts (SL/TP)"""
        current_high = df['high'].iloc[current_index]
        current_low = df['low'].iloc[current_index]
        current_close = df['close'].iloc[current_index]
        
        for trade in open_trades[:]:
            if trade['direction'] == 'LONG':
                # Check Stop Loss
                if current_low <= trade['stop_loss']:
                    pnl = (trade['stop_loss'] - trade['entry_price']) * trade['units']
                    self._close_trade(trade, trade['stop_loss'], 'STOP_LOSS', pnl, current_time)
                    open_trades.remove(trade)
                # Check Take Profit
                elif current_high >= trade['take_profit']:
                    pnl = (trade['take_profit'] - trade['entry_price']) * trade['units']
                    self._close_trade(trade, trade['take_profit'], 'TAKE_PROFIT', pnl, current_time)
                    open_trades.remove(trade)
                    
            else:  # SHORT
                # Check Stop Loss
                if current_high >= trade['stop_loss']:
                    pnl = (trade['entry_price'] - trade['stop_loss']) * trade['units']
                    self._close_trade(trade, trade['stop_loss'], 'STOP_LOSS', pnl, current_time)
                    open_trades.remove(trade)
                # Check Take Profit
                elif current_low <= trade['take_profit']:
                    pnl = (trade['entry_price'] - trade['take_profit']) * trade['units']
                    self._close_trade(trade, trade['take_profit'], 'TAKE_PROFIT', pnl, current_time)
                    open_trades.remove(trade)
        
        return open_trades
    
    def _close_trade(self, trade: Dict, exit_price: float, reason: str, 
                   pnl: float, exit_time: Any):
        """Ferme un trade avec calcul P&L corrigé"""
        
        # DEBUG: Vérifier les calculs
        print(f"🔧 DEBUG CLOSE: {trade['direction']} | "
            f"Entry: {trade['entry_price']} | Exit: {exit_price} | "
            f"Units: {trade['units']} | Lots: {trade['lots']}")
        
        # Calcul P&L CORRIGÉ
        if trade['direction'] == 'LONG':
            price_diff = exit_price - trade['entry_price']
        else:  # SHORT
            price_diff = trade['entry_price'] - exit_price
        
        # P&L = différence de prix × units
        pnl_corrected = price_diff * trade['units']
        
        closed_trade = {
            **trade,
            'exit_time': exit_time,
            'exit_price': round(exit_price, 5),
            'exit_reason': reason,
            'pnl': round(pnl_corrected, 2),  # ← UTILISER pnl_corrected
            'pnl_percent': round((pnl_corrected / self.money_management.current_capital) * 100, 4),
            'status': 'CLOSED'
        }
        
        self.closed_trades.append(closed_trade)
        self.money_management.update_capital(
            self.money_management.current_capital + pnl_corrected  # ← UTILISER pnl_corrected
        )
        
        result = "🟢 PROFIT" if pnl_corrected > 0 else "🔴 PERTE"
        print(f"{result} | CLOSE {trade['direction']} | P&L: {pnl_corrected:+.2f}€ | "
            f"Capital: {self.money_management.current_capital:.2f}€")
    
    def _in_killzone(self, df: pd.DataFrame, current_index: int) -> bool:
        """Vérifie si on est dans la killzone de trading"""
        # Implémentation simplifiée - à adapter selon vos données
        return True
    
    def _close_remaining_trades(self, open_trades: List, df: pd.DataFrame):
        """Ferme les trades restants à la fin des données"""
        if open_trades:
            last_price = df.iloc[-1]['close']
            for trade in open_trades:
                if trade['direction'] == 'LONG':
                    pnl = (last_price - trade['entry_price']) * trade['units']
                else:
                    pnl = (trade['entry_price'] - last_price) * trade['units']
                    
                self._close_trade(trade, last_price, 'END_OF_DATA', pnl, df.index[-1])
    
    def generate_report(self, symbol: str) -> Dict[str, Any]:
        """Génère un rapport de performance en utilisant ReportGenerator"""
        try:
            # Import avec chemin absolu
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from utils.report_generator import ReportGenerator
            
            # S'assurer que closed_trades existe
            closed_trades = getattr(self, 'closed_trades', [])
            capital = getattr(self.money_management, 'capital', 100000.0)
            
            print(f"🔧 DEBUG generate_report: {len(closed_trades)} trades fermés, capital: {capital}")
            
            return ReportGenerator.generate_trading_report(closed_trades, symbol, capital)
            
        except Exception as e:
            print(f"❌ Erreur génération rapport {symbol}: {e}")
            # Retourner un rapport d'urgence sécurisé
            return {
                "symbol": symbol,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "net_profit": 0,
                    "gross_profit": 0,
                    "gross_loss": 0,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "breakeven_trades": 0,
                    "win_rate": 0
                },
                "performance": {
                    "profit_factor": 0,
                    "average_win": 0,
                    "average_loss": 0,
                    "largest_win": 0,
                    "largest_loss": 0,
                    "risk_reward_ratio": 0,
                    "roi_percent": 0
                },
                "capital_evolution": {
                    "initial_capital": 100000.0,
                    "final_capital": 100000.0,
                    "net_profit": 0
                }
            }