class GPTAnalyzerTradeDemo:
    def __init__(self):
        pass

    def analyze_trade_with_fundamentals(self, trade: dict, fundamentals: str) -> dict:
        result = trade.copy()
        result['gpt_summary'] = f"Analyse fondamentale pour {trade['symbol']} : {fundamentals[:200]}..."
        if trade['signal'] == 1:
            result['gpt_confirmation'] = "Trade LONG cohérent selon analyse fondamentale"
        else:
            result['gpt_confirmation'] = "Trade SHORT cohérent selon analyse fondamentale"
        return result
