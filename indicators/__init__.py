
"""
Package d'indicateurs techniques
"""

from .base_indicator import BaseIndicator
from .bollinger_bands import BollingerBands
from .keltner_channel import KeltnerChannel
from .ema import EMA
from .rsi import RSI
from .ichimoku import Ichimoku
from .fibonacci import Fibonacci
from .candlestick_patterns import CandlestickPatterns

__all__ = [
    'BaseIndicator',
    'BollingerBands', 
    'KeltnerChannel',
    'EMA',
    'RSI',
    'Ichimoku',
    'Fibonacci',
    'CandlestickPatterns'
]

try:
    from stock_indicators import indicators
    STOCK_INDICATORS_AVAILABLE = True
except ImportError:
    STOCK_INDICATORS_AVAILABLE = False
    print("⚠️  StockIndicators non installé. Utilisez: pip install stock-indicators")