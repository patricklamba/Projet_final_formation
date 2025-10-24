import pandas as pd
import os

class FileManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir

    def load_csv(self, symbol: str) -> pd.DataFrame:
        path = f"{self.data_dir}/{symbol}.csv"
        
        # Vérifier l'existence du fichier
        if not os.path.exists(path):
            raise FileNotFoundError(f"Fichier {path} introuvable")
        
        # Charger avec séparateur tabulation
        df = pd.read_csv(path, sep='\t')
        
        # Nettoyage des colonnes
        df.columns = [col.strip("<>").lower() for col in df.columns]
        print(f"📊 Colonnes détectées: {list(df.columns)}")

        # Vérification des colonnes obligatoires
        required = {"open", "high", "low", "close"}
        if not required.issubset(df.columns):
            missing = required - set(df.columns)
            raise ValueError(f"Colonnes manquantes: {missing}")

        # Conversion en float
        for col in required:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Supprimer les NaN
        df.dropna(subset=required, inplace=True)

        # Créer index datetime
        if "date" in df.columns and "time" in df.columns:
            df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
            df.set_index("datetime", inplace=True)
            print(f"✅ Index datetime créé")
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            print(f"✅ Index date créé")

        print(f"✅ Données chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        return df