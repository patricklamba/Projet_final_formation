from utils.concurrent_executor import ConcurrentExecutor
import asyncio
import time

async def main_async():
    """
    Version asynchrone avec visualisation en temps réel
    """
    print("🤖 ROBOT DE TRADING AVEC CONCURRENCE")
    print("CAPITAL: 100,000€ | RISK: 1% par trade | R/R: 1.5")
    print("=" * 70)
    
    symbols = ["XAUUSD", "EURUSD"]
    
    # Exécution concurrente
    executor = ConcurrentExecutor(data_dir="data")
    start_time = time.time()
    
    results = await executor.run_multiple_strategies_async(symbols)
    
    end_time = time.time()
    print(f"\n⏱️  Temps total d'exécution: {end_time - start_time:.2f} secondes")
    
    # Affichage du résumé final
    print("\n📈 RÉSUMÉ FINAL DES PERFORMANCES:")
    print("=" * 50)
    
    total_profit = 0
    for result in results:
        if isinstance(result, dict) and 'money_management' in result:
            mm = result['money_management']
            symbol = result.get('symbol', 'Unknown')
            print(f"💰 {symbol}: {mm['net_profit']:+,.2f}€ ({mm['return_percent']:+.2f}%)")
            total_profit += mm['net_profit']
    
    print(f"\n🎯 PROFIT TOTAL: {total_profit:+,.2f}€")

def main_threaded():
    """
    Version threadée pour comparaison
    """
    print("🧵 VERSION THREADÉE")
    symbols = ["XAUUSD", "EURUSD"]
    
    executor = ConcurrentExecutor(data_dir="data")
    start_time = time.time()
    
    results = executor.run_multiple_strategies_threaded(symbols)
    
    end_time = time.time()
    print(f"⏱️  Temps threadé: {end_time - start_time:.2f} secondes")
    
    return results

if __name__ == "__main__":
    # Décommenter la version que vous voulez tester
    
    # Version asynchrone (recommandée)
    asyncio.run(main_async())
    
    # Version threadée
    # main_threaded()