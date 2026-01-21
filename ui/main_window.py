import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QComboBox, QScrollArea,
    QGridLayout, QMessageBox, QMainWindow, QSizePolicy, QFileDialog, QInputDialog, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction, QKeySequence, QShortcut

from widgets.product_button import ProductButton
from widgets.payment_method_dialog import PaymentMethodDialog, PAYMENT_METHODS
from managers.product_manager import ProductManager
from managers.client_manager import ClientManager
from managers.sales_history_manager import SalesHistoryManager
from reports.report_generator import build_day_report
from reports.excel_export import export_day_report
from utils.file_utils import load_json, save_json
from utils.validators import is_valid_date

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.products_path = "data/products.json"
        self.clients_path = "data/clients.json"
        self.total = 0.0
        self.cart = {}
        self.products_cache = []

        self.setWindowTitle("Cantina Colégio Ativa")
        self.setMinimumSize(1100, 650)

        # ---------------------------
        # MAIN CENTRAL WIDGET
        # ---------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # ---------------------------
        # MENU BAR (macOS + Windows)
        # ---------------------------
        menu_bar = self.menuBar()  # QMainWindow provides this

        # FILE MENU
        file_menu = menu_bar.addMenu("File")

        action_refresh_clients = QAction("Refresh Clients", self)
        action_refresh_clients.triggered.connect(self.populate_client_box)
        file_menu.addAction(action_refresh_clients)

        action_export_xlsx = QAction("Export Day Report", self)
        action_export_xlsx.triggered.connect(self.export_day_report)
        file_menu.addAction(action_export_xlsx)

        file_menu.addSeparator()

        action_quit = QAction("Quit", self)
        action_quit.triggered.connect(self.close)
        file_menu.addAction(action_quit)
        
        # MANAGE PRODUCTS | CLIENTS
        manage_menu = menu_bar.addMenu("Manage")
        
        manage_products_action = QAction("Manage Products", self)
        manage_products_action.triggered.connect(self.open_product_manager)
        manage_menu.addAction(manage_products_action)
        
        manage_clients_action = QAction("Manage Clients", self)
        manage_clients_action.triggered.connect(self.open_client_manager)
        manage_menu.addAction(manage_clients_action)

        manage_sales_action = QAction("Sales History", self)
        manage_sales_action.triggered.connect(self.open_sales_history)
        manage_menu.addAction(manage_sales_action)

        # ---------------------------
        # LEFT PANEL
        # ---------------------------

        left = QVBoxLayout()
        left.setSpacing(15)

        title = QLabel("Cantina Colégio Ativa")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        client_label = QLabel("Cliente:")
        client_label.setFont(QFont("Arial", 14))

        self.client_box = QComboBox()
        self.client_box.setEditable(True)
        self.client_box.setPlaceholderText("Digite ou selecione o cliente")
        self.populate_client_box()

        list_title = QLabel("Itens Selecionados:")
        list_title.setFont(QFont("Arial", 14))

        self.items_list = QListWidget()
        self.items_list.setMinimumHeight(300)

        cart_buttons = QHBoxLayout()
        self.btn_remove_item = QPushButton("Remover")
        self.btn_decrease_item = QPushButton("-")
        self.btn_increase_item = QPushButton("+")
        self.btn_clear_cart = QPushButton("Limpar")

        self.btn_remove_item.clicked.connect(self.remove_selected_item)
        self.btn_decrease_item.clicked.connect(self.decrease_selected_item)
        self.btn_increase_item.clicked.connect(self.increase_selected_item)
        self.btn_clear_cart.clicked.connect(self.clear_cart)

        cart_buttons.addWidget(self.btn_remove_item)
        cart_buttons.addWidget(self.btn_decrease_item)
        cart_buttons.addWidget(self.btn_increase_item)
        cart_buttons.addWidget(self.btn_clear_cart)

        total_label = QLabel("Total:")
        total_label.setFont(QFont("Arial", 18, QFont.Bold))

        self.total_value = QLabel("R$ 0,00")
        self.total_value.setFont(QFont("Arial", 28, QFont.Bold))
        self.total_value.setStyleSheet("color: #27ae60;")

        payment_method_label = QLabel("Modalidade:")
        payment_method_label.setFont(QFont("Arial", 14))
        
        self.payment_method_display = QLabel("Não selecionada")
        self.payment_method_display.setFont(QFont("Arial", 12))
        self.payment_method_display.setStyleSheet("color: #7f8c8d;")
        self.current_payment_method = None

        self.btn_finalizar = QPushButton("Finalizar Venda")
        self.btn_finalizar.setMinimumHeight(60)
        self.btn_finalizar.setFont(QFont("Arial", 18, QFont.Bold))
        self.btn_finalizar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                border-radius: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #44e98b;
            }
        """)
        self.btn_finalizar.clicked.connect(self.finish_order)
        self.btn_finalizar.setToolTip("Finalizar venda (Ctrl+Enter)")

        left.addWidget(title)
        left.addWidget(client_label)
        left.addWidget(self.client_box)
        left.addWidget(list_title)
        left.addWidget(self.items_list)
        left.addLayout(cart_buttons)
        left.addWidget(total_label)
        left.addWidget(self.total_value)
        left.addWidget(payment_method_label)
        left.addWidget(self.payment_method_display)
        left.addWidget(self.btn_finalizar)

        main_layout.addLayout(left, 35)

        # ---------------------------
        # RIGHT PANEL — PRODUCTS
        # ---------------------------

        right_layout = QVBoxLayout()

        product_label = QLabel("Produtos")
        product_label.setFont(QFont("Arial", 20, QFont.Bold))
        product_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(product_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()

        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(12)

        self.load_products(self.grid_layout)

        scroll.setWidget(container)
        right_layout.addWidget(scroll)

        main_layout.addLayout(right_layout, 65)

        QShortcut(QKeySequence("Ctrl+Enter"), self, self.finish_order)
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_cart)

    def open_product_manager(self):
        self.manager = ProductManager(self)
        self.manager.show()

        # reload products in main UI after changes
        self.load_products(self.grid_layout)

    def open_client_manager(self):
        dialog = ClientManager(self)
        dialog.exec()

    def open_sales_history(self):
        dialog = SalesHistoryManager(self, self.clients_path, self.products_path)
        dialog.exec()

    def export_day_report(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_input, ok = QInputDialog.getText(
            self, "Relatório Diário", "Data (YYYY-MM-DD):", text=date_str
        )
        if not ok:
            return

        if not is_valid_date(date_input):
            QMessageBox.warning(self, "Relatório", "Data inválida. Use YYYY-MM-DD.")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"relatorio_{date_input}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not output_path:
            return

        data = self.load_clients() or {}
        report = build_day_report(data, date_input)
        if not report["sales_rows"]:
            QMessageBox.information(self, "Relatório", "Não há vendas para esta data.")
            return

        try:
            export_day_report(report, output_path, date_input)
        except Exception as e:
            QMessageBox.critical(self, "Relatório", f"Erro ao exportar: {e}")
            return

        QMessageBox.information(self, "Relatório", "Relatório exportado com sucesso.")


    def load_products(self, grid_layout, columns=4):
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            
        # Criar arquivo se não existir
        # Criar arquivo se não existir
        if not os.path.exists(self.products_path):
            save_json(self.products_path, [])
        
        products = load_json(self.products_path, [])
        if products is None:
            products = []
        
        if not isinstance(products, list):
            QMessageBox.critical(self, "Produtos", "products.json precisa ser uma lista de objetos.")
            products = []

        self.products_cache = products
        
        row = 0
        col = 0

        for product in products:

            name = product.get("name")
            price = product.get("price")
            stock = product.get("stock", 0)

            if name is None or price is None:
                print(f"Skipping invalid product entry: {product}")
                continue

            stock_text = f"Estoque: {stock}"
            if stock <= 0:
                stock_text = "Sem estoque"
            elif stock <= 5:
                stock_text = f"Estoque baixo: {stock}"
            btn = ProductButton(f"{name}\nR${price:.2f}\n{stock_text}")
            btn.setEnabled(stock > 0)

            btn.clicked.connect(lambda _, n=name, p=price: self.add_to_cart(n, p))

            grid_layout.addWidget(btn, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def load_clients(self):
        if not os.path.exists(self.clients_path):
            return {}

        data = load_json(self.clients_path, None)
        if data is None:
            QMessageBox.critical(self, "Clientes", "Erro ao carregar clientes.")
            return {}
        return data


    def add_to_cart(self, name, price):
        stock = self.get_stock_for_product(name)
        current_qty = self.cart.get(name, {}).get("qty", 0)
        if stock is not None and stock <= current_qty:
            QMessageBox.warning(self, "Estoque", f"Sem estoque disponível para {name}.")
            return
        if name in self.cart:
            self.cart[name]["qty"] += 1
        else:
            self.cart[name] = {"price": price, "qty": 1}
        self.refresh_cart_list()

    def get_stock_for_product(self, name):
        for product in self.products_cache:
            if product.get("name") == name:
                return int(product.get("stock", 0))
        return None

    def update_total(self):
        self.total = sum(item["price"] * item["qty"] for item in self.cart.values())
        self.total_value.setText(f"R$ {self.total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def refresh_cart_list(self):
        self.items_list.clear()
        for name, item in self.cart.items():
            price = item["price"]
            qty = item["qty"]
            total_item = price * qty
            text = f"{name} x{qty} | Unit: R$ {price:.2f} | Total: R$ {total_item:.2f}"
            list_item = self.items_list.addItem(text)
            self.items_list.item(self.items_list.count() - 1).setData(Qt.UserRole, name)
        self.update_total()

    def get_selected_item_name(self):
        selected = self.items_list.currentItem()
        if not selected:
            return None
        return selected.data(Qt.UserRole)

    def remove_selected_item(self):
        name = self.get_selected_item_name()
        if not name:
            return
        self.cart.pop(name, None)
        self.refresh_cart_list()

    def decrease_selected_item(self):
        name = self.get_selected_item_name()
        if not name:
            return
        if name in self.cart:
            self.cart[name]["qty"] -= 1
            if self.cart[name]["qty"] <= 0:
                self.cart.pop(name, None)
        self.refresh_cart_list()

    def increase_selected_item(self):
        name = self.get_selected_item_name()
        if not name:
            return
        if name in self.cart:
            self.cart[name]["qty"] += 1
        self.refresh_cart_list()

    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart_list()

    def finish_order(self):
        client_name = self.client_box.currentText().strip()

        if client_name == "":
            QMessageBox.warning(self, "Cliente", "Selecione ou digite um cliente.")
            return

        if not self.cart:
            QMessageBox.warning(self, "Carrinho", "O carrinho está vazio.")
            return

        # Calculate total and items
        items = []
        total = 0.0
        for name, item in self.cart.items():
            price = item["price"]
            qty = item["qty"]
            line_total = price * qty
            total += line_total
            items.append({
                "name": name,
                "price": price,
                "quantity": qty,
                "line_total": line_total
            })

        # Build order structure
        order = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "total": total
        }

        # Validate stock before saving
        for item in items:
            stock = self.get_stock_for_product(item["name"])
            if stock is not None and item["quantity"] > stock:
                QMessageBox.warning(
                    self,
                    "Estoque",
                    f"Estoque insuficiente para {item['name']}. Disponível: {stock}."
                )
                return

        # Get client data for credit info
        clients_data = self.load_clients()
        available_credit = 0.0
        if client_name in clients_data:
            available_credit = float(clients_data[client_name].get("credits", 0.0))

        # Open payment method dialog
        payment_dialog = PaymentMethodDialog(self, total, available_credit)
        if payment_dialog.exec() != QDialog.Accepted:
            return
        
        payment_info_dialog = payment_dialog.get_payment_info()
        payment_method = payment_info_dialog["method"]
        installments = payment_info_dialog.get("installments", 1)
        
        # Get display name for payment method
        method_display = None
        for display_name, method_key in PAYMENT_METHODS.items():
            if method_key == payment_method:
                method_display = display_name
                break
        
        confirm_text = f"Confirmar venda de {client_name} no valor de R$ {total:.2f}?\nModalidade: {method_display or payment_method}"
        if payment_method == "parcelado":
            confirm_text += f"\nParcelas: {installments}x de R$ {total/installments:.2f}"
        
        confirm = QMessageBox.question(
            self,
            "Confirmar Venda",
            confirm_text,
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        # Add payment method to order
        order["payment_method"] = payment_method
        order["payment_method_display"] = method_display or payment_method
        order["installments"] = installments

        # Save to JSON
        payment_info = self.add_order_to_client(client_name, order)

        # Format total for display
        total_display = f"R$ {total:.2f}".replace(".", ",")

        # SHOW POPUP
        credit_used = payment_info.get("credit_used", 0.0)
        remaining = payment_info.get("remaining", 0.0)
        if credit_used > 0 and remaining > 0:
            payment_text = f"Crédito usado: R$ {credit_used:.2f} | Restante: R$ {remaining:.2f}"
        elif credit_used > 0:
            payment_text = f"Crédito usado: R$ {credit_used:.2f}"
        else:
            payment_text = "Sem uso de crédito"

        payment_method_display = order.get("payment_method_display", "N/A")
        message = f"Venda finalizada para {client_name} no valor de {total_display}.\nModalidade: {payment_method_display}"
        if payment_method == "parcelado":
            installments = order.get("installments", 1)
            installment_value = total / installments
            message += f"\nParcelas: {installments}x de R$ {installment_value:.2f}"
        message += f"\n{payment_text}"
        
        QMessageBox.information(
            self,
            "Venda Finalizada",
            message
        )

        # Reset UI
        self.update_stock_after_sale(items)
        self.cart.clear()
        self.refresh_cart_list()
        self.current_payment_method = None
        self.payment_method_display.setText("Não selecionada")
        self.payment_method_display.setStyleSheet("color: #7f8c8d;")

        print(f"Order saved for {client_name}.")
        self.total = 0.0 
        
        self.populate_client_box()
    
    def populate_client_box(self):
        self.client_box.clear()

        data = self.load_clients() or {}

        for client_name in sorted(data):
            self.client_box.addItem(client_name)
            
    def save_clients(self, data):
        save_json(self.clients_path, data)
            
    def add_order_to_client(self, client_name, order):
        data = self.load_clients()

        # If client does not exist → create
        if client_name not in data:
            data[client_name] = {
                "credits": 0.0,
                "sales": [],
                "credit_history": []
            }

        client = data[client_name]
        client.setdefault("sales", [])
        client.setdefault("credit_history", [])

        # Handle credit usage based on payment method
        payment_method = order.get("payment_method", "vista")
        credits_available = float(client.get("credits", 0.0))
        credit_used = 0.0
        remaining = order["total"]
        is_paid = False
        
        # Determine payment status based on payment method
        if payment_method == "credito":
            # Crédito: use available credit
            credit_used = min(credits_available, order["total"])
            remaining = order["total"] - credit_used
            client["credits"] = max(credits_available - credit_used, 0.0)
            is_paid = remaining == 0
            
            if credit_used > 0:
                client["credit_history"].append({
                    "timestamp": order["timestamp"],
                    "delta": -credit_used,
                    "reason": "Pagamento de venda"
                })
        elif payment_method in ["vista", "pix", "debito", "cartao_credito", "cartao_debito"]:
            # These methods are fully paid immediately
            is_paid = True
            remaining = 0.0
            credit_used = 0.0
        elif payment_method == "parcelado":
            # Parcelado: nothing paid initially, stays as pending
            is_paid = False
            remaining = order["total"]
            credit_used = 0.0
        
        client["sales"].append({
            "id": len(client["sales"]) + 1,
            "items": order["items"],
            "total": order["total"],
            "paid": is_paid,
            "paid_amount": order["total"] if is_paid else credit_used,
            "date": order["timestamp"].split(" ")[0],
            "cancelled": False,
            "payment_method": payment_method,
            "payment_method_display": order.get("payment_method_display", payment_method),
            "installments": order.get("installments", 1)
        })

        self.save_clients(data)
        return {"credit_used": credit_used, "remaining": remaining}

    def update_stock_after_sale(self, items):
        products = load_json(self.products_path, None)
        if products is None:
            return

        for product in products:
            for item in items:
                if product.get("name") == item["name"]:
                    stock = int(product.get("stock", 0))
                    product["stock"] = max(stock - item["quantity"], 0)

        save_json(self.products_path, products)

        self.load_products(self.grid_layout)