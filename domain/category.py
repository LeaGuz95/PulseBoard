from typing import List, Optional
from pulseboard.domain.sound import Sound


class Category:
    """Entidad de dominio que representa una categoría de sonidos."""

    def __init__(self, name: str):
        if not name:
            raise ValueError("Category name cannot be empty")

        self.name = name
        self.sounds: List[Sound] = []
        self.visible: bool = True

    def add_sound(self, sound: Sound) -> None:
        if sound not in self.sounds:
            self.sounds.append(sound)

    def remove_sound(self, sound: Sound) -> None:
        if sound in self.sounds:
            self.sounds.remove(sound)

    def toggle_visibility(self) -> None:
        self.visible = not self.visible

    def get_sound_by_key(self, key: str) -> Optional[Sound]:
        for sound in self.sounds:
            if sound.key == key.upper():
                return sound
        return None

    def __repr__(self):
        return f"Category(name='{self.name}', sounds={len(self.sounds)}, visible={self.visible})"
