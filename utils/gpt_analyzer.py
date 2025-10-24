"""
Module GPT pour confirmer un trade sur base des données fondamentales
"""

class GPTAnalyzer:
    def __init__(self):
        pass  # config API si nécessaire

    def analyze_trade_with_fundamentals(self, trade: dict, fundamentals: str) -> dict:
        """
        trade: {'symbol': 'XAUUSD', 'signal': 1, 'entry': 2050, 'stop_loss': 2040, 'take_profit': 2060}
        fundamentals: texte scrappé du jour
        Retour: dict avec résumé GPT + confirmation
        """
        # Pour démo : simulation de réponse GPT
        result = trade.copy()
        result['gpt_summary'] = f"Analyse fondamentale pour {trade['symbol']} : {fundamentals[:200]}..."
        if trade['signal'] == 1:
            result['gpt_confirmation'] = "Trade LONG cohérent selon analyse fondamentale"
        else:
            result['gpt_confirmation'] = "Trade SHORT cohérent selon analyse fondamentale"
        return result
