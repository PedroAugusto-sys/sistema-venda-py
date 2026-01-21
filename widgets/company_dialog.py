import customtkinter as ctk
from tkinter import messagebox
import re

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

def format_cnpj(event=None):
    """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
    widget = event.widget if event else None
    if not widget:
        return
    
    # Obter texto atual e remover formatação
    text = widget.get().replace('.', '').replace('/', '').replace('-', '')
    # Manter apenas números
    text = re.sub(r'\D', '', text)
    
    # Limitar a 14 dígitos
    if len(text) > 14:
        text = text[:14]
    
    # Aplicar formatação
    if len(text) <= 2:
        formatted = text
    elif len(text) <= 5:
        formatted = f"{text[:2]}.{text[2:]}"
    elif len(text) <= 8:
        formatted = f"{text[:2]}.{text[2:5]}.{text[5:]}"
    elif len(text) <= 12:
        formatted = f"{text[:2]}.{text[2:5]}.{text[5:8]}/{text[8:]}"
    else:
        formatted = f"{text[:2]}.{text[2:5]}.{text[5:8]}/{text[8:12]}-{text[12:]}"
    
    # Atualizar campo
    cursor_pos = widget.index(ctk.INSERT)
    widget.delete(0, ctk.END)
    widget.insert(0, formatted)
    
    # Reposicionar cursor
    new_pos = min(cursor_pos, len(formatted))
    widget.icursor(new_pos)

def format_phone(event=None):
    """Formata telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
    widget = event.widget if event else None
    if not widget:
        return
    
    # Obter texto atual e remover formatação
    text = widget.get().replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
    # Manter apenas números
    text = re.sub(r'\D', '', text)
    
    # Limitar a 11 dígitos (DDD + 9 dígitos ou DDD + 8 dígitos)
    if len(text) > 11:
        text = text[:11]
    
    # Aplicar formatação
    if len(text) == 0:
        formatted = ""
    elif len(text) <= 2:
        formatted = f"({text}"
    elif len(text) <= 6:
        # Telefone fixo: (XX) XXXX
        formatted = f"({text[:2]}) {text[2:]}"
    elif len(text) <= 10:
        # Telefone fixo: (XX) XXXX-XXXX
        formatted = f"({text[:2]}) {text[2:6]}-{text[6:]}"
    else:
        # Celular: (XX) XXXXX-XXXX
        formatted = f"({text[:2]}) {text[2:7]}-{text[7:]}"
    
    # Atualizar campo
    cursor_pos = widget.index(ctk.INSERT)
    widget.delete(0, ctk.END)
    widget.insert(0, formatted)
    
    # Reposicionar cursor
    new_pos = min(cursor_pos + 1 if cursor_pos < len(formatted) else cursor_pos, len(formatted))
    widget.icursor(new_pos)

