import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import json
import os

class AppGUI:
    def __init__(self, root, config, startup_manager, on_toggle_request, on_quit_request, on_mapping_change=None):
        self.root = root
        self.config = config
        self.startup_manager = startup_manager
        self.on_toggle_request = on_toggle_request
        self.on_quit_request = on_quit_request
        self.on_mapping_change = on_mapping_change
        
        self.root.title("FN Lock Simulator")
        self.root.geometry("350x500") # Increased height for profiles
        self.root.resizable(False, False)
        
        # Set Window Icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed to set icon: {e}")
        
        # Configura o fechamento da janela para apenas esconder (minimizar para tray)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self._build_ui()
        self.update_state(self.config.get("fn_lock_active"))

    def _build_ui(self):
        # Container principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- Profile Selector ---
        profile_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        profile_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(profile_frame, text="Perfil:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        
        self.profile_var = ctk.StringVar(value=self.config.get_current_profile_name())
        self.profile_combo = ctk.CTkComboBox(
            profile_frame,
            values=self.config.get_profile_names(),
            variable=self.profile_var,
            command=self._on_profile_change,
            width=150
        )
        self.profile_combo.pack(side="left", fill="x", expand=True)
        
        # Profile Action Button (+)
        add_profile_btn = ctk.CTkButton(
            profile_frame, 
            text="+", 
            width=30, 
            command=self._add_new_profile
        )
        add_profile_btn.pack(side="left", padx=(5, 0))

        # Delete Profile Button (Trash)
        del_profile_btn = ctk.CTkButton(
            profile_frame,
            text="🗑",
            width=30,
            fg_color="#C0392B",
            hover_color="#E74C3C",
            command=self._delete_current_profile
        )
        del_profile_btn.pack(side="left", padx=(5, 0))
        # -----------------------

        # Status Label
        self.status_label = ctk.CTkLabel(main_frame, text="FN LOCK: OFF", font=("Arial", 20, "bold"))
        self.status_label.pack(pady=(10, 20))
        
        # Botão Toggle
        self.toggle_btn = ctk.CTkButton(main_frame, text="ATIVAR", command=self._on_toggle_click, height=40, font=("Arial", 14))
        self.toggle_btn.pack(fill="x", padx=20, pady=10)
        
        # Botão Configurar Teclas
        self.config_btn = ctk.CTkButton(main_frame, text="Configurar Teclas", command=self._open_key_config, height=40, font=("Arial", 14), fg_color="transparent", border_width=2)
        self.config_btn.pack(fill="x", padx=20, pady=10)
        
        # Checkbox Startup
        is_registered = self.startup_manager.is_registered()
        self.startup_check = ctk.CTkCheckBox(
            main_frame, 
            text="Iniciar com o Windows", 
            command=self._on_startup_change
        )
        if is_registered:
            self.startup_check.select()
        self.startup_check.pack(pady=10)
        
        # Checkbox Smart Typing
        self.smart_typing_var = ctk.BooleanVar(value=self.config.get("smart_typing"))
        self.smart_typing_check = ctk.CTkCheckBox(
            main_frame,
            text="Smart Typing (Auto-pause)",
            variable=self.smart_typing_var,
            command=self._on_smart_typing_change
        )
        self.smart_typing_check.pack(pady=10)
        
        # Botão Sair (Totalmente)
        quit_btn = ctk.CTkButton(main_frame, text="Sair do Aplicativo", command=self.on_quit_request, fg_color="#C0392B", hover_color="#E74C3C")
        quit_btn.pack(side="bottom", fill="x", padx=20, pady=20)

    def _on_profile_change(self, choice):
        if self.config.set_active_profile(choice):
            # Refresh UI elements that depend on profile data
            self.smart_typing_var.set(self.config.get("smart_typing"))
            
            # Notify app to reload hooks
            if self.on_mapping_change:
                self.on_mapping_change()

    def _add_new_profile(self):
        dialog = ctk.CTkInputDialog(text="Nome do novo perfil:", title="Novo Perfil")
        new_name = dialog.get_input()
        
        if new_name:
            new_name = new_name.strip()
            if not new_name:
                return
                
            if self.config.create_profile(new_name):
                # Switch to new profile
                self.config.set_active_profile(new_name)
                
                # Update Combo
                self.profile_combo.configure(values=self.config.get_profile_names())
                self.profile_var.set(new_name)
                
                # Trigger update
                self._on_profile_change(new_name)
            else:
                messagebox.showerror("Erro", "Perfil já existe ou nome inválido.")

    def _delete_current_profile(self):
        current = self.profile_var.get()
        if current == "Default":
            messagebox.showinfo("Aviso", "Não é possível deletar o perfil padrão.")
            return
            
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o perfil '{current}'?"):
            if self.config.delete_profile(current):
                # Update Combo (auto switches to Default in config)
                self.profile_combo.configure(values=self.config.get_profile_names())
                self.profile_var.set("Default")
                
                # Trigger update
                self._on_profile_change("Default")

    def _on_toggle_click(self):
        # Solicita a mudança de estado
        current = self.config.get("fn_lock_active")
        self.on_toggle_request(not current)

    def _on_startup_change(self):
        if self.startup_check.get():
            self.startup_manager.register()
        else:
            self.startup_manager.unregister()

    def _on_smart_typing_change(self):
        self.config.set("smart_typing", self.smart_typing_var.get())
        # Notifica se necessário (o hook lerá do config ou podemos forçar update)
        if self.on_mapping_change:
            self.on_mapping_change()

    def update_state(self, is_active):
        """Atualiza a interface com base no estado atual (chamado externamente)."""
        if is_active:
            self.status_label.configure(text="FN LOCK: ON", text_color="#2ECC71") # Green
            self.toggle_btn.configure(text="DESATIVAR", fg_color="#E74C3C", hover_color="#C0392B")
        else:
            self.status_label.configure(text="FN LOCK: OFF", text_color="#E74C3C") # Red
            self.toggle_btn.configure(text="ATIVAR", fg_color="#1f6aa5", hover_color="#144870") # Default blue

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        self.root.withdraw()

    def _open_key_config(self):
        """Abre a janela de configuração de teclas."""
        KeyConfigWindow(self.root, self.config, self.on_mapping_change)


class KeyConfigWindow:
    def __init__(self, parent, config, on_save_callback):
        self.window = ctk.CTkToplevel(parent)
        
        current_profile = config.get_current_profile_name()
        self.window.title(f"Configurar Teclas - {current_profile}")
        
        self.window.geometry("450x650") # Increased height for activation key config
        self.window.attributes("-topmost", True)
        self.config = config
        self.on_save_callback = on_save_callback
        
        # Cópia local do mapa para edição
        self.key_map = self.config.get("key_map").copy()
        
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        # Frame de Input
        input_frame = ctk.CTkFrame(self.window)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(input_frame, text="Origem:").pack(side="left", padx=5)
        self.src_entry = ctk.CTkEntry(input_frame, width=80)
        self.src_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Destino:").pack(side="left", padx=5)
        self.dst_entry = ctk.CTkEntry(input_frame, width=80)
        self.dst_entry.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(input_frame, text="+", width=40, command=self._add_mapping)
        add_btn.pack(side="left", padx=10)
        
        # Lista (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.window, label_text="Mapeamentos Atuais")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Activation Key Config
        activation_frame = ctk.CTkFrame(self.window)
        activation_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(activation_frame, text="Tecla de Ativação:").pack(side="left", padx=10)
        
        self.activation_key_var = ctk.StringVar(value=self.config.get("activation_key") or "right alt")
        self.activation_menu = ctk.CTkOptionMenu(
            activation_frame,
            values=["right alt", "alt gr", "left alt", "right ctrl", "caps lock", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"],
            variable=self.activation_key_var
        )
        self.activation_menu.pack(side="right", padx=10)
        
        # Botões de Import/Export
        io_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        io_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(io_frame, text="Importar JSON", command=self._import_json, width=150).pack(side="left", padx=5)
        ctk.CTkButton(io_frame, text="Exportar JSON", command=self._export_json, width=150).pack(side="right", padx=5)
        
        # Botão Salvar
        ctk.CTkButton(self.window, text="Salvar e Fechar", command=self._save_and_close).pack(pady=20, padx=20, fill="x")

    def _refresh_list(self):
        # Limpa widgets antigos
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Cabeçalho
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="Original", width=100, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="->", width=30).pack(side="left")
        ctk.CTkLabel(header_frame, text="Nova Função", width=100, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        
        # Itens
        for src, dst in self.key_map.items():
            self._create_row(src, dst)

    def _create_row(self, src, dst):
        row = ctk.CTkFrame(self.scroll_frame)
        row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row, text=src, width=100, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text="->", width=30).pack(side="left")
        ctk.CTkLabel(row, text=dst, width=100, anchor="w").pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(row, text="X", width=30, fg_color="#C0392B", hover_color="#E74C3C",
                              command=lambda s=src: self._remove_mapping(s))
        del_btn.pack(side="right", padx=5)

    def _add_mapping(self):
        src = self.src_entry.get().strip().lower()
        dst = self.dst_entry.get().strip().lower()
        
        if not src or not dst:
            return
            
        self.key_map[src] = dst
        self._refresh_list()
        self.src_entry.delete(0, "end")
        self.dst_entry.delete(0, "end")

    def _remove_mapping(self, src):
        if src in self.key_map:
            del self.key_map[src]
            self._refresh_list()

    def _import_json(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.key_map = data
                        self._refresh_list()
                        messagebox.showinfo("Sucesso", "Layout importado com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Formato inválido.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar: {e}")

    def _export_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.key_map, f, indent=4)
                messagebox.showinfo("Sucesso", "Layout exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def _save_and_close(self):
        self.config.set("key_map", self.key_map)
        self.config.set("activation_key", self.activation_key_var.get())
        if self.on_save_callback:
            self.on_save_callback()
        self.window.destroy()
