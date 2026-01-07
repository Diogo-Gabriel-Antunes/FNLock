import json
import os

CONFIG_FILE = "settings.json"

class Config:
    PROFILE_SPECIFIC_KEYS = ['key_map', 'smart_typing', 'activation_key']

    def __init__(self):
        # Configuração base padrão
        self.default_profile_data = {
            "smart_typing": False,
            "activation_key": "right alt",
            "key_map": {
                'w': 'up',
                'a': 'left',
                's': 'down',
                'd': 'right'
            }
        }
        
        self.default_config = {
            "fn_lock_active": False,
            "start_minimized": False,
            "run_on_startup": False,
            "current_profile": "Default",
            "profiles": {
                "Default": self.default_profile_data.copy()
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """Carrega as configurações do arquivo JSON com migração automática."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    
                # Verifica se precisa de migração (se não tem a chave 'profiles')
                if "profiles" not in data:
                    print("Migrando configuração antiga para sistema de perfis...")
                    migrated_config = self.default_config.copy()
                    
                    # Copia configurações globais
                    migrated_config["fn_lock_active"] = data.get("fn_lock_active", False)
                    migrated_config["start_minimized"] = data.get("start_minimized", False)
                    migrated_config["run_on_startup"] = data.get("run_on_startup", False)
                    
                    # Cria o perfil Default com os dados antigos
                    default_profile = {
                        "key_map": data.get("key_map", self.default_profile_data["key_map"]),
                        "smart_typing": data.get("smart_typing", self.default_profile_data["smart_typing"]),
                        "activation_key": data.get("activation_key", self.default_profile_data["activation_key"])
                    }
                    migrated_config["profiles"]["Default"] = default_profile
                    
                    return migrated_config
                
                # Merge seguro com default (para novos campos)
                return {**self.default_config, **data}
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
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
        """Obtém um valor. Se for específico de perfil, pega do perfil atual."""
        if key in self.PROFILE_SPECIFIC_KEYS:
            current_profile = self.config.get("current_profile", "Default")
            profiles = self.config.get("profiles", {})
            profile_data = profiles.get(current_profile, self.default_profile_data)
            return profile_data.get(key, self.default_profile_data.get(key))
        
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        """Define um valor. Se for específico de perfil, salva no perfil atual."""
        if key in self.PROFILE_SPECIFIC_KEYS:
            current_profile = self.config.get("current_profile", "Default")
            if current_profile not in self.config["profiles"]:
                self.config["profiles"][current_profile] = self.default_profile_data.copy()
            self.config["profiles"][current_profile][key] = value
        else:
            self.config[key] = value
        self.save_config()

    # Métodos de Gerenciamento de Perfil

    def get_profile_names(self):
        return list(self.config["profiles"].keys())

    def get_current_profile_name(self):
        return self.config.get("current_profile", "Default")

    def create_profile(self, name):
        if name in self.config["profiles"]:
            return False # Já existe
        # Cria cópia do perfil padrão ou vazio
        self.config["profiles"][name] = self.default_profile_data.copy()
        self.save_config()
        return True

    def delete_profile(self, name):
        if name == "Default":
            return False # Não pode deletar o padrão
        if name in self.config["profiles"]:
            del self.config["profiles"][name]
            # Se deletou o atual, volta para Default
            if self.config["current_profile"] == name:
                self.config["current_profile"] = "Default"
            self.save_config()
            return True
        return False

    def set_active_profile(self, name):
        if name in self.config["profiles"]:
            self.config["current_profile"] = name
            self.save_config()
            return True
        return False
