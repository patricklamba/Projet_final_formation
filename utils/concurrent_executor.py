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
    Exécuteur concurrentiel avec visualisation en temps réel
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.file_activity = {}  # Suivi de l'activité des fichiers
        self.lock = threading.Lock()  # Pour la synchronisation
        
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
        print("🔄 ACTIVITÉ DES FICHIERS EN TEMPS RÉEL")
        print("=" * 60)
        
        for symbol, activity in self.file_activity.items():
            status_color = "🟢" if "terminé" in activity['action'].lower() else "🟡"
            print(f"{status_color} {symbol}: {activity['action']}")
            print(f"   ⏰ {activity['timestamp']} | {activity['details']}")
        print("-" * 60)

    async def run_single_strategy_async(self, symbol: str) -> Dict[str, Any]:
        """
        Exécute une stratégie pour un symbol avec suivi visuel
        """
        try:
            # 1️⃣ Ouverture du fichier
            self._log_file_activity(symbol, "Début ouverture fichier", f"Recherche {symbol}.csv")
            
            fm = FileManager(data_dir=self.data_dir)
            df = fm.load_csv(symbol)
            
            self._log_file_activity(symbol, "Fichier ouvert avec succès", f"{len(df)} lignes chargées")
            await asyncio.sleep(0.5)  # Pause pour visualisation

            # 2️⃣ Calcul des indicateurs
            self._log_file_activity(symbol, "Calcul des indicateurs", "Bollinger Bands + Keltner Channel")
            
            strategy = BBKeltnerStrategy()
            df_signals = strategy.generate_trading_signals(df)
            
            self._log_file_activity(symbol, "Indicateurs calculés", f"{len(df_signals)} signaux générés")
            await asyncio.sleep(0.5)

            # 3️⃣ Exécution des trades
            self._log_file_activity(symbol, "Exécution des trades", "Money management en cours...")
            
            closed_trades = strategy.execute_trading_strategy(df_signals)
            
            self._log_file_activity(symbol, "Trades exécutés", f"{len(closed_trades)} trades fermés")
            await asyncio.sleep(0.5)

            # 4️⃣ Génération du rapport
            self._log_file_activity(symbol, "Génération rapport", "Money management...")
            
            mm_report = strategy.generate_money_management_report(symbol)
            
            # 5️⃣ Sauvegarde des résultats
            output_path = f"{self.data_dir}/results_{symbol}.csv"
            df_signals.to_csv(output_path)
            
            report_path = f"{self.data_dir}/mm_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(mm_report, f, indent=2, default=str)

            self._log_file_activity(symbol, "✅ Analyse terminée", 
                                  f"Profit: {mm_report['money_management']['net_profit']:+.2f}€ | "
                                  f"Fichiers: {os.path.basename(output_path)}, {os.path.basename(report_path)}")

            return mm_report

        except Exception as e:
            self._log_file_activity(symbol, "❌ Erreur", str(e))
            return {"error": str(e), "symbol": symbol}

    async def run_multiple_strategies_async(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Exécute plusieurs stratégies en parallèle avec visualisation
        """
        print("🚀 LANCEMENT CONCURRENT DES STRATÉGIES")
        print(f"📊 Symboles: {', '.join(symbols)}")
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
        # Pour le threading, on utilise asyncio dans un thread séparé
        return asyncio.run(self.run_single_strategy_async(symbol))