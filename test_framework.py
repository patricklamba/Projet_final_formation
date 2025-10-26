# debug_pnl.py
from core.strategy import MultiSignalStrategy
import pandas as pd

# Charger vos données
df = pd.read_csv('resultat_3_1.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)

# Lancer avec debug
strategy = MultiSignalStrategy(initial_capital=100000)
trades = strategy.execute_strategy(df, "XAUUSD")

print("=== RAPPORT FINAL DEBUG ===")
print(f"Capital final: {strategy.money_management.current_capital:.2f}€")
print(f"Trades fermés: {len(strategy.closed_trades)}")