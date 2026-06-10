# -*- coding: utf-8 -*-
import customtkinter as ctk
import database
from ui_main import SistemaContableGUI

if __name__ == "__main__":
    # Inicializar la base de datos y poblar catálogo si está vacía
    database.init_db()
    
    # Iniciar la aplicación
    app = SistemaContableGUI()
    app.mainloop()
