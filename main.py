# -*- coding: utf-8 -*-
# Este archivo es el punto de inicio de toda la aplicación. Al abrir este archivo, se arranca el programa.

import customtkinter as ctk
import database
from ui_main import SistemaContableGUI

if __name__ == "__main__":
    # 1. Configurar y preparar la base de datos (donde se guardará la información de cuentas, usuarios y transacciones).
    # Si es la primera vez que se abre el programa, creará el archivo y las opciones iniciales por defecto.
    database.init_db()
    
    # 2. Iniciar la interfaz gráfica de usuario (las ventanas y botones que el usuario ve en pantalla).
    app = SistemaContableGUI()
    
    # 3. Mantener la ventana abierta y a la espera de que el usuario haga clic o interactúe con el programa.
    app.mainloop()

