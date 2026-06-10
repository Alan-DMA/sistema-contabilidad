# -*- coding: utf-8 -*-
import customtkinter as ctk
from ui_views import DiarioView, MayorView, BalanceComprobacionView, EstadosFinancierosView, CierreView

class SistemaContableGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema Contable v1.0")
        self.geometry("1100x700")
        
        # Configurar tema oscuro y verde según la CONSTITUCION
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Grid layout: 1 fila, 2 columnas (Menu, Contenido)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # ============ MENU LATERAL ============
        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.menu_frame.grid(row=0, column=0, sticky="nsew")
        self.menu_frame.grid_rowconfigure(6, weight=1) # Empujar botones hacia arriba
        
        self.logo_label = ctk.CTkLabel(self.menu_frame, text="Contabilidad v1.0", font=ctk.CTkFont(family="Roboto", size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))
        
        self.btn_diario = ctk.CTkButton(self.menu_frame, text="Libro Diario", command=lambda: self.mostrar_vista("Diario"))
        self.btn_diario.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_mayor = ctk.CTkButton(self.menu_frame, text="Libro Mayor", command=lambda: self.mostrar_vista("Mayor"))
        self.btn_mayor.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_balance = ctk.CTkButton(self.menu_frame, text="Balance de Comp.", command=lambda: self.mostrar_vista("Balance"))
        self.btn_balance.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_estados = ctk.CTkButton(self.menu_frame, text="Estados Financieros", command=lambda: self.mostrar_vista("Estados"))
        self.btn_estados.grid(row=4, column=0, padx=20, pady=10)
        
        self.btn_cierre = ctk.CTkButton(self.menu_frame, text="Cierre Contable", fg_color="#8B0000", hover_color="#5C0000", command=lambda: self.mostrar_vista("Cierre"))
        self.btn_cierre.grid(row=5, column=0, padx=20, pady=(40, 10))
        
        # ============ AREA DE CONTENIDO ============
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Diccionario de vistas
        self.vistas = {
            "Diario": DiarioView(self.content_frame),
            "Mayor": MayorView(self.content_frame),
            "Balance": BalanceComprobacionView(self.content_frame),
            "Estados": EstadosFinancierosView(self.content_frame),
            "Cierre": CierreView(self.content_frame)
        }
        
        # Mostrar vista inicial
        self.mostrar_vista("Diario")
        
    def mostrar_vista(self, nombre_vista):
        # Ocultar todas las vistas
        for vista in self.vistas.values():
            vista.grid_forget()
            
        # Mostrar la vista seleccionada y actualizarla si tiene el método
        vista_activa = self.vistas[nombre_vista]
        vista_activa.grid(row=0, column=0, sticky="nsew")
        if hasattr(vista_activa, "actualizar_datos"):
            vista_activa.actualizar_datos()
