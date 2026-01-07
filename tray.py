import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading

class TrayIcon:
    def __init__(self, on_toggle_request, on_open_request, on_quit_request):
        self.on_toggle_request = on_toggle_request
        self.on_open_request = on_open_request
        self.on_quit_request = on_quit_request
        self.icon = None
        self.is_active = False

    def create_image(self, active):
        """Gera um ícone dinâmico (Quadrado Verde = ON, Vermelho = OFF)."""
        width = 64
        height = 64
        color = "#2ECC71" if active else "#E74C3C" # Green / Red matching GUI
        
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        dc = ImageDraw.Draw(image)
        
        # Desenha um retângulo colorido
        dc.rectangle(
            (0, 0, width, height),
            fill=color
        )
        
        return image

    def update_state(self, is_active):
        self.is_active = is_active
        if self.icon:
            self.icon.icon = self.create_image(is_active)
            self.icon.title = "FN Lock: ATIVO" if is_active else "FN Lock: INATIVO"

    def update_tooltip(self, text):
        if self.icon:
            self.icon.title = text

    def _on_toggle_click(self, icon, item):
        self.on_toggle_request(not self.is_active)

    def _on_open_click(self, icon, item):
        self.on_open_request()

    def _on_quit_click(self, icon, item):
        self.on_quit_request()

    def setup_menu(self):
        return pystray.Menu(
            item('Abrir Interface', self._on_open_click, default=True),
            item(lambda text: 'Desativar FN Lock' if self.is_active else 'Ativar FN Lock', self._on_toggle_click),
            item('Sair', self._on_quit_click)
        )

    def run(self):
        """Inicia o ícone da bandeja (bloqueante, deve rodar em thread separada)."""
        self.icon = pystray.Icon(
            "FNLock", 
            self.create_image(self.is_active), 
            "FN Lock: ATIVO" if self.is_active else "FN Lock: INATIVO", 
            menu=self.setup_menu()
        )
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def start_thread(self):
        """Helper para iniciar em thread separada."""
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
