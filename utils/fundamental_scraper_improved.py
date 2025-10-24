# fundamental_scraper_improved.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class FundamentalScraperImproved:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
        })
    
    def scrape_investing_calendar_improved(self):
        """Version améliorée du scraping Investing.com"""
        try:
            url = "https://fr.investing.com/economic-calendar/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"Statut {response.status_code}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            events = []
            
            # Méthode plus robuste pour trouver les événements
            event_rows = soup.find_all('tr', class_=lambda x: x and 'event' in x)
            
            for row in event_rows[:10]:  # Prendre plus d'événements
                try:
                    # Extraire les données de différentes manières
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        # Heure
                        time_cell = cells[0]
                        event_time = time_cell.get_text(strip=True)
                        
                        # Devise
                        currency_cell = cells[1]
                        currency = currency_cell.get_text(strip=True)
                        
                        # Événement
                        event_cell = cells[2] 
                        event_name = event_cell.get_text(strip=True)
                        
                        # Impact (chercher l'icône d'impact)
                        impact = "Medium"
                        if row.find('i', class_=lambda x: x and 'red' in str(x)):
                            impact = "High"
                        elif row.find('i', class_=lambda x: x and 'orange' in str(x)):
                            impact = "Medium"
                        elif row.find('i', class_=lambda x: x and 'yellow' in str(x)):
                            impact = "Low"
                        
                        # Valeurs
                        actual = cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"
                        forecast = cells[4].get_text(strip=True) if len(cells) > 4 else "N/A"
                        previous = cells[5].get_text(strip=True) if len(cells) > 5 else "N/A"
                        
                        event_data = {
                            "time": event_time,
                            "currency": currency,
                            "event": event_name,
                            "impact": impact,
                            "actual": actual,
                            "forecast": forecast,
                            "previous": previous
                        }
                        
                        # Prendre même les événements medium impact pour avoir plus de données
                        if event_name and len(event_name) > 5:
                            events.append(event_data)
                            
                except Exception as e:
                    continue
            
            return {
                "source": "Investing.com Economic Calendar",
                "timestamp": datetime.now().isoformat(),
                "events_count": len(events),
                "events": events[:8]  # Limiter à 8 événements max
            }
            
        except Exception as e:
            return {"error": f"Erreur scraping: {e}"}
    
    def get_simulated_fundamental_data(self):
        """Données simulées réalistes quand le scraping échoue"""
        print("🔄 Utilisation de données fondamentales simulées...")
        
        # Événements économiques réalistes
        simulated_events = [
            {
                "time": "14:30",
                "currency": "USD", 
                "event": "CPI Inflation MoM",
                "impact": "High",
                "actual": "0.4%",
                "forecast": "0.3%",
                "previous": "0.2%"
            },
            {
                "time": "10:00", 
                "currency": "EUR",
                "event": "GDP Growth Rate Q3",
                "impact": "High", 
                "actual": "0.3%",
                "forecast": "0.2%",
                "previous": "0.1%"
            },
            {
                "time": "13:15",
                "currency": "EUR",
                "event": "ECB Interest Rate Decision", 
                "impact": "High",
                "actual": "4.50%",
                "forecast": "4.50%", 
                "previous": "4.50%"
            }
        ]
        
        # Sentiment marché réaliste
        sentiment_data = {
            "source": "Market Analysis",
            "timestamp": datetime.now().isoformat(),
            "sentiment_analysis": {
                "EURUSD": {
                    "bullish": 58,
                    "bearish": 42,
                    "trend": "Slightly Bullish",
                    "key_levels": {"support": 1.0650, "resistance": 1.0850}
                },
                "XAUUSD": {
                    "bullish": 72,
                    "bearish": 28, 
                    "trend": "Bullish",
                    "key_levels": {"support": 1950, "resistance": 2050}
                }
            },
            "market_conditions": {
                "volatility": "Medium",
                "risk_sentiment": "Risk-On", 
                "dominant_theme": "Central Bank Policies"
            }
        }
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": [
                {
                    "source": "Investing.com (Simulated)",
                    "events_count": len(simulated_events),
                    "events": simulated_events
                },
                sentiment_data
            ]
        }