from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QMessageBox, QDialog, QInputDialog, 
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.file_utils import load_json, save_json

class ProductManager(QDialog):
    def __init__(self, parent, products_file="data/products.json"):
        super().__init__(parent)
        self.parent = parent
        self.products_file = products_file

        self.setWindowTitle("Gerenciar Produtos")
        self.setMinimumWidth(420)

        self.build_ui()
        self.load_list()

    def build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Lista de Produtos")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.list_widget = QListWidget()

        btn_add = QPushButton("Adicionar")
        btn_edit = QPushButton("Editar")
        btn_delete = QPushButton("Deletar")

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

    def load_list(self):
        self.list_widget.clear()

        try:
            self.products = load_json(self.products_file, [])
        except Exception:
            self.products = []

        for product in self.products:
            name = product["name"]
            price = product["price"]
            stock = product.get("stock", 0)
            self.list_widget.addItem(f"{name} - R$ {price:.2f} | Estoque: {stock}")

    def save_products(self):
        for product in self.products:
            product.setdefault("stock", 0)
        save_json(self.products_file, self.products)

        self.parent.load_products(self.parent.grid_layout)

    def add_product(self):
        name, ok1 = QInputDialog.getText(self, "Adicionar Produto", "Nome:")
        if not ok1 or name.strip() == "":
            return

        price, ok2 = QInputDialog.getDouble(self, "Adicionar Produto", "Preço (R$):", 0, 0, 999.99, 2)
        if not ok2:
            return

        stock, ok3 = QInputDialog.getInt(self, "Adicionar Produto", "Estoque:", 0, 0, 100000, 1)
        if not ok3:
            return

        self.products.append({"name": name, "price": price, "stock": stock})
        self.save_products()
        self.load_list()

    def edit_product(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        old = self.products[selected]

        name, ok1 = QInputDialog.getText(self, "Editar Produto", "Nome:", text=old["name"])
        if not ok1 or name.strip() == "":
            return

        price, ok2 = QInputDialog.getDouble(
            self, "Editar Produto", "Preço (R$):", old["price"], 0, 999.99, 2
        )
        if not ok2:
            return

        stock, ok3 = QInputDialog.getInt(
            self, "Editar Produto", "Estoque:", old.get("stock", 0), 0, 100000, 1
        )
        if not ok3:
            return

        self.products[selected] = {"name": name, "price": price, "stock": stock}
        self.save_products()
        self.load_list()

    def delete_product(self):
        selected = self.list_widget.currentRow()
        if selected < 0:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            "Deseja realmente excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        self.products.pop(selected)
        self.save_products()
        self.load_list()
