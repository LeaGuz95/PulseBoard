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
    def __init__(self):
        pygame.mixer.init()
        self._sounds = {}     # sound_id -> pygame.mixer.Sound
        self._channels = {}   # sound_id -> pygame.mixer.Channel

    # ================= Playback =================

    def load_sound(self, sound_id: str, file_path: str) -> None:
        if sound_id not in self._sounds:
            self._sounds[sound_id] = pygame.mixer.Sound(file_path)

    def play(self, sound_id: str, volume: float, loop: bool) -> None:
        if sound_id not in self._sounds:
            raise ValueError(f"Sound {sound_id} not loaded")

        sound = self._sounds[sound_id]
        sound.set_volume(volume)

        loops = -1 if loop else 0
        channel = sound.play(loops=loops)

        if channel:
            self._channels[sound_id] = channel

    def stop(self, sound_id: str) -> None:
        channel = self._channels.get(sound_id)
        if channel:
            channel.stop()
            del self._channels[sound_id]

    def stop_all(self) -> None:
        for channel in self._channels.values():
            channel.stop()
        self._channels.clear()

    def is_playing(self, sound_id: str) -> bool:
        channel = self._channels.get(sound_id)
        return channel is not None and channel.get_busy()

    def unload_sound(self, sound_id: str) -> None:
        self.stop(sound_id)
        self._sounds.pop(sound_id, None)

    # ================= Cleanup =================

    def cleanup(self) -> None:
        self.stop_all()
        pygame.mixer.quit()
