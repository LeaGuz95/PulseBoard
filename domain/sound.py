"""
Entidad Sound - Núcleo del dominio
No conoce audio, UI ni persistencia. Solo estado y reglas de negocio.
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Sound:
    """
    Representa un sonido en el dominio.
    Contiene estado puro: identidad, configuración de reproducción, metadata.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    file_path: str = ""
    category: str = "General"
    
    # Configuración de reproducción
    volume: float = 1.0
    loop: bool = False
    hotkey: str = ""
    
    # Metadata visual
    image_path: Optional[str] = None
    
    # Efectos aplicados (nombres de efectos)
    effects: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not 0 <= self.volume <= 1:
            raise ValueError(f"Volume must be between 0 and 1, got {self.volume}")
        
        if self.file_path and not self.name:
            # Auto-generar nombre desde el archivo
            import os
            self.name = os.path.splitext(os.path.basename(self.file_path))[0]
    
    def set_volume(self, volume: float) -> None:
        """Establece el volumen con validación"""
        if not 0 <= volume <= 1:
            raise ValueError(f"Volume must be between 0 and 1, got {volume}")
        self.volume = volume
    
    def toggle_loop(self) -> None:
        """Alterna el estado de loop"""
        self.loop = not self.loop
    
    def assign_hotkey(self, key: str) -> None:
        """Asigna una tecla de acceso rápido"""
        self.hotkey = key.upper() if key else ""
    
    def set_image(self, path: str) -> None:
        """Establece la imagen asociada"""
        self.image_path = path
    
    def add_effect(self, effect_name: str) -> None:
        """Agrega un efecto a la lista"""
        if effect_name not in self.effects:
            self.effects.append(effect_name)
    
    def remove_effect(self, effect_name: str) -> None:
        """Remueve un efecto de la lista"""
        if effect_name in self.effects:
            self.effects.remove(effect_name)
    
    def clear_effects(self) -> None:
        """Limpia todos los efectos"""
        self.effects = []
    
    def to_dict(self) -> dict:
        """Serializa a diccionario para persistencia"""
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "category": self.category,
            "volume": self.volume,
            "loop": self.loop,
            "hotkey": self.hotkey,
            "image_path": self.image_path,
            "effects": self.effects
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sound':
        """Deserializa desde diccionario"""
        return cls(**data)