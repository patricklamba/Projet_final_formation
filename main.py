from core.strategy import BBKeltnerStrategy
from utils.file_manager import FileManager

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
    strategy = BBKeltnerStrategy()
    df_signals = strategy.generate_signals(df)

    # 3️⃣ Résumé
    summary = strategy.summary(df_signals)
    print(f"\n📊 Résumé des signaux détectés ({symbol}) : {summary}")

    # 4️⃣ Sauvegarde des résultats
    output_path = f"data/results_{symbol}.csv"
    df_signals.to_csv(output_path)
    print(f"💾 Résultats enregistrés dans {output_path}")

if __name__ == "__main__":
    for pair in ["XAUUSD", "EURUSD"]:
        run_strategy(pair)

    print("\n🎯 Exécution terminée avec succès.")
