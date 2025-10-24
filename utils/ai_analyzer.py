"""
Analyseur IA universel pour le trading
Supporte : OpenAI, DeepSeek, Claude
"""
import os
from typing import Dict, Optional
from utils.providers.openai_provider import OpenAIProvider
from utils.providers.deepseek_provider import DeepSeekProvider
from utils.providers.claude_provider import ClaudeProvider

class AIAnalyzer:
    """Analyseur IA interchangeable pour confirmation des signaux"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialise le provider IA selon la configuration"""
        provider_name = self.config.get('ai_provider', 'openai').lower()
        api_key = os.getenv('AI_API_KEY') or self.config.get('ai_api_key')
        
        providers = {
            'openai': OpenAIProvider,
            'deepseek': DeepSeekProvider,
            'claude': ClaudeProvider
        }
        
        if provider_name not in providers:
            raise ValueError(f"Provider IA non supporté: {provider_name}")
        
        return providers[provider_name](api_key, self.config)
    
    def analyze_trade_signal(self, signal_data: Dict) -> Dict:
        """
        Analyse un signal de trading avec l'IA
        
        Args:
            signal_data: Données du signal (pair, timeframe, indicateurs, etc.)
        
        Returns:
            Analyse IA avec recommandation
        """
        return self.provider.analyze_signal(signal_data)
    
    def get_market_analysis(self, market_data: Dict) -> Dict:
        """
        Analyse générale du marché
        """
        return self.provider.analyze_market(market_data)