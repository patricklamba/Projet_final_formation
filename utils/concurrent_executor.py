import asyncio
import concurrent.futures
import threading
import time
from typing import List, Dict, Any
from datetime import datetime
import os
from core.strategy import BBKeltnerStrategy
from utils.file_manager import FileManager

class ConcurrentExecutor:
    """
    Exécuteur concurrentiel avec démo visuelle des trades
    """
    
    def __init__(self, data_dir="data", demo_mode: bool = True, max_demo_trades: int = 5):
        self.data_dir = data_dir
        self.file_activity = {}
        self.lock = threading.Lock()
        self.demo_mode = demo_mode  # Mode démo activé
        self.max_demo_trades = max_demo_trades  # Nombre de trades à afficher
    
    def _log_file_activity(self, symbol: str, action: str, details: str = ""):
        """Journalise l'activité des fichiers en temps réel"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with self.lock:
            self.file_activity[symbol] = {
                'timestamp': timestamp,
                'action': action,
                'details': details
            }
            self._display_activity()

    def _display_activity(self):
        """Affiche l'activité en temps réel dans la console"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 ACTIVITÉ DES FICHIERS EN TEMPS RÉEL - MODE DÉMO")
        print("=" * 60)
        
        for symbol, activity in self.file_activity.items():
            status_color = "🟢" if "terminé" in activity['action'].lower() else "🟡"
            print(f"{status_color} {symbol}: {activity['action']}")
            print(f"   ⏰ {activity['timestamp']} | {activity['details']}")
        print("-" * 60)

    async def _display_trade_demo(self, symbol: str, trades: List[Dict], total_trades: int):
        """
        Affiche une démo visuelle des premiers trades
        """
        if not self.demo_mode or not trades:
            return
            
        print(f"\n🎯 DÉMO DES TRADES - {symbol}")
        print("=" * 50)
        print(f"📊 Total des trades générés: {total_trades}")
        print(f"🎭 Affichage des {min(self.max_demo_trades, len(trades))} premiers trades...")
        print("-" * 50)
        
        # Afficher les premiers trades un par un
        demo_trades = trades[:self.max_demo_trades]
        
        for i, trade in enumerate(demo_trades, 1):
            print(f"\n🔍 TRADE #{i}:")
            print(f"   📅 Date: {trade['entry_time']}")
            print(f"   🧭 Direction: {trade['direction']}")
            print(f"   💰 Prix entrée: {trade['entry_price']:.4f}")
            print(f"   🛑 Stop Loss: {trade['stop_loss']:.4f}")
            print(f"   🎯 Take Profit: {trade['take_profit']:.4f}")
            print(f"   📊 Lots: {trade['lots']}")
            print(f"   ⚠️  Risk: {trade['risk_amount']:.2f}€")
            print(f"   📈 Phase: {trade['phase']}")
            
            # Simulation d'attente pour l'effet démo
            await asyncio.sleep(1.5)  # Augmente le temps pour mieux voir
        
        if len(trades) > self.max_demo_trades:
            remaining = len(trades) - self.max_demo_trades
            print(f"\n⏩ ... et {remaining} autres trades exécutés automatiquement")
            print("🎬 Passage à l'exécution complète...")
            await asyncio.sleep(2)

    async def run_single_strategy_async(self, symbol: str) -> Dict[str, Any]:
        """
        Exécute une stratégie avec mode démo des trades
        """
        try:
            # 1️⃣ Ouverture du fichier
            self._log_file_activity(symbol, "Début ouverture fichier", f"Recherche {symbol}.csv")
            
            fm = FileManager(data_dir=self.data_dir)
            df = fm.load_csv(symbol)
            
            self._log_file_activity(symbol, "Fichier ouvert avec succès", f"{len(df)} lignes chargées")
            await asyncio.sleep(0.5)

            # 2️⃣ Calcul des indicateurs
            self._log_file_activity(symbol, "Calcul des indicateurs", "Bollinger Bands + Keltner Channel")
            
            strategy = BBKeltnerStrategy()
            df_signals = strategy.generate_trading_signals(df)
            
            self._log_file_activity(symbol, "Indicateurs calculés", f"{len(df_signals)} signaux générés")
            await asyncio.sleep(0.5)

            # 3️⃣ Exécution des trades
            self._log_file_activity(symbol, "Exécution des trades", "Money management en cours...")
            
            closed_trades = strategy.execute_trading_strategy(df_signals)
            
            # 4️⃣ AFFICHAGE DÉMO DES TRADES
            if closed_trades:
                await self._display_trade_demo(symbol, closed_trades, len(closed_trades))
            
            self._log_file_activity(symbol, "Trades exécutés", f"{len(closed_trades)} trades fermés")
            await asyncio.sleep(0.5)

            # 5️⃣ Génération du rapport
            self._log_file_activity(symbol, "Génération rapport", "Money management...")
            
            mm_report = strategy.generate_money_management_report(symbol)
            mm_report['symbol'] = symbol  # Ajout du symbole pour l'affichage
            
            # 6️⃣ Sauvegarde des résultats
            output_path = f"{self.data_dir}/results_{symbol}.csv"
            df_signals.to_csv(output_path)
            
            report_path = f"{self.data_dir}/mm_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(mm_report, f, indent=2, default=str)

            self._log_file_activity(symbol, "✅ Analyse terminée", 
                                  f"Profit: {mm_report['money_management']['net_profit']:+.2f}€ | "
                                  f"Trades: {len(closed_trades)} | "
                                  f"Win Rate: {mm_report['performance']['win_rate']}%")

            return mm_report

        except Exception as e:
            self._log_file_activity(symbol, "❌ Erreur", str(e))
            return {"error": str(e), "symbol": symbol}

    async def run_multiple_strategies_async(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Exécute plusieurs stratégies en parallèle avec démo
        """
        print("🚀 LANCEMENT CONCURRENT DES STRATÉGIES - MODE DÉMO")
        print(f"📊 Symboles: {', '.join(symbols)}")
        print(f"🎭 DÉMO: {self.max_demo_trades} premiers trades affichés par devise")
        print("=" * 60)
        
        # Initialisation du suivi
        for symbol in symbols:
            self._log_file_activity(symbol, "⏳ En attente...", "Prêt à démarrer")
        
        await asyncio.sleep(2)  # Pause pour voir l'état initial
        
        # Exécution concurrente
        tasks = [self.run_single_strategy_async(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        print("\n" + "=" * 60)
        print("✅ TOUTES LES STRATÉGIES TERMINÉES")
        
        return results

    def run_multiple_strategies_threaded(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Version threadée pour comparaison
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self._run_single_strategy_threaded, symbol): symbol for symbol in symbols}
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e), "symbol": symbol})
            
            return results

    def _run_single_strategy_threaded(self, symbol: str) -> Dict[str, Any]:
        """
        Version adaptée pour le threading
        """
        return asyncio.run(self.run_single_strategy_async(symbol))