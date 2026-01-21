from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QMessageBox, QDialog, 
    QTableWidget, QTableWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt
from utils.file_utils import load_json, save_json

CLIENTS_FILE = "data/clients.json"

def load_clients():
    return load_json(CLIENTS_FILE, {})

def save_clients(data):
    save_json(CLIENTS_FILE, data)

class ClientManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Clients")
        self.resize(600, 400)

        self.clients = load_clients()

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Name", "Credits (R$)", "Owes (R$)", "Paid"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.close_btn = QPushButton("Close")

        self.save_btn.clicked.connect(self.save_changes)
        self.close_btn.clicked.connect(self.close)

        btn_layout.addStretch()
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
                if not sale.get("paid", False) and not sale.get("cancelled", False)
            )

            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            credits_item = QTableWidgetItem(f"{credits:.2f}")
            credits_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, credits_item)

            owes_item = QTableWidgetItem(f"{owes:.2f}")
            owes_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            owes_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, owes_item)

            checkbox = QCheckBox()
            checkbox.setChecked(owes == 0)

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(row, 3, container)

    def save_changes(self):
        self.table.clearFocus()
        
        data = load_clients()
        invalid_credit = False

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()

            try:
                credits = float(self.table.item(row, 1).text())
            except (TypeError, ValueError):
                credits = 0.0
                invalid_credit = True
            if credits < 0:
                credits = 0.0
                invalid_credit = True

            cell_widget = self.table.cellWidget(row, 3)
            checkbox = cell_widget.findChild(QCheckBox)

            paid = checkbox.isChecked() if checkbox else False

            if name not in data:
                continue

            prev_credits = float(data[name].get("credits", 0.0))
            data[name]["credits"] = credits
            data[name].setdefault("credit_history", [])
            if credits != prev_credits:
                data[name]["credit_history"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "delta": credits - prev_credits,
                    "reason": "Ajuste manual de crédito"
                })

            if paid:
                for sale in data[name].get("sales", []):
                    sale["paid"] = True
                    sale["paid_amount"] = sale.get("total", 0.0)

        save_clients(data)

        message = "Client payments updated successfully."
        if invalid_credit:
            message = "Client payments updated. Créditos inválidos foram ajustados para 0."
        QMessageBox.information(self, "Saved", message)

        self.load_table()
