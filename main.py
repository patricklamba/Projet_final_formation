"""
Point d'entrée principal du framework de trading
"""
import asyncio
import time
from core.strategy import MultiSignalStrategy
from execution.concurrent_executor import ConcurrentExecutor

async def main_async():
    """
    Version asynchrone avec exécution concurrente
    """
    print("🤖 FRAMEWORK DE TRADING MODULAIRE - CONVERGENCE DE SIGNAL")
    print("=" * 60)
    
    symbols = ["XAUUSD", "EURUSD"]
    
    # Exécution concurrente avec le nouveau framework
    executor = ConcurrentExecutor(
        data_dir="data", 
        demo_mode=False,
    )
    
    start_time = time.time()
    results = await executor.run_multiple_strategies_async(symbols)
    end_time = time.time()
    
    # Affichage du résumé
    print("\n" + "=" * 60)
    print("📊 RAPPORT FINAL - FRAMEWORK MODULAIRE")
    print("=" * 60)
    
    # Votre code d'affichage des résultats...
    
    print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")

if __name__ == "__main__":
    asyncio.run(main_async())