class CompanyDialog(ctk.CTkToplevel):
    """Diálogo para editar informações da empresa"""
    
    def __init__(self, parent, company_data):
        super().__init__(parent)
        
        self.company_data = company_data.copy() if company_data else {}
        self.result = None
        
        self.title("Editar Informações da Empresa")
        self.resizable(False, False)
        
        # Centralizar janela
        self.transient(parent)
        self.grab_set()
        
        # Configurar tema
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Definir geometria inicial e centralizar na tela
        self.geometry("500x420")
        self.after(100, self._center_on_screen)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Informações da Empresa",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_light"]
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))
        
        # Nome da Empresa
        name_label = ctk.CTkLabel(
            main_frame,
            text="Nome:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"]
        )
        name_label.grid(row=1, column=0, sticky="w", padx=(20, 10), pady=10)
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            border_color="#3a3a3a",
            text_color=COLORS["text_light"]
        )
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=10)
        self.name_entry.insert(0, self.company_data.get("name", "Cantina Colégio Ativa"))
        
        # CNPJ
        cnpj_label = ctk.CTkLabel(
            main_frame,
            text="CNPJ:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"]
        )
        cnpj_label.grid(row=2, column=0, sticky="w", padx=(20, 10), pady=10)
        
        self.cnpj_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            border_color="#3a3a3a",
            text_color=COLORS["text_light"],
            placeholder_text="00.000.000/0001-00"
        )
        self.cnpj_entry.grid(row=2, column=1, sticky="ew", padx=(0, 20), pady=10)
        # Bind formatação automática
        self.cnpj_entry.bind("<KeyRelease>", format_cnpj)
        self.cnpj_entry.bind("<FocusOut>", format_cnpj)
        # Carregar e formatar valor existente
        cnpj_value = self.company_data.get("cnpj", "")
        if cnpj_value:
            # Remover formatação existente se houver e inserir apenas números
            cnpj_clean = re.sub(r'\D', '', str(cnpj_value))
            if cnpj_clean:
                self.cnpj_entry.insert(0, cnpj_clean)
                # Aplicar formatação após inserção
                self.after(50, lambda: self._format_cnpj_field())
        
        # Telefone
        phone_label = ctk.CTkLabel(
            main_frame,
            text="Telefone:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"]
        )
        phone_label.grid(row=3, column=0, sticky="w", padx=(20, 10), pady=10)
        
        self.phone_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            border_color="#3a3a3a",
            text_color=COLORS["text_light"],
            placeholder_text="(00) 0000-0000"
        )
        self.phone_entry.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=10)
        # Bind formatação automática
        self.phone_entry.bind("<KeyRelease>", format_phone)
        self.phone_entry.bind("<FocusOut>", format_phone)
        # Carregar e formatar valor existente
        phone_value = self.company_data.get("phone", "")
        if phone_value:
            # Remover formatação existente se houver e inserir apenas números
            phone_clean = re.sub(r'\D', '', str(phone_value))
            if phone_clean:
                self.phone_entry.insert(0, phone_clean)
                # Aplicar formatação após inserção
                self.after(50, lambda: self._format_phone_field())
        
        # Endereço (opcional, mas útil)
        address_label = ctk.CTkLabel(
            main_frame,
            text="Endereço:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_light"]
        )
        address_label.grid(row=4, column=0, sticky="w", padx=(20, 10), pady=10)
        
        self.address_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            border_color="#3a3a3a",
            text_color=COLORS["text_light"],
            placeholder_text="Endereço da empresa"
        )
        self.address_entry.grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=10)
        self.address_entry.insert(0, self.company_data.get("address", ""))
        
        # Botões
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(20, 20))
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(20, 5))
        
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Salvar",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.save
        )
        save_btn.grid(row=0, column=1, sticky="ew", padx=(5, 20))
        
        # Focar no primeiro campo
        self.name_entry.focus()
        
        # Bind Enter para salvar
        self.bind("<Return>", lambda e: self.save())
        self.bind("<Escape>", lambda e: self.cancel())
    
    def _format_cnpj_field(self):
        """Formata o campo CNPJ manualmente"""
        class FakeEvent:
            def __init__(self, widget):
                self.widget = widget
        format_cnpj(FakeEvent(self.cnpj_entry))
    
    def _format_phone_field(self):
        """Formata o campo Telefone manualmente"""
        class FakeEvent:
            def __init__(self, widget):
                self.widget = widget
        format_phone(FakeEvent(self.phone_entry))
    
    def save(self):
        """Salva as informações"""
        name = self.name_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Atenção", "O nome da empresa é obrigatório!")
            return
        
        # Obter valores formatados (mantendo apenas números para CNPJ e Telefone)
        cnpj = re.sub(r'\D', '', self.cnpj_entry.get().strip())
        phone = self.phone_entry.get().strip()  # Manter formatação do telefone
        
        self.result = {
            "name": name,
            "cnpj": cnpj,  # Salvar apenas números do CNPJ
            "phone": phone,  # Salvar telefone formatado
            "address": self.address_entry.get().strip()
        }
        
        self.destroy()
    
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
        
        # Desabilitar movimento da janela temporariamente
        try:
            self.attributes('-topmost', True)
            self.after(50, lambda: self.attributes('-topmost', False))
        except:
            pass
    
    def cancel(self):
        """Cancela a edição"""
        self.result = None
        self.destroy()
