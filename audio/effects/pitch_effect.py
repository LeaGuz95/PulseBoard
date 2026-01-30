"""
Efecto de Pitch - Cambia el tono sin modificar la velocidad
"""
import numpy as np
from scipy import signal
from  pulseboard.audio.effects.base_effect import AudioEffect


class PitchEffect(AudioEffect):
    """
    Efecto que modifica el pitch (tono) del audio.
    pitch_shift > 1.0 = más agudo (voz ardilla)
    pitch_shift < 1.0 = más grave
    """
    
    def __init__(self, pitch_shift: float = 1.0):
        """
        Args:
            pitch_shift: Factor de cambio de pitch (1.0 = sin cambio)
        """
        if pitch_shift <= 0:
            raise ValueError("pitch_shift must be positive")
        
        self.pitch_shift = pitch_shift
    
    @property
    def name(self) -> str:
        return f"Pitch ({self.pitch_shift:.2f}x)"
    
    def apply(self, samples: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Aplica el cambio de pitch usando resampling.
        Método simple: resample + interpolación para mantener duración.
        """
        if self.pitch_shift == 1.0:
            return samples
        
        # Si es stereo, procesar cada canal
        if len(samples.shape) > 1 and samples.shape[1] > 1:
            processed_channels = []
            for channel in range(samples.shape[1]):
                processed = self._shift_pitch_channel(samples[:, channel])
                processed_channels.append(processed)
            return np.column_stack(processed_channels)
        else:
            return self._shift_pitch_channel(samples)
    
    def _shift_pitch_channel(self, channel_data: np.ndarray) -> np.ndarray:
        """Aplica pitch shift a un canal mono"""
        # Número de muestras después del pitch shift
        new_length = int(len(channel_data) / self.pitch_shift)
        
        # Resample
        resampled = signal.resample(channel_data, new_length)
        
        # Interpolate back to original length para mantener duración
        indices = np.linspace(0, len(resampled) - 1, len(channel_data))
        interpolated = np.interp(indices, np.arange(len(resampled)), resampled)
        
        return interpolated.astype(np.float32)