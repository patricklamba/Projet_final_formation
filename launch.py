"""
POINT D'ENTRÉE PRINCIPAL - Framework de Trading Modulaire
"""
import asyncio
import sys
import os

# Ajouter le chemin racine au Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main_async

def launch_application():
    """Lance l'application de trading"""
    print("🚀 LANCEMENT DU FRAMEWORK DE TRADING MODULAIRE")
    print("=" * 60)
    
    try:
        # Lancer l'application asynchrone
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⏹️  Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    launch_application()