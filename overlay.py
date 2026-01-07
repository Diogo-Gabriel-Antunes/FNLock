import customtkinter as ctk
import win32gui
import win32con
import threading

class StatusOverlay:
    def __init__(self):
        self.window = None
        self.label = None
        self.is_visible = False
        
    def show(self):
        if self.is_visible:
            return
            
        # Create window in a separate thread if needed, but for Tkinter it usually runs in main loop.
        # Since main.py already has a root, we can use Toplevel.
        # However, Overlay needs to persist even if main window is hidden.
        # So Toplevel of root is fine.
        pass 

    # Better approach: The Overlay should be part of the main application class or a helper that creates a Toplevel.
    # But to keep it modular, let's define a class that takes the root.

class OverlayManager:
    def __init__(self, root):
        self.root = root
        self.overlay = None
        self.is_active = False

    def show(self):
        if self.overlay and self.overlay.winfo_exists():
            return

        self.overlay = ctk.CTkToplevel(self.root)
        self.overlay.overrideredirect(True) # No title bar
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.7) # Semi-transparent
        
        # Position: Bottom Right
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 150
        height = 40
        x = screen_width - width - 20
        y = screen_height - height - 60 # Above taskbar
        
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        self.overlay.configure(fg_color="#1a1a1a") # Dark background
        
        self.label = ctk.CTkLabel(self.overlay, text="FN LOCK: ON", font=("Arial", 12, "bold"), text_color="#2ECC71")
        self.label.pack(expand=True, fill="both")
        
        # Make click-through
        self._make_click_through()
        
        self.is_active = True

    def hide(self):
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.destroy()
            self.overlay = None
        self.is_active = False

    def update_text(self, text, color):
        if self.overlay and self.overlay.winfo_exists():
            self.label.configure(text=text, text_color=color)

    def _make_click_through(self):
        # Allow window to render but update style to be click-through
        self.overlay.update()
        hwnd = self.overlay.winfo_id() # Get HWND
        
        # Get current style
        try:
            extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        except Exception as e:
            print(f"Error making overlay click-through: {e}")
