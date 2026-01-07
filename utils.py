import sys
import os
import win32com.client

class StartupManager:
    def __init__(self, app_name="FNLockSimulator"):
        self.app_name = app_name
        self.shortcut_path = os.path.join(
            os.getenv('APPDATA'), 
            r'Microsoft\Windows\Start Menu\Programs\Startup', 
            f'{self.app_name}.lnk'
        )

    def is_registered(self):
        """Verifica se o atalho existe na pasta de inicialização."""
        return os.path.exists(self.shortcut_path)

    def register(self):
        """Cria um atalho na pasta de inicialização."""
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(self.shortcut_path)
            # Aponta para o executável python ou o script se estiver rodando via interpretador
            # Se for um executável compilado (exe), sys.executable é o caminho.
            # Se for script, precisamos chamar o pythonw.exe com o script.
            
            target = sys.executable
            
            # Se estiver rodando como script .py
            if not target.endswith('.exe'):
                 # Fallback improvável em ambiente normal, mas por segurança
                 target = sys.executable 

            shortcut.TargetPath = target
            
            # Se não estiver 'frozen' (compilado com pyinstaller), adiciona o script como argumento
            if not getattr(sys, 'frozen', False):
                # Usa pythonw.exe para não abrir console se possível, mas sys.executable geralmente é python.exe
                # O ideal para production é usar pythonw.exe
                if "python.exe" in target:
                    shortcut.TargetPath = target.replace("python.exe", "pythonw.exe")
                
                # Assume que o main.py está no diretório atual
                main_script = os.path.abspath("main.py")
                shortcut.Arguments = f'"{main_script}" --minimized'
            else:
                shortcut.Arguments = "--minimized"
                
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
            shortcut.IconLocation = target
            shortcut.save()
            return True
        except Exception as e:
            print(f"Erro ao registrar startup: {e}")
            return False

    def unregister(self):
        """Remove o atalho da pasta de inicialização."""
        try:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
            return True
        except Exception as e:
            print(f"Erro ao remover startup: {e}")
            return False
