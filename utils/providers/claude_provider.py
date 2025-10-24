"""
Provider Claude (Anthropic)
"""
import anthropic
from typing import Dict

class ClaudeProvider:
    def __init__(self, api_key: str, config: Dict):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.config = config
    
    def analyze_signal(self, signal_data: Dict) -> Dict:
        prompt = self._build_trading_prompt(signal_data)
        
        response = self.client.messages.create(
            model=self.config.get('claude_model', 'claude-3-sonnet-20240229'),
            max_tokens=1000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_response(response.content[0].text)