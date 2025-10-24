from core.strategy import BBKeltnerStrategy
from utils.file_manager import FileManager
import json
from datetime import datetime

def run_strategy(symbol: str):
    print(f"\n🎯 EXECUTION STRATEGIE TRADING pour {symbol}")
    print("=" * 50)

    # 1️⃣ Charger les données
    fm = FileManager(data_dir="data")
    try:
        df = fm.load_csv(symbol)
        print(f"✅ Données chargées : {len(df)} bougies")
    except Exception as e:
        print(f"❌ Erreur chargement données : {e}")
        return

    # 2️⃣ Créer et exécuter la stratégie
    strategy = BBKeltnerStrategy(
        killzone_start="03:00", 
        killzone_end="06:30",
        risk_reward_ratio=1.5
    )
    
    # 3️⃣ Générer les signaux
    df_signals = strategy.generate_trading_signals(df)
    
    # 4️⃣ Analyser les trades
    print(f"\n📊 ANALYSE DES TRADES pour {symbol}:")
    print("-" * 40)
    
    trading_report = strategy.generate_trading_report(df_signals, symbol)
    
    # 5️⃣ Affichage du rapport
    print(f"\n📈 RAPPORT DE PERFORMANCE {symbol}:")
    print("-" * 40)
    
    perf = trading_report["performance"]
    print(f"Nombre total de trades : {perf['total_trades']}")
    print(f"Trades gagnants : {perf['winning_trades']}")
    print(f"Trades perdants : {perf['losing_trades']}")
    print(f"Win Rate : {perf['win_rate']}%")
    print(f"Ratio Risk/Reward moyen : {perf['avg_risk_reward']}")
    
    phases = trading_report["analyse_phases"]
    print(f"Trades en contraction : {phases['trades_contraction']}")
    print(f"Trades en expansion : {phases['trades_expansion']}")
    
    # 6️⃣ Détail des trades
    if trading_report.get("trades_detailed"):
        print(f"\n🎯 TRADES DETAILLES:")
        print("-" * 40)
        for i, trade in enumerate(trading_report["trades_detailed"], 1):
            print(f"Trade #{i}:")
            print(f"  Direction: {trade['direction']}")
            print(f"  Date: {trade['entry_time']}")
            print(f"  Prix entrée: {trade['entry_price']:.2f}")
            print(f"  Stop Loss: {trade['stop_loss']:.2f}")
            print(f"  Take Profit: {trade['take_profit']:.2f}")
            print(f"  R/R: {trade['rr_ratio']}")
            print(f"  Phase: {trade['phase']}")
            print()

    # 7️⃣ Sauvegarde des résultats
    output_path = f"data/results_{symbol}.csv"
    df_signals.to_csv(output_path)
    
    # Sauvegarde du rapport trading
    report_path = f"data/trading_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(trading_report, f, indent=2, default=str)
    
    print(f"💾 Résultats enregistrés dans {output_path}")
    print(f"📊 Rapport trading enregistré dans {report_path}")

if __name__ == "__main__":
    print("🤖 ROBOT DE TRADING BB/KELTNER")
    print("STRATEGIE: Breakout Bollinger + Killzone 03h00-06h30")
    print("=" * 60)
    
    for pair in ["XAUUSD", "EURUSD"]:
        run_strategy(pair)

    print("\n✅ EXECUTION TERMINEE - Rapports générés dans dossier /data")