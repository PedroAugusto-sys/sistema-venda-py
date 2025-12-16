import os, sys, json
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QMessageBox, QDialog, 
    QTableWidget, QTableWidgetItem, QCheckBox
)
from PySide6.QtCore import Qt

CLIENTS_FILE = "data/clients.json"

def load_clients():
    with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_clients(data):
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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

            # Paid checkbox
            checkbox = QCheckBox()

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)

            self.table.setCellWidget(row, 3, container)

    def save_changes(self):
        self.table.clearFocus()
        
        data = load_clients()

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()

            credits = float(self.table.item(row, 1).text())
            owes = float(self.table.item(row, 2).text())

            cell_widget = self.table.cellWidget(row, 3)
            checkbox = cell_widget.findChild(QCheckBox)

            paid = checkbox.isChecked() if checkbox else False

            data[name]["credits"] = credits
            data[name]["paid"] = paid

        save_clients(data)

        QMessageBox.information(
            self, "Saved", "Client payments updated successfully."
        )

        self.load_table()
