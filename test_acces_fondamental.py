# test_acces_fondamental.py
import requests
from bs4 import BeautifulSoup
import time

def test_acces_sites():
    """Test minimal d'accès aux sites de fondamentaux"""
    
    sites = {
        "Investing.com Économie": "https://fr.investing.com/economic-calendar/",
        "FXStreet Actualités": "https://www.fxstreet.fr/actualites",
        "DailyFX Calendrier": "https://www.dailyfx.com/economic-calendar",
        "ForexFactory": "https://www.forexfactory.com/calendar",
        "Bloomberg Markets": "https://www.bloomberg.com/markets",
        "Reuters Business": "https://www.reuters.com/business/"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("🔍 TEST D'ACCÈS AUX SITES FONDAMENTAUX")
    print("=" * 60)
    
    for nom_site, url in sites.items():
        try:
            print(f"\n🌐 Test: {nom_site}")
            print(f"   📡 URL: {url}")
            
            # Test de connexion
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"   📊 Statut: {response.status_code}")
            
            if response.status_code == 200:
                # Test du parsing
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                print(f"   ✅ ACCÈS RÉUSSI - Titre: {title.get_text() if title else 'Non trouvé'}")
                
                # Chercher des éléments de contenu
                articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['news', 'article', 'event', 'calendar']))
                print(f"   📰 Éléments trouvés: {len(articles)}")
                
            elif response.status_code == 403:
                print("   ❌ ACCÈS BLOQUÉ (403 Forbidden)")
            elif response.status_code == 404:
                print("   ❌ PAGE NON TROUVÉE (404)")
            else:
                print(f"   ⚠️  Statut anormal: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ❌ TIMEOUT - Site trop lent")
        except requests.exceptions.ConnectionError:
            print("   ❌ ERREUR CONNEXION")
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
        
        # Pause entre les tests
        time.sleep(2)

def test_calendrier_economique():
    """Test spécifique des calendriers économiques"""
    print("\n📅 TEST CALENDRIERS ÉCONOMIQUES")
    print("=" * 50)
    
    calendriers = {
        "Investing.com Calendar": "https://fr.investing.com/economic-calendar/",
        "ForexFactory Calendar": "https://www.forexfactory.com/calendar",
        "DailyFX Calendar": "https://www.dailyfx.com/economic-calendar"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for nom, url in calendriers.items():
        try:
            print(f"\n📊 Test: {nom}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher des événements économiques
                events = soup.find_all(['tr', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['event', 'calendar', 'row']))
                
                print(f"   ✅ Connecté - Événements potentiels: {len(events)}")
                
                # Afficher quelques événements trouvés
                event_count = 0
                for event in events[:3]:  # Juste les 3 premiers
                    text = event.get_text(strip=True)
                    if text and len(text) > 20:
                        print(f"   📍 {text[:80]}...")
                        event_count += 1
                
                if event_count == 0:
                    print("   ℹ️  Aucun événement trouvé (peut nécessiter sélecteurs spécifiques)")
                    
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    print("🎯 TEST MINIMAL D'ACCÈS - ANALYSE FONDAMENTALE")
    print("Objectif: Vérifier quels sites sont accessibles pour le scraping")
    print("=" * 70)
    
    # Test général des sites
    test_acces_sites()
    
    # Test spécifique calendriers
    test_calendrier_economique()
    
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DES TESTS")
    print("✅ Sites en vert: Bon pour le scraping")
    print("❌ Sites en rouge: Problèmes d'accès")
    print("⚠️  Sites nécessitent peut-être des sélecteurs spécifiques")