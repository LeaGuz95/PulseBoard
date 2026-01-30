"""
Trimmer - Recorte de audio
Operación destructiva que genera un nuevo archivo.
"""
import soundfile as sf
import numpy as np
from pathlib import Path


class AudioTrimmer:
    """
    Recorta archivos de audio generando nuevos archivos.
    No modifica el original.
    """
    
    @staticmethod
    def trim(
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float
    ) -> str:
        """
        Recorta un archivo de audio.
        
        Args:
            input_path: Ruta del archivo original
            output_path: Ruta donde guardar el resultado
            start_time: Tiempo de inicio en segundos
            end_time: Tiempo de fin en segundos
        
        Returns:
            Ruta del archivo generado
        """
        # Validaciones
        if start_time < 0:
            raise ValueError("start_time cannot be negative")
        
        if end_time <= start_time:
            raise ValueError("end_time must be greater than start_time")
        
        # Leer archivo
        data, samplerate = sf.read(input_path)
        
        # Convertir tiempos a samples
        start_sample = int(start_time * samplerate)
        end_sample = int(end_time * samplerate)
        
        # Validar rangos
        total_samples = len(data)
        if start_sample >= total_samples:
            raise ValueError(f"start_time ({start_time}s) exceeds audio duration")
        
        end_sample = min(end_sample, total_samples)
        
        # Recortar
        trimmed = data[start_sample:end_sample]
        
        # Guardar
        sf.write(output_path, trimmed, samplerate)
        
        return output_path
    
    @staticmethod
    def get_duration(file_path: str) -> float:
        """
        Obtiene la duración de un archivo de audio en segundos.
        """
        info = sf.info(file_path)
        return info.duration
    
    @staticmethod
    def get_info(file_path: str) -> dict:
        """
        Obtiene información detallada de un archivo de audio.
        """
        info = sf.info(file_path)
        return {
            'duration': info.duration,
            'samplerate': info.samplerate,
            'channels': info.channels,
            'format': info.format,
            'subtype': info.subtype
        }