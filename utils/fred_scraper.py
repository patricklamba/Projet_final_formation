# Nouveau fichier: fred_scraper.py
import pandas as pd
import requests

class FREDScraper:
    """
    Scraper pour FRED - Données économiques très fiables
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    def __init__(self, api_key="your_key_here"):
        self.api_key = api_key
    
    def fetch_economic_data(self, series_id: str) -> pd.DataFrame:
        """
        Récupère les données économiques FRED
        Series IDs populaires:
        - DEXUSEU: EUR/USD
        - GOLDAMGBD228NLBM: Or
        - SP500: S&P 500
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': '2020-01-01'
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()
            
            if 'observations' in data:
                df = pd.DataFrame(data['observations'])
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df.set_index('date', inplace=True)
                df = df.rename(columns={'value': 'close'})
                return df
            else:
                print(f"❌ Données non disponibles: {data}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur FRED: {e}")
            return None