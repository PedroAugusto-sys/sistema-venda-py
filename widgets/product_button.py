from PySide6.QtWidgets import QPushButton, QSizePolicy

class ProductButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumSize(150, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f2c94c;
                border: 2px solid #e5b53f;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f7d878;
            }
        """)