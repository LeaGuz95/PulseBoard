"""
Controller - Facade entre UI y Application Services
Coordina hotkeys, filesystem y traduce eventos de UI en Commands.
"""
import keyboard
from typing import Optional, Callable, List, Dict

from pulseboard.application.soundboard_service import SoundboardService
from pulseboard.application.recording_service import RecordingService
from pulseboard.application import commands
from pulseboard.domain.sound import Sound


class SoundboardController:
    """
    Controlador principal que coordina UI, servicios y hotkeys.
    La UI llama a métodos de este controller, que traduce a Commands.
    """
    
    def __init__(
        self,
        soundboard_service: SoundboardService,
        recording_service: RecordingService
    ):
        self.soundboard_service = soundboard_service
        self.recording_service = recording_service
        
        # Observers para notificar a la UI
        self._sound_added_listeners: List[Callable[[Sound], None]] = []
        self._sound_removed_listeners: List[Callable[[str], None]] = []
        self._sound_updated_listeners: List[Callable[[Sound], None]] = []
        self._category_created_listeners: List[Callable[[str], None]] = []
        self._recording_started_listeners: List[Callable[[], None]] = []
        self._recording_stopped_listeners: List[Callable[[Sound], None]] = []
        
        # Hotkey handlers
        self._hotkey_handlers: Dict[str, any] = {}
    
    # ==================== INITIALIZATION ====================
    
    def initialize(self):
        """Inicializa el controller: carga config y setup hotkeys"""
        self.soundboard_service.load_config()
        self.setup_hotkeys()
    
    def shutdown(self):
        """Limpieza al cerrar"""
        self.cleanup_hotkeys()
        self.soundboard_service.config_repo.cleanup_empty_categories()
    
    # ==================== PLAYBACK ====================
    
    def play_sound(self, sound_id: str):
        """Reproduce un sonido"""
        cmd = commands.PlaySound(sound_id)
        self.soundboard_service.handle(cmd)
    
    def stop_sound(self, sound_id: str):
        """Detiene un sonido"""
        cmd = commands.StopSound(sound_id)
        self.soundboard_service.handle(cmd)
    
    def stop_all_sounds(self):
        """Detiene todos los sonidos"""
        cmd = commands.StopAllSounds()
        self.soundboard_service.handle(cmd)
    
    # ==================== CONFIGURATION ====================
    
    def set_volume(self, sound_id: str, volume: float):
        """Ajusta el volumen"""
        cmd = commands.SetVolume(sound_id, volume)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    def toggle_loop(self, sound_id: str):
        """Alterna el loop"""
        cmd = commands.ToggleLoop(sound_id)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    def assign_hotkey(self, sound_id: str, hotkey: str):
        """Asigna un hotkey"""
        try:
            cmd = commands.AssignHotkey(sound_id, hotkey)
            self.soundboard_service.handle(cmd)
            
            # Re-setup hotkeys
            self.setup_hotkeys()
            
            sound = self.soundboard_service.soundboard.get_sound(sound_id)
            if sound:
                self._notify_sound_updated(sound)
            
            return True
        except ValueError as e:
            # Hotkey en uso
            return False
    
    # ==================== SOUND MANAGEMENT ====================
    
    def add_sound_from_file(
        self,
        file_path: str,
        category: str,
        hotkey: str = "",
        volume: float = 1.0
    ) -> str:
        """Agrega un sonido desde un archivo"""
        cmd = commands.AddSoundFromFile(file_path, category, hotkey, volume)
        sound_id = self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_added(sound)
            
            # Setup hotkeys si tiene
            if hotkey:
                self.setup_hotkeys()
        
        return sound_id
    
    def delete_sound(self, sound_id: str, delete_file: bool = True):
        """Elimina un sonido"""
        # Limpiar hotkey primero
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound and sound.hotkey:
            self._remove_hotkey(sound.hotkey)
        
        cmd = commands.DeleteSound(sound_id, delete_file)
        self.soundboard_service.handle(cmd)
        
        self._notify_sound_removed(sound_id)
    
    def set_sound_image(self, sound_id: str, image_path: str):
        """Establece la imagen de un sonido"""
        cmd = commands.SetSoundImage(sound_id, image_path)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    def rename_sound(self, sound_id: str, new_name: str):
        """Renombra un sonido"""
        cmd = commands.RenameSound(sound_id, new_name)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    def move_sound_to_category(self, sound_id: str, target_category: str):
        """Mueve un sonido a otra categoría"""
        cmd = commands.MoveSoundToCategory(sound_id, target_category)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    # ==================== CATEGORIES ====================
    
    def create_category(self, name: str):
        """Crea una categoría"""
        cmd = commands.CreateCategory(name)
        self.soundboard_service.handle(cmd)
        self._notify_category_created(name)
    
    def delete_category(self, name: str):
        """Elimina una categoría"""
        # Obtener sonidos para limpiar hotkeys
        sounds = self.get_sounds_by_category(name)
        for sound in sounds:
            if sound.hotkey:
                self._remove_hotkey(sound.hotkey)
        
        cmd = commands.DeleteCategory(name)
        self.soundboard_service.handle(cmd)
    
    # ==================== RECORDING ====================
    
    def start_recording(self, category: str, device_id: Optional[int] = None):
        """Inicia grabación"""
        rec_id = self.recording_service.start_recording(category, device_id)
        self._notify_recording_started()
        return rec_id
    
    def stop_recording(self):
        """Detiene grabación y agrega el sonido"""
        sound = self.recording_service.stop_recording()
        
        # Agregar al soundboard
        self.soundboard_service.soundboard.add_sound(sound)
        
        # Cargar en motor de audio
        self.soundboard_service.audio_engine.load_sound(sound.id, sound.file_path)
        
        # Guardar config
        self.soundboard_service._save_config()
        
        # Notificar
        self._notify_recording_stopped(sound)
        self._notify_sound_added(sound)
        
        return sound.id
    
    def is_recording(self) -> bool:
        """Verifica si hay grabación activa"""
        return self.recording_service.is_recording()
    
    def get_available_devices(self) -> list:
        """Obtiene dispositivos de entrada disponibles"""
        return self.recording_service.get_available_devices()
    
    # ==================== EFFECTS ====================
    
    def apply_effect(self, sound_id: str, effect_name: str, parameters: dict = None):
        """Aplica un efecto"""
        if parameters is None:
            parameters = {}
        
        cmd = commands.ApplyEffect(sound_id, effect_name, parameters)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    def trim_sound(self, sound_id: str, start_time: float, end_time: float):
        """Recorta un sonido"""
        cmd = commands.TrimSound(sound_id, start_time, end_time)
        self.soundboard_service.handle(cmd)
        
        sound = self.soundboard_service.soundboard.get_sound(sound_id)
        if sound:
            self._notify_sound_updated(sound)
    
    # ==================== QUERIES ====================
    
    def get_all_sounds(self) -> List[Sound]:
        """Obtiene todos los sonidos"""
        return self.soundboard_service.get_all_sounds()
    
    def get_sounds_by_category(self, category: str) -> List[Sound]:
        """Obtiene sonidos de una categoría"""
        return self.soundboard_service.get_sounds_by_category(category)
    
    def get_categories(self) -> List[str]:
        """Obtiene todas las categorías"""
        return self.soundboard_service.get_categories()
    
    def get_sound(self, sound_id: str) -> Optional[Sound]:
        """Obtiene un sonido por ID"""
        return self.soundboard_service.soundboard.get_sound(sound_id)
    
    # ==================== HOTKEYS ====================
    
    def setup_hotkeys(self):
        """Configura todos los hotkeys globales"""
        # Limpiar hotkeys existentes
        self.cleanup_hotkeys()
        
        # Registrar nuevos hotkeys
        for sound in self.get_all_sounds():
            if sound.hotkey:
                self._register_hotkey(sound)
    
    def cleanup_hotkeys(self):
        """Limpia todos los hotkeys"""
        keyboard.unhook_all()
        self._hotkey_handlers.clear()
    
    def _register_hotkey(self, sound: Sound):
        """Registra un hotkey para un sonido"""
        if not sound.hotkey:
            return
        
        def handler():
            self.play_sound(sound.id)
        
        try:
            h = keyboard.add_hotkey(sound.hotkey.lower(), handler)
            self._hotkey_handlers[sound.hotkey] = h
        except Exception as e:
            print(f"Failed to register hotkey {sound.hotkey}: {e}")
    
    def _remove_hotkey(self, hotkey: str):
        """Remueve un hotkey específico"""
        if hotkey in self._hotkey_handlers:
            try:
                keyboard.remove_hotkey(self._hotkey_handlers[hotkey])
                del self._hotkey_handlers[hotkey]
            except Exception as e:
                print(f"Failed to remove hotkey {hotkey}: {e}")
    
    # ==================== OBSERVERS ====================
    
    def on_sound_added(self, listener: Callable[[Sound], None]):
        """Registra listener para cuando se agrega un sonido"""
        self._sound_added_listeners.append(listener)
    
    def on_sound_removed(self, listener: Callable[[str], None]):
        """Registra listener para cuando se elimina un sonido"""
        self._sound_removed_listeners.append(listener)
    
    def on_sound_updated(self, listener: Callable[[Sound], None]):
        """Registra listener para cuando se actualiza un sonido"""
        self._sound_updated_listeners.append(listener)
    
    def on_category_created(self, listener: Callable[[str], None]):
        """Registra listener para cuando se crea una categoría"""
        self._category_created_listeners.append(listener)
    
    def on_recording_started(self, listener: Callable[[], None]):
        """Registra listener para cuando inicia una grabación"""
        self._recording_started_listeners.append(listener)
    
    def on_recording_stopped(self, listener: Callable[[Sound], None]):
        """Registra listener para cuando termina una grabación"""
        self._recording_stopped_listeners.append(listener)
    
    def _notify_sound_added(self, sound: Sound):
        for listener in self._sound_added_listeners:
            listener(sound)
    
    def _notify_sound_removed(self, sound_id: str):
        for listener in self._sound_removed_listeners:
            listener(sound_id)
    
    def _notify_sound_updated(self, sound: Sound):
        for listener in self._sound_updated_listeners:
            listener(sound)
    
    def _notify_category_created(self, category: str):
        for listener in self._category_created_listeners:
            listener(category)
    
    def _notify_recording_started(self):
        for listener in self._recording_started_listeners:
            listener()
    
    def _notify_recording_stopped(self, sound: Sound):
        for listener in self._recording_stopped_listeners:
            listener(sound)