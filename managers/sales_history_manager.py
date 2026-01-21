from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt
from utils.file_utils import load_json, save_json

class SalesHistoryManager(QDialog):
    def __init__(self, parent=None, clients_path="data/clients.json", products_path="data/products.json"):
        super().__init__(parent)
        self.clients_path = clients_path
        self.products_path = products_path
        self.setWindowTitle("Histórico de Vendas")
        self.resize(900, 500)

        layout = QVBoxLayout(self)

        filters = QHBoxLayout()
        filters.addWidget(QLabel("Cliente:"))
        self.client_filter = QComboBox()
        filters.addWidget(self.client_filter)

        filters.addWidget(QLabel("Data (YYYY-MM-DD):"))
        self.date_filter = QLineEdit()
        filters.addWidget(self.date_filter)

        self.btn_apply = QPushButton("Filtrar")
        self.btn_apply.clicked.connect(self.load_table)
        filters.addWidget(self.btn_apply)

        layout.addLayout(filters)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Cliente", "Venda", "Data", "Total", "Modalidade", "Parcelas", "Pago", "Valor Pago", "Pendente"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancelar Venda")
        self.btn_close = QPushButton("Fechar")
        self.btn_cancel.clicked.connect(self.cancel_sale)
        self.btn_close.clicked.connect(self.close)
        actions.addStretch()
        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_close)
        layout.addLayout(actions)

        self.load_filters()
        self.load_table()

    def load_clients(self):
        return load_json(self.clients_path, {})

    def save_clients(self, data):
        save_json(self.clients_path, data)

    def load_products(self):
        return load_json(self.products_path, [])

    def save_products(self, products):
        save_json(self.products_path, products)

    def load_filters(self):
        self.client_filter.clear()
        self.client_filter.addItem("Todos")
        data = self.load_clients()
        for client_name in sorted(data.keys()):
            self.client_filter.addItem(client_name)

    def load_table(self):
        data = self.load_clients()
        client_filter = self.client_filter.currentText()
        date_filter = self.date_filter.text().strip()

        rows = []
        for client_name, client in data.items():
            if client_filter != "Todos" and client_name != client_filter:
                continue
            for sale in client.get("sales", []):
                if date_filter and sale.get("date") != date_filter:
                    continue
                rows.append((client_name, sale))

        self.table.setRowCount(len(rows))
        for row, (client_name, sale) in enumerate(rows):
            total = float(sale.get("total", 0.0))
            paid_amount = float(sale.get("paid_amount", 0.0))
            if sale.get("paid", False) and paid_amount == 0.0:
                paid_amount = total
            remaining = max(total - paid_amount, 0.0)
            status = "Cancelada" if sale.get("cancelled", False) else "Ativa"
            if sale.get("cancelled", False):
                paid_amount = 0.0
                remaining = 0.0

            payment_method = sale.get("payment_method_display", sale.get("payment_method", "N/A"))
            installments = sale.get("installments", 1)
            installments_text = f"{installments}x" if installments > 1 else "-"
            
            values = [
                client_name,
                str(sale.get("id", "")),
                sale.get("date", ""),
                f"{total:.2f}",
                payment_method,
                installments_text,
                "Sim" if sale.get("paid", False) else "Não",
                f"{paid_amount:.2f}",
                f"{remaining:.2f}"
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col in (3, 6, 7, 8):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            self.table.item(row, 0).setData(Qt.UserRole, {"client": client_name, "sale_id": sale.get("id")})

    def cancel_sale(self):
        current = self.table.currentRow()
        if current < 0:
            return

        data_info = self.table.item(current, 0).data(Qt.UserRole) or {}
        client_name = data_info.get("client")
        sale_id = data_info.get("sale_id")
        if not client_name or sale_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Cancelar Venda",
            "Deseja cancelar esta venda? O estoque será restaurado.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        data = self.load_clients()
        products = self.load_products()

        client = data.get(client_name, {})
        for sale in client.get("sales", []):
            if sale.get("id") == sale_id:
                if sale.get("cancelled", False):
                    QMessageBox.information(self, "Cancelar Venda", "Esta venda já está cancelada.")
                    return
                sale["cancelled"] = True
                sale["paid"] = True
                sale["paid_amount"] = 0.0

                for item in sale.get("items", []):
                    for product in products:
                        if product.get("name") == item.get("name"):
                            qty = int(item.get("quantity", 1))
                            product["stock"] = int(product.get("stock", 0)) + qty
                break

        self.save_clients(data)
        self.save_products(products)
        self.load_table()
