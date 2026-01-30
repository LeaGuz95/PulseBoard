"""
Base para efectos de audio - Interface común
"""
from abc import ABC, abstractmethod
import numpy as np


class AudioEffect(ABC):
    """
    Clase base para efectos de audio.
    Define el contrato que todos los efectos deben cumplir.
    """
    
    @abstractmethod
    def apply(self, samples: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Aplica el efecto a las muestras de audio.
        
        Args:
            samples: Array numpy con las muestras (mono o stereo)
            samplerate: Frecuencia de muestreo
        
        Returns:
            Array numpy con las muestras procesadas
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del efecto"""
        pass
    
    def __call__(self, samples: np.ndarray, samplerate: int) -> np.ndarray:
        """Permite usar el efecto como callable"""
        return self.apply(samples, samplerate)