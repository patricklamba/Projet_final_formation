import pandas as pd

class BollingerBandsDemo:
    def __init__(self, series, window=20, num_std=2):
        self.series = series
        self.window = window
        self.num_std = num_std

    def middle_band(self):
        return self.series.rolling(self.window).mean()

    def upper_band(self):
        return self.middle_band() + self.series.rolling(self.window).std() * self.num_std

    def lower_band(self):
        return self.middle_band() - self.series.rolling(self.window).std() * self.num_std
