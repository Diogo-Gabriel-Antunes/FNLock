import keyboard
import threading
import time

class KeyboardHandler:
    def __init__(self, config, on_toggle_callback=None, on_pause_callback=None):
        self.config = config
        self.active = self.config.get("fn_lock_active")
        self.smart_typing = self.config.get("smart_typing")
        
        self.on_toggle_callback = on_toggle_callback
        self.on_pause_callback = on_pause_callback
        
        self.remap_hooks = []
        self.activation_hooks = [] # Store activation hooks to remove them later
        self.key_map = self.config.get("key_map")
        
        # Smart Typing State
        self.paused = False
        self.last_typing_time = 0
        self.running = True
        
        # Monitor Thread for Smart Typing
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Global hook to detect typing
        keyboard.hook(self._global_hook)
        
        # Inicia hooks de ativação
        self._setup_activation_hooks()
        
        # Se já estiver ativo na config, aplica os hooks
        if self.active:
            self._apply_hooks()

    def _setup_activation_hooks(self):
        """Configura os hooks para a tecla de ativação."""
        # Remove old hooks if any
        for hook in self.activation_hooks:
            try:
                keyboard.unhook(hook)
            except:
                pass
        self.activation_hooks.clear()

        activation_key = self.config.get("activation_key")
        if not activation_key:
            activation_key = "right alt"
            
        keys_to_hook = [activation_key]
        
        # Compatibilidade com ABNT2 (Alt Gr muitas vezes é identificado separado)
        if activation_key == "right alt":
            keys_to_hook.append("alt gr")
            
        for key in keys_to_hook:
            try:
                # Usa suppress=False para não bloquear a tecla original (opcional, mas seguro para Alt)
                hook = keyboard.on_release_key(key, self._on_activation_key)
                self.activation_hooks.append(hook)
            except Exception as e:
                print(f"Aviso: Não foi possível hookar a tecla '{key}': {e}")

    def _on_activation_key(self, event):
        self.toggle()

    def _global_hook(self, event):
        """Detecta digitação para o Smart Typing."""
        if event.event_type == keyboard.KEY_DOWN:
            # Ignora teclas modificadoras e a própria tecla de ativação
            ignored_keys = ['right alt', 'alt', 'ctrl', 'shift', 'caps lock', 'alt gr', 'left alt', 'right ctrl', 'left ctrl']
            
            # Adiciona a tecla de ativação atual à lista de ignorados
            current_activation = self.config.get("activation_key")
            if current_activation and current_activation not in ignored_keys:
                ignored_keys.append(current_activation)

            if event.name.lower() in ignored_keys:
                return

            # Se for uma tecla mapeada, e o lock estiver ATIVO e NÃO PAUSADO, ignoramos (é remapeamento)
            # Mas se estiver pausado, é digitação normal.
            is_mapped = event.name.lower() in self.key_map
            
            if not is_mapped:
                # É uma tecla de digitação (não mapeada)
                self.last_typing_time = time.time()
                
                if self.active and self.smart_typing and not self.paused:
                    self.paused = True
                    self._remove_hooks()
                    if self.on_pause_callback:
                        self.on_pause_callback(True)
                        
            elif is_mapped and self.paused:
                # Se é uma tecla mapeada, MAS estamos pausados, conta como digitação contínua
                # Ex: estou digitando "water", o 'w' é mapeado, mas como estou pausado, ele é texto.
                self.last_typing_time = time.time()

    def _monitor_loop(self):
        """Verifica se deve retomar o bloqueio após pausa."""
        while self.running:
            if self.paused and self.active:
                if time.time() - self.last_typing_time > 1.0: # 1 segundo de silêncio
                    self.paused = False
                    self._apply_hooks()
                    if self.on_pause_callback:
                        self.on_pause_callback(False)
            time.sleep(0.1)

    def toggle(self):
        self.active = not self.active
        self.config.set("fn_lock_active", self.active)
        self.paused = False # Reset pause on toggle
        
        if self.active:
            self._apply_hooks()
        else:
            self._remove_hooks()
            
        if self.on_toggle_callback:
            self.on_toggle_callback(self.active)
            
        # Ensure pause state is cleared in UI
        if self.on_pause_callback:
            self.on_pause_callback(False)

    def set_state(self, state):
        if self.active != state:
            self.toggle()

    def update_config(self):
        """Recarrega configurações (mapeamento e smart typing)."""
        was_active = self.active
        
        if was_active:
            self._remove_hooks()
            
        self.key_map = self.config.get("key_map")
        self.smart_typing = self.config.get("smart_typing")
        
        # Atualiza hooks de ativação também
        self._setup_activation_hooks()
        
        if was_active:
            self._apply_hooks()

    def _apply_hooks(self):
        if self.remap_hooks:
            return

        try:
            for src, dst in self.key_map.items():
                hook = keyboard.on_press_key(src, self._make_callback(dst), suppress=True)
                self.remap_hooks.append(hook)
        except Exception as e:
            print(f"Erro ao aplicar hooks: {e}")

    def _make_callback(self, dst_key):
        return lambda e: keyboard.send(dst_key)

    def _remove_hooks(self):
        for hook in self.remap_hooks:
            keyboard.unhook(hook)
        self.remap_hooks.clear()

    def stop(self):
        self.running = False
        self._remove_hooks()
        # Remove activation hooks
        for hook in self.activation_hooks:
            try:
                keyboard.unhook(hook)
            except:
                pass
        keyboard.unhook_all()
