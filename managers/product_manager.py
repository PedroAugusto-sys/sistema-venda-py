import json
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QMessageBox, QDialog, QInputDialog, 
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from widgets.product_dialog import ProductDialog

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

class ProductManager(QDialog):
    def __init__(self, parent, products_file="data/products.json"):
        super().__init__(parent)
        self.parent = parent
        self.products_file = products_file

        self.setWindowTitle("Gerenciar Produtos")
        self.setMinimumWidth(420)
        
        # Aplicar tema escuro
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS["bg_dark"]};
                color: {COLORS["text_light"]};
            }}
            QLabel {{
                background-color: transparent;
                color: {COLORS["text_light"]};
            }}
            QListWidget {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS["green"]};
                color: {COLORS["bg_dark"]};
            }}
            QPushButton {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: none;
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
            QPushButton:pressed {{
                background-color: #1a1a1a;
            }}
        """)

        self.build_ui()
        self.load_list()

    def build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Lista de Produtos")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.list_widget = QListWidget()

        # Buttons row
        btn_add = QPushButton("Adicionar")
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["green"]};
                color: {COLORS["bg_dark"]};
                border: none;
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #26c463;
            }}
        """)
        
        btn_edit = QPushButton("Editar")
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: none;
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
        """)
        
        btn_delete = QPushButton("Deletar")
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["red"]};
                color: {COLORS["text_light"]};
                border: none;
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ff3838;
            }}
        """)

        btn_add.clicked.connect(self.add_product)
        btn_edit.clicked.connect(self.edit_product)
        btn_delete.clicked.connect(self.delete_product)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_delete)

        layout.addWidget(title)
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_row)

    # -----------------------------
    # LOAD PRODUCTS TO LIST
    # -----------------------------
    def load_list(self):
        # Limpar lista atual
        self.list_widget.clear()

        # Recarregar produtos do arquivo
        try:
            with open(self.products_file, "r", encoding="utf-8") as f:
                self.products = json.load(f)
        except FileNotFoundError:
            self.products = []
        except json.JSONDecodeError:
            self.products = []
        except Exception:
            self.products = []

        # Se não houver categoria/ícone nos produtos antigos, adicionar valores padrão
        needs_save = False
        for product in self.products:
            if "category" not in product:
                product["category"] = "Salgados"  # Categoria padrão
                needs_save = True
            if "icon" not in product:
                product["icon"] = "📦"  # Ícone padrão
                needs_save = True
        
        # Salvar se houver alterações
        if needs_save:
            self.save_products()

        # Adicionar produtos à lista
        for product in self.products:
            name = product.get("name", "")
            price = product.get("price", 0.0)
            category = product.get("category", "Salgados")
            icon = product.get("icon", "📦")
            if name:  # Só adiciona se tiver nome
                display_text = f"{icon} {name} - R$ {price:.2f}"
                if category:
                    display_text += f" [{category}]"
                self.list_widget.addItem(display_text)
        
        # Forçar atualização visual imediata
        self.list_widget.viewport().update()
        self.update()
        self.repaint()

    # -----------------------------
    # SAVE PRODUCTS
    # -----------------------------
    def save_products(self):
        # Garantir que o diretório existe
        import os
        os.makedirs(os.path.dirname(self.products_file) if os.path.dirname(self.products_file) else ".", exist_ok=True)
        
        # Salvar produtos no arquivo
        with open(self.products_file, "w", encoding="utf-8") as f:
            json.dump(self.products, f, indent=4, ensure_ascii=False)
        
        # Forçar escrita no disco
        import sys
        if hasattr(sys, 'flush'):
            sys.stdout.flush()

        # Refresh main window grid (se o parent tiver o método)
        if self.parent and hasattr(self.parent, 'load_products'):
            try:
                # Tenta chamar o método sem parâmetros (CustomTkinter)
                self.parent.load_products()
            except (TypeError, AttributeError):
                # Se falhar, ignora silenciosamente
                pass

    # -----------------------------
    # ADD PRODUCT
    # -----------------------------
    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        product_data = dialog.get_product_data()
        
        if not product_data["name"].strip():
            QMessageBox.warning(self, "Aviso", "O nome do produto é obrigatório!")
            return
        
        # Adicionar produto à lista em memória
        self.products.append(product_data)
        
        # Adicionar diretamente à lista visual (mais rápido e confiável)
        icon = product_data.get("icon", "📦")
        category = product_data.get("category", "")
        display_text = f"{icon} {product_data['name']} - R$ {product_data['price']:.2f}"
        if category:
            display_text += f" [{category}]"
        self.list_widget.addItem(display_text)
        
        # Salvar no arquivo
        self.save_products()
        
        # Forçar atualização visual da lista
        self.list_widget.scrollToBottom()  # Rolar para o novo item
        self.list_widget.update()
        self.list_widget.repaint()

    # -----------------------------
    # EDIT PRODUCT
    # -----------------------------
    def edit_product(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        # Verificar se há produtos e se o índice é válido
        if not self.products or selected >= len(self.products):
            return

        old_product = self.products[selected]
        
        dialog = ProductDialog(self, product=old_product)
        if dialog.exec() != QDialog.Accepted:
            return
        
        product_data = dialog.get_product_data()
        
        if not product_data["name"].strip():
            QMessageBox.warning(self, "Aviso", "O nome do produto é obrigatório!")
            return

        # Atualizar produto na lista em memória
        self.products[selected] = product_data
        
        # Atualizar item na lista visual diretamente
        icon = product_data.get("icon", "📦")
        category = product_data.get("category", "")
        display_text = f"{icon} {product_data['name']} - R$ {product_data['price']:.2f}"
        if category:
            display_text += f" [{category}]"
        self.list_widget.item(selected).setText(display_text)
        
        # Salvar no arquivo
        self.save_products()
        
        # Forçar atualização visual
        self.list_widget.update()
        self.list_widget.repaint()

    # -----------------------------
    # DELETE PRODUCT
    # -----------------------------
    def delete_product(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar Exclusão")
        msg.setText("Deseja realmente excluir este produto?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS["bg_dark"]};
                color: {COLORS["text_light"]};
            }}
            QPushButton {{
                background-color: {COLORS["green"]};
                color: {COLORS["bg_dark"]};
                border: none;
                padding: 8px 20px;
                border-radius: 10px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #26c463;
            }}
        """)
        confirm = msg.exec()

        if confirm != QMessageBox.Yes:
            return

        # Verificar se há produtos e se o índice é válido
        if not self.products or selected >= len(self.products):
            return

        # Remover produto da lista em memória
        self.products.pop(selected)
        
        # Remover item da lista visual diretamente
        self.list_widget.takeItem(selected)
        
        # Salvar no arquivo
        self.save_products()
        
        # Forçar atualização visual
        self.list_widget.update()
        self.list_widget.repaint()
