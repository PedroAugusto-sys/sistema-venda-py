import os, json
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QComboBox, QScrollArea,
    QGridLayout, QMessageBox, QMainWindow, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QAction

from widgets.product_button import ProductButton
from managers.product_manager import ProductManager
from managers.client_manager import ClientManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.products_path = "data/products.json"
        self.clients_path = "data/clients.json"
        self.total = 0.0

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

        total_label = QLabel("Total:")
        total_label.setFont(QFont("Arial", 18, QFont.Bold))

        self.total_value = QLabel("R$ 0,00")
        self.total_value.setFont(QFont("Arial", 28, QFont.Bold))
        self.total_value.setStyleSheet("color: #27ae60;")

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

        left.addWidget(title)
        left.addWidget(client_label)
        left.addWidget(self.client_box)
        left.addWidget(list_title)
        left.addWidget(self.items_list)
        left.addWidget(total_label)
        left.addWidget(self.total_value)
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

    def action_export_xlsx(self):
        pass
    
    def open_product_manager(self):
        self.manager = ProductManager(self)
        self.manager.show()

        # reload products in main UI after changes
        self.load_products(self.grid_layout)

    def open_client_manager(self):
        dialog = ClientManager(self)
        dialog.exec()

    def load_products(self, grid_layout, columns=4):
        while grid_layout.count():
            item = grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            
        if not os.path.exists(self.products_path):
            return
        
        try:
            with open(self.products_path, "r", encoding="utf-8") as f:
                products = json.load(f)
        except Exception as e:
            print(f"ERROR loading products.json: {e}")
            return
        
        if not isinstance(products, list):
            print("ERROR: products.json must contain a list of objects")
            return
        
        row = 0
        col = 0

        for product in products:

            name = product.get("name")
            price = product.get("price")

            if name is None or price is None:
                print(f"Skipping invalid product entry: {product}")
                continue

            btn = ProductButton(f"{name}\nR${price:.2f}")

            btn.clicked.connect(lambda _, n=name, p=price: self.add_to_cart(n, p))

            grid_layout.addWidget(btn, row, col)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def load_clients(self):
        if not os.path.exists(self.clients_path):
            return {}

        with open(self.clients_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def add_to_cart(self, name, price):
        self.items_list.addItem(f"{name} - R$ {price:.2f}")

        # Use internal total
        self.total += price

        # Update UI
        formatted = f"R$ {self.total:.2f}".replace(".", ",")
        self.total_value.setText(formatted)

    def update_total(self):
        self.total_value.setText(f"R$ {self.total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def finish_order(self):
        client_name = self.client_box.currentText().strip()

        if client_name == "":
            print("Select or enter a client name.")
            return

        # Extract selected items
        items = []
        for i in range(self.items_list.count()):
            text = self.items_list.item(i).text()  # "Coxinha - R$ 5,00"
            name, value = text.split(" - R$ ")
            price = float(value.replace(",", "."))
            items.append({"name": name, "price": price})

        if not items:
            print("Cart is empty.")
            return

        # Calculate total
        total_text = self.total_value.text().replace("R$ ", "").replace(",", ".")
        total = float(total_text)

        # Build order structure
        order = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "total": total
        }

        # Save to JSON
        self.add_order_to_client(client_name, order)

        # Format total for display
        total_display = f"R$ {total:.2f}".replace(".", ",")

        # SHOW POPUP
        QMessageBox.information(
            self,
            "Venda Finalizada",
            f"Venda finalizada para {client_name} no valor de {total_display}."
        )

        # Reset UI
        self.items_list.clear()
        self.total_value.setText("R$ 0,00")

        print(f"Order saved for {client_name}.")
        
        self.items_list.clear()
        self.total_value.setText("R$ 0,00")
        self.total = 0.0 
        
        self.populate_client_box()
    
    def populate_client_box(self):
        self.client_box.clear()

        data = self.load_clients() or {}

        for client_name in sorted(data):
            self.client_box.addItem(client_name)
            
    def save_clients(self, data):
        with open(self.clients_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    def add_order_to_client(self, client_name, order):
        data = self.load_clients()

        # If client already exists
        if client_name in data:
            client = data[client_name]

            client["sales"].append({
                "id": len(client["sales"]) + 1,
                "items": order["items"],
                "total": order["total"],
                "paid": False,
                "date": order["timestamp"].split(" ")[0]
            })

            self.save_clients(data)
            return

        # If client does not exist → create
        data[client_name] = {
            "credits": 0.0,
            "sales": [
                {
                    "id": 1,
                    "items": order["items"],
                    "total": order["total"],
                    "date": order["timestamp"].split(" ")[0]
                }
            ]
        }

        self.save_clients(data)
        self.populate_client_box()