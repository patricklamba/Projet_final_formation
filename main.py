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
