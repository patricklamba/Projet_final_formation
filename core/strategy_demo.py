import pandas as pd
from indicators.bollinger_bands_demo import BollingerBandsDemo
from indicators.keltner_channel_demo import KeltnerChannelDemo

class BBKeltnerStrategyDemo:
    def __init__(self):
        pass

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        bb = BollingerBandsDemo(df['close'])
        kc = KeltnerChannelDemo(df['high'], df['low'], df['close'])

        df['bb_upper'] = bb.upper_band()
        df['bb_lower'] = bb.lower_band()
        df['kc_upper'] = kc.upper_band()
        df['kc_lower'] = kc.lower_band()

        df['final_signal'] = 0
        df.loc[(df['close'] > df['bb_upper']) & (df['close'] > df['kc_upper']), 'final_signal'] = 1
        df.loc[(df['close'] < df['bb_lower']) & (df['close'] < df['kc_lower']), 'final_signal'] = -1
        return df
