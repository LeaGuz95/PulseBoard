"""
Servicio principal del Soundboard - Application Layer
Interpreta comandos y coordina dominio + audio + persistencia.
"""
from typing import Optional, List
import os
import uuid
from pathlib import Path

from pulseboard.domain.soundboard import Soundboard
from pulseboard.domain.sound import Sound
from pulseboard.audio.audio_engine import AudioEngine
from pulseboard.audio.effects.pitch_effect import PitchEffect
from pulseboard.audio.effects.speed_effect import SpeedEffect, SlowedEffect, FastEffect
from pulseboard.audio.editors.trimmer import AudioTrimmer
from pulseboard.persistence.config_repository import ConfigRepository
from . import commands


class SoundboardService:
    """
    Servicio de aplicación que coordina todas las operaciones del soundboard.
    No conoce la UI, solo recibe comandos y emite eventos.
    """
    
    def __init__(
        self,
        soundboard: Soundboard,
        audio_engine: AudioEngine,
        config_repo: ConfigRepository
    ):
        self.soundboard = soundboard
        self.audio_engine = audio_engine
        self.config_repo = config_repo
        
        # Mapeo de efectos disponibles
        self._effect_factory = {
            'pitch_high': lambda: PitchEffect(1.5),
            'pitch_low': lambda: PitchEffect(0.7),
            'slowed': lambda: SlowedEffect(),
            'fast': lambda: FastEffect(),
            'speed': lambda params: SpeedEffect(params.get('factor', 1.0))
        }
    
    def handle(self, command):
        """
        Despacha un comando al handler apropiado.
        """
        handler_name = f"_handle_{command.__class__.__name__}"
        handler = getattr(self, handler_name, None)
        
        if handler is None:
            raise ValueError(f"No handler for command {command.__class__.__name__}")
        
        return handler(command)
    
    # ==================== PLAYBACK ====================
    
    def _handle_PlaySound(self, cmd: commands.PlaySound):
        """Reproduce un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        # Cargar si no está cargado
        self.audio_engine.load_sound(sound.id, sound.file_path)
             
        self.audio_engine.play(sound.id, volume=sound.volume, loop=0)
    
    def _handle_StopSound(self, cmd: commands.StopSound):
        """Detiene un sonido"""
        self.audio_engine.stop(cmd.sound_id)
    
    def _handle_StopAllSounds(self, cmd: commands.StopAllSounds):
        """Detiene todos los sonidos"""
        self.audio_engine.stop_all()
    
    # ==================== CONFIGURATION ====================
    
    def _handle_SetVolume(self, cmd: commands.SetVolume):
        """Ajusta el volumen de un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        sound.set_volume(cmd.volume)
        self._save_config()
    
    def _handle_ToggleLoop(self, cmd: commands.ToggleLoop):
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError("Sound not found")

        # 1. Cambiar estado de dominio
        sound.toggle_loop()

        # 2. Reiniciar reproducción en loop
        self.audio_engine.stop(sound.id)

        self.audio_engine.play(
            sound.id,
            volume=sound.volume,
            loop=sound.loop
        )

    
    def _handle_AssignHotkey(self, cmd: commands.AssignHotkey):
        """Asigna un hotkey a un sonido"""
        self.soundboard.update_sound_hotkey(cmd.sound_id, cmd.hotkey)
        self._save_config()
    
    # ==================== SOUND MANAGEMENT ====================
    
    def _handle_AddSoundFromFile(self, cmd: commands.AddSoundFromFile):
        """Agrega un sonido desde un archivo"""
        # Copiar archivo a la carpeta de la categoría
        dest_path = self.config_repo.copy_sound_to_category(
            cmd.file_path,
            cmd.category
        )
        
        # Crear entidad Sound
        sound = Sound(
            file_path=str(dest_path),
            category=cmd.category,
            volume=cmd.volume,
            hotkey=cmd.hotkey
        )
        
        # Agregar al soundboard
        self.soundboard.add_sound(sound)
        
        # Cargar en el motor de audio
        self.audio_engine.load_sound(sound.id, sound.file_path)
        
        self._save_config()
        
        return sound.id
    
    def _handle_DeleteSound(self, cmd: commands.DeleteSound):
        """Elimina un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            return
        
        # Detener si está sonando
        self.audio_engine.stop(cmd.sound_id)
        
        # Descargar del motor
        self.audio_engine.unload_sound(cmd.sound_id)
        
        # Eliminar archivo si se solicita
        if cmd.delete_file:
            self.config_repo.delete_sound_file(sound.file_path)
            if sound.image_path:
                self.config_repo.delete_image_file(sound.image_path)
        
        # Remover del dominio
        self.soundboard.remove_sound(cmd.sound_id)
        
        self._save_config()
    
    def _handle_SetSoundImage(self, cmd: commands.SetSoundImage):
        """Establece la imagen de un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        # Copiar imagen a la carpeta de imágenes
        ext = Path(cmd.image_path).suffix
        new_filename = f"{uuid.uuid4().hex}{ext}"
        dest_path = self.config_repo.copy_image(cmd.image_path, new_filename)
        
        # Actualizar sonido
        sound.set_image(str(dest_path))
        
        self._save_config()
    
    def _handle_RenameSound(self, cmd: commands.RenameSound):
        """Renombra un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        sound.name = cmd.new_name
        self._save_config()
    
    def _handle_MoveSoundToCategory(self, cmd: commands.MoveSoundToCategory):
        """Mueve un sonido a otra categoría"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        # Mover archivo físicamente
        old_path = Path(sound.file_path)
        new_path = self.config_repo.get_sound_path(
            cmd.target_category,
            old_path.name
        )
        
        import shutil
        shutil.move(str(old_path), str(new_path))
        
        # Actualizar en dominio
        self.soundboard.remove_sound(cmd.sound_id)
        sound.file_path = str(new_path)
        sound.category = cmd.target_category
        self.soundboard.add_sound(sound)
        
        self._save_config()
    
    # ==================== CATEGORIES ====================
    
    def _handle_CreateCategory(self, cmd: commands.CreateCategory):
        """Crea una nueva categoría"""
        self.soundboard.create_category(cmd.name)
        
        # Crear carpeta física
        category_path = self.config_repo.sound_folder / cmd.name
        category_path.mkdir(exist_ok=True)
        
        self._save_config()
    
    def _handle_DeleteCategory(self, cmd: commands.DeleteCategory):
        """Elimina una categoría y todos sus sonidos"""
        # Obtener sonidos de la categoría
        sounds = self.soundboard.get_sounds_by_category(cmd.name)
        
        # Eliminar cada sonido
        for sound in sounds:
            self.handle(commands.DeleteSound(sound.id, delete_file=True))
        
        # Eliminar categoría del dominio
        self.soundboard.delete_category(cmd.name)
        
        self._save_config()
    
    # ==================== EFFECTS ====================
    
    def _handle_ApplyEffect(self, cmd: commands.ApplyEffect):
        """Aplica un efecto a un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        # Obtener efecto
        if cmd.effect_name not in self._effect_factory:
            raise ValueError(f"Unknown effect: {cmd.effect_name}")
        
        effect_instance = self._effect_factory[cmd.effect_name]()
        if callable(self._effect_factory[cmd.effect_name]):
            effect_instance = self._effect_factory[cmd.effect_name](cmd.parameters)
        
        # Generar archivo de salida
        output_path = self._get_effect_output_path(sound, cmd.effect_name)
        
        # Aplicar efecto
        self.audio_engine.apply_effects_to_file(
            sound.file_path,
            str(output_path),
            [effect_instance]
        )
        
        # Actualizar sound para usar el nuevo archivo
        sound.file_path = str(output_path)
        sound.add_effect(cmd.effect_name)
        
        # Recargar en el motor
        self.audio_engine.load_sound(sound.id, sound.file_path)
        
        self._save_config()
    
    def _handle_TrimSound(self, cmd: commands.TrimSound):
        """Recorta un sonido"""
        sound = self.soundboard.get_sound(cmd.sound_id)
        if not sound:
            raise ValueError(f"Sound {cmd.sound_id} not found")
        
        # Generar archivo de salida
        output_path = self._get_trimmed_output_path(sound)
        
        # Recortar
        AudioTrimmer.trim(
            sound.file_path,
            str(output_path),
            cmd.start_time,
            cmd.end_time
        )
        
        # Actualizar sound
        sound.file_path = str(output_path)
        
        # Recargar
        self.audio_engine.load_sound(sound.id, sound.file_path)
        
        self._save_config()
    
    # ==================== HELPERS ====================
    
    def _save_config(self):
        """Guarda la configuración actual"""
        data = self.soundboard.to_dict()
        self.config_repo.save(data)
    
    def load_config(self):
        """Carga la configuración guardada"""
        data = self.config_repo.load()
        if data:
            loaded_board = Soundboard.from_dict(data)
            self.soundboard = loaded_board
            
            # Cargar todos los sonidos en el motor de audio
            for sound in self.soundboard.get_all_sounds():
                if os.path.exists(sound.file_path):
                    self.audio_engine.load_sound(sound.id, sound.file_path)
    
    def _get_effect_output_path(self, sound: Sound, effect_name: str) -> Path:
        """Genera ruta para archivo con efecto aplicado"""
        base = Path(sound.file_path)
        stem = base.stem
        ext = base.suffix
        
        new_name = f"{stem}_{effect_name}{ext}"
        return self.config_repo.get_sound_path(sound.category, new_name)
    
    def _get_trimmed_output_path(self, sound: Sound) -> Path:
        """Genera ruta para archivo recortado"""
        base = Path(sound.file_path)
        stem = base.stem
        ext = base.suffix
        
        new_name = f"{stem}_trimmed{ext}"
        return self.config_repo.get_sound_path(sound.category, new_name)
    
    def get_all_sounds(self) -> List[Sound]:
        """Obtiene todos los sonidos"""
        return self.soundboard.get_all_sounds()
    
    def get_sounds_by_category(self, category: str) -> List[Sound]:
        """Obtiene sonidos de una categoría"""
        return self.soundboard.get_sounds_by_category(category)
    
    def get_categories(self) -> List[str]:
        """Obtiene todas las categorías"""
        return self.soundboard.get_categories()
    
    def find_sound_by_hotkey(self, hotkey: str) -> Optional[Sound]:
        """Encuentra un sonido por hotkey"""
        return self.soundboard.find_sound_by_hotkey(hotkey)