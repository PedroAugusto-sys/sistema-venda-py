import customtkinter as ctk
import os

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

class ConfirmationDialog(ctk.CTkToplevel):
    """Diálogo estilizado de confirmação de venda finalizada"""
    
    def __init__(self, parent, client_name, total, payment_method):
        super().__init__(parent)
        
        self.result = None
        
        self.title("Venda Finalizada")
        self.resizable(False, False)
        
        # Centralizar janela na tela
        self.transient(parent)
        self.grab_set()
        
        # Configurar tema
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Centralizar na tela após widgets serem criados
        self.after(100, self._center_on_screen)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Ícone de sucesso (emoji ou texto)
        icon_label = ctk.CTkLabel(
            main_frame,
            text="✓",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=COLORS["green"]
        )
        icon_label.pack(pady=(20, 10))
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Venda Finalizada",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_light"]
        )
        title_label.pack(pady=(0, 20))
        
        # Informações da venda
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Cliente
        client_label = ctk.CTkLabel(
            info_frame,
            text=f"Cliente: {client_name}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_gray"]
        )
        client_label.pack(anchor="w", pady=5)
        
        # Total
        total_label = ctk.CTkLabel(
            info_frame,
            text=f"Total: R$ {total:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["green"]
        )
        total_label.pack(anchor="w", pady=5)
        
        # Método de pagamento
        method_label = ctk.CTkLabel(
            info_frame,
            text=f"Método: {payment_method}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_gray"]
        )
        method_label.pack(anchor="w", pady=5)
        
        # Botões - Posicionar no final do modal para garantir visibilidade
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", side="bottom", padx=30, pady=(15, 25))
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Botão Emitir Comprovante
        receipt_btn = ctk.CTkButton(
            buttons_frame,
            text="📄 Emitir Comprovante",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=45,
            fg_color=COLORS["bg_panel"],
            hover_color="#333333",
            command=self.emit_receipt_action
        )
        receipt_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Botão Finalizar
        finish_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ Finalizar",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=10,
            height=45,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.finish_action
        )
        finish_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Focar no botão Finalizar
        finish_btn.focus()
        
        # Bind Enter para Finalizar e Escape para Finalizar também
        self.bind("<Return>", lambda e: self.finish_action())
        self.bind("<Escape>", lambda e: self.finish_action())
        
        # Definir geometria inicial antes de centralizar - Altura aumentada para garantir visibilidade dos botões
        self.geometry("500x420")
    
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
        
        # Desabilitar movimento da janela (tornar não arrastável)
        # Em CustomTkinter, podemos fazer isso removendo a barra de título ou usando protocol
        try:
            # Tentar remover a capacidade de arrastar (funciona no Windows)
            self.attributes('-topmost', True)
            self.after(50, lambda: self.attributes('-topmost', False))
        except:
            pass
    
    def emit_receipt_action(self):
        """Ação quando clica em Emitir Comprovante"""
        self.result = True
        self.destroy()
    
    def finish_action(self):
        """Ação quando clica em Finalizar"""
        self.result = False
        self.destroy()
