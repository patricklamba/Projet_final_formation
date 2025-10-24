from utils.concurrent_executor import ConcurrentExecutor
import asyncio
import time

async def main_async():
    """
    Version asynchrone avec DÉMO VISUELLE des trades
    """
    print("🤖 ROBOT DE TRADING - MODE DÉMONSTRATION")
    print("CAPITAL: 100,000€ | RISK: 1% par trade | R/R: 1.5")
    print("🎭 5 premiers trades affichés en détail par devise")
    print("=" * 70)
    
    symbols = ["XAUUSD", "EURUSD"]
    
    # Exécution concurrente AVEC MODE DÉMO
    executor = ConcurrentExecutor(
        data_dir="data", 
        demo_mode=True, 
        max_demo_trades=5  # Affiche 5 trades par devise
    )
    
    start_time = time.time()
    results = await executor.run_multiple_strategies_async(symbols)
    end_time = time.time()
    
    # Affichage du résumé final détaillé
    print("\n" + "=" * 70)
    print("📊 RAPPORT FINAL DÉTAILLÉ")
    print("=" * 70)
    
    total_profit = 0
    total_trades = 0
    winning_trades = 0
    
    for result in results:
        if isinstance(result, dict) and 'money_management' in result:
            mm = result['money_management']
            perf = result['performance']
            symbol = result.get('symbol', 'Unknown')
            
            print(f"\n💰 {symbol}:")
            print(f"   📈 Profit: {mm['net_profit']:+,.2f}€ ({mm['return_percent']:+.2f}%)")
            print(f"   🎯 Trades: {perf['total_trades']} (Gagnants: {perf['winning_trades']} | Perdants: {perf['losing_trades']})")
            print(f"   📊 Win Rate: {perf['win_rate']}%")
            print(f"   ⚠️  Drawdown: {mm['max_drawdown']}%")
            print(f"   📈 Profit Factor: {perf['profit_factor']}")
            
            total_profit += mm['net_profit']
            total_trades += perf['total_trades']
            winning_trades += perf['winning_trades']
    
    # Résumé global
    global_win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print(f"\n🎯 RÉSUMÉ GLOBAL:")
    print(f"   💰 PROFIT TOTAL: {total_profit:+,.2f}€")
    print(f"   📊 TOTAL TRADES: {total_trades}")
    print(f"   🏆 WIN RATE GLOBAL: {global_win_rate:.1f}%")
    print(f"   ⏱️  TEMPS D'EXÉCUTION: {end_time - start_time:.2f} secondes")
    
    print(f"\n💾 FICHIERS GÉNÉRÉS:")
    print(f"   📄 Résultats: data/results_*.csv")
    print(f"   📊 Rapports: data/mm_report_*.json")

def main_simple():
    """
    Version simple sans démo (pour comparaison)
    """
    print("⚡ VERSION RAPIDE SANS DÉMO")
    symbols = ["XAUUSD", "EURUSD"]
    
    executor = ConcurrentExecutor(data_dir="data", demo_mode=False)
    start_time = time.time()
    
    results = asyncio.run(executor.run_multiple_strategies_async(symbols))
    
    end_time = time.time()
    print(f"⏱️  Temps sans démo: {end_time - start_time:.2f} secondes")
    
    return results

if __name__ == "__main__":
    # Version avec DÉMO (recommandée pour la présentation)
    asyncio.run(main_async())
    
    # Décommente pour tester la version rapide
    # main_simple()