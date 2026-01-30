"""
Agregado raíz del dominio - Soundboard
Gestiona la colección de sonidos y categorías con reglas de negocio.
"""
from typing import Dict, List, Optional
from pulseboard.domain.sound import Sound


class Soundboard:
    """
    Agregado raíz que gestiona sonidos organizados por categorías.
    Asegura invariantes: hotkeys únicos, sonidos válidos, etc.
    """
    
    def __init__(self):
        self._sounds: Dict[str, Sound] = {}  # id -> Sound
        self._categories: Dict[str, List[str]] = {}  # category -> [sound_ids]
    
    def add_sound(self, sound: Sound) -> None:
        """
        Agrega un sonido al soundboard.
        Valida que no haya hotkeys duplicados.
        """
        # Validar hotkey único
        if sound.hotkey and self._is_hotkey_in_use(sound.hotkey, exclude_id=sound.id):
            raise ValueError(f"Hotkey '{sound.hotkey}' is already in use")
        
        # Agregar a la colección
        self._sounds[sound.id] = sound
        
        # Agregar a la categoría
        if sound.category not in self._categories:
            self._categories[sound.category] = []
        
        if sound.id not in self._categories[sound.category]:
            self._categories[sound.category].append(sound.id)
    
    def remove_sound(self, sound_id: str) -> None:
        """Elimina un sonido del soundboard"""
        if sound_id not in self._sounds:
            return
        
        sound = self._sounds[sound_id]
        
        # Remover de la categoría
        if sound.category in self._categories:
            if sound_id in self._categories[sound.category]:
                self._categories[sound.category].remove(sound_id)
            
            # Limpiar categoría vacía
            if not self._categories[sound.category]:
                del self._categories[sound.category]
        
        # Remover del diccionario principal
        del self._sounds[sound_id]
    
    def get_sound(self, sound_id: str) -> Optional[Sound]:
        """Obtiene un sonido por ID"""
        return self._sounds.get(sound_id)
    
    def get_sounds_by_category(self, category: str) -> List[Sound]:
        """Obtiene todos los sonidos de una categoría"""
        if category not in self._categories:
            return []
        
        return [self._sounds[sid] for sid in self._categories[category] if sid in self._sounds]
    
    def get_all_sounds(self) -> List[Sound]:
        """Obtiene todos los sonidos"""
        return list(self._sounds.values())
    
    def get_categories(self) -> List[str]:
        """Obtiene todas las categorías"""
        return list(self._categories.keys())
    
    def find_sound_by_hotkey(self, hotkey: str) -> Optional[Sound]:
        """Encuentra un sonido por su hotkey"""
        for sound in self._sounds.values():
            if sound.hotkey == hotkey.upper():
                return sound
        return None
    
    def update_sound_hotkey(self, sound_id: str, new_hotkey: str) -> None:
        """
        Actualiza el hotkey de un sonido.
        Valida que no esté en uso.
        """
        if sound_id not in self._sounds:
            raise ValueError(f"Sound {sound_id} not found")
        
        new_hotkey = new_hotkey.upper() if new_hotkey else ""
        
        if new_hotkey and self._is_hotkey_in_use(new_hotkey, exclude_id=sound_id):
            raise ValueError(f"Hotkey '{new_hotkey}' is already in use")
        
        self._sounds[sound_id].assign_hotkey(new_hotkey)
    
    def _is_hotkey_in_use(self, hotkey: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica si un hotkey ya está en uso"""
        hotkey = hotkey.upper()
        for sid, sound in self._sounds.items():
            if sid == exclude_id:
                continue
            if sound.hotkey == hotkey:
                return True
        return False
    
    def create_category(self, category_name: str) -> None:
        """Crea una categoría vacía"""
        if category_name not in self._categories:
            self._categories[category_name] = []
    
    def rename_category(self, old_name: str, new_name: str) -> None:
        """Renombra una categoría y actualiza todos sus sonidos"""
        if old_name not in self._categories:
            return
        
        if new_name in self._categories and new_name != old_name:
            raise ValueError(f"Category '{new_name}' already exists")
        
        # Actualizar sonidos
        for sound_id in self._categories[old_name]:
            if sound_id in self._sounds:
                self._sounds[sound_id].category = new_name
        
        # Renombrar categoría
        self._categories[new_name] = self._categories.pop(old_name)
    
    def delete_category(self, category_name: str) -> None:
        """
        Elimina una categoría y todos sus sonidos.
        CUIDADO: operación destructiva.
        """
        if category_name not in self._categories:
            return
        
        # Eliminar todos los sonidos de la categoría
        sound_ids = self._categories[category_name].copy()
        for sound_id in sound_ids:
            self.remove_sound(sound_id)
        
        # Eliminar categoría
        if category_name in self._categories:
            del self._categories[category_name]
    
    def to_dict(self) -> dict:
        """Serializa el soundboard completo"""
        return {
            "sounds": [s.to_dict() for s in self._sounds.values()],
            "categories": list(self._categories.keys())
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Soundboard':
        """Deserializa un soundboard"""
        board = cls()
        
        for sound_data in data.get("sounds", []):
            sound = Sound.from_dict(sound_data)
            board.add_sound(sound)
        
        # Crear categorías vacías si existen
        for category in data.get("categories", []):
            if category not in board._categories:
                board.create_category(category)
        
        return board