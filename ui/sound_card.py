"""
Componente visual de una tarjeta de sonido
Diseño pixel art / retro
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path

from pulseboard.domain.sound import Sound
from pulseboard.controller.soundboard_controller import SoundboardController


class SoundCard(ctk.CTkFrame):
    """
    Tarjeta visual de un sonido.
    Muestra info, controles de reproducción, volumen, etc.
    """
    
    def __init__(
        self,
        parent,
        sound: Sound,
        controller: SoundboardController,
        main_window
    ):
        super().__init__(
            parent,
            fg_color=main_window.BG_CARD,
            border_width=2,
            border_color=main_window.ACCENT_DIM,
            corner_radius=0
        )
        
        self.sound = sound
        self.controller = controller
        self.main_window = main_window
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz de la tarjeta"""
        # Contenedor principal con padding
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=8, pady=8)
        
        # Fila 1: Imagen + Info + Equalizer
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        
        # Imagen
        self.image_label = ctk.CTkLabel(
            top_row,
            text="+ IMG",
            width=60,
            height=60,
            fg_color=self.main_window.BG_LIGHTER,
            text_color=self.main_window.ACCENT_DIM,
            font=self.main_window.font_small,
            corner_radius=0
        )
        self.image_label.pack(side="left", padx=(0, 10))
        self.image_label.bind("<Button-1>", lambda e: self._set_image())
        
        # Info (nombre + estado)
        info_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        self.name_label = ctk.CTkLabel(
            info_frame,
            text=self.sound.name.upper(),
            font=self.main_window.font_main_bold,
            text_color=self.main_window.ACCENT,
            anchor="w"
        )
        self.name_label.pack(anchor="w")
        
        status_text = "LOOP" if self.sound.loop else "READY"
        self.status_label = ctk.CTkLabel(
            info_frame,
            text=f"0:00 // {status_text}",
            font=self.main_window.font_small,
            text_color=self.main_window.ACCENT_DIM,
            anchor="w"
        )
        self.status_label.pack(anchor="w")
        
        # Equalizer icon
        eq_label = ctk.CTkLabel(
            top_row,
            text="📶",
            font=ctk.CTkFont("Segoe UI Emoji", 32),
            text_color=self.main_window.ACCENT_DIM
        )
        eq_label.pack(side="right", padx=(10, 0))
        
        # Separador
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.main_window.ACCENT_DIM,
            corner_radius=0
        )
        separator.pack(fill="x", pady=10)
        
        # Fila 2: Botones de control
        controls = ctk.CTkFrame(content, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 10))
        
        # Play button
        play_btn = ctk.CTkButton(
            controls,
            text="▸",
            font=self.main_window.font_main_bold,
            width=80,
            height=35,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color="#0E4F10",
            border_width=2,
            border_color=self.main_window.SUCCESS,
            text_color=self.main_window.SUCCESS,
            corner_radius=0,
            command=self._play
        )
        play_btn.pack(side="left", padx=2)
        
        # Stop button
        stop_btn = ctk.CTkButton(
            controls,
            text="🟥",
            font=self.main_window.font_main_bold,
            width=80,
            height=35,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color="#3E0E4F",
            border_width=2,
            border_color=self.main_window.ACCENT,
            text_color=self.main_window.ACCENT,
            corner_radius=0,
            command=self._stop
        )
        stop_btn.pack(side="left", padx=2)
        
        # Loop button
        loop_color = self.main_window.SUCCESS if self.sound.loop else self.main_window.ACCENT_DIM
        self.loop_btn = ctk.CTkButton(
            controls,
            text="LOOP",
            font=self.main_window.font_small,
            width=70,
            height=35,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color="#112B80",
            border_width=2,
            border_color=loop_color,
            text_color=loop_color,
            corner_radius=0,
            command=self._toggle_loop
        )
        self.loop_btn.pack(side="left", padx=2)
        
        # Hotkey button
        hotkey_text = self.sound.hotkey if self.sound.hotkey else "Tecla"
        self.hotkey_btn = ctk.CTkButton(
            controls,
            text=hotkey_text,
            font=self.main_window.font_small,
            width=60,
            height=35,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color="#4D4F0E",
            border_width=2,
            border_color=self.main_window.WARNING,
            text_color=self.main_window.WARNING,
            corner_radius=0,
            command=self._assign_hotkey
        )
        self.hotkey_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            controls,
            text="🗑️",
            font=self.main_window.font_main_bold,
            width=50,
            height=35,
            fg_color=self.main_window.BG_LIGHTER,
            hover_color="#4F0E0E",
            border_width=2,
            border_color=self.main_window.DANGER,
            text_color=self.main_window.DANGER,
            corner_radius=0,
            command=self._delete
        )
        delete_btn.pack(side="right", padx=2)
        
        # Fila 3: Volume control
        volume_frame = ctk.CTkFrame(content, fg_color="transparent")
        volume_frame.pack(fill="x")
        
        # Volume label
        vol_label_frame = ctk.CTkFrame(volume_frame, fg_color="transparent")
        vol_label_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            vol_label_frame,
            text="VOL_LEVEL",
            font=self.main_window.font_small,
            text_color=self.main_window.ACCENT
        ).pack(side="left")
        
        self.volume_percent_label = ctk.CTkLabel(
            vol_label_frame,
            text=f"{int(self.sound.volume * 100)}%",
            font=self.main_window.font_small,
            text_color=self.main_window.ACCENT
        )
        self.volume_percent_label.pack(side="right")
        
        # Volume bar (pixel style)
        self._build_volume_bar(volume_frame)
        
        # Cargar imagen si existe
        if self.sound.image_path:
            self._load_image(self.sound.image_path)
    
    def _build_volume_bar(self, parent):
        """Construye una barra de volumen estándar"""
        self.volume_bar = ctk.CTkProgressBar(
            parent,
            orientation="horizontal",
            height=12,
            corner_radius=0,
            fg_color="#000000",
            progress_color=self.main_window.ACCENT
        )
        self.volume_bar.pack(fill="x", expand=True, pady=(2, 0))

        self.volume_bar.set(self.sound.volume)

        # Click para ajustar volumen
        self.volume_bar.bind("<Button-1>", self._on_volume_click)

    def _update_volume_visual(self):
        self.volume_bar.set(self.sound.volume)
    def _on_volume_click(self, event):
        width = self.volume_bar.winfo_width()
        if width <= 0:
            return

        new_volume = event.x / width
        new_volume = max(0.0, min(1.0, new_volume))

        self.controller.set_volume(self.sound.id, new_volume)
    

    # ==================== ACTIONS ====================
    
    def _play(self):
        """Reproduce el sonido"""
        self.controller.play_sound(self.sound.id)
    
    def _stop(self):
        """Detiene el sonido"""
        self.controller.stop_sound(self.sound.id)
    
    def _toggle_loop(self):
        """Alterna el loop"""
        self.controller.toggle_loop(self.sound.id)
    
    def _assign_hotkey(self):
        """Asigna un hotkey"""
        popup = ctk.CTkToplevel(self.main_window)
        popup.title("Asignar Tecla")
        popup.geometry("300x150")
        popup.transient(self.main_window)
        popup.grab_set()
        popup.configure(fg_color=self.main_window.BG_MAIN)
        
        ctk.CTkLabel(
            popup,
            text="Presiona una tecla",
            font=self.main_window.font_subtitle,
            text_color=self.main_window.ACCENT
        ).pack(expand=True)
        
        def capture(e):
            key = e.keysym.upper()
            success = self.controller.assign_hotkey(self.sound.id, key)
            
            if not success:
                messagebox.showerror("Error", "Tecla en uso")
            
            popup.destroy()
        
        popup.bind("<KeyPress>", capture)
    
    def _delete(self):
        """Elimina el sonido"""
        if messagebox.askyesno("Eliminar", "¿Borrar este sonido?"):
            self.controller.delete_sound(self.sound.id, delete_file=True)
    
    def _set_image(self):
        """Establece la imagen del sonido"""
        file = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagen", "*.png *.jpg *.jpeg *.gif")]
        )
        if file:
            self.controller.set_sound_image(self.sound.id, file)
    
    def _load_image(self, path: str):
        """Carga y muestra la imagen"""
        try:
            img = Image.open(path).resize((60, 60))
            img_tk = ctk.CTkImage(img, img, size=(60, 60))
            self.image_label.configure(image=img_tk, text="")
            self.image_label.image = img_tk
        except Exception as e:
            print(f"Failed to load image {path}: {e}")
    
    # ==================== UPDATE ====================
    
    def update_from_sound(self, sound: Sound):
        """Actualiza la UI desde el estado del sonido"""
        self.sound = sound
        
        # Actualizar nombre
        self.name_label.configure(text=sound.name.upper())
        
        # Actualizar estado
        status_text = "LOOP" if sound.loop else "READY"
        self.status_label.configure(text=f"0:00 // {status_text}")
        
        # Actualizar botón de loop
        loop_color = self.main_window.SUCCESS if sound.loop else self.main_window.ACCENT_DIM
        self.loop_btn.configure(border_color=loop_color, text_color=loop_color)
        
        # Actualizar hotkey
        hotkey_text = sound.hotkey if sound.hotkey else "KEY"
        self.hotkey_btn.configure(text=hotkey_text)
        
        # Actualizar volumen
        self.volume_percent_label.configure(text=f"{int(sound.volume * 100)}%")
        self._update_volume_visual()
        
        # Actualizar imagen
        if sound.image_path:
            self._load_image(sound.image_path)