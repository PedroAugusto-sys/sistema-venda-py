import customtkinter as ctk
from PIL import Image, ImageTk
import os
import hashlib

# Cores por categoria (geradas de forma determinística mas variadas)
CATEGORY_COLORS = {
    "Salgados": ["#3a5f7a", "#4a6b8a", "#5a7b9a", "#6a8baa", "#7a9bba"],
    "Doces": ["#8b5a7a", "#9b6a8a", "#ab7a9a", "#bb8aaa", "#cb9aba"],
    "Bebidas": ["#5a7a9a", "#6a8aaa", "#7a9aba", "#8aaaca", "#9abada"],
    "Saudáveis": ["#5a9a7a", "#6aaa8a", "#7aba9a", "#8acaaa", "#9adaaa"]
}

def get_category_color(category, name):
    """Gera uma cor baseada na categoria e nome do produto (determinística)"""
    if category not in CATEGORY_COLORS:
        category = "Salgados"  # Fallback
    
    # Usar hash do nome para selecionar cor de forma determinística
    hash_value = int(hashlib.md5(name.encode()).hexdigest(), 16)
    color_index = hash_value % len(CATEGORY_COLORS[category])
    
    return CATEGORY_COLORS[category][color_index]

class ProductCard(ctk.CTkFrame):
    """Card de produto moderno com CustomTkinter"""
    
    def __init__(self, parent, name, price, icon="📦", category="Salgados", image_path=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.name = name
        self.price = price
        self.icon = icon
        self.category = category
        self.selected = False
        
        # Gerar cor baseada na categoria
        card_color = get_category_color(category, name)
        
        # Configuração do card com cor da categoria
        self.configure(
            corner_radius=15,
            fg_color=(card_color, card_color),
            border_width=2,
            border_color=(card_color, card_color)
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
            # Clarear a cor no hover
            current_color = self.cget("fg_color")[0] if isinstance(self.cget("fg_color"), tuple) else self.cget("fg_color")
            self.configure(border_color="#2ed573", border_width=3)
    
    def on_leave(self, event):
        """Remove efeito hover ao sair do mouse"""
        if not self.selected:
            card_color = get_category_color(self.category, self.name)
            self.configure(border_color=(card_color, card_color), border_width=2)
    
    def select(self):
        """Marca o card como selecionado"""
        self.selected = True
        self.configure(border_color="#2ed573", border_width=3)
    
    def deselect(self):
        """Remove seleção do card"""
        self.selected = False
        card_color = get_category_color(self.category, self.name)
        self.configure(border_color=(card_color, card_color), border_width=2)
