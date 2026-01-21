import json
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Name", "Credits (R$)", "Owes (R$)"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.settle_btn = QPushButton("Settle Debts")
        self.save_btn = QPushButton("Save")
        self.close_btn = QPushButton("Close")

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

        QMessageBox.information(
            self, "Saved", "Changes saved successfully."
        )

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
            QMessageBox.information(
                self,
                "Nothing to Settle",
                "No clients have enough credits to settle their debts."
            )
            return

        reply = QMessageBox.question(
            self,
            "Settle Debts",
            (
                f"{len(payable_clients)} client(s) can have their debts settled.\n\n"
                "Do you want to proceed and use credits to pay all possible debts?"
            ),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Aplica abatimento
        for name, credits, owes in payable_clients:
            client = data[name]

            client["credits"] = round(credits - owes, 2)

            for sale in client.get("sales", []):
                sale["paid"] = True

        save_clients(data)

        QMessageBox.information(
            self,
            "Done",
            "Debts settled successfully."
        )

        self.load_table()
