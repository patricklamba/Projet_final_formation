"""
SCRIPT DE LANCEMENT SIMPLIFIÉ
"""
import asyncio
import argparse
from main import main_async, main_simple
try:
    from stock_indicators import indicators
    print("✅ StockIndicators importé avec succès")
except ImportError as e:
    print("❌ StockIndicators non installé")
    print("💡 Installation: pip install stock-indicators")
    sys.exit(1)

def run_strategy(demo_mode=False, symbols=None):
    """Lance la stratégie avec les paramètres donnés"""
    
    if symbols is None:
        symbols = ["XAUUSD", "EURUSD"]
    
    print(f"🎯 Stratégie lancée sur: {', '.join(symbols)}")
    print(f"🎭 Mode démo: {'ACTIVÉ' if demo_mode else 'DÉSACTIVÉ'}")
    
    # Vous pouvez choisir la version asynchrone ou simple
    if demo_mode:
        return main_simple()
    else:
        return asyncio.run(main_async())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Framework de Trading Modulaire")
    parser.add_argument('--demo', action='store_true', help='Mode démo')
    parser.add_argument('--symbols', nargs='+', help='Symboles à trader')
    
    args = parser.parse_args()
    
    run_strategy(demo_mode=args.demo, symbols=args.symbols)