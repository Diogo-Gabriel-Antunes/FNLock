import sys
import tkinter as tk
import customtkinter as ctk
import threading
import time

from config import Config
from utils import StartupManager
from keyboard_hook import KeyboardHandler
from gui import AppGUI
from tray import TrayIcon
from overlay import OverlayManager

class MainApp:
    def __init__(self):
        self.config = Config()
        self.startup_manager = StartupManager()
        
        # Configuração global do CustomTkinter
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Inicializa a raiz do CustomTkinter
        self.root = ctk.CTk()
        
        # Overlay Manager
        self.overlay = OverlayManager(self.root)
        
        # Callbacks centrais
        self.keyboard_handler = KeyboardHandler(
            self.config, 
            on_toggle_callback=self.on_state_change_from_keyboard,
            on_pause_callback=self.on_pause_change_from_keyboard
        )
        
        self.tray = TrayIcon(
            on_toggle_request=self.toggle_state,
            on_open_request=self.open_gui,
            on_quit_request=self.quit_app
        )
        
        self.gui = AppGUI(
            self.root, 
            self.config, 
            self.startup_manager, 
            on_toggle_request=self.toggle_state,
            on_quit_request=self.quit_app,
            on_mapping_change=self.reload_mapping
        )

        # Sincroniza estado inicial
        initial_state = self.config.get("fn_lock_active")
        self.tray.update_state(initial_state)
        self.update_overlay(initial_state, False)
        
    def start(self):
        # Inicia Tray em thread
        self.tray.start_thread()
        
        # Verifica argumentos de linha de comando para iniciar minimizado
        start_minimized = "--minimized" in sys.argv or self.config.get("start_minimized")
        
        if start_minimized:
            self.gui.hide_window()
        else:
            self.gui.show_window()
            
        # Inicia loop do Tkinter (Bloqueante)
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()

    def toggle_state(self, new_state):
        """Chamado pela GUI ou Tray para mudar o estado."""
        self.keyboard_handler.set_state(new_state)
        self.update_all_uis(new_state)

    def on_state_change_from_keyboard(self, new_state):
        """Callback vindo do KeyboardHook (ex: Right Alt pressionado)."""
        self.root.after(0, lambda: self.update_all_uis(new_state))

    def on_pause_change_from_keyboard(self, is_paused):
        """Callback quando o Smart Typing pausa/resume."""
        is_active = self.keyboard_handler.active
        self.root.after(0, lambda: self.update_overlay(is_active, is_paused))
        # Atualiza Tooltip do Tray também
        status_text = "FN Lock: PAUSADO" if is_paused else ("FN Lock: ATIVO" if is_active else "FN Lock: OFF")
        self.tray.update_tooltip(status_text)

    def update_all_uis(self, is_active):
        self.gui.update_state(is_active)
        self.tray.update_state(is_active)
        self.update_overlay(is_active, False)

    def update_overlay(self, is_active, is_paused):
        if not is_active:
            self.overlay.hide()
        else:
            if is_paused:
                self.overlay.show()
                self.overlay.update_text("FN LOCK: PAUSED", "#F1C40F") # Yellow
            else:
                self.overlay.show()
                self.overlay.update_text("FN LOCK: ON", "#2ECC71") # Green

    def open_gui(self):
        self.root.after(0, self.gui.show_window)

    def reload_mapping(self):
        self.keyboard_handler.update_config()

    def quit_app(self):
        self.keyboard_handler.stop()
        self.tray.stop()
        self.root.quit()
        sys.exit(0)

if __name__ == "__main__":
    app = MainApp()
    app.start()
