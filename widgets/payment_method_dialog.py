from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QRadioButton, QButtonGroup, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

PAYMENT_METHODS = {
    "À Vista": "vista",
    "Crédito (Fiado)": "credito",
    "Parcelado": "parcelado",
    "Débito": "debito",
    "PIX": "pix",
    "Cartão de Crédito": "cartao_credito",
    "Cartão de Débito": "cartao_debito"
}

class PaymentMethodDialog(QDialog):
    def __init__(self, parent=None, total=0.0, available_credit=0.0):
        super().__init__(parent)
        self.setWindowTitle("Modalidade de Pagamento")
        self.setMinimumWidth(400)
        self.payment_method = None
        self.installments = 1
        self.total = total
        self.available_credit = available_credit
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Selecione a Modalidade de Pagamento")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        total_label = QLabel(f"Total: R$ {total:.2f}")
        total_label.setFont(QFont("Arial", 14))
        total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(total_label)
        
        if available_credit > 0:
            credit_label = QLabel(f"Crédito Disponível: R$ {available_credit:.2f}")
            credit_label.setFont(QFont("Arial", 12))
            credit_label.setStyleSheet("color: #27ae60;")
            credit_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(credit_label)
        
        self.button_group = QButtonGroup(self)
        self.radio_buttons = {}
        
        for display_name, method_key in PAYMENT_METHODS.items():
            radio = QRadioButton(display_name)
            self.radio_buttons[method_key] = radio
            self.button_group.addButton(radio)
            layout.addWidget(radio)
        
        if "vista" in self.radio_buttons:
            self.radio_buttons["vista"].setChecked(True)
        
        installments_layout = QHBoxLayout()
        installments_layout.addWidget(QLabel("Número de Parcelas:"))
        self.installments_input = QLineEdit()
        self.installments_input.setText("1")
        self.installments_input.setEnabled(False)
        self.installments_input.setMaximumWidth(80)
        installments_layout.addWidget(self.installments_input)
        installments_layout.addStretch()
        layout.addLayout(installments_layout)
        
        for method_key, radio in self.radio_buttons.items():
            radio.toggled.connect(lambda checked, key=method_key: self.on_method_changed(key, checked))
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_confirm = QPushButton("Confirmar")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm.clicked.connect(self.accept_payment)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)
    
    def on_method_changed(self, method_key, checked):
        if checked and method_key == "parcelado":
            self.installments_input.setEnabled(True)
        else:
            self.installments_input.setEnabled(False)
            if not checked:
                self.installments_input.setText("1")
    
    def accept_payment(self):
        selected_method = None
        for method_key, radio in self.radio_buttons.items():
            if radio.isChecked():
                selected_method = method_key
                break
        
        if not selected_method:
            QMessageBox.warning(self, "Modalidade", "Selecione uma modalidade de pagamento.")
            return
        
        if selected_method == "parcelado":
            try:
                installments = int(self.installments_input.text())
                if installments < 1:
                    QMessageBox.warning(self, "Parcelas", "Número de parcelas deve ser maior que 0.")
                    return
                self.installments = installments
            except ValueError:
                QMessageBox.warning(self, "Parcelas", "Número de parcelas inválido.")
                return
        
        self.payment_method = selected_method
        self.accept()
    
    def get_payment_info(self):
        return {
            "method": self.payment_method,
            "installments": self.installments if self.payment_method == "parcelado" else 1
        }
