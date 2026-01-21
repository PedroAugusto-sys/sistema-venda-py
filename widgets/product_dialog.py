from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QGridLayout,
    QWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

# Ícones disponíveis por categoria
ICONS_BY_CATEGORY = {
    "Salgados": ["🍕", "🌭", "🍔", "🌮", "🥪", "🥟", "🥐", "🧀", "🍗", "🥓", "🍖", "🥨"],
    "Doces": ["🍰", "🍪", "🍩", "🍫", "🍬", "🍭", "🧁", "🍮", "🍯", "🥧", "🍨", "🍦"],
    "Bebidas": ["🥤", "🧃", "🧊", "☕", "🍵", "🥛", "🧉", "🍺", "🍷", "🥤", "🧋", "🍹"],
    "Saudáveis": ["🥗", "🥑", "🥒", "🥕", "🌽", "🥦", "🍎", "🍌", "🍊", "🍇", "🥝", "🍓"]
}

ALL_ICONS = [
    "🍕", "🌭", "🍔", "🌮", "🥪", "🥟", "🥐", "🧀", "🍗", "🥓", "🍖", "🥨",
    "🍰", "🍪", "🍩", "🍫", "🍬", "🍭", "🧁", "🍮", "🍯", "🥧", "🍨", "🍦",
    "🥤", "🧃", "🧊", "☕", "🍵", "🥛", "🧉", "🍺", "🍷", "🥤", "🧋", "🍹",
    "🥗", "🥑", "🥒", "🥕", "🌽", "🥦", "🍎", "🍌", "🍊", "🍇", "🥝", "🍓",
    "📦", "🛒", "🍽️", "🥄", "🍴", "🥢"
]

class ProductDialog(QDialog):
    """Diálogo para adicionar/editar produto com categoria e ícone"""
    
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.selected_icon = None
        
        self.setWindowTitle("Adicionar Produto" if product is None else "Editar Produto")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # Aplicar tema escuro
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS["bg_dark"]};
                color: {COLORS["text_light"]};
            }}
            QLabel {{
                color: {COLORS["text_light"]};
                background-color: transparent;
            }}
            QLineEdit {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS["green"]};
            }}
            QComboBox {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox:hover {{
                border: 1px solid {COLORS["green"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                selection-background-color: {COLORS["green"]};
                selection-color: {COLORS["bg_dark"]};
            }}
            QPushButton {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #333333;
                border: 1px solid {COLORS["green"]};
            }}
            QPushButton:pressed {{
                background-color: #1a1a1a;
            }}
        """)
        
        self.build_ui()
        self.load_product_data()
    
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Adicionar Produto" if self.product is None else "Editar Produto")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Nome
        name_label = QLabel("Nome do Produto:")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Digite o nome do produto")
        layout.addWidget(self.name_input)
        
        # Preço
        price_label = QLabel("Preço (R$):")
        price_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(price_label)
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setValidator(None)  # Aceita números decimais
        layout.addWidget(self.price_input)
        
        # Categoria
        category_label = QLabel("Categoria:")
        category_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Salgados", "Doces", "Bebidas", "Saudáveis"])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo)
        
        # Ícone selecionado (preview)
        icon_preview_label = QLabel("Ícone Selecionado:")
        icon_preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(icon_preview_label)
        
        self.icon_preview = QLabel("📦")
        self.icon_preview.setFont(QFont("Arial", 48))
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS["bg_panel"]};
                border: 2px solid {COLORS["green"]};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        layout.addWidget(self.icon_preview)
        
        # Seletor de ícones
        icon_label = QLabel("Selecione um Ícone:")
        icon_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(icon_label)
        
        # Scroll area para ícones
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS["bg_panel"]};
                border: 1px solid #3a3a3a;
                border-radius: 10px;
            }}
        """)
        
        icons_widget = QWidget()
        icons_layout = QGridLayout(icons_widget)
        icons_layout.setSpacing(5)
        
        self.icon_buttons = []
        for i, icon in enumerate(ALL_ICONS):
            btn = QPushButton(icon)
            btn.setFont(QFont("Arial", 24))
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS["bg_dark"]};
                    border: 2px solid #3a3a3a;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    border: 2px solid {COLORS["green"]};
                    background-color: #333333;
                }}
            """)
            btn.clicked.connect(lambda checked, ic=icon: self.select_icon(ic))
            self.icon_buttons.append(btn)
            icons_layout.addWidget(btn, i // 6, i % 6)
        
        scroll.setWidget(icons_widget)
        layout.addWidget(scroll)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["green"]};
                color: {COLORS["bg_dark"]};
            }}
            QPushButton:hover {{
                background-color: #26c463;
            }}
        """)
        self.save_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_category_changed(self, category):
        """Atualiza ícones disponíveis quando categoria muda"""
        # Por enquanto, mantém todos os ícones disponíveis
        # Pode ser melhorado para filtrar por categoria
        pass
    
    def select_icon(self, icon):
        """Seleciona um ícone"""
        self.selected_icon = icon
        self.icon_preview.setText(icon)
        
        # Destacar botão selecionado
        for btn in self.icon_buttons:
            if btn.text() == icon:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS["green"]};
                        border: 2px solid {COLORS["green"]};
                        border-radius: 10px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS["bg_dark"]};
                        border: 2px solid #3a3a3a;
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid {COLORS["green"]};
                        background-color: #333333;
                    }}
                """)
    
    def load_product_data(self):
        """Carrega dados do produto se estiver editando"""
        if self.product:
            self.name_input.setText(self.product.get("name", ""))
            self.price_input.setText(str(self.product.get("price", 0.0)))
            
            category = self.product.get("category", "Salgados")
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            icon = self.product.get("icon", "📦")
            self.select_icon(icon)
        else:
            self.select_icon("📦")  # Ícone padrão
    
    def get_product_data(self):
        """Retorna os dados do produto"""
        try:
            price = float(self.price_input.text().replace(",", "."))
        except ValueError:
            price = 0.0
        
        return {
            "name": self.name_input.text().strip(),
            "price": price,
            "category": self.category_combo.currentText(),
            "icon": self.selected_icon or "📦"
        }
