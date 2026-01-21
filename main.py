import sys
import customtkinter as ctk
from ui.main_window import MainWindow

def main():
    # Inicializar CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Criar e executar aplicação
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
