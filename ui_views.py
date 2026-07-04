# -*- coding: utf-8 -*-
# Este archivo contiene los diseños y el comportamiento visual de cada una de las pantallas
# individuales del sistema contable (Login, Registro Diario, Libros Diario y Mayor, Reportes, Cuentas y Cierre).

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import database
import logic
import export_pdf

class LoginView(ctk.CTkFrame):
    # Pantalla de Login: Muestra el formulario para escribir correo y contraseña
    # y valida las credenciales del usuario para permitir el ingreso.
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="#F8FAFC")
        self.on_login_success = on_login_success
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Tarjeta central blanca
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        card.grid(row=0, column=0)
        
        # Centrar contenido en la tarjeta
        card.grid_columnconfigure(0, weight=1)
        
        import os
        img_ctk = None
        if os.path.exists("logo.png"):
            try:
                from PIL import Image, ImageDraw
                img = Image.open("logo.png").convert("RGBA")
                size = min(img.size)
                img = img.crop(((img.width - size) // 2, (img.height - size) // 2, (img.width + size) // 2, (img.height + size) // 2))
                img = img.resize((140, 140), Image.Resampling.LANCZOS)
                
                mask = Image.new("L", (140, 140), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 140, 140), fill=255)
                
                output = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
                output.paste(img, (0, 0), mask=mask)
                
                img_ctk = ctk.CTkImage(light_image=output, dark_image=output, size=(140, 140))
            except Exception:
                pass
                
        if img_ctk:
            ctk.CTkLabel(card, text="", image=img_ctk).grid(row=0, column=0, pady=(30, 0))
            
        ctk.CTkLabel(card, text="AuraBooks v1.5", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#111827").grid(row=1, column=0, pady=(20, 5))
        ctk.CTkLabel(card, text="Acceso al portal financiero", font=ctk.CTkFont(size=16), text_color="#6B7280").grid(row=2, column=0, pady=(0, 30))
        
        # Frame para formulario
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.grid(row=3, column=0, sticky="ew", padx=40)
        form.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(form, text="Correo electrónico", font=ctk.CTkFont(size=14), text_color="#374151").grid(row=0, column=0, sticky="w")
        self.entry_user = ctk.CTkEntry(form, height=46, width=368, placeholder_text="tu@empresa.com", border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827")
        self.entry_user.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        
        # Contraseña con header y link
        pass_header = ctk.CTkFrame(form, fg_color="transparent")
        pass_header.grid(row=2, column=0, sticky="ew")
        pass_header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pass_header, text="Contraseña", font=ctk.CTkFont(size=14), text_color="#374151").grid(row=0, column=0, sticky="w")
        btn_olvido = ctk.CTkLabel(pass_header, text="¿Olvidaste tu contraseña?", font=ctk.CTkFont(size=14), text_color="#3B82F6", cursor="hand2")
        btn_olvido.grid(row=0, column=1, sticky="e")
        btn_olvido.bind("<Button-1>", lambda e: messagebox.showinfo("Recuperar contraseña", "Por favor, comunícate con el administrador del sistema para restablecer tu contraseña."))
        
        self.entry_pass = ctk.CTkEntry(form, height=46, width=368, placeholder_text="••••••••", show="*", border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827")
        self.entry_pass.grid(row=3, column=0, sticky="ew", pady=(5, 20))
        
        self.btn_login = ctk.CTkButton(form, text="Iniciar Sesión \u2192", height=46, fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(size=16, weight="bold"), command=self.hacer_login)
        self.btn_login.grid(row=4, column=0, sticky="ew", pady=(10, 20))
        
        # Footer
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=5, column=0, pady=(10, 20))
        ctk.CTkLabel(footer, text="¿No tienes una cuenta?", font=ctk.CTkFont(size=14), text_color="#6B7280").grid(row=0, column=0, padx=(0, 5))
        ctk.CTkLabel(footer, text="Solicitar acceso", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10B981", cursor="hand2").grid(row=0, column=1)

    def hacer_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Error", "Ingrese usuario y contraseña")
            return
            
        usuario_db = database.autenticar_usuario(user, pwd)
        if usuario_db:
            self.on_login_success(usuario_db)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

class RegistroDiarioView(ctk.CTkFrame):
    # Pantalla de Nuevo Asiento: Formulario con filas dinámicas para que el usuario ingrese
    # la fecha, concepto y los montos en el Debe y el Haber para registrar una nueva transacción.
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header (Título y Botón Guardar)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_frame, text="Nuevo Asiento Contable", font=ctk.CTkFont(size=26, weight="bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Registre una nueva transacción en el libro diario.", font=ctk.CTkFont(size=15), text_color="#6B7280").pack(anchor="w")
        
        self.btn_guardar_top = ctk.CTkButton(header_frame, text="Guardar Asiento", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), command=self.guardar_asiento)
        self.btn_guardar_top.grid(row=0, column=2, sticky="e")
        
        # Tarjeta Blanca Principal
        self.card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        self.card.grid(row=1, column=0, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(2, weight=1)
        
        # Formulario Superior
        form_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        form_frame.grid_columnconfigure(1, weight=1)
        
        fecha_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fecha_frame.grid(row=0, column=0, sticky="w", padx=(0, 20))
        ctk.CTkLabel(fecha_frame, text="Fecha", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.entry_fecha = ctk.CTkEntry(fecha_frame, width=200, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(pady=(5, 0))
        
        concepto_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        concepto_frame.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(concepto_frame, text="Concepto / Glosa", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.entry_concepto = ctk.CTkEntry(concepto_frame, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827", placeholder_text="Ej: Compra de mercadería con factura...")
        self.entry_concepto.pack(fill="x", pady=(5, 0))
        
        # Tabla Headers
        headers_frame = ctk.CTkFrame(self.card, fg_color="#F9FAFB", corner_radius=0, height=40)
        headers_frame.grid(row=1, column=0, sticky="ew", padx=20)
        headers_frame.grid_propagate(False)
        headers_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(headers_frame, text="Cuenta Contable", font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ctk.CTkLabel(headers_frame, text="Debe", font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151", width=120, anchor="e").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(headers_frame, text="Haber", font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151", width=120, anchor="e").grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkLabel(headers_frame, text="Acción", font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151", width=60, anchor="center").grid(row=0, column=3, padx=10, pady=10)
        
        # Contenedor de Filas
        self.filas_frame = ctk.CTkScrollableFrame(self.card, fg_color="transparent")
        self.filas_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.filas_frame.grid_columnconfigure(0, weight=1)
        
        self.lineas = []
        self.cuentas = []
        self.cuentas_dict = {}
        
        # Footer (Totales y Agregar)
        footer_frame = ctk.CTkFrame(self.card, fg_color="#F9FAFB", corner_radius=0, height=50)
        footer_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        footer_frame.grid_propagate(False)
        footer_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_agregar = ctk.CTkButton(footer_frame, text="+ Agregar Fila", fg_color="transparent", text_color="#10B981", hover_color="#ECFDF5", font=ctk.CTkFont(weight="bold"), command=self.agregar_linea)
        self.btn_agregar.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        
        self.lbl_total_debe = ctk.CTkLabel(footer_frame, text="0.00", font=ctk.CTkFont(weight="bold"), text_color="#111827", width=120, anchor="e")
        self.lbl_total_debe.grid(row=0, column=1, padx=10, pady=10)
        
        self.lbl_total_haber = ctk.CTkLabel(footer_frame, text="0.00", font=ctk.CTkFont(weight="bold"), text_color="#111827", width=120, anchor="e")
        self.lbl_total_haber.grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkLabel(footer_frame, text="", width=60).grid(row=0, column=3, padx=10) # Spacer
        
        self.actualizar_datos()
        
    def actualizar_datos(self):
        datos_cuentas = database.get_cuentas()
        self.cuentas = [f"{c[1]} {c[2]}" for c in datos_cuentas]
        self.cuentas_dict = {f"{c[1]} {c[2]}": c[0] for c in datos_cuentas}
        
        # Si ya hay líneas existentes, actualizamos sus comboboxes con las nuevas cuentas
        # sin borrar el contenido que el usuario ya haya ingresado.
        if self.lineas:
            for l in self.lineas:
                current_val = l["combo"].get()
                l["combo"].configure(values=self.cuentas)
                if current_val in self.cuentas:
                    l["combo"].set(current_val)
                elif self.cuentas:
                    l["combo"].set(self.cuentas[0])
        else:
            self.agregar_linea()
            self.agregar_linea()
        
    def agregar_linea(self):
        row_idx = len(self.lineas)
        frame = ctk.CTkFrame(self.filas_frame, fg_color="transparent")
        frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
        frame.grid_columnconfigure(0, weight=1)
        
        combo = ctk.CTkComboBox(frame, values=self.cuentas, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827", dropdown_fg_color="#FFFFFF", dropdown_text_color="#111827")
        combo.grid(row=0, column=0, sticky="ew", padx=10)
        
        debe = ctk.CTkEntry(frame, width=120, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827", justify="right")
        debe.insert(0, "0.00")
        debe.grid(row=0, column=1, padx=10)
        debe.bind("<KeyRelease>", self.validar_totales)
        
        haber = ctk.CTkEntry(frame, width=120, border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827", justify="right")
        haber.insert(0, "0.00")
        haber.grid(row=0, column=2, padx=10)
        haber.bind("<KeyRelease>", self.validar_totales)
        
        btn_eliminar = ctk.CTkButton(frame, text="🗑", width=60, fg_color="transparent", text_color="#EF4444", hover_color="#FEE2E2", font=ctk.CTkFont(size=18), command=lambda f=frame: self.eliminar_linea(f))
        btn_eliminar.grid(row=0, column=3, padx=10)
        
        self.lineas.append({"frame": frame, "combo": combo, "debe": debe, "haber": haber})
        self.validar_totales(None)
        
    def eliminar_linea(self, frame):
        if len(self.lineas) <= 2: return
        for linea in self.lineas:
            if linea["frame"] == frame:
                linea["frame"].destroy()
                self.lineas.remove(linea)
                break
        self.validar_totales(None)
        
    def validar_totales(self, event):
        tot_debe = 0.0
        tot_haber = 0.0
        for l in self.lineas:
            try:
                tot_debe += float(l["debe"].get() or 0)
                tot_haber += float(l["haber"].get() or 0)
            except ValueError:
                pass
        self.lbl_total_debe.configure(text=f"{tot_debe:,.2f}")
        self.lbl_total_haber.configure(text=f"{tot_haber:,.2f}")
        
        if round(tot_debe, 2) == round(tot_haber, 2) and tot_debe > 0:
            self.lbl_total_debe.configure(text_color="#10B981")
            self.lbl_total_haber.configure(text_color="#10B981")
            self.btn_guardar_top.configure(state="normal", fg_color="#10B981")
        else:
            self.lbl_total_debe.configure(text_color="#EF4444")
            self.lbl_total_haber.configure(text_color="#EF4444")
            self.btn_guardar_top.configure(state="disabled", fg_color="#D1D5DB")
            
    def guardar_asiento(self):
        fecha = self.entry_fecha.get()
        concepto = self.entry_concepto.get()
        if not fecha or not concepto:
            messagebox.showwarning("Faltan Datos", "Debe ingresar fecha y concepto.")
            return
        detalles = []
        try:
            for l in self.lineas:
                c_str = l["combo"].get()
                c_id = self.cuentas_dict.get(c_str)
                d = float(l["debe"].get() or 0)
                h = float(l["haber"].get() or 0)
                if c_id and (d > 0 or h > 0):
                    detalles.append((c_id, d, h))
        except:
            return
        
        valido, msg_f = logic.validar_fecha_asiento(fecha)
        if not valido:
            messagebox.showerror("Bloqueo de Período", msg_f)
            return
            
        if not logic.validar_equilibrio(detalles):
            messagebox.showwarning("Error", "El asiento está descuadrado.")
            return
            
        exito, msg = database.insertar_asiento(fecha, concepto, detalles)
        if exito:
            messagebox.showinfo("Éxito", "Asiento registrado.")
            self.entry_concepto.delete(0, 'end')
            self.actualizar_datos()
        else:
            messagebox.showerror("Error", msg)

class ReporteDiarioView(ctk.CTkFrame):
    # Pantalla del Libro Diario: Muestra el listado cronológico de todas las transacciones
    # asentadas en el sistema, agrupadas por su número de asiento contable.
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text="Libro Diario", font=ctk.CTkFont(size=26, weight="bold"), text_color="#111827").grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Filtros
        filters = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        filters.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        df = ctk.CTkFrame(filters, fg_color="transparent")
        df.pack(side="left", padx=20, pady=20)
        ctk.CTkLabel(df, text="Rango de Fechas", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        
        dates_row = ctk.CTkFrame(df, fg_color="transparent")
        dates_row.pack(anchor="w")
        self.d_desde = ctk.CTkEntry(dates_row, width=120, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.d_desde.pack(side="left")
        ctk.CTkLabel(dates_row, text=" - ", text_color="#111827").pack(side="left", padx=5)
        self.d_hasta = ctk.CTkEntry(dates_row, width=120, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.d_hasta.pack(side="left")
        
        bf = ctk.CTkFrame(filters, fg_color="transparent")
        bf.pack(side="left", padx=20, pady=20)
        ctk.CTkLabel(bf, text="Buscar Cuenta / Concepto", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.b_txt = ctk.CTkEntry(bf, width=200, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827", placeholder_text="Ej. Compras, 101...")
        self.b_txt.pack(anchor="w")
        
        # Botones Exportar Imprimir
        btn_f = ctk.CTkFrame(filters, fg_color="transparent")
        btn_f.pack(side="right", padx=20, pady=20)
        self.btn_export = ctk.CTkButton(btn_f, text="Exportar", fg_color="#10B981", border_width=1, border_color="#10B981", text_color="#FFFFFF", hover_color="#059669", width=100, command=self.exportar_pdf)
        self.btn_export.pack(side="left", padx=10)
        
        # Tabla Principal
        self.card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        self.card.grid(row=2, column=0, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(1, weight=1)
        
        # Headers Tabla
        h = ctk.CTkFrame(self.card, fg_color="#F9FAFB", height=40, corner_radius=0)
        h.grid(row=0, column=0, sticky="ew")
        h.grid_propagate(False)
        h.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(h, text="Fecha", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280", width=100, anchor="w").grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(h, text="Código", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280", width=80, anchor="w").grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(h, text="Cuenta / Concepto", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280", anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(h, text="Debe ($)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280", width=100, anchor="e").grid(row=0, column=3, padx=10, pady=10)
        ctk.CTkLabel(h, text="Haber ($)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280", width=100, anchor="e").grid(row=0, column=4, padx=10, pady=10)
        
        self.scroll = ctk.CTkScrollableFrame(self.card, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        
    def actualizar_datos(self):
        for w in self.scroll.winfo_children(): w.destroy()
        registros = database.get_libro_diario()
        # Agrupar por asiento
        asientos = {}
        for r in registros:
            # a.id, a.fecha, a.descripcion, c.codigo, c.nombre, d.debe, d.haber
            a_id = r[0]
            if a_id not in asientos:
                asientos[a_id] = {"fecha": r[1], "desc": r[2], "detalles": []}
            asientos[a_id]["detalles"].append({"codigo": r[3], "nombre": r[4], "debe": r[5], "haber": r[6]})
            
        row_idx = 0
        tot_d = 0.0
        tot_h = 0.0
        
        for a_id, data in asientos.items():
            # Cabecera asiento
            f_cab = ctk.CTkFrame(self.scroll, fg_color="#F9FAFB", corner_radius=0)
            f_cab.grid(row=row_idx, column=0, sticky="ew", pady=(10, 0))
            f_cab.grid_columnconfigure(2, weight=1)
            
            ctk.CTkLabel(f_cab, text=data["fecha"], font=ctk.CTkFont(weight="bold"), text_color="#10B981", width=100, anchor="w").grid(row=0, column=0, padx=10, pady=5)
            ctk.CTkLabel(f_cab, text="", width=80).grid(row=0, column=1, padx=10)
            ctk.CTkLabel(f_cab, text=f"Asiento #{a_id:03d} - {data['desc']}", font=ctk.CTkFont(weight="bold"), text_color="#4B5563", anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=5)
            ctk.CTkLabel(f_cab, text="", width=100).grid(row=0, column=3, padx=10)
            ctk.CTkLabel(f_cab, text="", width=100).grid(row=0, column=4, padx=10)
            row_idx += 1
            
            for d in data["detalles"]:
                f_det = ctk.CTkFrame(self.scroll, fg_color="transparent")
                f_det.grid(row=row_idx, column=0, sticky="ew")
                f_det.grid_columnconfigure(2, weight=1)
                
                ctk.CTkLabel(f_det, text="", width=100).grid(row=0, column=0, padx=10)
                ctk.CTkLabel(f_det, text=d["codigo"], text_color="#3B82F6", width=80, anchor="w").grid(row=0, column=1, padx=10, pady=2)
                
                # Indentar si es haber
                indent = "      " if d["haber"] > 0 else ""
                pref = "a " if d["haber"] > 0 else ""
                ctk.CTkLabel(f_det, text=f"{indent}{pref}{d['nombre']}", text_color="#111827", anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=2)
                
                debe_txt = f"{d['debe']:,.2f}" if d["debe"] > 0 else "0.00"
                haber_txt = f"{d['haber']:,.2f}" if d["haber"] > 0 else "0.00"
                
                ctk.CTkLabel(f_det, text=debe_txt, text_color="#111827" if d["debe"]>0 else "#9CA3AF", width=100, anchor="e").grid(row=0, column=3, padx=10)
                ctk.CTkLabel(f_det, text=haber_txt, text_color="#111827" if d["haber"]>0 else "#9CA3AF", width=100, anchor="e").grid(row=0, column=4, padx=10)
                row_idx += 1
                
                tot_d += d["debe"]
                tot_h += d["haber"]
                
        # Footer
        f_foot = ctk.CTkFrame(self.scroll, fg_color="#F9FAFB")
        f_foot.grid(row=row_idx, column=0, sticky="ew", pady=(10, 20))
        f_foot.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f_foot, text="TOTAL PÁGINA", font=ctk.CTkFont(weight="bold"), text_color="#4B5563", anchor="e").grid(row=0, column=0, sticky="e", padx=20, pady=10)
        ctk.CTkLabel(f_foot, text=f"{tot_d:,.2f}", font=ctk.CTkFont(weight="bold"), text_color="#10B981", width=100, anchor="e").grid(row=0, column=1, padx=10)
        ctk.CTkLabel(f_foot, text=f"{tot_h:,.2f}", font=ctk.CTkFont(weight="bold"), text_color="#10B981", width=100, anchor="e").grid(row=0, column=2, padx=10)

    def exportar_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Libro Diario", initialfile="Libro_Diario.pdf")
        if not filepath: return
        registros = database.get_libro_diario()
        datos = []
        for r in registros:
            datos.append({
                "fecha": r[1],
                "asiento_id": f"#{r[0]:03d}",
                "concepto": f"{r[3]} - {r[4]}",
                "debe": f"{r[5]:,.2f}" if r[5] > 0 else "-",
                "haber": f"{r[6]:,.2f}" if r[6] > 0 else "-"
            })
        try:
            export_pdf.exportar_diario_pdf(filepath, datos)
            messagebox.showinfo("Exportar", f"Libro Diario exportado con éxito a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\\n{e}")

class MayorView(ctk.CTkFrame):
    # Pantalla del Libro Mayor: Permite seleccionar una cuenta contable específica
    # para ver detalladamente cada uno de sus movimientos históricos y su saldo acumulado.
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header y Combobox
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        titulo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        titulo_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(titulo_frame, text="Libro Mayor", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(titulo_frame, text="Visualiza el historial de transacciones por cuenta.", font=ctk.CTkFont(size=15), text_color="#6B7280").pack(anchor="w")
        
        self.cuentas = []
        
        self.combo_cuenta = ctk.CTkComboBox(header_frame, values=[], font=ctk.CTkFont(size=15), width=300, command=self.on_cuenta_select, fg_color="#FFFFFF", border_color="#D1D5DB")
        self.combo_cuenta.grid(row=0, column=2, sticky="e")
        
        # Tarjeta de Resumen
        self.resumen_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.resumen_card.grid(row=1, column=0, sticky="ew", padx=30, pady=10)
        self.resumen_card.grid_columnconfigure(1, weight=1)
        
        # Icono (simulado con emoji)
        icono_bg = ctk.CTkFrame(self.resumen_card, fg_color="#E0E7FF", width=48, height=48, corner_radius=24)
        icono_bg.grid(row=0, column=0, padx=(20, 15), pady=20)
        icono_bg.grid_propagate(False)
        ctk.CTkLabel(icono_bg, text="🏛", font=ctk.CTkFont(size=26), text_color="#4F46E5").place(relx=0.5, rely=0.5, anchor="center")
        
        info_frame = ctk.CTkFrame(self.resumen_card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w")
        self.lbl_cuenta_nombre = ctk.CTkLabel(info_frame, text="Seleccione una cuenta", font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color="#111827")
        self.lbl_cuenta_nombre.pack(anchor="w")
        self.lbl_cuenta_codigo = ctk.CTkLabel(info_frame, text="Código: --", font=ctk.CTkFont(size=13), text_color="#6B7280")
        self.lbl_cuenta_codigo.pack(anchor="w")
        
        saldo_frame = ctk.CTkFrame(self.resumen_card, fg_color="transparent")
        saldo_frame.grid(row=0, column=2, sticky="e", padx=20)
        ctk.CTkLabel(saldo_frame, text="SALDO ACTUAL", font=ctk.CTkFont(size=11, weight="bold"), text_color="#6B7280").pack(anchor="e")
        self.lbl_saldo_actual = ctk.CTkLabel(saldo_frame, text="$ 0.00", font=ctk.CTkFont(family="Inter", size=35, weight="bold"), text_color="#10B981")
        self.lbl_saldo_actual.pack(anchor="e")
        
        # Tarjeta de Movimientos
        self.mov_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.mov_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 30))
        self.mov_card.grid_columnconfigure(0, weight=1)
        self.mov_card.grid_rowconfigure(2, weight=1)
        
        mov_header = ctk.CTkFrame(self.mov_card, fg_color="transparent")
        mov_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        mov_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(mov_header, text="Movimientos", font=ctk.CTkFont(size=18, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w")
        self.btn_export = ctk.CTkButton(mov_header, text="Exportar", font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent", text_color="#10B981", hover_color="#ECFDF5", width=80, command=self.exportar_pdf)
        self.btn_export.grid(row=0, column=1, sticky="e")
        
        # Tabla Headers
        th = ctk.CTkFrame(self.mov_card, fg_color="#F9FAFB", height=40, corner_radius=0)
        th.grid(row=1, column=0, sticky="ew")
        th.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(th, text="FECHA", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="w").grid(row=0, column=0, padx=(20, 10), pady=10)
        ctk.CTkLabel(th, text="CONCEPTO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(th, text="DEBE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="e").grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkLabel(th, text="HABER", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="e").grid(row=0, column=3, padx=10, pady=10)
        ctk.CTkLabel(th, text="SALDO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=120, anchor="e").grid(row=0, column=4, padx=(10, 20), pady=10)
        
        # Contenedor Scroll
        self.scroll_mov = ctk.CTkScrollableFrame(self.mov_card, fg_color="transparent")
        self.scroll_mov.grid(row=2, column=0, sticky="nsew")
        self.scroll_mov.grid_columnconfigure(0, weight=1)
        
        # Footer Totales
        self.footer = ctk.CTkFrame(self.mov_card, fg_color="#F9FAFB", height=50, corner_radius=0, border_width=1, border_color="#E5E7EB")
        self.footer.grid(row=3, column=0, sticky="ew")
        self.footer.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.footer, text="TOTALES", font=ctk.CTkFont(size=12, weight="bold"), text_color="#111827").grid(row=0, column=1, sticky="e", padx=10, pady=15)
        self.lbl_total_debe = ctk.CTkLabel(self.footer, text="0.00", font=ctk.CTkFont(size=13, weight="bold"), text_color="#10B981", width=100, anchor="e")
        self.lbl_total_debe.grid(row=0, column=2, padx=10)
        self.lbl_total_haber = ctk.CTkLabel(self.footer, text="0.00", font=ctk.CTkFont(size=13, weight="bold"), text_color="#EF4444", width=100, anchor="e")
        self.lbl_total_haber.grid(row=0, column=3, padx=10)
        self.lbl_total_saldo = ctk.CTkLabel(self.footer, text="0.00", font=ctk.CTkFont(size=13, weight="bold"), text_color="#111827", width=120, anchor="e")
        self.lbl_total_saldo.grid(row=0, column=4, padx=(10, 20))
        
    def actualizar_datos(self):
        self.cuentas = database.get_cuentas()
        opciones = [f"{c[1]} - {c[2]}" for c in self.cuentas]
        self.combo_cuenta.configure(values=opciones)
        
        # Mantener la selección anterior si aún existe en el catálogo actualizado
        current_selection = self.combo_cuenta.get()
        if current_selection in opciones:
            self.combo_cuenta.set(current_selection)
            self.on_cuenta_select(current_selection)
        elif opciones:
            self.combo_cuenta.set(opciones[0])
            self.on_cuenta_select(opciones[0])
            
    def on_cuenta_select(self, valor):
        codigo = valor.split(" - ")[0]
        cuenta_obj = next((c for c in self.cuentas if c[1] == codigo), None)
        if not cuenta_obj: return
        
        cuenta_id = cuenta_obj[0]
        self.cuenta_actual_id = cuenta_id
        self.lbl_cuenta_nombre.configure(text=cuenta_obj[2])
        self.lbl_cuenta_codigo.configure(text=f"Código: {cuenta_obj[1]} | {cuenta_obj[3]}")
        
        for w in self.scroll_mov.winfo_children(): w.destroy()
        
        movimientos = logic.calcular_movimientos_mayor(cuenta_id)
        
        row = 0
        total_debe = 0.0
        total_haber = 0.0
        saldo_final = 0.0
        
        for i, mov in enumerate(movimientos):
            bg_color = "#F9FAFB" if i % 2 == 0 else "#FFFFFF"
            f = ctk.CTkFrame(self.scroll_mov, fg_color=bg_color, corner_radius=0, height=45)
            f.grid(row=row, column=0, sticky="ew")
            f.grid_columnconfigure(1, weight=1)
            # Se eliminó f.grid_propagate(False) para permitir que la fila ajuste su ancho al contenido y no se oculte
            
            fecha_str = mov["fecha"].split()[0] if " " in mov["fecha"] else mov["fecha"]
            ctk.CTkLabel(f, text=fecha_str, font=ctk.CTkFont(size=13), text_color="#4B5563", width=100, anchor="w").grid(row=0, column=0, padx=(20, 10), pady=10)
            ctk.CTkLabel(f, text=mov["concepto"], font=ctk.CTkFont(size=13), text_color="#111827", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
            
            val_debe = mov["debe"]
            txt_debe = f"{val_debe:,.2f}" if val_debe > 0 else "-"
            col_debe = "#10B981" if val_debe > 0 else "#9CA3AF"
            ctk.CTkLabel(f, text=txt_debe, font=ctk.CTkFont(size=13), text_color=col_debe, width=100, anchor="e").grid(row=0, column=2, padx=10)
            
            val_haber = mov["haber"]
            txt_haber = f"{val_haber:,.2f}" if val_haber > 0 else "-"
            col_haber = "#EF4444" if val_haber > 0 else "#9CA3AF"
            ctk.CTkLabel(f, text=txt_haber, font=ctk.CTkFont(size=13), text_color=col_haber, width=100, anchor="e").grid(row=0, column=3, padx=10)
            
            val_saldo = mov["saldo"]
            saldo_final = val_saldo
            ctk.CTkLabel(f, text=f"{val_saldo:,.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#111827", width=120, anchor="e").grid(row=0, column=4, padx=(10, 20))
            
            total_debe += val_debe
            total_haber += val_haber
            row += 1
            
        self.lbl_total_debe.configure(text=f"{total_debe:,.2f}")
        self.lbl_total_haber.configure(text=f"{total_haber:,.2f}")
        self.lbl_total_saldo.configure(text=f"{saldo_final:,.2f}")
        
        color_saldo = "#10B981" if saldo_final >= 0 else "#EF4444"
        self.lbl_saldo_actual.configure(text=f"$ {saldo_final:,.2f}", text_color=color_saldo)


        self.lbl_total_saldo.configure(text=f"{saldo_final:,.2f}")
        
    def exportar_pdf(self):
        if not hasattr(self, 'cuenta_actual_id') or not self.cuenta_actual_id:
            messagebox.showwarning("Aviso", "No hay ninguna cuenta seleccionada.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Libro Mayor", initialfile="Libro_Mayor.pdf")
        if not filepath: return
        
        movimientos = logic.calcular_movimientos_mayor(self.cuenta_actual_id)
        datos = []
        for mov in movimientos:
            datos.append({
                "fecha": mov["fecha"].split()[0] if " " in mov["fecha"] else mov["fecha"],
                "concepto": mov["concepto"],
                "debe": f"{mov['debe']:,.2f}" if mov['debe'] > 0 else "-",
                "haber": f"{mov['haber']:,.2f}" if mov['haber'] > 0 else "-",
                "saldo": f"{mov['saldo']:,.2f}"
            })
            
        cuenta_nombre = self.lbl_cuenta_nombre.cget("text")
        
        try:
            export_pdf.exportar_mayor_pdf(filepath, cuenta_nombre, datos)
            messagebox.showinfo("Exportar", f"Libro Mayor exportado con éxito a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

class BalanceComprobacionView(ctk.CTkFrame):
    # Pantalla de Hoja de Trabajo: Presenta una tabla analítica detallada de 12 columnas
    # con sumas, saldos y agrupaciones para control financiero.
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        titulo_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        titulo_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(titulo_frame, text="Hoja de Trabajo (Working Papers)", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(titulo_frame, text="Matriz Analítica de 12 Columnas", font=ctk.CTkFont(size=15), text_color="#6B7280").pack(anchor="w")
        
        btn_export = ctk.CTkButton(header_frame, text="Exportar", font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent", text_color="#10B981", hover_color="#ECFDF5", width=80, border_width=1, border_color="#D1D5DB", command=self.exportar_pdf)
        btn_export.grid(row=0, column=1, sticky="e")
        
        # Tabla Card
        self.table_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.table_card.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 30))
        self.table_card.grid_columnconfigure(0, weight=1)
        self.table_card.grid_rowconfigure(1, weight=1)
        
        # Table Headers (2 rows)
        th = ctk.CTkFrame(self.table_card, fg_color="#F9FAFB", corner_radius=0)
        th.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        
        th.grid_columnconfigure(0, weight=1)
        
        # Row 1 (Grupos)
        ctk.CTkLabel(th, text="Cuenta Contable", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151", anchor="w").grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=(10, 5))
        ctk.CTkLabel(th, text="Sumas", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=1, columnspan=2, sticky="ew", pady=(10, 5))
        ctk.CTkLabel(th, text="Saldos", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=3, columnspan=2, sticky="ew", pady=(10, 5))
        ctk.CTkLabel(th, text="Ajustes", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=5, columnspan=2, sticky="ew", pady=(10, 5))
        ctk.CTkLabel(th, text="Ajustados", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=7, columnspan=2, sticky="ew", pady=(10, 5))
        ctk.CTkLabel(th, text="Resultados", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=9, columnspan=2, sticky="ew", pady=(10, 5))
        ctk.CTkLabel(th, text="Balance G.", font=ctk.CTkFont(size=12, weight="bold"), text_color="#374151").grid(row=0, column=11, columnspan=2, sticky="ew", padx=(0, 20), pady=(10, 5))
        
        # Row 2 (Debe/Haber)
        col_w = 85
        ctk.CTkLabel(th, text="", height=1).grid(row=1, column=0)
        
        sub_headers = [
            ("Debe", "Haber"), ("Debe", "Haber"), ("Debe", "Haber"), 
            ("Debe", "Haber"), ("Gasto", "Ingreso"), ("Activo", "Pas+Pat")
        ]
        col_idx = 1
        for d, h in sub_headers:
            ctk.CTkLabel(th, text=d, font=ctk.CTkFont(size=11), text_color="#6B7280", width=col_w, anchor="e").grid(row=1, column=col_idx, sticky="ew", padx=5, pady=(0, 10))
            ctk.CTkLabel(th, text=h, font=ctk.CTkFont(size=11), text_color="#6B7280", width=col_w, anchor="e").grid(row=1, column=col_idx+1, sticky="ew", padx=5, pady=(0, 10))
            col_idx += 2
            
        # Separadores Header (entre Debe y Haber)
        for c in [1, 3, 5, 7, 9, 11]:
            ctk.CTkFrame(th, fg_color="#D1D5DB", width=1, height=1).grid(row=0, column=c, rowspan=2, sticky="nse")
            
        self.scroll_mov = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        
        self.scroll_mov.grid(row=1, column=0, sticky="nsew")
        self.scroll_mov.grid_columnconfigure(0, weight=1)
        
        # Footer Totales
        self.footer = ctk.CTkFrame(self.table_card, fg_color="#F9FAFB", height=50, corner_radius=0, border_width=1, border_color="#E5E7EB")
        self.footer.grid(row=2, column=0, sticky="ew", padx=(0, 16))
        
        self.footer.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.footer, text="SUMAS IGUALES", font=ctk.CTkFont(size=12, weight="bold"), text_color="#111827", anchor="e").grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=15)
        
        # Separadores Footer (entre Debe y Haber)
        for c in [1, 3, 5, 7, 9, 11]:
            ctk.CTkFrame(self.footer, fg_color="#D1D5DB", width=1, height=1).grid(row=0, column=c, sticky="nse")
            
        self.lbls_totales = []
        col_idx = 1
        for _ in range(12):
            lbl = ctk.CTkLabel(self.footer, text="0.00", font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981", width=col_w, anchor="e")
            lbl.grid(row=0, column=col_idx, sticky="ew", padx=5)
            self.lbls_totales.append(lbl)
            col_idx += 1
            
    def actualizar_datos(self):
        for w in self.scroll_mov.winfo_children(): w.destroy()
        
        filas, totales = logic.calcular_hoja_trabajo()
        
        row_idx = 0
        col_w = 85
        
        for i, fila in enumerate(filas):
            bg_color = "#F9FAFB" if i % 2 == 0 else "#FFFFFF"
            f = ctk.CTkFrame(self.scroll_mov, fg_color=bg_color, corner_radius=0, height=24)
            f.grid(row=row_idx, column=0, sticky="ew")
            
            f.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(f, text=fila["cuenta"], font=ctk.CTkFont(size=11), text_color="#111827", anchor="w").grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=2)
            
            # Separadores Data (entre Debe y Haber)
            for c in [1, 3, 5, 7, 9, 11]:
                ctk.CTkFrame(f, fg_color="#E5E7EB", width=1, height=1).grid(row=0, column=c, sticky="nse")
            
            valores = [
                fila["sum_d"], fila["sum_h"],
                fila["sal_d"], fila["sal_h"],
                fila["aju_d"], fila["aju_h"],
                fila["aju_sal_d"], fila["aju_sal_h"],
                fila["res_d"], fila["res_h"],
                fila["bg_d"], fila["bg_h"]
            ]
            
            col_idx = 1
            for val in valores:
                txt = f"{val:,.2f}" if val > 0 else "-"
                ctk.CTkLabel(f, text=txt, font=ctk.CTkFont(size=11), text_color="#4B5563", width=col_w, anchor="e").grid(row=0, column=col_idx, sticky="ew", padx=5, pady=2)
                col_idx += 1
                
            row_idx += 1
            
        # Actualizar totales
        tot_vals = [
            totales["sum_d"], totales["sum_h"],
            totales["sal_d"], totales["sal_h"],
            totales["aju_d"], totales["aju_h"],
            totales["aju_sal_d"], totales["aju_sal_h"], 
            totales["res_d"], totales["res_h"],
            totales["bg_d"], totales["bg_h"]
        ]
        
        # Add utility adjustment rows if needed, but for now just show basic totals
        for i, val in enumerate(tot_vals):
            self.lbls_totales[i].configure(text=f"{val:,.2f}" if val > 0 else "-")

    def exportar_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Hoja de Trabajo", initialfile="Hoja_de_Trabajo.pdf")
        if not filepath: return
        
        filas, totales = logic.calcular_hoja_trabajo()
        try:
            export_pdf.exportar_hoja_trabajo_pdf(filepath, filas, totales)
            messagebox.showinfo("Exportar", f"Hoja de Trabajo exportada con éxito a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

class EstadosFinancierosView(ctk.CTkFrame):
    # Pantalla del Centro de Reportes: Contiene pestañas para navegar entre la Hoja de Trabajo,
    # el Estado de Resultados (ingresos y gastos) y el Balance General (activos, pasivos y capital).
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="Centro de Reportes Financieros", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w")
        btn_export = ctk.CTkButton(header_frame, text="Exportar a PDF", font=ctk.CTkFont(size=13, weight="bold"), fg_color="transparent", text_color="#10B981", hover_color="#ECFDF5", width=120, border_width=1, border_color="#D1D5DB", command=self.exportar_pdf)
        btn_export.grid(row=0, column=1, sticky="e")
        
        self.tabview = ctk.CTkTabview(self, fg_color="#FFFFFF", border_width=1, border_color="#E5E7EB", segmented_button_selected_color="#10B981", segmented_button_selected_hover_color="#059669")
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        
        self.tabview._segmented_button.configure(font=ctk.CTkFont(family="Inter", size=18), height=36)
        
        self.tabview.add("Hoja de Trabajo")
        self.tabview.add("Estado de Resultados")
        self.tabview.add("Balance General")
        
        # 1. Hoja de Trabajo
        self.hoja_trabajo_view = BalanceComprobacionView(self.tabview.tab("Hoja de Trabajo"))
        self.hoja_trabajo_view.pack(expand=True, fill="both")
        self.hoja_trabajo_view.configure(fg_color="transparent")
        for child in self.hoja_trabajo_view.winfo_children():
            child.grid_configure(padx=10)
        
        # 2. Estado de Resultados
        self.frame_resultados = ctk.CTkScrollableFrame(self.tabview.tab("Estado de Resultados"), fg_color="transparent")
        self.frame_resultados.pack(expand=True, fill="both", padx=20, pady=20)
        
        # 3. Balance General
        self.frame_situacion = ctk.CTkScrollableFrame(self.tabview.tab("Balance General"), fg_color="transparent")
        self.frame_situacion.pack(expand=True, fill="both", padx=20, pady=20)
        
    def add_row(self, parent, text, amount, is_header=False, indent=0, is_total=False):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=10, pady=2)
        f.grid_columnconfigure(1, weight=1)
        
        font_w = "bold" if is_header or is_total else "normal"
        text_c = "#111827" if is_header or is_total else "#4B5563"
        
        ctk.CTkLabel(f, text=text, font=ctk.CTkFont(family="Inter", size=14, weight=font_w), text_color=text_c, anchor="w").grid(row=0, column=0, sticky="w", padx=(indent, 10))
        if amount is not None:
            amt_str = f"$ {amount:,.2f}"
            ctk.CTkLabel(f, text=amt_str, font=ctk.CTkFont(family="Inter", size=14, weight=font_w), text_color=text_c, anchor="e", width=120).grid(row=0, column=2, sticky="e")

    def actualizar_datos(self):
        self.hoja_trabajo_view.actualizar_datos()
        
        for w in self.frame_resultados.winfo_children(): w.destroy()
        for w in self.frame_situacion.winfo_children(): w.destroy()
        
        # --- ESTADO DE RESULTADOS ---
        title_res = ctk.CTkLabel(self.frame_resultados, text="LOS EXCELENTES PSM\nESTADO DE RESULTADOS\nDEL 01 DE ENERO AL 31 DE DICIEMBRE", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#111827", justify="center")
        title_res.pack(pady=(0, 20))
        
        saldos = logic.calcular_saldos_mayor()
        ingresos = [s for s in saldos if s["tipo"] == "Ingreso" and s["saldo"] != 0]
        egresos = [s for s in saldos if s["tipo"] == "Egreso" and s["saldo"] != 0]
        
        tot_ingresos = sum(s["saldo"] for s in ingresos)
        tot_egresos = sum(s["saldo"] for s in egresos)
        
        self.add_row(self.frame_resultados, "INGRESOS", None, is_header=True)
        for s in ingresos:
            self.add_row(self.frame_resultados, f"{s['codigo']} - {s['nombre']}", s["saldo"], indent=20)
        
        ctk.CTkFrame(self.frame_resultados, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        self.add_row(self.frame_resultados, "Total Ingresos", tot_ingresos, is_total=True, indent=20)
        
        self.add_row(self.frame_resultados, "EGRESOS", None, is_header=True)
        for s in egresos:
            self.add_row(self.frame_resultados, f"{s['codigo']} - {s['nombre']}", s["saldo"], indent=20)
            
        ctk.CTkFrame(self.frame_resultados, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        self.add_row(self.frame_resultados, "Total Egresos", tot_egresos, is_total=True, indent=20)
        
        utilidad = tot_ingresos - tot_egresos
        lbl_res = "UTILIDAD NETA DEL EJERCICIO" if utilidad >= 0 else "PÉRDIDA NETA DEL EJERCICIO"
        
        ctk.CTkFrame(self.frame_resultados, height=2, fg_color="#111827").pack(fill="x", padx=10, pady=(15, 5))
        self.add_row(self.frame_resultados, lbl_res, utilidad, is_total=True)
        ctk.CTkFrame(self.frame_resultados, height=1, fg_color="#111827").pack(fill="x", padx=10, pady=(0, 20))
        
        # --- BALANCE GENERAL ---
        title_bg = ctk.CTkLabel(self.frame_situacion, text="LOS EXCELENTES PSM\nBALANCE GENERAL\nAL DÍA DE HOY", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#111827", justify="center")
        title_bg.pack(pady=(0, 20))
        
        activos = [s for s in saldos if s["tipo"] == "Activo" and s["saldo"] != 0]
        pasivos = [s for s in saldos if s["tipo"] == "Pasivo" and s["saldo"] != 0]
        capital = [s for s in saldos if s["tipo"] == "Capital" and s["saldo"] != 0]
        
        tot_activos = sum(s["saldo"] for s in activos)
        tot_pasivos = sum(s["saldo"] for s in pasivos)
        tot_capital = sum(s["saldo"] for s in capital)
        
        self.add_row(self.frame_situacion, "ACTIVO", None, is_header=True)
        for s in activos:
            self.add_row(self.frame_situacion, f"{s['codigo']} - {s['nombre']}", s["saldo"], indent=20)
        ctk.CTkFrame(self.frame_situacion, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        self.add_row(self.frame_situacion, "Total Activos", tot_activos, is_total=True, indent=20)
        
        self.add_row(self.frame_situacion, "PASIVO", None, is_header=True)
        for s in pasivos:
            self.add_row(self.frame_situacion, f"{s['codigo']} - {s['nombre']}", s["saldo"], indent=20)
        ctk.CTkFrame(self.frame_situacion, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        self.add_row(self.frame_situacion, "Total Pasivos", tot_pasivos, is_total=True, indent=20)
        
        self.add_row(self.frame_situacion, "CAPITAL", None, is_header=True)
        for s in capital:
            self.add_row(self.frame_situacion, f"{s['codigo']} - {s['nombre']}", s["saldo"], indent=20)
            
        if utilidad != 0:
            lbl_util = "Utilidad del Ejercicio" if utilidad > 0 else "Pérdida del Ejercicio"
            self.add_row(self.frame_situacion, f"3.1.xx - {lbl_util}", utilidad, indent=20)
            
        tot_patrimonio = tot_capital + utilidad
        ctk.CTkFrame(self.frame_situacion, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        self.add_row(self.frame_situacion, "Total Capital", tot_patrimonio, is_total=True, indent=20)
        
        tot_pasivo_patrimonio = tot_pasivos + tot_patrimonio
        ctk.CTkFrame(self.frame_situacion, height=2, fg_color="#111827").pack(fill="x", padx=10, pady=(15, 5))
        
        f_igual = ctk.CTkFrame(self.frame_situacion, fg_color="transparent")
        f_igual.pack(fill="x", padx=10, pady=2)
        f_igual.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f_igual, text="TOTAL ACTIVO", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(f_igual, text=f"$ {tot_activos:,.2f}", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#111827", anchor="e", width=120).grid(row=0, column=2, sticky="e")
        
        f_igual2 = ctk.CTkFrame(self.frame_situacion, fg_color="transparent")
        f_igual2.pack(fill="x", padx=10, pady=2)
        f_igual2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f_igual2, text="TOTAL PASIVO + PATRIMONIO", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(f_igual2, text=f"$ {tot_pasivo_patrimonio:,.2f}", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color="#111827", anchor="e", width=120).grid(row=0, column=2, sticky="e")

    def exportar_pdf(self):
        tab_actual = self.tabview.get()
        if tab_actual == "Hoja de Trabajo":
            self.hoja_trabajo_view.exportar_pdf()
        elif tab_actual == "Estado de Resultados":
            self.exportar_resultados()
        elif tab_actual == "Balance General":
            self.exportar_balance()
            
    def exportar_resultados(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Estado de Resultados", initialfile="Estado_de_Resultados.pdf")
        if not filepath: return
        
        saldos = logic.calcular_saldos_mayor()
        ingresos = [s for s in saldos if s["tipo"] == "Ingreso" and s["saldo"] != 0]
        egresos = [s for s in saldos if s["tipo"] == "Egreso" and s["saldo"] != 0]
        
        tot_ingresos = sum(s["saldo"] for s in ingresos)
        tot_egresos = sum(s["saldo"] for s in egresos)
        utilidad = tot_ingresos - tot_egresos
        
        datos = []
        datos.append(["INGRESOS", "", True])
        for s in ingresos:
            datos.append([f"  {s['codigo']} - {s['nombre']}", f"{s['saldo']:,.2f}"])
        datos.append(["Total Ingresos", f"{tot_ingresos:,.2f}", True])
        
        datos.append(["EGRESOS", "", True])
        for s in egresos:
            datos.append([f"  {s['codigo']} - {s['nombre']}", f"{s['saldo']:,.2f}"])
        datos.append(["Total Egresos", f"{tot_egresos:,.2f}", True])
        
        lbl_res = "UTILIDAD NETA DEL EJERCICIO" if utilidad >= 0 else "PÉRDIDA NETA DEL EJERCICIO"
        datos.append([lbl_res, f"{utilidad:,.2f}", True])
        
        try:
            export_pdf.exportar_estados_financieros_pdf(filepath, "Estado de Resultados", datos)
            messagebox.showinfo("Exportar", f"Estado de Resultados exportado con éxito a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

    def exportar_balance(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], title="Guardar Balance General", initialfile="Balance_General.pdf")
        if not filepath: return
        
        saldos = logic.calcular_saldos_mayor()
        activos = [s for s in saldos if s["tipo"] == "Activo" and s["saldo"] != 0]
        pasivos = [s for s in saldos if s["tipo"] == "Pasivo" and s["saldo"] != 0]
        capital = [s for s in saldos if s["tipo"] == "Capital" and s["saldo"] != 0]
        
        # Calcular utilidad neta
        ingresos = [s for s in saldos if s["tipo"] == "Ingreso" and s["saldo"] != 0]
        egresos = [s for s in saldos if s["tipo"] == "Egreso" and s["saldo"] != 0]
        tot_ingresos = sum(s["saldo"] for s in ingresos)
        tot_egresos = sum(s["saldo"] for s in egresos)
        utilidad = tot_ingresos - tot_egresos
        
        tot_activos = sum(s["saldo"] for s in activos)
        tot_pasivos = sum(s["saldo"] for s in pasivos)
        tot_capital = sum(s["saldo"] for s in capital)
        
        datos = []
        datos.append(["ACTIVO", "", True])
        for s in activos:
            datos.append([f"  {s['codigo']} - {s['nombre']}", f"{s['saldo']:,.2f}"])
        datos.append(["Total Activos", f"{tot_activos:,.2f}", True])
        
        datos.append(["PASIVO", "", True])
        for s in pasivos:
            datos.append([f"  {s['codigo']} - {s['nombre']}", f"{s['saldo']:,.2f}"])
        datos.append(["Total Pasivos", f"{tot_pasivos:,.2f}", True])
        
        datos.append(["CAPITAL", "", True])
        for s in capital:
            datos.append([f"  {s['codigo']} - {s['nombre']}", f"{s['saldo']:,.2f}"])
            
        if utilidad != 0:
            lbl_util = "Utilidad del Ejercicio" if utilidad > 0 else "Pérdida del Ejercicio"
            datos.append([f"  3.1.xx - {lbl_util}", f"{utilidad:,.2f}"])
            
        tot_patrimonio = tot_capital + utilidad
        datos.append(["Total Capital", f"{tot_patrimonio:,.2f}", True])
        
        datos.append(["TOTAL PASIVO + PATRIMONIO", f"{tot_pasivos + tot_patrimonio:,.2f}", True])
        
        try:
            export_pdf.exportar_estados_financieros_pdf(filepath, "Balance General", datos)
            messagebox.showinfo("Exportar", f"Balance General exportado con éxito a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

class CierreView(ctk.CTkFrame):
    # Pantalla de Cierre Contable: Muestra una advertencia sobre la irreversibilidad del cierre
    # y proporciona el botón para consolidar las cuentas nominales y bloquear el periodo contable.
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.card.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(3, weight=1)
        
        ctk.CTkLabel(self.card, text="CIERRE CONTABLE", font=ctk.CTkFont(size=26, weight="bold"), text_color="#111827").grid(row=0, column=0, pady=(40, 10))
        
        warning_frame = ctk.CTkFrame(self.card, fg_color="#FEF2F2", border_width=1, border_color="#FCA5A5", corner_radius=8)
        warning_frame.grid(row=1, column=0, padx=40, pady=20, sticky="ew")
        warning_frame.grid_columnconfigure(0, weight=1)
        
        info = "⚠️ ADVERTENCIA ⚠️\n\nEl cierre contable consolidará las cuentas nominales (Ingresos y Egresos)\ny transferirá el resultado a la cuenta de Capital Social.\n\nAl realizar el cierre, se BLOQUEARÁ EL PERÍODO. No podrá ingresar\nningún asiento nuevo con fecha igual o anterior a la fecha de cierre.\n\nEsta acción es irreversible."
        ctk.CTkLabel(warning_frame, text=info, font=ctk.CTkFont(size=15, weight="bold"), text_color="#EF4444", justify="center").pack(pady=20, padx=20)
        
        form_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        form_frame.grid(row=2, column=0, pady=20)
        
        ctk.CTkLabel(form_frame, text="Fecha de Cierre (YYYY-MM-DD)", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.entry_fecha = ctk.CTkEntry(form_frame, width=200, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(pady=(5, 20))
        
        self.btn_cierre = ctk.CTkButton(form_frame, text="EJECUTAR CIERRE DEL EJERCICIO", fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(weight="bold"), command=self.ejecutar_cierre, height=40)
        self.btn_cierre.pack(fill="x")
        
    def ejecutar_cierre(self):
        fecha = self.entry_fecha.get()
        if not fecha: return
            
        confirm = messagebox.askyesno("Confirmar Cierre", f"¿Está absolutamente seguro de cerrar el período con fecha {fecha}?\nEsto bloqueará el registro de asientos pasados.")
        if confirm:
            exito, msg = logic.ejecutar_cierre_contable(fecha)
            if exito:
                messagebox.showinfo("Cierre Exitoso", msg)
            else:
                messagebox.showerror("Fallo en el Cierre", msg)

class GestionCuentasView(ctk.CTkFrame):
    # Pantalla del Catálogo de Cuentas: Permite crear nuevas cuentas contables ingresando su código,
    # nombre y tipo, y muestra el catálogo completo actual en una lista a la derecha.
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Catálogo de Cuentas", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#111827").pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Gestione las cuentas contables del sistema.", font=ctk.CTkFont(size=15), text_color="#6B7280").pack(anchor="w")
        
        # Layout principal
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Formulario
        self.form_card = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        ctk.CTkLabel(self.form_card, text="Nueva Cuenta", font=ctk.CTkFont(size=18, weight="bold"), text_color="#111827").pack(anchor="w", padx=20, pady=(20, 15))
        
        f_cod = ctk.CTkFrame(self.form_card, fg_color="transparent")
        f_cod.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(f_cod, text="Código", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.entry_codigo = ctk.CTkEntry(f_cod, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.entry_codigo.pack(fill="x", pady=(5, 0))
        
        f_nom = ctk.CTkFrame(self.form_card, fg_color="transparent")
        f_nom.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(f_nom, text="Nombre", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.entry_nombre = ctk.CTkEntry(f_nom, fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.entry_nombre.pack(fill="x", pady=(5, 0))
        
        f_tip = ctk.CTkFrame(self.form_card, fg_color="transparent")
        f_tip.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkLabel(f_tip, text="Tipo de Cuenta", font=ctk.CTkFont(size=13), text_color="#6B7280").pack(anchor="w")
        self.combo_tipo = ctk.CTkComboBox(f_tip, values=["Activo", "Pasivo", "Capital", "Ingreso", "Egreso"], fg_color="#F9FAFB", border_color="#D1D5DB", text_color="#111827")
        self.combo_tipo.pack(fill="x", pady=(5, 0))
        
        self.btn_crear = ctk.CTkButton(self.form_card, text="Crear Cuenta", fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold"), height=40, command=self.crear_cuenta)
        self.btn_crear.pack(fill="x", padx=20, pady=(0, 20))
        
        # Tabla de Cuentas
        self.table_card = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.table_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        self.table_card.grid_rowconfigure(1, weight=1)
        self.table_card.grid_columnconfigure(0, weight=1)
        
        th = ctk.CTkFrame(self.table_card, fg_color="#F9FAFB", height=40, corner_radius=0)
        th.grid(row=0, column=0, sticky="ew")
        th.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(th, text="CÓDIGO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=80, anchor="w").grid(row=0, column=0, padx=(20, 10), pady=10)
        ctk.CTkLabel(th, text="NOMBRE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(th, text="TIPO", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="w").grid(row=0, column=2, padx=(10, 20), pady=10)
        
        self.scroll_table = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.scroll_table.grid(row=1, column=0, sticky="nsew")
        self.scroll_table.grid_columnconfigure(1, weight=1)
        
    def crear_cuenta(self):
        cod = self.entry_codigo.get().strip()
        nom = self.entry_nombre.get().strip()
        tip = self.combo_tipo.get()
        
        if not cod or not nom:
            messagebox.showwarning("Error", "Ingrese código y nombre de la cuenta.")
            return
            
        exito, msg = database.insertar_cuenta(cod, nom, tip)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.entry_codigo.delete(0, 'end')
            self.entry_nombre.delete(0, 'end')
            self.actualizar_datos()
        else:
            messagebox.showerror("Error", msg)
            
    def actualizar_datos(self):
        for w in self.scroll_table.winfo_children(): w.destroy()
        cuentas = database.get_cuentas()
        
        for i, c in enumerate(cuentas):
            bg_color = "#F9FAFB" if i % 2 == 0 else "#FFFFFF"
            f = ctk.CTkFrame(self.scroll_table, fg_color=bg_color, corner_radius=0, height=35)
            f.pack(fill="x")
            f.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(f, text=c[1], font=ctk.CTkFont(size=13), text_color="#111827", width=80, anchor="w").grid(row=0, column=0, padx=(20, 10), pady=5)
            ctk.CTkLabel(f, text=c[2], font=ctk.CTkFont(size=13), text_color="#4B5563", anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=5)
            ctk.CTkLabel(f, text=c[3], font=ctk.CTkFont(size=13), text_color="#4B5563", width=100, anchor="w").grid(row=0, column=2, padx=(10, 20), pady=5)

class DashboardView(ctk.CTkScrollableFrame):
    # Pantalla del Panel de Control (Dashboard): Presenta un resumen rápido con tarjetas de KPI
    # (balances, ingresos, egresos), un gráfico del flujo de caja, actividades recientes y alertas del sistema.
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        self.grid_columnconfigure(0, weight=1)
        
        # --- KPIs ---
        kpis_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpis_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        kpis_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        def create_kpi_card(parent, col, title, amount, icon, icon_color, icon_bg, subtitle=None, subtitle_color=None):
            card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
            card.grid(row=0, column=col, sticky="nsew", padx=10)
            
            top_f = ctk.CTkFrame(card, fg_color="transparent")
            top_f.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(top_f, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280").pack(side="left")
            
            icon_f = ctk.CTkFrame(top_f, fg_color=icon_bg, width=24, height=24, corner_radius=12)
            icon_f.pack(side="right")
            icon_f.pack_propagate(False)
            ctk.CTkLabel(icon_f, text=icon, font=ctk.CTkFont(size=13), text_color=icon_color).place(relx=0.5, rely=0.5, anchor="center")
            
            val_lbl = ctk.CTkLabel(card, text=amount, font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#111827", anchor="w")
            val_lbl.pack(fill="x", padx=15)
            
            if subtitle:
                ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=12), text_color=subtitle_color, anchor="w").pack(fill="x", padx=15, pady=(0, 15))
            else:
                ctk.CTkFrame(card, fg_color="transparent", height=15).pack(fill="x")
            return val_lbl
                
        self.lbl_balance = create_kpi_card(kpis_frame, 0, "Balance Total", "$0.00", "🏛", "#10B981", "#D1FAE5", "↗ +4.2% mes ant.", "#10B981")
        self.lbl_ingresos = create_kpi_card(kpis_frame, 1, "Ingresos del Mes", "$0.00", "↓", "#10B981", "#D1FAE5")
        self.lbl_egresos = create_kpi_card(kpis_frame, 2, "Egresos del Mes", "$0.00", "↑", "#6B7280", "#E5E7EB")
        self.lbl_cobrar = create_kpi_card(kpis_frame, 3, "Cuentas por Cobrar", "$0.00", "📄", "#6B7280", "#E5E7EB")
        
        # --- CHART ---
        chart_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB", height=300)
        chart_card.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 20))
        chart_card.grid_propagate(False)
        
        header_f = ctk.CTkFrame(chart_card, fg_color="transparent")
        header_f.pack(fill="x", padx=20, pady=15)
        self.lbl_chart_title = ctk.CTkLabel(header_f, text="Flujo de Caja", font=ctk.CTkFont(size=18, weight="bold"), text_color="#111827")
        self.lbl_chart_title.pack(side="left")
        
        legend_f = ctk.CTkFrame(header_f, fg_color="transparent")
        legend_f.pack(side="right")
        
        ctk.CTkFrame(legend_f, fg_color="#10B981", width=12, height=12, corner_radius=2).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(legend_f, text="Ingresos", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(side="left", padx=(0, 15))
        
        ctk.CTkFrame(legend_f, fg_color="#9CA3AF", width=12, height=12, corner_radius=2).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(legend_f, text="Egresos", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(side="left")
        
        import tkinter as tk
        self.canvas = tk.Canvas(chart_card, bg="#FFFFFF", highlightthickness=0, height=220)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Enlazar evento para redibujar el gráfico si la ventana cambia de tamaño (diseño responsivo)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # --- BOTTOM SECTION ---
        bottom_f = ctk.CTkFrame(self, fg_color="transparent")
        bottom_f.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 20))
        bottom_f.grid_columnconfigure(0, weight=2)
        bottom_f.grid_columnconfigure(1, weight=1)
        
        self.act_card = ctk.CTkFrame(bottom_f, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.act_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.act_card.grid_columnconfigure(0, weight=1)
        
        self.alert_card = ctk.CTkFrame(bottom_f, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        self.alert_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.alert_card.grid_columnconfigure(0, weight=1)

    def on_canvas_configure(self, event):
        # Redibuja el gráfico de flujo de caja cuando la ventana cambia de tamaño
        # para que se adapte perfectamente al espacio disponible (diseño responsivo).
        if hasattr(self, 'datos_flujo') and self.datos_flujo:
            self.dibujar_grafico()

    def dibujar_grafico(self):
        # Dibuja dinámicamente las líneas y áreas de ingresos/egresos mensuales
        # calculados de la base de datos real.
        self.canvas.delete("all")
        
        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W <= 1 or H <= 1:
            W = 900
            H = 220
            
        padding_left = 65
        padding_right = 20
        padding_top = 20
        padding_bottom = 30
        
        h_draw = H - padding_top - padding_bottom
        w_draw = W - padding_left - padding_right
        
        # Calcular el máximo valor para el eje Y
        valores_y = []
        for mes_str in [f"{i:02d}" for i in range(1, 13)]:
            valores_y.append(self.datos_flujo[mes_str]["ingresos"])
            valores_y.append(self.datos_flujo[mes_str]["egresos"])
            
        max_val = max(valores_y) if valores_y else 0.0
        if max_val == 0:
            max_val = 1000.0
            
        limit_y = max_val * 1.15
        
        # Dibujar líneas de cuadrícula y etiquetas de monto (Eje Y)
        for pct in [0.0, 0.25, 0.5, 0.75, 1.0]:
            val = pct * limit_y
            y_pos = padding_top + h_draw - (pct * h_draw)
            self.canvas.create_line(padding_left, y_pos, W - padding_right, y_pos, fill="#F3F4F6", dash=(4, 4))
            self.canvas.create_text(padding_left - 10, y_pos, text=f"${val:,.0f}", anchor="e", font=("Helvetica", 9), fill="#6B7280")
            
        # Nombres de los meses (Eje X)
        meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        # Puntos de Egresos (Área y Línea)
        puntos_egresos = [padding_left, padding_top + h_draw]
        for i in range(12):
            mes_str = f"{i+1:02d}"
            val = self.datos_flujo[mes_str]["egresos"]
            x = padding_left + (i * w_draw / 11)
            y = padding_top + h_draw - (val / limit_y * h_draw)
            puntos_egresos.extend([x, y])
        puntos_egresos.extend([W - padding_right, padding_top + h_draw])
        
        # Puntos de Ingresos (Área y Línea)
        puntos_ingresos = [padding_left, padding_top + h_draw]
        for i in range(12):
            mes_str = f"{i+1:02d}"
            val = self.datos_flujo[mes_str]["ingresos"]
            x = padding_left + (i * w_draw / 11)
            y = padding_top + h_draw - (val / limit_y * h_draw)
            puntos_ingresos.extend([x, y])
        puntos_ingresos.extend([W - padding_right, padding_top + h_draw])
        
        # Dibujar áreas de fondo
        self.canvas.create_polygon(puntos_egresos, fill="#F9FAFB", outline="")
        self.canvas.create_polygon(puntos_ingresos, fill="#ECFDF5", outline="")
        
        # Dibujar líneas de contorno suavizadas (Bezier)
        if len(puntos_egresos) >= 6:
            line_egresos = puntos_egresos[2:-2]
            self.canvas.create_line(line_egresos, fill="#9CA3AF", width=2, smooth=True)
            
        if len(puntos_ingresos) >= 6:
            line_ingresos = puntos_ingresos[2:-2]
            self.canvas.create_line(line_ingresos, fill="#10B981", width=2, smooth=True)
            
        # Dibujar marcas y textos del eje X
        for i in range(12):
            x = padding_left + (i * w_draw / 11)
            self.canvas.create_line(x, padding_top + h_draw, x, padding_top + h_draw + 5, fill="#E5E7EB")
            self.canvas.create_text(x, padding_top + h_draw + 15, text=meses_nombres[i], font=("Helvetica", 9), fill="#6B7280")

    def actualizar_datos(self):
        data = database.get_dashboard_data()
        
        self.lbl_balance.configure(text=data["balance_total"])
        self.lbl_ingresos.configure(text=data["ingresos"])
        self.lbl_egresos.configure(text=data["egresos"])
        self.lbl_cobrar.configure(text=data["cuentas_cobrar"])
        
        # Obtener y actualizar los datos reales para el gráfico del flujo de caja
        anio = database.get_ultimo_anio_asiento()
        self.datos_flujo = database.get_flujo_caja(anio)
        self.lbl_chart_title.configure(text=f"Flujo de Caja ({anio})")
        self.dibujar_grafico()
        
        for w in self.act_card.winfo_children(): w.destroy()
        
        act_head = ctk.CTkFrame(self.act_card, fg_color="transparent")
        act_head.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        act_head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(act_head, text="Actividad Reciente", font=ctk.CTkFont(size=18, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(act_head, text="Ver todo", font=ctk.CTkFont(size=13, weight="bold"), text_color="#10B981", cursor="hand2").grid(row=0, column=1, sticky="e")
        
        th = ctk.CTkFrame(self.act_card, fg_color="#F9FAFB", height=30, corner_radius=0)
        th.grid(row=1, column=0, sticky="ew")
        th.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(th, text="Fecha", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="w").grid(row=0, column=0, padx=(20, 10))
        ctk.CTkLabel(th, text="Descripción", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", anchor="w").grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(th, text="Categoría", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="w").grid(row=0, column=2)
        ctk.CTkLabel(th, text="Monto", font=ctk.CTkFont(size=12, weight="bold"), text_color="#6B7280", width=100, anchor="e").grid(row=0, column=3, padx=(10, 20))
        
        row_idx = 2
        for a in data["actividades"]:
            tr = ctk.CTkFrame(self.act_card, fg_color="transparent", height=45)
            tr.grid(row=row_idx, column=0, sticky="ew")
            tr.grid_columnconfigure(1, weight=1)
            tr.grid_propagate(False)
            
            ctk.CTkLabel(tr, text=a["fecha"], font=ctk.CTkFont(size=13), text_color="#4B5563", width=100, anchor="w").grid(row=0, column=0, padx=(20, 10), pady=10)
            ctk.CTkLabel(tr, text=a["descripcion"], font=ctk.CTkFont(size=13), text_color="#111827", anchor="w").grid(row=0, column=1, sticky="ew", pady=10)
            
            bg_c = "#D1FAE5" if a["monto_str"].startswith("+") else "#E5E7EB"
            txt_c = "#10B981" if a["monto_str"].startswith("+") else "#4B5563"
            
            cat_f = ctk.CTkFrame(tr, fg_color=bg_c, corner_radius=10, height=20)
            cat_f.grid(row=0, column=2, pady=12, sticky="w")
            cat_f.pack_propagate(False)
            ctk.CTkLabel(cat_f, text=a["categoria"], font=ctk.CTkFont(size=10, weight="bold"), text_color=txt_c).pack(padx=8, pady=2)
            
            val_col = "#10B981" if a["monto_str"].startswith("+") else "#6B7280"
            ctk.CTkLabel(tr, text=a["monto_str"], font=ctk.CTkFont(size=13), text_color=val_col, width=100, anchor="e").grid(row=0, column=3, padx=(10, 20), pady=10)
            
            if row_idx < len(data["actividades"]) + 1:
                ctk.CTkFrame(self.act_card, fg_color="#F3F4F6", height=1).grid(row=row_idx, column=0, sticky="esw")
            row_idx += 1

        if not data["actividades"]:
            ctk.CTkLabel(self.act_card, text="No hay actividad reciente", font=ctk.CTkFont(size=13), text_color="#6B7280").grid(row=2, column=0, pady=20)
            
        for w in self.alert_card.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.alert_card, text="Alertas y Acciones", font=ctk.CTkFont(size=18, weight="bold"), text_color="#111827").grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        if data["num_asientos"] > 0:
            red_a = ctk.CTkFrame(self.alert_card, fg_color="#F3F4F6", corner_radius=8, border_width=1, border_color="#E5E7EB")
            red_a.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
            red_a.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(red_a, text="ℹ", font=ctk.CTkFont(size=20), text_color="#4B5563").grid(row=0, column=0, padx=(15, 10), pady=15, sticky="n")
            red_txt = ctk.CTkFrame(red_a, fg_color="transparent")
            red_txt.grid(row=0, column=1, sticky="ew", pady=15, padx=(0, 15))
            ctk.CTkLabel(red_txt, text=f"{data['num_asientos']} Asientos registrados", font=ctk.CTkFont(size=13, weight="bold"), text_color="#111827", anchor="w").pack(fill="x")
            ctk.CTkLabel(red_txt, text="Revisa el cierre mensual.", font=ctk.CTkFont(size=12), text_color="#4B5563", anchor="w", justify="left").pack(fill="x", pady=(2, 0))
            
        grn_a = ctk.CTkFrame(self.alert_card, fg_color="#ECFDF5", corner_radius=8, border_width=1, border_color="#6EE7B7")
        grn_a.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        grn_a.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(grn_a, text="✓", font=ctk.CTkFont(size=20), text_color="#10B981").grid(row=0, column=0, padx=(15, 10), pady=15, sticky="n")
        grn_txt = ctk.CTkFrame(grn_a, fg_color="transparent")
        grn_txt.grid(row=0, column=1, sticky="ew", pady=15, padx=(0, 15))
        ctk.CTkLabel(grn_txt, text="Sistema al día", font=ctk.CTkFont(size=13, weight="bold"), text_color="#111827", anchor="w").pack(fill="x")
        ctk.CTkLabel(grn_txt, text="Todo está en orden.", font=ctk.CTkFont(size=12), text_color="#4B5563", anchor="w", justify="left").pack(fill="x", pady=(2, 5))
