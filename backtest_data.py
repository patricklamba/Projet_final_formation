import yfinance as yf
import os

# Dossier data
os.makedirs("data", exist_ok=True)

symbols = ['XAUUSD=X', 'EURUSD=X']
for sym in symbols:
    # Télécharger les données
    data = yf.download(sym, start='2023-01-01', end='2025-01-01', interval='15m')

    # Nettoyer le DataFrame
    data = data.reset_index()  # datetime en colonne
    data.rename(columns={
        'Date': 'datetime',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Adj Close': 'adj_close',
        'Volume': 'volume'
    }, inplace=True)

    # Garder uniquement les colonnes utiles
    data = data[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    # Convertir en float si nécessaire
    data[['open', 'high', 'low', 'close', 'volume']] = data[['open', 'high', 'low', 'close', 'volume']].astype(float)

    # Sauvegarder CSV
    filename = f"data/{sym.replace('=X','')}.csv"
    data.to_csv(filename, index=False)
    print(f"✅ Données enregistrées pour {sym} → {filename}")
