# main_claude_final.py
from core.strategy import BBKeltnerStrategy
from utils.file_manager import FileManager
from utils.claude_analyzer import ClaudeAnalyzer
from utils.fundamental_scraper_improved import FundamentalScraperImproved
import pandas as pd

def demo_claude_final():
    """
    DÉMO FINALE avec données fondamentales améliorées
    """
    print("🎯 DÉMO CLAUDE AI - VERSION FINALE")
    print("=" * 50)
    
    # 1. Charger les données
    fm = FileManager(data_dir="data")
    df = fm.load_csv("XAUUSD")
    print(f"✅ Données chargées: {len(df)} bougies")
    
    # 2. Générer un signal
    strategy = BBKeltnerStrategy()
    df_signals = strategy.generate_trading_signals(df)
    
    # 3. Trouver le premier signal
    signal_row = None
    signal_index = None
    for index, row in df_signals.iterrows():
        if row["signal"] in [1, -1] and row["in_killzone"]:
            signal_row = row
            signal_index = index
            break
    
    if signal_row is None:
        print("❌ Aucun signal trouvé dans la killzone")
        return
    
    # 4. Préparer le trade
    trade_data = {
        "symbol": "XAUUSD",
        "direction": "LONG" if signal_row["signal"] == 1 else "SHORT",
        "entry_price": round(signal_row["close"], 2),
        "stop_loss": round(signal_row["bb_middle"], 2),
        "take_profit": round(signal_row["close"] + (signal_row["close"] - signal_row["bb_middle"]) * 1.5, 2),
        "risk_amount": 100,
        "entry_time": signal_index.isoformat(),
        "phase": signal_row["phase"]
    }
    
    print(f"\n📊 TRADE DÉTECTÉ:")
    print(f"   📍 {trade_data['direction']} {trade_data['symbol']}")
    print(f"   💰 Entrée: {trade_data['entry_price']}")
    print(f"   🛑 Stop Loss: {trade_data['stop_loss']}") 
    print(f"   🎯 Take Profit: {trade_data['take_profit']}")
    print(f"   📈 Phase: {trade_data['phase']}")
    
    # 5. Scraper données fondamentales (version améliorée)
    print("\n📡 COLLECTE DONNÉES FONDAMENTALES...")
    fundamental_scraper = FundamentalScraperImproved()
    
    # Essayer le scraping réel, sinon utiliser données simulées
    real_data = fundamental_scraper.scrape_investing_calendar_improved()
    
    if "error" in real_data or real_data.get("events_count", 0) == 0:
        print("   🔄 Scraping échoué - utilisation données simulées")
        fundamental_data = fundamental_scraper.get_simulated_fundamental_data()
    else:
        print(f"   ✅ {real_data['events_count']} événements trouvés")
        fundamental_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": [real_data]
        }
    
    # 6. Analyse Claude AI
    print("\n🤖 ANALYSE CLAUDE AI...")
    claude = ClaudeAnalyzer()
    
    # Test connexion d'abord
    connection_test = claude.test_connection()
    print(f"   📡 {connection_test['message']}")
    
    if connection_test['status'] == 'error':
        print("❌ Claude AI non disponible")
        return
    
    # Analyse du trade
    analysis = claude.analyze_trade_coherence(trade_data, fundamental_data)
    
    # 7. Affichage des résultats
    print(f"\n🎯 RÉSULTAT CLAUDE AI:")
    print(f"   📊 Cohérence: {analysis['coherence'].upper()}")
    print(f"   💡 Recommandation: {analysis['recommendation'].upper()}")
    print(f"   📝 Raison: {analysis['reason']}")
    print(f"   ⏱️  Temps analyse: {analysis['analysis_time']:.2f}s")
    
    # 8. Décision finale avec code couleur
    print(f"\n🚀 DÉCISION FINALE:")
    
    if analysis['recommendation'] == 'execute':
        print("🟢 EXÉCUTER LE TRADE - Claude AI valide")
        print("   ✅ Le trade est cohérent avec l'analyse fondamentale")
        # Ici tu appelles ta fonction d'exécution réelle
        # execute_trade(trade_data)
        
    elif analysis['recommendation'] == 'avoid':
        print("🔴 NE PAS EXÉCUTER - Claude AI déconseille")
        print("   ❌ Le trade présente des risques élevés")
        
    elif analysis['recommendation'] == 'wait':
        print("🟡 ATTENDRE - Claude AI recommande la prudence")
        print("   ⚠️  Manque de données ou conditions incertaines")
    
    # 9. Suggestions d'amélioration
    print(f"\n💡 SUGGESTIONS POUR AMÉLIORER:")
    if analysis['coherence'] == 'low':
        print("   • Vérifier les stop loss et take profit")
        print("   • Attendre de meilleures conditions marché")
    elif analysis['coherence'] == 'medium': 
        print("   • Chercher plus de données fondamentales")
        print("   • Surveiller les prochains événements économiques")
    else:
        print("   • Trade bien structuré - continuer la stratégie")

if __name__ == "__main__":
    demo_claude_final()