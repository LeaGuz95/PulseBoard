"""
Ventana principal - UI estilo pixel art / retro
Inspirada en el diseño de index.html
"""
import customtkinter as ctk
from customtkinter import CTkFont
import ctypes
import os
import sys
from typing import Dict

from pulseboard.ui.category_view import CategoryView
from pulseboard.ui.sound_card import SoundCard
from pulseboard.controller.soundboard_controller import SoundboardController


def resource_path(relative_path):
    """Obtiene la ruta absoluta para archivos, incluso dentro del exe"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_font_windows(ttf_path):
    """Carga una fuente en Windows (opcional)"""
    try:
        path = resource_path(ttf_path)
        if not os.path.exists(path):
            print(f"⚠️ Font not found: {path}, using system default")
            return False
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)
        return True
    except Exception as e:
        print(f"⚠️ Failed to load font {ttf_path}: {e}")
        return False


class MainWindow(ctk.CTk):
    """
    Ventana principal del Soundboard.
    Diseño pixel art / retro inspirado en terminales antiguas.
    """
    
    # THEME COLORS (inspirado en tu HTML)
    BG_MAIN = "#0a0a0a"
    BG_CARD = "#121214"
    BG_LIGHTER = "#1a1a1c"
    ACCENT = "#25aff4"
    ACCENT_DIM = "#3b4c54"
    SUCCESS = "#4ade80"
    WARNING = "#fbbf24"
    DANGER = "#ef4444"
    
    def __init__(self, controller: SoundboardController, fonts_folder: str):
        super().__init__()
        
        self.controller = controller
        
        # Cargar fuentes
        load_font_windows(os.path.join(fonts_folder, "orbitron-medium.ttf"))
        load_font_windows(os.path.join(fonts_folder, "Rajdhani-Regular.ttf"))
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configurar ventana
        self.title("PulseBoard")
        self.geometry("900x700")
        self.configure(fg_color=self.BG_MAIN)
        
        # Fuentes
        self.font_title = CTkFont("Orbitron", 20, "bold")
        self.font_subtitle = CTkFont("Orbitron", 12, "bold")
        self.font_main = CTkFont("Rajdhani", 13)
        self.font_main_bold = CTkFont("Rajdhani", 13, "bold")
        self.font_small = CTkFont("Rajdhani", 10)
        self.font_footer = CTkFont("Orbitron", 8)
        
        # Estado
        self.category_views: Dict[str, CategoryView] = {}
        self.sound_cards: Dict[str, SoundCard] = {}
        
        # Construir UI
        self._build_ui()
        
        # Registrar observers
        self._setup_observers()
        
        # Cargar contenido inicial
        self._load_initial_content()
    
    def _build_ui(self):
        """Construye la interfaz"""
        # Header
        self._build_header()
        
        # Subheader con tabs
        self._build_tabs()
        
        # Action bar
        self._build_action_bar()
        
        # Contenedor scrollable para categorías
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color=self.BG_MAIN
        )
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Footer
        self._build_footer()
    
    def _build_header(self):
        """Construye el header estilo terminal"""
        header = ctk.CTkFrame(
            self,
            fg_color=self.BG_CARD,
            height=70,
            corner_radius=0
        )
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)
        
        # Icono + título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=10)
        
        # Terminal icon (emoji)
        icon_label = ctk.CTkLabel(
            title_frame,
            text=":D",
            font=CTkFont("Segoe UI Emoji", 32),
            text_color=self.ACCENT
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="PULSEBOARD",
            font=self.font_title,
            text_color=self.ACCENT
        )
        title_label.pack(side="left")
        
        # Botón de configuración
        settings_btn = ctk.CTkButton(
            header,
            text="⚙️",
            font=CTkFont("Segoe UI Emoji", 20),
            width=50,
            height=50,
            fg_color=self.BG_LIGHTER,
            hover_color=self.ACCENT_DIM,
            border_width=2,
            border_color=self.ACCENT,
            text_color=self.ACCENT,
            corner_radius=0,
            command=self._show_settings
        )
        settings_btn.pack(side="right", padx=20, pady=10)
    
    def _build_tabs(self):
        """Construye la barra de tabs para filtrar categorías"""
        tabs_container = ctk.CTkFrame(
            self,
            fg_color=self.BG_CARD,
            height=45,
            corner_radius=0
        )
        tabs_container.pack(fill="x", pady=(0, 2))
        tabs_container.pack_propagate(False)
        
        # Versión label
        version_label = ctk.CTkLabel(
            tabs_container,
            text=" SOUNDBOARD_V6.0",
            font=self.font_small,
            text_color=self.ACCENT
        )
        version_label.pack(side="left", padx=20, pady=10)
        
        # TODO: Implementar tabs de categorías
        
    
    def _build_action_bar(self):
        """Construye la barra de acciones"""
        action_bar = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=50
        )
        action_bar.pack(fill="x", padx=10, pady=(10, 5))
        
        # Botón crear carpeta
        create_folder_btn = ctk.CTkButton(
            action_bar,
            text="📂 Nueva Carpeta",
            font=self.font_main_bold,
            height=40,
            fg_color=self.BG_LIGHTER,
            hover_color=self.ACCENT_DIM,
            border_width=2,
            border_color=self.ACCENT,
            text_color=self.ACCENT,
            corner_radius=0,
            command=self._create_category
        )
        create_folder_btn.pack(side="left", padx=5)
        
        # Botón agregar sonido
        add_sound_btn = ctk.CTkButton(
            action_bar,
            text="🎵 Agregar Sonido",
            font=self.font_main_bold,
            height=40,
            fg_color=self.BG_LIGHTER,
            hover_color=self.ACCENT_DIM,
            border_width=2,
            border_color=self.SUCCESS,
            text_color=self.SUCCESS,
            corner_radius=0,
            command=self._add_sound
        )
        add_sound_btn.pack(side="left", padx=5)
        
        # Botón grabar
        self.record_btn = ctk.CTkButton(
            action_bar,
            text="🎙️Grabar",
            font=self.font_main_bold,
            height=40,
            fg_color=self.BG_LIGHTER,
            hover_color=self.ACCENT_DIM,
            border_width=2,
            border_color=self.DANGER,
            text_color=self.DANGER,
            corner_radius=0,
            command=self._toggle_recording
        )
        self.record_btn.pack(side="left", padx=5)
        
        # Botón detener todos
        stop_all_btn = ctk.CTkButton(
            action_bar,
            text="X Detener Todo",
            font=self.font_main_bold,
            height=40,
            fg_color=self.BG_LIGHTER,
            hover_color=self.ACCENT_DIM,
            border_width=2,
            border_color=self.WARNING,
            text_color=self.WARNING,
            corner_radius=0,
            command=self.controller.stop_all_sounds
        )
        stop_all_btn.pack(side="right", padx=5)
    
    def _build_footer(self):
        """Construye el footer"""
        footer = ctk.CTkFrame(
            self,
            fg_color=self.BG_CARD,
            height=40,
            corner_radius=0
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        footer_text = ctk.CTkLabel(
            footer,
            text="SOFTWARE BY LEANDROGUZMAN // SYSTEM READY",
            font=self.font_footer,
            text_color=self.ACCENT_DIM
        )
        footer_text.pack(pady=10)
    
    # ==================== ACTIONS ====================
    
    def _create_category(self):
        """Crea una nueva categoría"""
        from tkinter import simpledialog
        
        name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if name:
            try:
                self.controller.create_category(name)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", str(e))
    
    def _add_sound(self):
        """Agrega un sonido desde archivo"""
        from tkinter import filedialog, messagebox
        
        categories = self.controller.get_categories()
        if not categories:
            messagebox.showerror("Error", "Crea una carpeta primero")
            return
        
        # Seleccionar archivo
        file = filedialog.askopenfilename(
            title="Seleccionar sonido",
            filetypes=[("Audio", "*.wav *.mp3 *.ogg")]
        )
        if not file:
            return
        
        # Seleccionar categoría
        category = self._select_category_dialog("Seleccionar carpeta")
        if not category:
            return
        
        try:
            self.controller.add_sound_from_file(file, category)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _toggle_recording(self):
        """Inicia o detiene grabación"""
        if self.controller.is_recording():
            # Detener
            try:
                self.controller.stop_recording()
                self.record_btn.configure(
                    text="🎙️Grabar",
                    border_color=self.DANGER,
                    text_color=self.DANGER
                )
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", str(e))
        else:
            # Iniciar
            categories = self.controller.get_categories()
            if not categories:
                from tkinter import messagebox
                messagebox.showerror("Error", "Crea una carpeta primero")
                return
            
            category = self._select_category_dialog("Grabar en carpeta")
            if not category:
                return
            
            # Seleccionar dispositivo (opcional)
            # Por ahora usamos el default
            device_id = None
            
            try:
                self.controller.start_recording(category, device_id)
                self.record_btn.configure(
                    text=" 🎙️Terminar ",
                    border_color=self.SUCCESS,
                    text_color=self.SUCCESS
                )
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", str(e))
    
    def _show_settings(self):
        """Muestra ventana de configuración"""
        # TODO: Implementar
        from tkinter import messagebox
        messagebox.showinfo("Configuración", "Próximamente...")
    
    def _select_category_dialog(self, title: str) -> str:
        """Muestra diálogo para seleccionar categoría"""
        from tkinter import simpledialog
        
        categories = self.controller.get_categories()
        
        # Crear popup
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("300x400")
        popup.transient(self)
        popup.grab_set()
        popup.configure(fg_color=self.BG_MAIN)
        
        selected = [None]  # Usar lista para closure
        
        ctk.CTkLabel(
            popup,
            text=title,
            font=self.font_subtitle,
            text_color=self.ACCENT
        ).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(popup, fg_color=self.BG_CARD)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        def select(cat):
            selected[0] = cat
            popup.destroy()
        
        for cat in categories:
            btn = ctk.CTkButton(
                scroll,
                text=cat,
                font=self.font_main,
                height=40,
                fg_color=self.BG_LIGHTER,
                hover_color=self.ACCENT_DIM,
                border_width=2,
                border_color=self.ACCENT,
                text_color=self.ACCENT,
                corner_radius=0,
                command=lambda c=cat: select(c)
            )
            btn.pack(fill="x", pady=5)
        
        self.wait_window(popup)
        return selected[0]
    
    # ==================== OBSERVERS ====================
    
    def _setup_observers(self):
        """Registra observers en el controller"""
        self.controller.on_sound_added(self._on_sound_added)
        self.controller.on_sound_removed(self._on_sound_removed)
        self.controller.on_sound_updated(self._on_sound_updated)
        self.controller.on_category_created(self._on_category_created)
    
    def _on_sound_added(self, sound):
        """Handler cuando se agrega un sonido"""
        # Obtener o crear category view
        if sound.category not in self.category_views:
            self._create_category_view(sound.category)
        
        category_view = self.category_views[sound.category]
        
        # Crear sound card
        sound_card = SoundCard(
            category_view.content_frame,
            sound,
            self.controller,
            self
        )
        sound_card.pack(fill="x", pady=6)
        
        self.sound_cards[sound.id] = sound_card
    
    def _on_sound_removed(self, sound_id):
        """Handler cuando se elimina un sonido"""
        if sound_id in self.sound_cards:
            self.sound_cards[sound_id].destroy()
            del self.sound_cards[sound_id]
    
    def _on_sound_updated(self, sound):
        """Handler cuando se actualiza un sonido"""
        if sound.id in self.sound_cards:
            self.sound_cards[sound.id].update_from_sound(sound)
    
    def _on_category_created(self, category):
        """Handler cuando se crea una categoría"""
        self._create_category_view(category)
    
    # ==================== CONTENT ====================
    
    def _load_initial_content(self):
        """Carga el contenido inicial"""
        # Crear vistas de categorías
        for category in self.controller.get_categories():
            self._create_category_view(category)
        
        # Crear cards de sonidos
        for sound in self.controller.get_all_sounds():
            self._on_sound_added(sound)
    
    def _create_category_view(self, category: str):
        """Crea una vista de categoría"""
        if category in self.category_views:
            return
        
        category_view = CategoryView(
            self.scroll_container,
            category,
            self.controller,
            self
        )
        category_view.pack(fill="x", pady=10)
        
        self.category_views[category] = category_view