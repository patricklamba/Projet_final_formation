"""
Générateur de rapports de performance avancé
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics


class ReportGenerator:
    """Génère des rapports de performance détaillés"""
    
    @staticmethod
    def generate_trading_report(closed_trades: List[Dict], symbol: str, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """Génère un rapport complet de performance"""
        
        if not closed_trades:
            return ReportGenerator._empty_report(symbol, initial_capital)
        
        try:
            # Calculs de base
            total_trades = len(closed_trades)
            winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
            losing_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]
            breakeven_trades = [t for t in closed_trades if t.get('pnl', 0) == 0]
            
            win_count = len(winning_trades)
            loss_count = len(losing_trades)
            
            # Calculs P&L
            gross_profit = sum(trade.get('pnl', 0) for trade in winning_trades)
            gross_loss = sum(trade.get('pnl', 0) for trade in losing_trades)
            net_profit = gross_profit + gross_loss
            
            # Métriques de performance
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
            profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf')
            
            # Calculs avancés
            avg_win = statistics.mean([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
            avg_loss = statistics.mean([t.get('pnl', 0) for t in losing_trades]) if losing_trades else 0
            largest_win = max([t.get('pnl', 0) for t in winning_trades]) if winning_trades else 0
            largest_loss = min([t.get('pnl', 0) for t in losing_trades]) if losing_trades else 0
            
            # ROI et drawdown
            final_capital = initial_capital + net_profit
            roi = (net_profit / initial_capital) * 100
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "net_profit": round(net_profit, 2),
                    "gross_profit": round(gross_profit, 2),
                    "gross_loss": round(gross_loss, 2),
                    "total_trades": total_trades,
                    "winning_trades": win_count,
                    "losing_trades": loss_count,
                    "breakeven_trades": len(breakeven_trades),
                    "win_rate": round(win_rate, 1)
                },
                "performance": {
                    "profit_factor": round(profit_factor, 2),
                    "average_win": round(avg_win, 2),
                    "average_loss": round(avg_loss, 2),
                    "largest_win": round(largest_win, 2),
                    "largest_loss": round(largest_loss, 2),
                    "risk_reward_ratio": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
                    "roi_percent": round(roi, 2)
                },
                "capital_evolution": {
                    "initial_capital": initial_capital,
                    "final_capital": round(final_capital, 2),
                    "net_profit": round(net_profit, 2)
                }
            }
        except Exception as e:
            print(f"❌ Erreur lors de la génération du rapport: {e}")
            return ReportGenerator._empty_report(symbol, initial_capital)
    
    @staticmethod
    def _empty_report(symbol: str, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """Retourne un rapport vide"""
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
                "initial_capital": initial_capital,
                "final_capital": initial_capital,
                "net_profit": 0
            }
        }
    
    @staticmethod
    def format_report_for_display(report: Dict[str, Any]) -> str:
        """Formate le rapport pour l'affichage console"""
        try:
            summary = report.get('summary', {})
            
            # Formatage avec emojis
            net_profit = summary.get('net_profit', 0)
            gross_profit = summary.get('gross_profit', 0)
            gross_loss = summary.get('gross_loss', 0)
            
            net_profit_str = f"+{net_profit:,.2f}€" if net_profit >= 0 else f"{net_profit:,.2f}€"
            gross_profit_str = f"+{gross_profit:,.2f}€" if gross_profit >= 0 else f"{gross_profit:,.2f}€"
            gross_loss_str = f"{gross_loss:,.2f}€"
            
            return f"""
    RÉSUMÉ GLOBAL:
    💰 PROFIT NET TOTAL: {net_profit_str}
    💹 GAINS BRUTS TOTAUX: {gross_profit_str}
    📉 PERTES BRUTES TOTALES: {gross_loss_str}
    📊 TOTAL TRADES: {summary.get('total_trades', 0)}
    ✅ TRADES GAGNANTS: {summary.get('winning_trades', 0)}
    ❌ TRADES PERDANTS: {summary.get('losing_trades', 0)}
    🏆 WIN RATE GLOBAL: {summary.get('win_rate', 0)}%
    """
        except Exception as e:
            return f"❌ Erreur de formatage du rapport: {e}"