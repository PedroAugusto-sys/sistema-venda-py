import json
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

CLIENTS_FILE = "data/clients.json"

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

def load_clients():
    with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_clients(data):
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


class ClientManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Clientes")
        self.resize(600, 400)
        
        # Aplicar tema escuro
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS["bg_dark"]};
                color: {COLORS["text_light"]};
            }}
            QTableWidget {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                border: 1px solid #3a3a3a;
                gridline-color: #3a3a3a;
            }}
            QHeaderView::section {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {COLORS["green"]};
            }}
            QTableWidget::item {{
                background-color: {COLORS["bg_panel"]};
                color: {COLORS["text_light"]};
                padding: 5px;
            }}
            QTableWidget::item:selected {{
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

        self.clients = load_clients()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Nome", "Créditos (R$)", "Deve (R$)"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.settle_btn = QPushButton("Quitar Dívidas")
        self.settle_btn.setStyleSheet(f"""
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
        
        self.save_btn = QPushButton("Salvar")
        self.save_btn.setStyleSheet(f"""
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
        
        self.close_btn = QPushButton("Fechar")
        self.close_btn.setStyleSheet(f"""
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

        self.settle_btn.clicked.connect(self.settle_debts)
        self.save_btn.clicked.connect(self.save_changes)
        self.close_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(self.settle_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        self.load_table()

    def load_table(self):
        self.clients = load_clients()
        self.table.setRowCount(len(self.clients))

        for row, (name, data) in enumerate(self.clients.items()):
            credits = data.get("credits", 0.0)

            owes = sum(
                sale["total"]
                for sale in data.get("sales", [])
                if not sale.get("paid", False)
            )

            # Name (read-only)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            # Credits (editable)
            credits_item = QTableWidgetItem(f"{credits:.2f}")
            credits_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, credits_item)

            # Owes (read-only)
            owes_item = QTableWidgetItem(f"{owes:.2f}")
            owes_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            owes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, owes_item)

    def save_changes(self):
        self.table.clearFocus()
        data = load_clients()

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            credits = float(self.table.item(row, 1).text())

            data[name]["credits"] = credits

        save_clients(data)

        msg = QMessageBox(self)
        msg.setWindowTitle("Salvo")
        msg.setText("Alterações salvas com sucesso.")
        msg.setIcon(QMessageBox.Information)
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
        msg.exec()

        self.load_table()

    def settle_debts(self):
        data = load_clients()

        payable_clients = []

        # Identifica quem pode quitar
        for name, client in data.items():
            credits = client.get("credits", 0.0)
            owes = sum(
                sale["total"]
                for sale in client.get("sales", [])
                if not sale.get("paid", False)
            )

            if owes > 0 and credits >= owes:
                payable_clients.append((name, credits, owes))

        if not payable_clients:
            msg = QMessageBox(self)
            msg.setWindowTitle("Nada para Quitar")
            msg.setText("Nenhum cliente possui créditos suficientes para quitar suas dívidas.")
            msg.setIcon(QMessageBox.Information)
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
            msg.exec()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Quitar Dívidas")
        msg.setText(
            f"{len(payable_clients)} cliente(s) podem ter suas dívidas quitadas.\n\n"
            "Deseja prosseguir e usar os créditos para pagar todas as dívidas possíveis?"
        )
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
        reply = msg.exec()

        if reply != QMessageBox.Yes:
            return

        # Aplica abatimento
        for name, credits, owes in payable_clients:
            client = data[name]

            client["credits"] = round(credits - owes, 2)

            for sale in client.get("sales", []):
                sale["paid"] = True

        save_clients(data)

        msg = QMessageBox(self)
        msg.setWindowTitle("Concluído")
        msg.setText("Dívidas quitadas com sucesso.")
        msg.setIcon(QMessageBox.Information)
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
        msg.exec()

        self.load_table()
