import json
import os

CONFIG_FILE = "settings.json"

class Config:
    def __init__(self):
        self.default_config = {
            "fn_lock_active": False,
            "start_minimized": False,
            "run_on_startup": False,
            "smart_typing": False,
            "activation_key": "right alt",
            "key_map": {
                'w': 'up',
                'a': 'left',
                's': 'down',
                'd': 'right'
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """Carrega as configurações do arquivo JSON."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return {**self.default_config, **json.load(f)}
            except Exception:
                return self.default_config
        return self.default_config

    def save_config(self):
        """Salva as configurações atuais no arquivo JSON."""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
