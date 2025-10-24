# Nouveau fichier: investing_scraper.py
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import random

class InvestingScraper:
    """
    Scraper pour Investing.com - Données Forex et Commodities
    """
    
    BASE_URLS = {
        'XAUUSD': 'https://fr.investing.com/currencies/xau-usd-historical-data',
        'EURUSD': 'https://fr.investing.com/currencies/eur-usd-historical-data',
        'AAPL': 'https://fr.investing.com/equities/apple-computer-inc-historical-data'
    }
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_data(self, symbol: str) -> pd.DataFrame:
        """
        Récupère les données historiques depuis Investing.com
        """
        if symbol not in self.BASE_URLS:
            print(f"❌ Symbole non supporté: {symbol}")
            return None
            
        try:
            url = self.BASE_URLS[symbol]
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver le tableau des données historiques
            table = soup.find('table', {'class': 'common-table medium js-table'})
            
            if not table:
                print("❌ Tableau non trouvé")
                return None
            
            # Extraire les données
            data = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    date = cols[0].get_text(strip=True)
                    price = cols[1].get_text(strip=True)
                    high = cols[2].get_text(strip=True)
                    low = cols[3].get_text(strip=True)
                    close = cols[4].get_text(strip=True)
                    
                    data.append({
                        'date': date,
                        'price': price,
                        'high': high,
                        'low': low,
                        'close': close
                    })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')
                df.set_index('date', inplace=True)
                
                # Convertir les prix en float
                for col in ['price', 'high', 'low', 'close']:
                    df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur scraping Investing.com: {e}")
            return None
        
        finally:
            # Respectful scraping - pause aléatoire
            time.sleep(random.uniform(1, 3))