"""
Servicio de grabación - Maneja el estado de grabación
"""
import uuid
from typing import Optional
from pathlib import Path

from pulseboard.audio.audio_engine import AudioEngine
from pulseboard.persistence.config_repository import ConfigRepository
from pulseboard.domain.sound import Sound


class RecordingService:
    """
    Servicio especializado en grabación de audio.
    Maneja estado, nombra archivos, devuelve Sound listo.
    """
    
    def __init__(
        self,
        audio_engine: AudioEngine,
        config_repo: ConfigRepository
    ):
        self.audio_engine = audio_engine
        self.config_repo = config_repo
        self._current_category: Optional[str] = None
        self._current_recording_id: Optional[str] = None
    
    def start_recording(self, category: str, device_id: Optional[int] = None) -> str:
        """
        Inicia una grabación.
        
        Args:
            category: Categoría donde se guardará
            device_id: ID del dispositivo de entrada (None = default)
        
        Returns:
            ID de la grabación
        """
        if self.is_recording():
            raise RuntimeError("Already recording")
        
        self._current_category = category
        self._current_recording_id = str(uuid.uuid4())
        
        # Iniciar grabación en el motor
        self.audio_engine.start_recording(device_id=device_id)
        
        return self._current_recording_id
    
    def stop_recording(self) -> Sound:
        """
        Detiene la grabación y retorna un Sound listo para usar.
        
        Returns:
            Entidad Sound con el archivo grabado
        """
        if not self.is_recording():
            raise RuntimeError("No recording active")
        
        # Generar nombre de archivo
        filename = f"rec_{uuid.uuid4().hex}.wav"
        output_path = self.config_repo.get_sound_path(
            self._current_category,
            filename
        )
        
        # Detener y guardar
        self.audio_engine.stop_recording(str(output_path))
        
        # Crear entidad Sound
        sound = Sound(
            file_path=str(output_path),
            category=self._current_category,
            name=f"Recording {self._current_recording_id[:8]}"
        )
        
        # Limpiar estado
        self._current_category = None
        self._current_recording_id = None
        
        return sound
    
    def is_recording(self) -> bool:
        """Verifica si hay una grabación activa"""
        return self.audio_engine.is_recording()
    
    def get_recording_id(self) -> Optional[str]:
        """Obtiene el ID de la grabación actual"""
        return self._current_recording_id
    
    def get_available_devices(self) -> list:
        """Obtiene lista de dispositivos de entrada disponibles"""
        return self.audio_engine.get_available_input_devices()