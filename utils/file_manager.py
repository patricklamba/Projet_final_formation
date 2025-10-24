"""
File Manager Utility
--------------------
Gère le chargement, la validation et la préparation des données CSV
pour la stratégie de trading (XAUUSD, EURUSD, etc.)
"""

import os
import pandas as pd

class FileManager:
    def __init__(self, data_dir: str = "data"):
        """
        Initialise le gestionnaire de fichiers.
        :param data_dir: dossier contenant les CSV (par défaut 'data')
        """
        self.data_dir = data_dir

    def load_csv(self, symbol: str) -> pd.DataFrame:
        """
        Charge un fichier CSV pour un symbole donné (ex: 'XAUUSD').
        Vérifie que le fichier existe et que les colonnes sont correctes.
        """
        path = os.path.join(self.data_dir, f"{symbol}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Fichier introuvable : {path}")

        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise RuntimeError(f"⚠️ Erreur lors du chargement du CSV : {e}")

        # Nettoyage et standardisation
        df.columns = [col.lower() for col in df.columns]
        expected_cols = {'open', 'high', 'low', 'close'}
        if not expected_cols.issubset(df.columns):
            raise ValueError(f"⚠️ Le CSV doit contenir les colonnes : {expected_cols}")

        # Si une colonne 'datetime' existe → la mettre en index
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def list_data_files(self):
        """Liste les fichiers CSV disponibles dans le dossier data."""
        return [f for f in os.listdir(self.data_dir) if f.endswith(".csv")]
