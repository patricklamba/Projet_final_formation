import pandas as pd

class BollingerBands:
    """
    Calcule les bandes de Bollinger.
    """
    def __init__(self, period: int = 20, std_dev: float = 2):
        self.period = period
        self.std_dev = std_dev

    def calculate(self, data: pd.Series):
        """
        Retourne moyenne, bande sup et bande inférieure.
        """
        ma = data.rolling(self.period).mean()
        std = data.rolling(self.period).std()
        upper = ma + (self.std_dev * std)
        lower = ma - (self.std_dev * std)
        return ma, upper, lower
