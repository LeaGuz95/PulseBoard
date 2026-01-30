"""
Vista de categoría - Contenedor colapsable
"""
import customtkinter as ctk
import os
from tkinter import messagebox


class CategoryView(ctk.CTkFrame):
    """
    Vista de una categoría.
    Header con nombre, botones de acción y contenido colapsable.
    """
    
    def __init__(self, parent, category_name: str, controller, main_window):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0
        )
        
        self.category_name = category_name
        self.controller = controller
        self.main_window = main_window
        self.visible = True
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz"""
        # Header
        header_frame = ctk.CTkFrame(
            self,
            fg_color=self.main_window.BG_CARD,
            height=50,
            corner_radius=0
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Botón de toggle (nombre de categoría)
        self.toggle_btn = ctk.CTkButton(
            header_frame,
            text=f"{self.category_name.upper()}",
            font=self.main_window.font_main_bold,
            fg_color="transparent",
            hover_color=self.main_window.BG_LIGHTER,
            text_color=self.main_window.ACCENT,
            anchor="w",
            corner_radius=0,
            command=self._toggle
        )
        self.toggle_btn.pack(side="left", fill="both", expand=True, padx=10)
        
        # Botón abrir carpeta
        folder_btn = ctk.CTkButton(
            header_frame,
            text="📁",
            font=self.main_window.font_main_bold,
            width=40,
            height=40,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color=self.main_window.ACCENT_DIM,
            border_width=2,
            border_color=self.main_window.ACCENT,
            text_color=self.main_window.ACCENT,
            corner_radius=0,
            command=self._open_folder
        )
        folder_btn.pack(side="right", padx=5)
        
        # Contenedor de contenido
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="x", pady=(5, 0))
    
    def _toggle(self):
        """Alterna visibilidad del contenido"""
        if self.visible:
            self.content_frame.pack_forget()
            self.toggle_btn.configure(text=f" {self.category_name.upper()}")
        else:
            self.content_frame.pack(fill="x", pady=(5, 0))
            self.toggle_btn.configure(text=f"▼ {self.category_name.upper()}")
        
        self.visible = not self.visible
    
    def _open_folder(self):
        """Abre la carpeta de la categoría"""
        path = os.path.join(
            self.controller.soundboard_service.config_repo.sound_folder,
            self.category_name
        )
        
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("Error", "La carpeta no existe")