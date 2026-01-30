"""
Motor de audio - Infraestructura de reproducción y grabación
Maneja pygame, sounddevice y aplicación de efectos.
"""
import pygame
import sounddevice as sd
import soundfile as sf
import numpy as np
from typing import Optional, Callable, List
from pathlib import Path


class AudioEngine:
    """
    Motor de audio que abstrae pygame y sounddevice.
    Reproduce, detiene, graba y aplica cadenas de efectos.
    """
    
    def __init__(self):
        pygame.mixer.init()
        self._playing_sounds = {}  # sound_id -> pygame.mixer.Sound
        self._recording_stream = None
        self._recording_buffer = []
        self._recording_active = False
    
    def load_sound(self, sound_id: str, file_path: str) -> None:
        """Carga un sonido en memoria"""
        try:
            sound_obj = pygame.mixer.Sound(file_path)
            self._playing_sounds[sound_id] = sound_obj
        except Exception as e:
            raise RuntimeError(f"Failed to load sound {file_path}: {e}")
    
    def play(self, sound_id: str, volume: float = 1.0, loops: int = 0) -> None:
        """
        Reproduce un sonido.
        loops: 0 = una vez, -1 = infinito
        """
        if sound_id not in self._playing_sounds:
            raise ValueError(f"Sound {sound_id} not loaded")
        
        sound = self._playing_sounds[sound_id]
        sound.set_volume(volume)
        sound.play(loops=loops)
    
    def stop(self, sound_id: str) -> None:
        """Detiene un sonido específico"""
        if sound_id in self._playing_sounds:
            self._playing_sounds[sound_id].stop()
    
    def stop_all(self) -> None:
        """Detiene todos los sonidos"""
        pygame.mixer.stop()
    
    def is_playing(self, sound_id: str) -> bool:
        """Verifica si un sonido está reproduciéndose"""
        if sound_id not in self._playing_sounds:
            return False
        
        # pygame.mixer no tiene forma directa de saber esto por sonido
        # Asumimos que si hay algún canal activo, algo está sonando
        return pygame.mixer.get_busy()
    
    def unload_sound(self, sound_id: str) -> None:
        """Descarga un sonido de memoria"""
        if sound_id in self._playing_sounds:
            self._playing_sounds[sound_id].stop()
            del self._playing_sounds[sound_id]
    
    def start_recording(
        self, 
        device_id: Optional[int] = None,
        samplerate: int = 44100,
        channels: int = 2
    ) -> None:
        """
        Inicia grabación de audio.
        device_id: ID del dispositivo de entrada (None = default)
        """
        if self._recording_active:
            raise RuntimeError("Recording already active")
        
        self._recording_buffer = []
        self._recording_active = True
        
        def callback(indata, frames, time, status):
            if self._recording_active:
                self._recording_buffer.append(indata.copy())
        
        self._recording_stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            device=device_id,
            callback=callback,
            dtype='float32'
        )
        
        self._recording_stream.start()
    
    def stop_recording(self, output_path: str) -> str:
        """
        Detiene la grabación y guarda el archivo.
        Retorna la ruta del archivo guardado.
        """
        if not self._recording_active:
            raise RuntimeError("No recording active")
        
        self._recording_active = False
        
        if self._recording_stream:
            self._recording_stream.stop()
            self._recording_stream.close()
            self._recording_stream = None
        
        if not self._recording_buffer:
            raise RuntimeError("No audio data recorded")
        
        # Concatenar buffers
        audio_data = np.concatenate(self._recording_buffer, axis=0)
        
        # Guardar archivo
        sf.write(output_path, audio_data, 44100)
        
        # Limpiar buffer
        self._recording_buffer = []
        
        return output_path
    
    def is_recording(self) -> bool:
        """Verifica si hay una grabación activa"""
        return self._recording_active
    
    def get_available_input_devices(self) -> List[dict]:
        """
        Retorna lista de dispositivos de entrada disponibles.
        Útil para seleccionar loopback, stereo mix, etc.
        """
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                devices.append({
                    'id': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels'],
                    'is_loopback': 'loopback' in dev['name'].lower()
                })
        return devices
    
    def apply_effects_to_file(
        self,
        input_path: str,
        output_path: str,
        effect_chain: List[Callable[[np.ndarray, int], np.ndarray]]
    ) -> None:
        """
        Aplica una cadena de efectos a un archivo de audio.
        effect_chain: lista de funciones que toman (samples, samplerate) y retornan samples procesados
        """
        # Leer archivo
        data, samplerate = sf.read(input_path)
        
        # Aplicar efectos en cadena
        processed = data
        for effect in effect_chain:
            processed = effect(processed, samplerate)
        
        # Guardar resultado
        sf.write(output_path, processed, samplerate)
    
    def cleanup(self) -> None:
        """Limpia recursos"""
        if self._recording_stream:
            self._recording_stream.stop()
            self._recording_stream.close()
        
        pygame.mixer.quit()