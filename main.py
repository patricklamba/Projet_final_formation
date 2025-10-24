from utils.concurrent_executor import ConcurrentExecutor
import asyncio
import time

async def main_async():
    """
    Version asynchrone avec exécution concurrente
    """
    print("🤖 ROBOT DE TRADING - STRATÉGIE CONVERGENCE BB/KELTNER")
    print("CAPITAL: 100,000€ | RISK: 1% par trade | R/R: 1.5")
    print("=" * 60)
    
    symbols = ["XAUUSD", "EURUSD"]
    
    # Exécution concurrente SANS MODE DÉMO
    executor = ConcurrentExecutor(
        data_dir="data", 
        demo_mode=False  # ← CHANGÉ: désactivé le mode démo
    )
    
    start_time = time.time()
    results = await executor.run_multiple_strategies_async(symbols)
    end_time = time.time()
    
    # Affichage du résumé final CORRIGÉ
    print("\n" + "=" * 60)
    print("📊 RAPPORT FINAL")
    print("=" * 60)
    
    total_profit = 0
    total_trades = 0
    winning_trades = 0
    total_gains = 0
    total_losses = 0

    for result in results:
        if isinstance(result, dict) and 'money_management' in result:
            mm = result['money_management']
            perf = result['performance']
            symbol = result.get('symbol', 'Unknown')
            
            # Calcul des gains et pertes réels
            gains = 0
            losses = 0
            
            # Analyser les trades détaillés pour calculer gains/pertes
            if 'trades_detailed' in result:
                for trade in result['trades_detailed']:
                    pnl = trade.get('pnl', 0)
                    if pnl > 0:
                        gains += pnl
                    else:
                        losses += abs(pnl)  # Les pertes sont négatives, on prend la valeur absolue
            
            print(f"\n💰 {symbol}:")
            print(f"   📈 Profit Net: {mm['net_profit']:+,.2f}€ ({mm['return_percent']:+.2f}%)")
            print(f"   💹 Gains Bruts: {gains:+,.2f}€")
            print(f"   📉 Pertes Brutes: {losses:+,.2f}€")
            print(f"   🎯 Trades: {perf['total_trades']} (✅ {perf['winning_trades']} | ❌ {perf['losing_trades']})")
            print(f"   📊 Win Rate: {perf['win_rate']}%")
            print(f"   ⚠️  Drawdown: {mm['max_drawdown']}%")
            print(f"   📈 Profit Factor: {perf['profit_factor']}")
            
            total_profit += mm['net_profit']
            total_trades += perf['total_trades']
            winning_trades += perf['winning_trades']
            total_gains += gains
            total_losses += losses

    # Résumé global CORRIGÉ
    global_win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    print(f"\n🎯 RÉSUMÉ GLOBAL:")
    print(f"   💰 PROFIT NET TOTAL: {total_profit:+,.2f}€")
    print(f"   💹 GAINS BRUTS TOTAUX: {total_gains:+,.2f}€")
    print(f"   📉 PERTES BRUTES TOTALES: {total_losses:+,.2f}€")
    print(f"   📊 TOTAL TRADES: {total_trades}")
    print(f"   ✅ TRADES GAGNANTS: {winning_trades}")
    print(f"   ❌ TRADES PERDANTS: {total_trades - winning_trades}")
    print(f"   🏆 WIN RATE GLOBAL: {global_win_rate:.1f}%")
    print(f"   ⏱️  TEMPS D'EXÉCUTION: {end_time - start_time:.2f} secondes")

def main_simple():
    """
    Version simple (identique maintenant)
    """
    print("⚡ VERSION RAPIDE")
    symbols = ["XAUUSD", "EURUSD"]
    
    executor = ConcurrentExecutor(data_dir="data", demo_mode=False)
    start_time = time.time()
    
    results = asyncio.run(executor.run_multiple_strategies_async(symbols))
    
    end_time = time.time()
    print(f"⏱️  Temps d'exécution: {end_time - start_time:.2f} secondes")
    
    return results

if __name__ == "__main__":
    # Version principale
    asyncio.run(main_async())