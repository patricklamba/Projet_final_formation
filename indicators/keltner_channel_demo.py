import pandas as pd

class KeltnerChannelDemo:
    def __init__(self, high, low, close, window=20, multiplier=1.5):
        self.high = high
        self.low = low
        self.close = close
        self.window = window
        self.multiplier = multiplier

    def typical_price(self):
        return (self.high + self.low + self.close) / 3

    def atr(self):
        tr = pd.concat([self.high - self.low,
                        (self.high - self.close.shift()).abs(),
                        (self.low - self.close.shift()).abs()], axis=1)
        return tr.max(axis=1).rolling(self.window).mean()

    def upper_band(self):
        return self.typical_price().rolling(self.window).mean() + self.atr() * self.multiplier

    def lower_band(self):
        return self.typical_price().rolling(self.window).mean() - self.atr() * self.multiplier
