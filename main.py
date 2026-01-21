import os
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import get_logger
from utils.file_utils import load_json, save_json

def initialize_data_files():
    """Inicializa os arquivos JSON necessários se não existirem"""
    os.makedirs("data", exist_ok=True)
    
    # Inicializar products.json se não existir
    products_path = "data/products.json"
    if not os.path.exists(products_path):
        save_json(products_path, [])
        print(f"Arquivo {products_path} criado.")
    
    # Inicializar clients.json se não existir
    clients_path = "data/clients.json"
    if not os.path.exists(clients_path):
        save_json(clients_path, {})
        print(f"Arquivo {clients_path} criado.")

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    get_logger()
    initialize_data_files()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
    