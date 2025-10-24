import pandas as pd

class KeltnerChannel:
    """
    Calcule le canal de Keltner.
    """
    def __init__(self, period: int = 20, multiplier: float = 1.5):
        self.period = period
        self.multiplier = multiplier

    def calculate(self, high: pd.Series, low: pd.Series, close: pd.Series):
        atr = (high - low).rolling(self.period).mean()
        middle = close.rolling(self.period).mean()
        upper = middle + self.multiplier * atr
        lower = middle - self.multiplier * atr
        return middle, upper, lower
