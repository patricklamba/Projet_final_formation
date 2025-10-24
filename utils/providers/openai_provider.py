"""
Provider OpenAI (ChatGPT)
"""
import openai
from typing import Dict

class OpenAIProvider:
    def __init__(self, api_key: str, config: Dict):
        self.client = openai.OpenAI(api_key=api_key)
        self.config = config
    
    def analyze_signal(self, signal_data: Dict) -> Dict:
        prompt = self._build_trading_prompt(signal_data)
        
        response = self.client.chat.completions.create(
            model=self.config.get('openai_model', 'gpt-4'),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _build_trading_prompt(self, signal_data: Dict) -> str:
        return f"""
        Analyse ce signal de trading et donne ton avis :
        
        Paire: {signal_data.get('pair')}
        Timeframe: {signal_data.get('timeframe')}
        Signal: {signal_data.get('signal_type')}
        Prix actuel: {signal_data.get('price')}
        Indicateurs: {signal_data.get('indicators', {})}
        
        Réponds au format JSON avec:
        - confidence_score (0-100)
        - recommendation (BUY/SELL/HOLD)
        - reasoning (raisonnement)
        - risk_level (LOW/MEDIUM/HIGH)
        """
    
    def _parse_response(self, response: str) -> Dict:
        # Logique de parsing de la réponse
        return {"raw_response": response, "provider": "openai"}