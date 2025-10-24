import pandas as pd
import numpy as np
from datetime import time

from indicators.bollinger_bands import BollingerBands
from indicators.keltner_channel import KeltnerChannel

class BBKeltnerStrategy:
    """
    Stratégie de convergence entre Bollinger Bands et Keltner Channels,
    utilisée pour détecter les phases de contraction/expansion de volatilité.
    Les signaux ne sont exécutés que durant la killzone (03h00–06h30).
    """

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_period: int = 20,
        kc_mult: float = 1.5,
        killzone_start: str = "03:00",
        killzone_end: str = "06:30",
    ):
        self.bb = BollingerBands(period=bb_period, std_dev=bb_std)
        self.kc = KeltnerChannel(period=kc_period, multiplier=kc_mult)

        h_start, m_start = map(int, killzone_start.split(":"))
        h_end, m_end = map(int, killzone_end.split(":"))
        self.killzone_start = time(h_start, m_start)
        self.killzone_end = time(h_end, m_end)

    # --- Vérifie si une bougie est dans la killzone ---
    def in_killzone(self, dt: pd.Timestamp) -> bool:
        t = dt.time()
        return self.killzone_start <= t <= self.killzone_end

    # --- Calcul des signaux principaux ---
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Vérifications de colonnes
        for col in ["high", "low", "close"]:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante : {col}")

        # Calcul des indicateurs
        bb_mid, bb_up, bb_low = self.bb.calculate(df["close"])
        kc_mid, kc_up, kc_low = self.kc.calculate(df["high"], df["low"], df["close"])

        df["bb_upper"] = bb_up
        df["bb_lower"] = bb_low
        df["kc_upper"] = kc_up
        df["kc_lower"] = kc_low

        # --- Détection des phases ---
        df["phase"] = np.where(
            (df["bb_lower"] > df["kc_lower"]) & (df["bb_upper"] < df["kc_upper"]),
            "contraction",
            "expansion",
        )

        # --- Génération des signaux ---
        df["signal"] = 0
        df.loc[df["close"] > df["bb_upper"], "signal"] = 1   # Breakout haussier
        df.loc[df["close"] < df["bb_lower"], "signal"] = -1  # Breakout baissier

        # --- Filtrage Killzone ---
        df["in_killzone"] = df.index.map(self.in_killzone)
        df["final_signal"] = df["signal"].where(df["in_killzone"], 0)

        return df

    # --- Affichage résumé ---
    def summary(self, df: pd.DataFrame) -> dict:
        long_signals = (df["final_signal"] == 1).sum()
        short_signals = (df["final_signal"] == -1).sum()
        total = long_signals + short_signals
        return {
            "total_signaux": total,
            "longs": long_signals,
            "shorts": short_signals,
            "periode": f"{self.killzone_start.strftime('%H:%M')}–{self.killzone_end.strftime('%H:%M')}",
        }
