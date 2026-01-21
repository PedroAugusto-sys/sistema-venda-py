import customtkinter as ctk

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "yellow": "#ffa502",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

class AlertDialog(ctk.CTkToplevel):
    """Diálogo estilizado de alerta/atenção"""
    
    def __init__(self, parent, title, message, alert_type="warning", show_back_button=False, on_ok_callback=None):
        super().__init__(parent)
        
        self.result = None
        self.show_back_button = show_back_button
        self.on_ok_callback = on_ok_callback  # Callback opcional quando OK é clicado
        
        self.title(title)
        self.resizable(False, False)
        
        self.dialog_width = 520 if show_back_button else 450  # Largura maior se houver dois botões
        
        # Centralizar janela na tela
        self.transient(parent)
        self.grab_set()
        
        # Definir geometria inicial (será ajustada após criar widgets)
        self.geometry(f"{self.dialog_width}x400")
        
        # Configurar tema
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Frame principal com padding adequado
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Determinar cor do ícone e tipo
        if alert_type == "error":
            icon_color = COLORS["red"]
            icon_text = "✕"
        elif alert_type == "info":
            icon_color = COLORS["green"]
            icon_text = "ℹ"
        else:  # warning
            icon_color = COLORS["yellow"]
            icon_text = "!"
        
        # Ícone
        icon_label = ctk.CTkLabel(
            main_frame,
            text=icon_text,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=icon_color
        )
        icon_label.pack(pady=(20, 10))
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_light"]
        )
        title_label.pack(pady=(0, 15))
        
        # Mensagem - usar CTkTextbox para mensagens longas ou CTkLabel para curtas
        # Calcular quantas linhas aproximadamente a mensagem terá
        lines = message.count('\n') + 1
        # Estimar largura de texto (aproximadamente 50 caracteres por linha com wraplength)
        char_per_line = 50
        estimated_lines = max(lines, len(message) // char_per_line + 1)
        
        # Se a mensagem for muito longa (mais de 6 linhas estimadas) ou tiver caminhos longos, usar Textbox scrollável
        # Caminhos longos (mais de 80 caracteres) sempre usam textbox
        has_long_path = len(message) > 80 and ('/' in message or '\\' in message)
        
        if estimated_lines > 6 or has_long_path:
            message_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            message_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
            # Calcular altura adequada para o textbox
            textbox_height = min(max(100, estimated_lines * 18), 200)
            
            message_textbox = ctk.CTkTextbox(
                message_frame,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_gray"],
                fg_color=COLORS["bg_dark"],
                wrap="word",
                height=textbox_height,
                corner_radius=10,
                border_width=1,
                border_color="#3a3a3a"
            )
            message_textbox.pack(fill="both", expand=True)
            message_textbox.insert("1.0", message)
            message_textbox.configure(state="disabled")
            
            # Armazenar referência para uso no ajuste de altura
            self.message_widget = message_textbox
        else:
            message_label = ctk.CTkLabel(
                main_frame,
                text=message,
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_gray"],
                wraplength=self.dialog_width - 100,
                justify="center"
            )
            message_label.pack(pady=(0, 15), padx=20)
            self.message_widget = message_label
        
        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=30, pady=(20, 25))
        buttons_frame.grid_columnconfigure(0, weight=1)
        if self.show_back_button:
            buttons_frame.grid_columnconfigure(1, weight=1)
        
        if self.show_back_button:
            # Modo com dois botões: Voltar ao Carrinho e OK
            back_btn = ctk.CTkButton(
                buttons_frame,
                text="← Voltar ao Carrinho",
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=10,
                height=45,
                fg_color=COLORS["bg_panel"],
                hover_color="#333333",
                command=self.back_action,
                width=180
            )
            back_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            
            ok_btn = ctk.CTkButton(
                buttons_frame,
                text="OK",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=10,
                height=45,
                fg_color=COLORS["green"],
                hover_color="#26c463",
                command=self.ok_action,
                width=150
            )
            ok_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
            
            # Focar no botão Voltar
            back_btn.focus()
        else:
            # Modo simples: apenas OK
            ok_btn = ctk.CTkButton(
                buttons_frame,
                text="OK",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=10,
                height=45,
                fg_color=COLORS["green"],
                hover_color="#26c463",
                command=self.ok_action,
                width=150
            )
            ok_btn.grid(row=0, column=0, sticky="", padx=0)
            
            # Focar no botão OK
            ok_btn.focus()
        
        # Bind Enter para OK e Escape para voltar (se houver botão de voltar)
        self.bind("<Return>", lambda e: self.ok_action())
        if self.show_back_button:
            self.bind("<Escape>", lambda e: self.back_action())
        else:
            self.bind("<Escape>", lambda e: self.ok_action())
        
        # Ajustar tamanho após todos os widgets serem criados
        self.after(100, self._adjust_and_center)
    
    def _adjust_and_center(self):
        """Ajusta o tamanho da janela baseado no conteúdo e centraliza"""
        self.update_idletasks()
        
        # Forçar atualização de layout completo
        self.update()
        self.update_idletasks()
        
        # Obter dimensões reais requeridas pelo conteúdo
        required_height = self.winfo_reqheight()
        
        # Se há widget de mensagem (textbox), verificar sua altura necessária
        if hasattr(self, 'message_widget'):
            try:
                self.update_idletasks()
                msg_height = self.message_widget.winfo_reqheight()
                # Se a mensagem requer muito espaço, ajustar
                if msg_height > 150:
                    required_height += (msg_height - 150)
            except:
                pass
        
        # Adicionar espaço extra para garantir que o botão não seja cortado
        # Mais espaço se houver botão de voltar
        extra_padding = 50 if self.show_back_button else 40
        min_height = max(360, required_height + extra_padding)
        
        # Garantir altura mínima para botões não serem cortados
        if self.show_back_button:
            min_height = max(400, min_height)  # Mais espaço para dois botões
        else:
            min_height = max(380, min_height)  # Mais espaço para garantir visibilidade do botão
        
        # Limitar altura máxima para não ultrapassar a tela
        screen_height = self.winfo_screenheight()
        max_height = screen_height - 100  # Deixar margem de 50px em cada lado
        dialog_height = min(min_height, max_height)
        
        # Atualizar geometria
        self.geometry(f"{self.dialog_width}x{dialog_height}")
        
        # Centralizar na tela após ajuste
        self.update_idletasks()
        self._center_on_screen()
    
    def _center_on_screen(self):
        """Centraliza a janela no centro da tela"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Desabilitar movimento da janela (tornar não arrastável temporariamente)
        # Isso faz com que a janela apareça no centro e não possa ser facilmente movida
        try:
            # Tornar topmost brevemente para garantir que apareça no centro
            self.attributes('-topmost', True)
            self.after(50, lambda: self.attributes('-topmost', False))
        except:
            pass
    
    def ok_action(self):
        """Ação quando clica em OK"""
        self.result = True
        # Executar callback se fornecido
        if self.on_ok_callback:
            try:
                self.on_ok_callback()
            except Exception as e:
                print(f"Erro ao executar callback: {e}")
        self.destroy()
    
    def back_action(self):
        """Ação quando clica em Voltar ao Carrinho"""
        self.result = "back"
        self.destroy()
