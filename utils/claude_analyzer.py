"""
Module Claude AI pour analyser la cohérence des trades
avec les données fondamentales
"""

import anthropic
import json
import time
from datetime import datetime

class ClaudeAnalyzer:
    def __init__(self, api_key: str = "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"):
        self.api_key = api_key
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Initialise le client Claude avec gestion d'erreur"""
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            print("✅ Client Claude AI initialisé")
        except Exception as e:
            print(f"❌ Erreur initialisation Claude: {e}")
            self.client = None
    
    def test_connection(self):
        """Test la connexion à l'API Claude"""
        if not self.client:
            return {"status": "error", "message": "Client non initialisé"}
        
        try:
            start_time = time.time()
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[{
                    "role": "user", 
                    "content": "Réponds simplement 'OK' pour tester la connexion."
                }]
            )
            
            latency = time.time() - start_time
            
            return {
                "status": "success",
                "message": f"Connexion Claude OK - Latence: {latency:.2f}s",
                "response": response.content[0].text,
                "latency": latency
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Erreur connexion: {e}"}
    
    def analyze_trade_coherence(self, trade_data: dict, fundamental_data: dict) -> dict:
        """
        Analyse la cohérence d'un trade avec les données fondamentales
        Optimisé pour la latence - analyse rapide d'un seul trade
        """
        if not self.client:
            return {
                "coherence": "unknown",
                "reason": "API Claude non disponible",
                "analysis_time": 0
            }
        
        print("🤖 Claude AI analyse la cohérence du trade...")
        start_time = time.time()
        
        try:
            # Préparer le prompt optimisé pour vitesse
            prompt = self._build_fast_analysis_prompt(trade_data, fundamental_data)
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Modèle plus rapide
                max_tokens=500,  # Limité pour la vitesse
                temperature=0.1,  # Moins créatif = plus rapide
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_time = time.time() - start_time
            analysis_result = self._parse_claude_response(response.content[0].text)
            
            print(f"✅ Analyse Claude terminée en {analysis_time:.2f}s")
            
            return {
                **analysis_result,
                "analysis_time": analysis_time,
                "raw_response": response.content[0].text
            }
            
        except Exception as e:
            analysis_time = time.time() - start_time
            print(f"❌ Erreur analyse Claude: {e}")
            
            return {
                "coherence": "error",
                "reason": f"Erreur API: {e}",
                "analysis_time": analysis_time
            }
    
    def _build_fast_analysis_prompt(self, trade_data: dict, fundamental_data: dict) -> str:
        """Construit un prompt optimisé pour analyse rapide"""
        
        trade_info = f"""
        TRADE À ANALYSER:
        - Symbole: {trade_data.get('symbol', 'N/A')}
        - Direction: {trade_data.get('direction', 'N/A')}
        - Prix entrée: {trade_data.get('entry_price', 'N/A')}
        - Stop Loss: {trade_data.get('stop_loss', 'N/A')}
        - Take Profit: {trade_data.get('take_profit', 'N/A')}
        - Risque: {trade_data.get('risk_amount', 'N/A')}€
        """
        
        fundamental_info = "AUCUNE DONNÉE FONDAMENTALE DISPONIBLE"
        if fundamental_data and 'data_sources' in fundamental_data:
            events = []
            for source in fundamental_data['data_sources']:
                if 'high_impact_events' in source:
                    for event in source['high_impact_events'][:3]:  # Seulement 3 événements max
                        events.append(f"- {event['time']} {event['currency']}: {event['event']} (Actuel: {event['actual']})")
            
            if events:
                fundamental_info = "ÉVÉNEMENTS ÉCONOMIQUES RÉCENTS:\n" + "\n".join(events)
        
        prompt = f"""
        Tu es un analyste trading expert. Analyse RAPIDEMENT la cohérence de ce trade.
        
        {trade_info}
        
        {fundamental_info}
        
        Réponds UNIQUEMENT au format JSON suivant:
        {{
            "coherence": "high|medium|low",
            "reason": "Explication courte et concise",
            "recommendation": "execute|avoid|wait"
        }}
        
        Règles:
        - HIGH: Trade aligné avec fondamentaux et technique
        - MEDIUM: Quelques risques mais acceptable  
        - LOW: Contredit les fondamentaux ou risque élevé
        - execute: Bon trade, exécuter
        - avoid: Mauvais trade, éviter
        - wait: Attendre meilleure opportunité
        
        Réponse ULTRA concise. Maximum 3 phrases.
        """
        
        return prompt
    
    def _parse_claude_response(self, response_text: str) -> dict:
        """Parse la réponse de Claude en JSON structuré"""
        try:
            # Essayer de parser le JSON directement
            if "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: analyse manuelle
        response_lower = response_text.lower()
        
        if "high" in response_lower:
            coherence = "high"
        elif "medium" in response_lower:
            coherence = "medium" 
        elif "low" in response_lower:
            coherence = "low"
        else:
            coherence = "unknown"
        
        if "execute" in response_lower:
            recommendation = "execute"
        elif "avoid" in response_lower:
            recommendation = "avoid"
        elif "wait" in response_lower:
            recommendation = "wait"
        else:
            recommendation = "unknown"
        
        return {
            "coherence": coherence,
            "reason": "Analyse automatique - réponse non structurée",
            "recommendation": recommendation
        }

# TEST DE CONNEXION ET DÉMO
def test_claude_integration():
    """Test l'intégration Claude AI avec un trade exemple"""
    print("🧪 TEST INTÉGRATION CLAUDE AI")
    print("=" * 50)
    
    # Initialiser Claude
    claude = ClaudeAnalyzer()
    
    # Test connexion
    print("🔗 Test connexion API Claude...")
    connection_test = claude.test_connection()
    print(f"📡 {connection_test['message']}")
    
    if connection_test['status'] == 'error':
        print("❌ Impossible de continuer sans connexion Claude")
        return
    
    # Données fondamentales simulées (comme ton scraper)
    fundamental_data = {
        "data_sources": [
            {
                "source": "Investing.com",
                "high_impact_events": [
                    {
                        "time": "10:00",
                        "currency": "EUR",
                        "event": "GDP Growth Rate",
                        "actual": "0.3%",
                        "forecast": "0.2%"
                    },
                    {
                        "time": "13:30", 
                        "currency": "USD",
                        "event": "CPI Inflation",
                        "actual": "3.2%",
                        "forecast": "3.1%"
                    }
                ]
            }
        ]
    }
    
    # Trade exemple pour la démo
    sample_trade = {
        "symbol": "EURUSD",
        "direction": "LONG", 
        "entry_price": 1.0750,
        "stop_loss": 1.0700,
        "take_profit": 1.0850,
        "risk_amount": 150.0,
        "entry_time": datetime.now().isoformat()
    }
    
    print(f"\n🎯 Analyse du trade: {sample_trade['symbol']} {sample_trade['direction']}")
    print(f"💰 Entrée: {sample_trade['entry_price']} | SL: {sample_trade['stop_loss']} | TP: {sample_trade['take_profit']}")
    
    # Analyse avec Claude
    analysis = claude.analyze_trade_coherence(sample_trade, fundamental_data)
    
    print(f"\n📊 RÉSULTAT ANALYSE CLAUDE:")
    print(f"   Cohérence: {analysis['coherence'].upper()}")
    print(f"   Recommandation: {analysis['recommendation'].upper()}")
    print(f"   Raison: {analysis['reason']}")
    print(f"   ⏱️  Temps analyse: {analysis['analysis_time']:.2f}s")
    
    # Décision trading basée sur l'analyse
    if analysis['recommendation'] == 'execute':
        print("🎯 DÉCISION: TRADE CONFIRMÉ - Exécution recommandée")
    elif analysis['recommendation'] == 'avoid':
        print("🚫 DÉCISION: TRADE REJETÉ - Éviter ce trade")
    elif analysis['recommendation'] == 'wait':
        print("⏳ DÉCISION: ATTENDRE - Meilleure opportunité à venir")
    else:
        print("❓ DÉCISION: INCONNUE - Analyse non concluante")

if __name__ == "__main__":
    test_claude_integration()