"""
Interface de base pour tous les indicateurs techniques
"""
from abc import ABC, abstractmethod
import pandas as pd

class BaseIndicator(ABC):
    """Classe abstraite pour tous les indicateurs techniques"""
    
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule l'indicateur et retourne le DataFrame modifié"""
        pass
    
    @abstractmethod
    def get_signal(self, df: pd.DataFrame, current_index: int) -> int:
        """
        Retourne le signal de trading
        Returns: 1 (ACHAT), -1 (VENTE), 0 (NEUTRE)
        """
        pass
    
    def get_name(self) -> str:
        """Retourne le nom de l'indicateur"""
        return self.__class__.__name__