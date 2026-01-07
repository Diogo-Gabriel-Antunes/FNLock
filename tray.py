import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import os
import sys

class TrayIcon:
    def __init__(self, on_toggle_request, on_open_request, on_quit_request):
        self.on_toggle_request = on_toggle_request
        self.on_open_request = on_open_request
        self.on_quit_request = on_quit_request
        self.icon = None
        self.is_active = False
        
        # Carrega o ícone personalizado
        self.custom_icon_path = self._get_resource_path("icon.png")
        self.has_custom_icon = os.path.exists(self.custom_icon_path)

    def _get_resource_path(self, relative_path):
        """Obtém o caminho absoluto para recursos, compatível com PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def create_image(self, active):
        """Retorna o ícone do app, com um indicador de estado se possível."""
        if self.has_custom_icon:
            try:
                # Carrega o ícone original
                base_img = Image.open(self.custom_icon_path).convert("RGBA")
                
                # Cria um indicador de estado (círculo colorido no canto)
                width, height = base_img.size
                indicator_size = width // 3
                
                # Camada para o indicador
                overlay = Image.new('RGBA', (width, height), (0,0,0,0))
                draw = ImageDraw.Draw(overlay)
                
                # Cor do estado (Verde = ON, Vermelho = OFF)
                color = "#2ECC71" if active else "#E74C3C"
                
                # Desenha círculo no canto inferior direito
                margin = 2
                x0 = width - indicator_size - margin
                y0 = height - indicator_size - margin
                x1 = width - margin
                y1 = height - margin
                
                draw.ellipse([x0, y0, x1, y1], fill=color, outline="white", width=1)
                
                # Combina
                return Image.alpha_composite(base_img, overlay)
                
            except Exception as e:
                print(f"Erro ao carregar ícone personalizado: {e}")
                
        # Fallback para o quadrado colorido antigo
        width = 64
        height = 64
        color = "#2ECC71" if active else "#E74C3C"
        
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, width, height), fill=color)
        
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
