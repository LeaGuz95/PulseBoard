"""
Repositorio de configuración - Persistencia de estado
Guarda y carga el Soundboard completo desde JSON.
"""
import json
import os
from pathlib import Path
from typing import Optional
import sys


class ConfigRepository:
    """
    Maneja la persistencia del estado del soundboard.
    Guarda en JSON en la carpeta de datos del usuario.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Args:
            base_dir: Directorio base (por defecto junto al ejecutable)
        """
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        self.base_dir = Path(base_dir)
        self.user_data_dir = self.base_dir / "Soundboard"
        self.sound_folder = self.user_data_dir / "sounds"
        self.img_folder = self.user_data_dir / "img"
        self.config_file = self.user_data_dir / "config.json"
        
        # Crear directorios si no existen
        self.user_data_dir.mkdir(exist_ok=True)
        self.sound_folder.mkdir(exist_ok=True)
        self.img_folder.mkdir(exist_ok=True)
    
    def save(self, soundboard_data: dict) -> None:
        """
        Guarda el estado del soundboard.
        
        Args:
            soundboard_data: Diccionario con el estado (de Soundboard.to_dict())
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(soundboard_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {e}")
    
    def load(self) -> Optional[dict]:
        """
        Carga el estado del soundboard.
        
        Returns:
            Diccionario con el estado o None si no existe
        """
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {e}")
    
    def get_sound_path(self, category: str, filename: str) -> Path:
        """
        Construye la ruta para un archivo de sonido.
        """
        category_folder = self.sound_folder / category
        category_folder.mkdir(exist_ok=True)
        return category_folder / filename
    
    def get_image_path(self, filename: str) -> Path:
        """
        Construye la ruta para una imagen.
        """
        return self.img_folder / filename
    
    def cleanup_empty_categories(self) -> None:
        """
        Elimina carpetas de categorías vacías.
        """
        if not self.sound_folder.exists():
            return
        
        for category_path in self.sound_folder.iterdir():
            if category_path.is_dir():
                # Verificar si está vacía
                if not any(category_path.iterdir()):
                    try:
                        category_path.rmdir()
                    except Exception as e:
                        print(f"Could not remove empty category {category_path}: {e}")
    
    def delete_sound_file(self, file_path: str) -> None:
        """
        Elimina un archivo de sonido del filesystem.
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        except Exception as e:
            print(f"Could not delete sound file {file_path}: {e}")
    
    def delete_image_file(self, file_path: str) -> None:
        """
        Elimina un archivo de imagen del filesystem.
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
        except Exception as e:
            print(f"Could not delete image file {file_path}: {e}")
    
    def copy_sound_to_category(self, source_path: str, category: str) -> Path:
        """
        Copia un archivo de sonido a la carpeta de una categoría.
        
        Returns:
            Path del archivo copiado
        """
        import shutil
        
        source = Path(source_path)
        dest = self.get_sound_path(category, source.name)
        
        # Si ya existe, no copiar
        if dest.exists():
            return dest
        
        shutil.copy(source, dest)
        return dest
    
    def copy_image(self, source_path: str, new_filename: str) -> Path:
        """
        Copia una imagen a la carpeta de imágenes.
        
        Returns:
            Path de la imagen copiada
        """
        import shutil
        
        source = Path(source_path)
        dest = self.img_folder / new_filename
        
        shutil.copy(source, dest)
        return dest