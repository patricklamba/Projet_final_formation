"""
Test complet du système de scraping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.scraper import YahooScraper
from utils.fundamental_scraper import FundamentalScraper
import pandas as pd
from datetime import datetime

def test_yahoo_scraper():
    """Test du scraper Yahoo Finance"""
    print("🔍 TEST DU SCRAPER YAHOO FINANCE")
    print("=" * 50)
    
    scraper = YahooScraper()
    test_symbols = ["AAPL", "MSFT", "XAUUSD", "EURUSD"]
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 Tentative de scraping pour {symbol}...")
            df = scraper.fetch_data(symbol)
            
            if df is not None and not df.empty:
                print(f"✅ SUCCÈS pour {symbol}")
                print(f"   📈 Données récupérées: {len(df)} lignes")
                print(f"   📅 Période: {df.index[0]} to {df.index[-1]}")
                print(f"   🏷️  Colonnes: {list(df.columns)}")
                print(f"   📊 Exemple de données:")
                print(df.head(3).to_string())
            else:
                print(f"❌ Aucune donnée pour {symbol}")
                
        except Exception as e:
            print(f"❌ ERREUR pour {symbol}: {e}")

def test_fundamental_scraper():
    """Test du scraper de données fondamentales"""
    print("\n🔍 TEST DU SCRAPER FONDAMENTAL")
    print("=" * 50)
    
    scraper = FundamentalScraper()
    
    try:
        print("📰 Récupération des nouvelles économiques...")
        news = scraper.fetch_news()
        
        if news:
            print("✅ Données fondamentales récupérées:")
            print(news[:500] + "..." if len(news) > 500 else news)
        else:
            print("❌ Aucune donnée fondamentale récupérée")
            
    except Exception as e:
        print(f"❌ Erreur scraping fondamental: {e}")

def test_integration_complete():
    """Test d'intégration complet"""
    print("\n🎯 TEST D'INTÉGRATION COMPLET")
    print("=" * 50)
    
    # Test avec un symbole connu
    symbol = "AAPL"
    
    try:
        # Scraping des données
        yahoo_scraper = YahooScraper()
        fundamental_scraper = FundamentalScraper()
        
        print(f"🔄 Scraping des données pour {symbol}...")
        price_data = yahoo_scraper.fetch_data(symbol)
        news_data = fundamental_scraper.fetch_news()
        
        if price_data is not None and not price_data.empty:
            print(f"✅ Prix scrapés: {len(price_data)} bougies")
            
            # Sauvegarde des données scrapées
            scraped_file = f"data/scraped_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            price_data.to_csv(scraped_file)
            print(f"💾 Données sauvegardées: {scraped_file}")
            
            # Affichage d'un échantillon
            print("\n📊 ÉCHANTILLON DES DONNÉES:")
            print(price_data.head().to_string())
            
        else:
            print("❌ Échec du scraping des prix")
            
        if news_data:
            print(f"\n📰 DONNÉES FONDAMENTALES:")
            print(news_data[:300] + "..." if len(news_data) > 300 else news_data)
            
            # Sauvegarde des nouvelles
            news_file = f"data/news_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(news_file, 'w', encoding='utf-8') as f:
                f.write(news_data)
            print(f"💾 Nouvelles sauvegardées: {news_file}")
        else:
            print("❌ Aucune donnée fondamentale")
            
    except Exception as e:
        print(f"❌ Erreur d'intégration: {e}")

if __name__ == "__main__":
    print("🧪 SUITE DE TESTS COMPLÈTE DU SCRAPING")
    print("=" * 60)
    
    # Test Yahoo Scraper
    test_yahoo_scraper()
    
    # Test Fundamental Scraper  
    test_fundamental_scraper()
    
    # Test d'intégration
    test_integration_complete()
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS TERMINÉS")