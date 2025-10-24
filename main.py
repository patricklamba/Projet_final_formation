"""
main.py
--------
Point d'entrée du projet : charge les données, exécute la stratégie
et affiche les résultats.
"""

from core.strategy import BBKeltnerStrategy
from utils.file_manager import FileManager
import pandas as pd

def run_strategy(symbol: str):
    print(f"\n🚀 Exécution de la stratégie pour {symbol}...")

    # 1️⃣ Charger les données
    fm = FileManager(data_dir="data")
    try:
        df = fm.load_csv(symbol)
        print(f"✅ Données chargées : {len(df)} lignes")
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return

    # 2️⃣ Créer et exécuter la stratégie
    strategy = BBKeltnerStrategy(data=df)
    result = strategy.run()

    # 3️⃣ Résumé
    print(f"\n📊 Résumé des signaux détectés ({symbol}) :")
    print(result.tail(5))

    # 4️⃣ Sauvegarde des résultats (optionnel)
    output_path = f"data/results_{symbol}.csv"
    result.to_csv(output_path)
    print(f"💾 Résultats enregistrés dans {output_path}")

if __name__ == "__main__":
    # Tu peux tester sur une ou plusieurs paires :
    for pair in ["XAUUSD", "EURUSD"]:
        run_strategy(pair)

    print("\n🎯 Exécution terminée avec succès.")
