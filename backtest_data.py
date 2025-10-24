import yfinance as yf

symbols = ['XAUUSD=X', 'EURUSD=X']
for sym in symbols:
    data = yf.download(sym, start='2023-01-01', end='2025-01-01', interval='15m')
    data.to_csv(f"data/{sym.replace('=X','')}.csv")
    print(f"✅ Données enregistrées pour {sym}")
