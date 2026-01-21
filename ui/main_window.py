import os
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw

# Importar managers (ainda usando PySide6, mas podemos adaptar depois)
from managers.product_manager import ProductManager
from managers.client_manager import ClientManager

# Configuração do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Cores customizadas
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

class MainWindow(ctk.CTk):
    """Janela principal do sistema PDV com CustomTkinter"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Cantina Colégio Ativa")
        self.geometry("1400x800")
        self.minsize(1000, 600)
        
        # Caminhos dos arquivos
        self.products_path = "data/products.json"
        self.clients_path = "data/clients.json"
        
        # Estado da aplicação
        self.total = 0.0
        self.cart = {}  # {name: {"price": float, "qty": int}}
        self.current_client = None
        self.client_credits = 0.0
        self.filtered_products = []
        self.current_category = "Todos"
        self.selected_cart_item = None  # Item selecionado no carrinho
        self.current_columns = 4  # Número atual de colunas no grid
        
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=35, minsize=350)  # Sidebar com tamanho mínimo
        self.grid_columnconfigure(1, weight=65, minsize=500)  # Produtos com tamanho mínimo
        self.grid_rowconfigure(0, weight=1)
        
        # Bind para redimensionamento
        self.bind("<Configure>", self.on_window_resize)
        
        # Criar interface
        self.create_sidebar()
        self.create_products_section()
        
        # Carregar dados
        self.load_products()
        self.load_clients()
        
        # Bind teclado
        self.bind("<F12>", lambda e: self.finish_order())
        self.bind("<Control-l>", lambda e: self.clear_cart())
        
        # Focar na janela
        self.focus_set()
    
    def create_sidebar(self):
        """Cria a sidebar esquerda (35% da tela)"""
        # Frame principal da sidebar
        sidebar = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_panel"]
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        sidebar.grid_columnconfigure(0, weight=1)
        # Configurar rows para distribuição responsiva
        sidebar.grid_rowconfigure(0, weight=0)  # Header - não expande
        sidebar.grid_rowconfigure(1, weight=0)  # Cliente - não expande
        sidebar.grid_rowconfigure(2, weight=1)  # Carrinho - expande
        sidebar.grid_rowconfigure(3, weight=0)  # Pagamento - não expande
        sidebar.grid_rowconfigure(4, weight=0)  # Total/Footer - não expande
        sidebar.grid_rowconfigure(5, weight=0)  # Menu - não expande
        
        # Header
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 30))
        
        title = ctk.CTkLabel(
            header,
            text="Cantina Colégio Ativa",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_light"]
        )
        title.pack()
        
        # Seção de Cliente
        client_section = ctk.CTkFrame(sidebar, fg_color="transparent")
        client_section.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        client_section.grid_columnconfigure(0, weight=1)
        
        client_label = ctk.CTkLabel(
            client_section,
            text="CLIENTE",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_gray"]
        )
        client_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # ComboBox de clientes
        self.client_combo = ctk.CTkComboBox(
            client_section,
            values=[],
            font=ctk.CTkFont(size=14),
            corner_radius=15,
            height=40,
            command=self.on_client_selected
        )
        self.client_combo.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.client_combo.set("Selecione o estudante")
        
        # Card de saldo
        self.balance_card = ctk.CTkFrame(
            client_section,
            corner_radius=15,
            fg_color=COLORS["bg_dark"]
        )
        self.balance_card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        balance_content = ctk.CTkFrame(self.balance_card, fg_color="transparent")
        balance_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        balance_icon = ctk.CTkLabel(
            balance_content,
            text="👤",
            font=ctk.CTkFont(size=32)
        )
        balance_icon.pack(side="left", padx=(0, 15))
        
        balance_info = ctk.CTkFrame(balance_content, fg_color="transparent")
        balance_info.pack(side="left", fill="both", expand=True)
        
        self.balance_name_label = ctk.CTkLabel(
            balance_info,
            text="Estudante",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_light"]
        )
        self.balance_name_label.pack(anchor="w")
        
        balance_text = ctk.CTkLabel(
            balance_info,
            text="Saldo:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_gray"]
        )
        balance_text.pack(anchor="w", pady=(5, 0))
        
        self.balance_value_label = ctk.CTkLabel(
            balance_info,
            text="R$ 0,00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["green"]
        )
        self.balance_value_label.pack(anchor="w")
        
        # Seção do Carrinho
        cart_section = ctk.CTkFrame(sidebar, fg_color="transparent")
        cart_section.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        cart_section.grid_columnconfigure(0, weight=1)
        cart_section.grid_rowconfigure(1, weight=1)
        
        cart_label = ctk.CTkLabel(
            cart_section,
            text="CARRINHO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_gray"]
        )
        cart_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Frame scrollável do carrinho (sem altura fixa para ser responsivo)
        self.cart_scroll = ctk.CTkScrollableFrame(
            cart_section,
            corner_radius=15,
            fg_color=COLORS["bg_dark"]
        )
        self.cart_scroll.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.cart_scroll.grid_columnconfigure(0, weight=1)
        
        # Botões de controle do carrinho
        cart_controls = ctk.CTkFrame(cart_section, fg_color="transparent")
        cart_controls.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.btn_remove = ctk.CTkButton(
            cart_controls,
            text="Remover",
            font=ctk.CTkFont(size=12),
            corner_radius=15,
            fg_color=COLORS["red"],
            hover_color="#ff3838",
            width=80,
            height=35,
            command=self.remove_selected_item
        )
        self.btn_remove.pack(side="left", padx=(0, 5))
        
        self.btn_decrease = ctk.CTkButton(
            cart_controls,
            text="-",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            width=40,
            height=35,
            command=self.decrease_selected_item
        )
        self.btn_decrease.pack(side="left", padx=(0, 5))
        
        self.btn_increase = ctk.CTkButton(
            cart_controls,
            text="+",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=15,
            width=40,
            height=35,
            command=self.increase_selected_item
        )
        self.btn_increase.pack(side="left", padx=(0, 5))
        
        self.btn_clear = ctk.CTkButton(
            cart_controls,
            text="Limpar",
            font=ctk.CTkFont(size=12),
            corner_radius=15,
            width=80,
            height=35,
            command=self.clear_cart
        )
        self.btn_clear.pack(side="left")
        
        # Métodos de Pagamento
        payment_section = ctk.CTkFrame(sidebar, fg_color="transparent")
        payment_section.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        payment_label = ctk.CTkLabel(
            payment_section,
            text="MÉTODO DE PAGAMENTO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_gray"]
        )
        payment_label.pack(anchor="w", pady=(0, 10))
        
        payment_buttons_frame = ctk.CTkFrame(payment_section, fg_color="transparent")
        payment_buttons_frame.pack(fill="x")
        
        self.payment_methods = {
            "Dinheiro": "💵",
            "Cartão": "💳",
            "Crédito Aluno": "🎓"
        }
        self.selected_payment = None
        self.payment_buttons = {}
        
        for method, icon in self.payment_methods.items():
            btn = ctk.CTkButton(
                payment_buttons_frame,
                text=f"{icon}\n{method}",
                font=ctk.CTkFont(size=11),
                corner_radius=15,
                width=100,
                height=70,
                fg_color=COLORS["bg_dark"],
                hover_color="#333333",
                command=lambda m=method: self.select_payment_method(m)
            )
            btn.pack(side="left", padx=5, fill="x", expand=True)
            self.payment_buttons[method] = btn
        
        # Total e Botão Finalizar
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        
        total_label = ctk.CTkLabel(
            footer,
            text="TOTAL",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_gray"]
        )
        total_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.total_value_label = ctk.CTkLabel(
            footer,
            text="R$ 0,00",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["green"]
        )
        self.total_value_label.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        self.btn_finish = ctk.CTkButton(
            footer,
            text="FINALIZAR VENDA (F12)",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=15,
            height=60,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.finish_order
        )
        self.btn_finish.grid(row=2, column=0, sticky="ew")
        
        # Menu superior (simulado com botões)
        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=40)
        menu_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        btn_products = ctk.CTkButton(
            menu_frame,
            text="Gerenciar Produtos",
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            height=35,
            command=self.open_product_manager
        )
        btn_products.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        btn_clients = ctk.CTkButton(
            menu_frame,
            text="Gerenciar Clientes",
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            height=35,
            command=self.open_client_manager
        )
        btn_clients.pack(side="left", fill="x", expand=True)
    
    def create_products_section(self):
        """Cria a seção de produtos (65% da tela)"""
        # Frame principal
        products_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_dark"]
        )
        products_frame.grid(row=0, column=1, sticky="nsew")
        products_frame.grid_columnconfigure(0, weight=1)
        products_frame.grid_rowconfigure(0, weight=0)  # Toolbar - não expande
        products_frame.grid_rowconfigure(1, weight=0)  # Título - não expande
        products_frame.grid_rowconfigure(2, weight=1)  # Grid de produtos - expande
        
        # Barra de ferramentas (responsiva)
        toolbar = ctk.CTkFrame(products_frame, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        toolbar.grid_columnconfigure(0, weight=1)
        toolbar.grid_columnconfigure(1, weight=0)
        
        # Campo de busca (expande)
        search_frame = ctk.CTkFrame(toolbar, fg_color=COLORS["bg_panel"], corner_radius=15)
        search_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_icon = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=18),
            width=40
        )
        search_icon.grid(row=0, column=0, padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar produtos...",
            font=ctk.CTkFont(size=14),
            corner_radius=15,
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        # Botões de filtro (scrollável se necessário)
        filter_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        filter_frame.grid(row=0, column=1, sticky="e")
        
        categories = ["Todos", "Salgados", "Doces", "Bebidas", "Saudáveis"]
        self.category_buttons = {}
        
        for cat in categories:
            btn = ctk.CTkButton(
                filter_frame,
                text=cat,
                font=ctk.CTkFont(size=12),
                corner_radius=15,
                width=70,  # Reduzido para ser mais compacto
                height=35,
                fg_color=COLORS["bg_panel"],
                hover_color="#333333",
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(side="left", padx=3)  # Padding reduzido
            self.category_buttons[cat] = btn
        
        # Título
        title_label = ctk.CTkLabel(
            products_frame,
            text="PRODUTOS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_gray"]
        )
        title_label.grid(row=1, column=0, sticky="nw", padx=20, pady=(0, 10))
        
        # Grid de produtos (scrollável)
        self.products_scroll = ctk.CTkScrollableFrame(
            products_frame,
            corner_radius=0,
            fg_color="transparent"
        )
        self.products_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.products_scroll.grid_columnconfigure(0, weight=1)
        
        # Grid interno para produtos (colunas dinâmicas)
        self.products_grid = ctk.CTkFrame(self.products_scroll, fg_color="transparent")
        self.products_grid.pack(fill="both", expand=True)
        
        # Configurar grid inicial (será atualizado no redimensionamento)
        # Delay para garantir que a janela foi renderizada
        self.after(100, self.update_products_grid_columns)
    
    def load_products(self):
        """Carrega produtos do arquivo JSON"""
        if not os.path.exists(self.products_path):
            return
        
        try:
            with open(self.products_path, "r", encoding="utf-8") as f:
                self.all_products = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            self.all_products = []
        
        self.filtered_products = self.all_products.copy()
        self.display_products()
    
    def load_products_grid(self, grid_layout=None):
        """Método de compatibilidade para ProductManager (PySide6)"""
        # Este método é chamado pelo ProductManager antigo
        # Redireciona para nosso novo método
        self.load_products()
    
    def calculate_columns(self):
        """Calcula o número de colunas baseado no tamanho disponível"""
        try:
            # Obter largura disponível do frame de produtos
            self.update_idletasks()
            products_frame_width = self.products_scroll.winfo_width()
            
            if products_frame_width < 100:
                # Se ainda não foi renderizado, usar largura da janela
                window_width = self.winfo_width()
                if window_width < 100:
                    return 4  # Fallback se janela ainda não renderizou
                # Subtrair sidebar (35%) e padding
                products_frame_width = int(window_width * 0.65) - 60
            
            # Calcular colunas: cada card precisa de ~220px (200 + 20 padding)
            # Com margem de segurança e padding entre cards
            card_min_width = 180  # Largura mínima do card
            padding_per_card = 20  # Padding entre cards
            card_total_width = card_min_width + padding_per_card
            
            columns = max(2, int(products_frame_width / card_total_width))
            
            # Limitar entre 2 e 6 colunas para manter legibilidade
            columns = min(max(2, columns), 6)
            
            return columns
        except Exception as e:
            print(f"Erro ao calcular colunas: {e}")
            return 4  # Fallback
    
    def update_products_grid_columns(self):
        """Atualiza o número de colunas do grid de produtos"""
        columns = self.calculate_columns()
        
        if columns != self.current_columns:
            self.current_columns = columns
            
            # Limpar configuração anterior
            for i in range(10):  # Limpar até 10 colunas
                self.products_grid.grid_columnconfigure(i, weight=0)
            
            # Configurar novas colunas
            for i in range(columns):
                self.products_grid.grid_columnconfigure(i, weight=1, uniform="col")
    
    def on_window_resize(self, event=None):
        """Callback quando a janela é redimensionada"""
        if event and event.widget == self:
            # Atualizar número de colunas
            old_columns = self.current_columns
            self.update_products_grid_columns()
            
            # Se o número de colunas mudou, redesenhar produtos
            if old_columns != self.current_columns:
                self.after(100, self.display_products)  # Delay para evitar múltiplos redraws
    
    def display_products(self):
        """Exibe produtos no grid"""
        # Atualizar número de colunas antes de exibir
        self.update_products_grid_columns()
        columns = self.current_columns
        
        # Limpar produtos existentes
        for widget in self.products_grid.winfo_children():
            widget.destroy()
        
        # Adicionar produtos
        row = 0
        col = 0
        
        for product in self.filtered_products:
            name = product.get("name")
            price = product.get("price")
            icon = product.get("icon", "📦")
            
            if name is None or price is None:
                continue
            
            # Criar card de produto (sem tamanho fixo para ser responsivo)
            from widgets.product_button import ProductCard
            card = ProductCard(
                self.products_grid,
                name=name,
                price=price,
                icon=icon
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Bind click
            card.bind("<Button-1>", lambda e, n=name, p=price: self.add_to_cart(n, p))
            for widget in [card.image_label, card.name_label, card.price_label]:
                widget.bind("<Button-1>", lambda e, n=name, p=price: self.add_to_cart(n, p))
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
    
    def on_search(self, event=None):
        """Filtra produtos conforme busca"""
        search_term = self.search_entry.get().lower()
        
        if not search_term:
            self.filtered_products = self.all_products.copy()
        else:
            self.filtered_products = [
                p for p in self.all_products
                if search_term in p.get("name", "").lower()
            ]
        
        # Aplicar filtro de categoria também
        if self.current_category != "Todos":
            self.filtered_products = [
                p for p in self.filtered_products
                if p.get("category", "").lower() == self.current_category.lower()
            ]
        
        self.display_products()
    
    def filter_by_category(self, category):
        """Filtra produtos por categoria"""
        self.current_category = category
        
        # Atualizar botões
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(fg_color=COLORS["green"], hover_color="#26c463")
            else:
                btn.configure(fg_color=COLORS["bg_panel"], hover_color="#333333")
        
        # Aplicar filtro
        search_term = self.search_entry.get().lower()
        if not search_term:
            if category == "Todos":
                self.filtered_products = self.all_products.copy()
            else:
                # Filtro por categoria real do produto
                self.filtered_products = [
                    p for p in self.all_products
                    if p.get("category", "").lower() == category.lower()
                ]
        else:
            self.on_search()
        
        self.display_products()
    
    def load_clients(self):
        """Carrega clientes do arquivo JSON"""
        if not os.path.exists(self.clients_path):
            return
        
        try:
            with open(self.clients_path, "r", encoding="utf-8") as f:
                self.clients_data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            self.clients_data = {}
        
        # Atualizar ComboBox
        client_names = sorted(self.clients_data.keys())
        self.client_combo.configure(values=client_names)
    
    def on_client_selected(self, choice):
        """Callback quando cliente é selecionado"""
        if choice and choice in self.clients_data:
            self.current_client = choice
            client_data = self.clients_data[choice]
            self.client_credits = float(client_data.get("credits", 0.0))
            
            # Atualizar UI
            self.balance_name_label.configure(text=choice)
            self.balance_value_label.configure(text=f"R$ {self.client_credits:.2f}")
        else:
            self.current_client = None
            self.client_credits = 0.0
            self.balance_name_label.configure(text="Estudante")
            self.balance_value_label.configure(text="R$ 0,00")
    
    def add_to_cart(self, name, price):
        """Adiciona produto ao carrinho"""
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"price": price, "qty": 1}
        
        self.update_cart_display()
        self.update_total()
    
    def update_cart_display(self):
        """Atualiza a exibição do carrinho"""
        # Limpar carrinho
        for widget in self.cart_scroll.winfo_children():
            widget.destroy()
        
        # Adicionar itens
        for name, item in self.cart.items():
            price = item["price"]
            qty = item["qty"]
            subtotal = price * qty
            
            # Determinar cor do frame (selecionado ou não)
            is_selected = (self.selected_cart_item == name)
            frame_color = COLORS["green"] if is_selected else COLORS["bg_dark"]
            border_color = COLORS["green"] if is_selected else COLORS["bg_dark"]
            
            item_frame = ctk.CTkFrame(
                self.cart_scroll,
                corner_radius=10,
                fg_color=frame_color,
                border_width=2 if is_selected else 0,
                border_color=border_color
            )
            item_frame.pack(fill="x", padx=5, pady=5)
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Bind click para seleção
            item_frame.bind("<Button-1>", lambda e, n=name: self.select_cart_item(n))
            
            item_text = f"{name} (x{qty})"
            item_label = ctk.CTkLabel(
                item_frame,
                text=item_text,
                font=ctk.CTkFont(size=12),
                anchor="w",
                fg_color="transparent"
            )
            item_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
            item_label.bind("<Button-1>", lambda e, n=name: self.select_cart_item(n))
            
            price_text = f"R$ {subtotal:.2f}"
            price_label = ctk.CTkLabel(
                item_frame,
                text=price_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["green"] if not is_selected else COLORS["bg_dark"],
                anchor="e",
                fg_color="transparent"
            )
            price_label.grid(row=0, column=1, sticky="e", padx=10, pady=5)
            price_label.bind("<Button-1>", lambda e, n=name: self.select_cart_item(n))
    
    def update_total(self):
        """Atualiza o total da venda"""
        self.total = sum(item["price"] * item["qty"] for item in self.cart.values())
        self.total_value_label.configure(text=f"R$ {self.total:.2f}")
        
        # Efeito visual de atualização
        self.after(50, lambda: self.total_value_label.configure(
            text_color=COLORS["green"]
        ))
    
    def select_cart_item(self, item_name):
        """Seleciona um item do carrinho"""
        if item_name in self.cart:
            self.selected_cart_item = item_name
            self.update_cart_display()
    
    def remove_selected_item(self):
        """Remove item selecionado do carrinho"""
        if self.selected_cart_item and self.selected_cart_item in self.cart:
            del self.cart[self.selected_cart_item]
            self.selected_cart_item = None
            self.update_cart_display()
            self.update_total()
        elif self.cart:
            # Se nenhum item selecionado, remove o último
            last_item = list(self.cart.keys())[-1]
            del self.cart[last_item]
            self.update_cart_display()
            self.update_total()
    
    def decrease_selected_item(self):
        """Diminui quantidade do item selecionado"""
        if self.selected_cart_item and self.selected_cart_item in self.cart:
            if self.cart[self.selected_cart_item]["qty"] > 1:
                self.cart[self.selected_cart_item]["qty"] -= 1
            else:
                del self.cart[self.selected_cart_item]
                self.selected_cart_item = None
            self.update_cart_display()
            self.update_total()
        elif self.cart:
            # Se nenhum item selecionado, diminui o último
            last_item = list(self.cart.keys())[-1]
            if self.cart[last_item]["qty"] > 1:
                self.cart[last_item]["qty"] -= 1
            else:
                del self.cart[last_item]
            self.update_cart_display()
            self.update_total()
    
    def increase_selected_item(self):
        """Aumenta quantidade do item selecionado"""
        if self.selected_cart_item and self.selected_cart_item in self.cart:
            self.cart[self.selected_cart_item]["qty"] += 1
            self.update_cart_display()
            self.update_total()
        elif self.cart:
            # Se nenhum item selecionado, aumenta o último
            last_item = list(self.cart.keys())[-1]
            self.cart[last_item]["qty"] += 1
            self.update_cart_display()
            self.update_total()
    
    def clear_cart(self):
        """Limpa o carrinho"""
        self.cart = {}
        self.selected_cart_item = None
        self.update_cart_display()
        self.update_total()
    
    def select_payment_method(self, method):
        """Seleciona método de pagamento"""
        # Resetar todos os botões
        for btn in self.payment_buttons.values():
            btn.configure(fg_color=COLORS["bg_dark"], hover_color="#333333")
        
        # Destacar selecionado
        if method in self.payment_buttons:
            self.payment_buttons[method].configure(
                fg_color=COLORS["green"],
                hover_color="#26c463"
            )
            self.selected_payment = method
    
    def finish_order(self):
        """Finaliza a venda"""
        if not self.current_client:
            messagebox.showwarning("Atenção", "Selecione um cliente primeiro!")
            return
        
        if not self.cart:
            messagebox.showwarning("Atenção", "O carrinho está vazio!")
            return
        
        if not self.selected_payment:
            messagebox.showwarning("Atenção", "Selecione um método de pagamento!")
            return
        
        # Construir ordem
        items = []
        for name, item in self.cart.items():
            items.append({
                "name": name,
                "price": item["price"],
                "quantity": item["qty"]
            })
        
        order = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "total": self.total,
            "payment_method": self.selected_payment
        }
        
        # Salvar venda
        self.add_order_to_client(self.current_client, order)
        
        # Mensagem de sucesso
        messagebox.showinfo(
            "Venda Finalizada",
            f"Venda finalizada para {self.current_client}\n"
            f"Total: R$ {self.total:.2f}\n"
            f"Método: {self.selected_payment}"
        )
        
        # Limpar carrinho
        self.clear_cart()
        self.selected_payment = None
        for btn in self.payment_buttons.values():
            btn.configure(fg_color=COLORS["bg_dark"], hover_color="#333333")
    
    def add_order_to_client(self, client_name, order):
        """Adiciona ordem ao cliente"""
        if client_name not in self.clients_data:
            self.clients_data[client_name] = {
                "credits": 0.0,
                "sales": []
            }
        
        client = self.clients_data[client_name]
        client["sales"].append({
            "id": len(client.get("sales", [])) + 1,
            "items": order["items"],
            "total": order["total"],
            "paid": self.selected_payment != "Crédito Aluno",
            "date": order["timestamp"].split(" ")[0],
            "payment_method": order["payment_method"]
        })
        
        # Processar crédito se necessário
        if self.selected_payment == "Crédito Aluno":
            if self.client_credits >= self.total:
                client["credits"] = self.client_credits - self.total
                # Marcar como pago
                client["sales"][-1]["paid"] = True
            else:
                # Fica pendente
                client["sales"][-1]["paid"] = False
        
        # Salvar
        with open(self.clients_path, "w", encoding="utf-8") as f:
            json.dump(self.clients_data, f, indent=4, ensure_ascii=False)
        
        # Recarregar
        self.load_clients()
        if self.current_client:
            self.on_client_selected(self.current_client)
    
    def open_product_manager(self):
        """Abre gerenciador de produtos (PySide6)"""
        # Por enquanto, manter compatibilidade com PySide6
        try:
            from PySide6.QtWidgets import QApplication
            import sys
            
            if not hasattr(self, '_qt_app'):
                self._qt_app = QApplication.instance()
                if self._qt_app is None:
                    self._qt_app = QApplication(sys.argv)
            
            # Criar um parent dummy para o ProductManager
            from PySide6.QtWidgets import QWidget
            dummy_parent = QWidget()
            dummy_parent.hide()
            
            manager = ProductManager(dummy_parent, self.products_path)
            # Substituir o parent para que o refresh funcione
            manager.parent = self
            manager.exec()
            
            # Recarregar produtos
            self.load_products()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o gerenciador: {e}")
    
    def open_client_manager(self):
        """Abre gerenciador de clientes (PySide6)"""
        try:
            from PySide6.QtWidgets import QApplication
            import sys
            
            if not hasattr(self, '_qt_app'):
                self._qt_app = QApplication.instance()
                if self._qt_app is None:
                    self._qt_app = QApplication(sys.argv)
            
            # Criar um parent dummy para o ClientManager
            from PySide6.QtWidgets import QWidget
            dummy_parent = QWidget()
            dummy_parent.hide()
            
            manager = ClientManager(dummy_parent)
            manager.exec()
            
            # Recarregar clientes
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o gerenciador: {e}")
