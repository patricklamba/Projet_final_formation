class Backtester:
    """
    Simple backtester pour la stratégie BB+Keltner.
    """
    def __init__(self, data: pd.DataFrame, strategy):
        self.data = data.copy()
        self.strategy = strategy

    def run(self):
        self.data = self.strategy.generate_signals(self.data)
        return self.evaluate()

    def evaluate(self):
        """
        Retourne un score simple : nombre de signaux haussiers / baissiers.
        """
        long_signals = (self.data['final_signal'] == 1).sum()
        short_signals = (self.data['final_signal'] == -1).sum()
        return {
            "long_signals": long_signals,
            "short_signals": short_signals,
            "total": long_signals + short_signals
        }
