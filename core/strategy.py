import pandas as pd
from datetime import time

from indicators.bollinger_bands import BollingerBands
from indicators.keltner_channel import KeltnerChannel

class BBKeltnerStrategy:
    """
    Stratégie de convergence entre Bollinger et Keltner
    pendant la killzone 03h00–06h30.
    """

    def __init__(self, bb_period=20, bb_std=2, kc_period=20, kc_mult=1.5):
        self.bb = BollingerBands(bb_period, bb_std)
        self.kc = KeltnerChannel(kc_period, kc_mult)

    def in_killzone(self, dt):
        return time(3, 0) <= dt.time() <= time(6, 30)

    def generate_signals(self, df: pd.DataFrame):
        ma, bb_up, bb_low = self.bb.calculate(df['close'])
        mid, kc_up, kc_low = self.kc.calculate(df['high'], df['low'], df['close'])

        df['signal'] = 0
        df.loc[(bb_low > kc_low) & (bb_up < kc_up), 'signal'] = 1  # contraction
        df.loc[(bb_low < kc_low) & (bb_up > kc_up), 'signal'] = -1 # expansion

        df['in_killzone'] = df.index.map(self.in_killzone)
        df['final_signal'] = df['signal'] * df['in_killzone']
        return df
