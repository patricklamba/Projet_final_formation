"""
Scraper de Yahoo Finance + parsing regex pour récupérer OHLC
"""

import requests
import pandas as pd
import re
from datetime import datetime

class YahooScraper:
    BASE_URL = "https://finance.yahoo.com/quote/{symbol}/history?p={symbol}"

    @staticmethod
    def fetch_data(symbol: str) -> pd.DataFrame:
        url = YahooScraper.BASE_URL.format(symbol=symbol)
        headers = {"User-Agent": "Mozilla/5.0"}

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise ConnectionError(f"Erreur lors de la connexion à Yahoo Finance : {resp.status_code}")

        html = resp.text

        # Regex pour trouver les lignes de tableau des prix
        pattern = r'(\d{1,2}-\w{3}-\d{4}),(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*),(\d+\.?\d*),.*'
        matches = re.findall(pattern, html)

        if not matches:
            raise ValueError("Impossible de parser les données avec regex.")

        df = pd.DataFrame(matches, columns=['date','open','high','low','close'])
        df['date'] = pd.to_datetime(df['date'])
        df[['open','high','low','close']] = df[['open','high','low','close']].astype(float)
        df.set_index('date', inplace=True)

        return df
