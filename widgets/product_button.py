import customtkinter as ctk
from PIL import Image, ImageTk
import os

class ProductCard(ctk.CTkFrame):
    """Card de produto moderno com CustomTkinter"""
    
    def __init__(self, parent, name, price, icon="📦", image_path=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.name = name
        self.price = price
        self.icon = icon
        self.selected = False
        
        # Configuração do card
        self.configure(
            corner_radius=15,
            fg_color=("#2b2b2b", "#2b2b2b"),
            border_width=2,
            border_color=("#2b2b2b", "#2b2b2b")
        )
        
        # Layout interno - responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Imagem expande
        self.grid_rowconfigure(1, weight=0)  # Nome fixo
        self.grid_rowconfigure(2, weight=0)  # Preço fixo
        
        # Ícone do produto (emoji ou imagem)
        self.image_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=48),
            anchor="center"
        )
        self.image_label.grid(row=0, column=0, pady=(15, 10), padx=15, sticky="nsew")
        
        # Nome do produto (sem wraplength fixo para ser responsivo)
        self.name_label = ctk.CTkLabel(
            self,
            text=name,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=200  # Ajustado para ser mais flexível
        )
        self.name_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        
        # Preço
        self.price_label = ctk.CTkLabel(
            self,
            text=f"R$ {price:.2f}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2ed573"
        )
        self.price_label.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="ew")
        
        # Bind para hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Bind para todos os widgets filhos
        for widget in [self.image_label, self.name_label, self.price_label]:
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Efeito hover ao passar o mouse"""
        if not self.selected:
            self.configure(border_color="#2ed573")
    
    def on_leave(self, event):
        """Remove efeito hover ao sair do mouse"""
        if not self.selected:
            self.configure(border_color=("#2b2b2b", "#2b2b2b"))
    
    def select(self):
        """Marca o card como selecionado"""
        self.selected = True
        self.configure(border_color="#2ed573", border_width=3)
    
    def deselect(self):
        """Remove seleção do card"""
        self.selected = False
        self.configure(border_color=("#2b2b2b", "#2b2b2b"), border_width=2)
