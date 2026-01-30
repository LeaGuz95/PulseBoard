"""
Efecto de velocidad - Cambia la velocidad y el pitch simultáneamente
"""
import numpy as np
from scipy import signal
from pulseboard.audio.effects.base_effect import AudioEffect


class SpeedEffect(AudioEffect):
    """
    Efecto que modifica la velocidad de reproducción.
    speed > 1.0 = más rápido (y más agudo)
    speed < 1.0 = más lento (slowed, y más grave)
    """
    
    def __init__(self, speed: float = 1.0):
        """
        Args:
            speed: Factor de velocidad (1.0 = sin cambio)
        """
        if speed <= 0:
            raise ValueError("speed must be positive")
        
        self.speed = speed
    
    @property
    def name(self) -> str:
        if self.speed < 1.0:
            return f"Slowed ({self.speed:.2f}x)"
        elif self.speed > 1.0:
            return f"Fast ({self.speed:.2f}x)"
        return "Normal Speed"
    
    def apply(self, samples: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Aplica el cambio de velocidad usando resampling.
        Cambia tanto la duración como el pitch.
        """
        if self.speed == 1.0:
            return samples
        
        # Calcular nueva longitud
        new_length = int(len(samples) / self.speed)
        
        # Resample
        if len(samples.shape) > 1 and samples.shape[1] > 1:
            # Stereo
            processed_channels = []
            for channel in range(samples.shape[1]):
                resampled = signal.resample(samples[:, channel], new_length)
                processed_channels.append(resampled)
            result = np.column_stack(processed_channels)
        else:
            # Mono
            result = signal.resample(samples, new_length)
        
        return result.astype(np.float32)


class SlowedEffect(SpeedEffect):
    """Preset para efecto slowed (0.8x)"""
    def __init__(self):
        super().__init__(speed=0.8)


class FastEffect(SpeedEffect):
    """Preset para efecto fast (1.5x)"""
    def __init__(self):
        super().__init__(speed=1.5)