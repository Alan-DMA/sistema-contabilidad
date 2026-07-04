# -*- coding: utf-8 -*-
# Este archivo contiene la ventana principal del sistema (el contenedor o marco general).
# Diseña el menú lateral izquierdo (Sidebar) y controla el cambio entre las diferentes pantallas de la aplicación.

import customtkinter as ctk
from ui_views import LoginView, RegistroDiarioView, ReporteDiarioView, MayorView, BalanceComprobacionView, EstadosFinancierosView, CierreView, GestionCuentasView, DashboardView

class SistemaContableGUI(ctk.CTk):
    # Esta es la clase principal que abre y da estilo a la ventana principal de la aplicación.
    def __init__(self):
        super().__init__()
        
        self.title("AuraBooks v1.5")
        self.geometry("1200x800")
        
        # Fijar modo de apariencia en Claro y configurar el fondo
        ctk.set_appearance_mode("light")
        self.configure(fg_color="#F8FAFC")
        
        # Configurar la cuadrícula básica para que la ventana se estire fluidamente
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.usuario_actual = None
        # Al abrir la aplicación por primera vez, mostrar la pantalla de Login
        self.mostrar_login()
        
    def mostrar_login(self):
        # Limpia cualquier ventana/botón de la pantalla y dibuja el formulario de inicio de sesión.
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_view = LoginView(self, self.iniciar_dashboard)
        self.login_view.grid(row=0, column=0, sticky="nsew")
        
    def iniciar_dashboard(self, usuario):
        # Esta función se activa cuando el usuario inicia sesión correctamente.
        # Dibuja la barra de menú lateral (Sidebar) y prepara el lienzo de trabajo a la derecha.
        self.usuario_actual = usuario
        
        for widget in self.winfo_children():
            widget.destroy()
            
        # Reconfigurar cuadrícula: Columna 0 es para el Menú Lateral, Columna 1 es para el Contenido de la derecha
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Sidebar fija
        self.grid_columnconfigure(1, weight=1) # Contenido estirable
        
        # ============ MENÚ LATERAL (SIDEBAR) ============
        self.sidebar = ctk.CTkFrame(self, width=264, fg_color="#FFFFFF", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(9, weight=1)
        
        # Header Sidebar
        self.header_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.header_f.grid(row=0, column=0, padx=20, pady=(30, 0), sticky="ew")
        
        import os
        logo_path = "logo.png"
        img_ctk = None
        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageDraw
                img = Image.open(logo_path).convert("RGBA")
                size = min(img.size)
                img = img.crop(((img.width - size) // 2, (img.height - size) // 2, (img.width + size) // 2, (img.height + size) // 2))
                img = img.resize((110, 110), Image.Resampling.LANCZOS)
                
                mask = Image.new("L", (110, 110), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 110, 110), fill=255)
                
                output = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
                output.paste(img, (0, 0), mask=mask)
                
                img_ctk = ctk.CTkImage(light_image=output, dark_image=output, size=(110, 110))
            except Exception as e:
                print("Error loading logo:", e)
                
        if img_ctk:
            self.logo_icon = ctk.CTkLabel(self.header_f, text="", image=img_ctk)
            self.logo_icon.pack(pady=(0, 15))
            
        title_f = ctk.CTkFrame(self.header_f, fg_color="transparent")
        title_f.pack()
            
        self.logo_lbl = ctk.CTkLabel(title_f, text="AuraBooks", font=ctk.CTkFont(size=24, weight="bold"), text_color="#111827")
        self.logo_lbl.pack(side="left")
        
        self.version_lbl = ctk.CTkLabel(title_f, text="v1.5", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10B981")
        self.version_lbl.pack(side="left", padx=(5, 0), anchor="s", pady=(0, 4))
        
        self.user_lbl = ctk.CTkLabel(self.sidebar, text=f"{usuario['rol']} ({usuario['username']})", font=ctk.CTkFont(size=14), text_color="#6B7280")
        self.user_lbl.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")
        
        btn_kwargs = {
            "fg_color": "transparent",
            "text_color": "#374151",
            "hover_color": "#F3F4F6",
            "anchor": "w",
            "font": ctk.CTkFont(size=17)
        }
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.mostrar_vista("Dashboard"), **btn_kwargs)
        self.btn_dashboard.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_nuevo = ctk.CTkButton(self.sidebar, text="Nuevo Asiento", command=lambda: self.mostrar_vista("Nuevo"), **btn_kwargs)
        self.btn_nuevo.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_diario = ctk.CTkButton(self.sidebar, text="Libro Diario", command=lambda: self.mostrar_vista("Diario"), **btn_kwargs)
        self.btn_diario.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_mayor = ctk.CTkButton(self.sidebar, text="Libro Mayor", command=lambda: self.mostrar_vista("Mayor"), **btn_kwargs)
        self.btn_mayor.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_reportes = ctk.CTkButton(self.sidebar, text="Reportes", command=lambda: self.mostrar_vista("Reportes"), **btn_kwargs)
        self.btn_reportes.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_cuentas = ctk.CTkButton(self.sidebar, text="Catálogo de Cuentas", command=lambda: self.mostrar_vista("Cuentas"), **btn_kwargs)
        self.btn_cuentas.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_cierre = ctk.CTkButton(self.sidebar, text="Cierre Contable", command=lambda: self.mostrar_vista("Cierre"), **btn_kwargs)
        self.btn_cierre.grid(row=8, column=0, padx=10, pady=5, sticky="ew")
        
        # Logout alineado abajo
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", command=self.mostrar_login, **btn_kwargs)
        self.btn_logout.grid(row=10, column=0, padx=10, pady=20, sticky="ew")
        
        # ============ CONTENIDO PRINCIPAL ============
        self.main_content = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        self.top_bar = ctk.CTkFrame(self.main_content, fg_color="transparent", height=50)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.lbl_titulo_vista = ctk.CTkLabel(self.top_bar, text="Dashboard", font=ctk.CTkFont(size=26, weight="bold"), text_color="#111827")
        self.lbl_titulo_vista.pack(side="left")
        
        self.view_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.view_container.grid(row=1, column=0, sticky="nsew")
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)
        
        self.vistas = {
            "Dashboard": DashboardView(self.view_container),
            "Nuevo": RegistroDiarioView(self.view_container),
            "Diario": ReporteDiarioView(self.view_container),
            "Mayor": MayorView(self.view_container),
            "Reportes": EstadosFinancierosView(self.view_container),
            "Cuentas": GestionCuentasView(self.view_container),
            "Cierre": CierreView(self.view_container)
        }
        
        self.mostrar_vista("Dashboard")
        
    def mostrar_vista(self, nombre_vista):
        self.lbl_titulo_vista.configure(text=nombre_vista)
        
        botones = {
            "Dashboard": self.btn_dashboard,
            "Nuevo": self.btn_nuevo,
            "Diario": self.btn_diario,
            "Mayor": self.btn_mayor,
            "Reportes": self.btn_reportes,
            "Cuentas": self.btn_cuentas,
            "Cierre": self.btn_cierre
        }
        
        for nombre, btn in botones.items():
            if nombre == nombre_vista:
                btn.configure(fg_color="#E5E7EB", text_color="#111827", font=ctk.CTkFont(size=17, weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#374151", font=ctk.CTkFont(size=17, weight="normal"))
                
        for vista in self.vistas.values():
            vista.grid_forget()
            
        vista_activa = self.vistas.get(nombre_vista)
        if vista_activa:
            vista_activa.grid(row=0, column=0, sticky="nsew")
            if hasattr(vista_activa, "actualizar_datos"):
                vista_activa.actualizar_datos()
