import os

base_path = r"C:\Users\lamba\Documents\DEV\Python_formation\Projet_final_formation"

files_content = {
    "indicators/bollinger_bands.py": '''\
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
''',

    "indicators/keltner_channel.py": '''\
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
''',

    "core/strategy.py": '''\
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
''',

    "core/backtester.py": '''\
import pandas as pd

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
''',

    "utils/file_manager.py": '''\
import pandas as pd
import os

class FileManager:
    """
    Gère la lecture/écriture de fichiers CSV (OHLC data).
    """

    @staticmethod
    def load_csv(filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fichier introuvable : {filepath}")
        return pd.read_csv(filepath, parse_dates=True, index_col=0)

    @staticmethod
    def save_csv(df: pd.DataFrame, filepath: str):
        df.to_csv(filepath)
''',

    "main.py": '''\
from core.strategy import BBKeltnerStrategy
from core.backtester import Backtester
from utils.file_manager import FileManager

def main():
    print("=== Backtest BB + Keltner (Killzone 03h00–06h30) ===")
    data_path = "data/XAUUSD_15m.csv"  # à placer manuellement dans /data
    try:
        df = FileManager.load_csv(data_path)
    except FileNotFoundError:
        print("⚠️ Données non trouvées. Placez un fichier CSV OHLC dans /data/")
        return

    strat = BBKeltnerStrategy()
    backtester = Backtester(df, strat)
    results = backtester.run()

    print("Résultats du backtest :", results)

if __name__ == "__main__":
    main()
'''
}

for path, content in files_content.items():
    full_path = os.path.join(base_path, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ Fichier créé : {full_path}")

print("\n🎯 Squelette de projet généré avec succès !")
