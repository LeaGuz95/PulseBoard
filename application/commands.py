"""
Commands - Objetos que representan intenciones del usuario
Pattern: Command Pattern para desacoplar UI de lógica
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaySound:
    """Comando para reproducir un sonido"""
    sound_id: str


@dataclass
class StopSound:
    """Comando para detener un sonido"""
    sound_id: str


@dataclass
class StopAllSounds:
    """Comando para detener todos los sonidos"""
    pass


@dataclass
class SetVolume:
    """Comando para ajustar el volumen de un sonido"""
    sound_id: str
    volume: float


@dataclass
class ToggleLoop:
    """Comando para alternar el loop de un sonido"""
    sound_id: str


@dataclass
class AssignHotkey:
    """Comando para asignar un hotkey a un sonido"""
    sound_id: str
    hotkey: str


@dataclass
class AddSoundFromFile:
    """Comando para agregar un sonido desde un archivo"""
    file_path: str
    category: str
    hotkey: str = ""
    volume: float = 1.0


@dataclass
class DeleteSound:
    """Comando para eliminar un sonido"""
    sound_id: str
    delete_file: bool = True


@dataclass
class SetSoundImage:
    """Comando para establecer la imagen de un sonido"""
    sound_id: str
    image_path: str


@dataclass
class CreateCategory:
    """Comando para crear una nueva categoría"""
    name: str


@dataclass
class DeleteCategory:
    """Comando para eliminar una categoría"""
    name: str


@dataclass
class StartRecording:
    """Comando para iniciar grabación de audio"""
    category: str


@dataclass
class StopRecording:
    """Comando para detener grabación y guardar"""
    pass


@dataclass
class ApplyEffect:
    """Comando para aplicar un efecto a un sonido"""
    sound_id: str
    effect_name: str
    parameters: dict


@dataclass
class TrimSound:
    """Comando para recortar un sonido"""
    sound_id: str
    start_time: float
    end_time: float


@dataclass
class RenameSound:
    """Comando para renombrar un sonido"""
    sound_id: str
    new_name: str


@dataclass
class MoveSoundToCategory:
    """Comando para mover un sonido a otra categoría"""
    sound_id: str
    target_category: str