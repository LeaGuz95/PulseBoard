"""
Contenido de todos los archivos __init__.py del proyecto
Copia cada sección en su carpeta correspondiente
"""

# ==================== pulseboard/__init__.py ====================
"""
PulseBoard - Soundboard con arquitectura limpia
"""
__version__ = "2.0.0"


# ==================== pulseboard/domain/__init__.py ====================
"""
Domain layer - Núcleo del negocio
"""
from pulseboard.domain.sound import Sound
from pulseboard.domain.soundboard import Soundboard

__all__ = ['Sound', 'Soundboard']


# ==================== pulseboard/application/__init__.py ====================
"""
Application layer - Casos de uso
"""
from . import commands
from pulseboard.application.soundboard_service import SoundboardService
from pulseboard.application.recording_service import RecordingService

__all__ = ['commands', 'SoundboardService', 'RecordingService']


# ==================== pulseboard/audio/__init__.py ====================
"""
Audio infrastructure layer
"""
from pulseboard.audio.audio_engine import AudioEngine

__all__ = ['AudioEngine']


# ==================== pulseboard/audio/effects/__init__.py ====================
"""
Audio effects
"""
from pulseboard.audio.effects.base_effect import AudioEffect
from pulseboard.audio.effects.pitch_effect import PitchEffect
from pulseboard.audio.effects.speed_effect import SpeedEffect, SlowedEffect, FastEffect

__all__ = [
    'AudioEffect',
    'PitchEffect',
    'SpeedEffect',
    'SlowedEffect',
    'FastEffect'
]


# ==================== pulseboard/audio/editors/__init__.py ====================
"""
Audio editors
"""
from pulseboard.audio.editors.trimmer import AudioTrimmer

__all__ = ['AudioTrimmer']


# ==================== pulseboard/persistence/__init__.py ====================
"""
Persistence layer
"""
from pulseboard.persistence.config_repository import ConfigRepository

__all__ = ['ConfigRepository']


# ==================== pulseboard/ui/__init__.py ====================
"""
UI layer
"""
from pulseboard.ui.main_window import MainWindow
from pulseboard.ui.sound_card import SoundCard
from pulseboard.ui.category_view import CategoryView

__all__ = ['MainWindow', 'SoundCard', 'CategoryView']


# ==================== pulseboard/controller/__init__.py ====================
"""
Controller layer
"""
from pulseboard.controller.soundboard_controller import SoundboardController

__all__ = ['SoundboardController']