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
