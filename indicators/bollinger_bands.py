"""
Bollinger Bands Indicator
-------------------------
Calcule les bandes de Bollinger pour une série de prix.

Formule :
- SMA = moyenne mobile simple
- Upper Band = SMA + K * STD
- Lower Band = SMA - K * STD
"""

import pandas as pd

class BollingerBands:
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        """
        Initialise les paramètres des bandes de Bollinger.
        :param period: période de la moyenne mobile (par défaut 20)
        :param std_dev: multiplicateur de l'écart type (par défaut 2.0)
        """
        self.period = period
        self.std_dev = std_dev

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les bandes de Bollinger sur une DataFrame contenant une colonne 'close'.
        Retourne une DataFrame avec colonnes ['BB_Middle', 'BB_Upper', 'BB_Lower'].
        """
        if 'close' not in data.columns:
            raise ValueError("La DataFrame doit contenir une colonne 'close'.")

        df = data.copy()
        df['BB_Middle'] = df['close'].rolling(window=self.period).mean()
        df['BB_STD'] = df['close'].rolling(window=self.period).std(ddof=0)
        df['BB_Upper'] = df['BB_Middle'] + (self.std_dev * df['BB_STD'])
        df['BB_Lower'] = df['BB_Middle'] - (self.std_dev * df['BB_STD'])
        df.drop(columns=['BB_STD'], inplace=True)
        return df
