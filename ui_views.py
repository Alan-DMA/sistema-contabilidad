# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import database
import logic

class DiarioView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(self, text="NUEVO ASIENTO - LIBRO DIARIO", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # --- Cabecera ---
        cabecera_frame = ctk.CTkFrame(self)
        cabecera_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        cabecera_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(cabecera_frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
        self.entry_fecha = ctk.CTkEntry(cabecera_frame, width=120)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        ctk.CTkLabel(cabecera_frame, text="Concepto:").grid(row=0, column=2, padx=10, pady=10)
        self.entry_concepto = ctk.CTkEntry(cabecera_frame, width=300)
        self.entry_concepto.grid(row=0, column=3, sticky="we", padx=10, pady=10)
        
        # --- Cuerpo de Transacciones ---
        self.transacciones_frame = ctk.CTkScrollableFrame(self)
        self.transacciones_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        self.transacciones_frame.grid_columnconfigure(1, weight=1)
        
        # Titulos columnas
        ctk.CTkLabel(self.transacciones_frame, text="Cuenta", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(self.transacciones_frame, text="Debe ($)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(self.transacciones_frame, text="Haber ($)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5)
        
        self.lineas = []
        self.cuentas = []
        self.cuentas_dict = {}
        
        # --- Controles Inferiores ---
        controles_frame = ctk.CTkFrame(self, fg_color="transparent")
        controles_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.btn_agregar = ctk.CTkButton(controles_frame, text="+ Agregar línea", command=self.agregar_linea, width=120)
        self.btn_agregar.pack(side="left", padx=5)
        
        # --- Totales y Guardar ---
        totales_frame = ctk.CTkFrame(self)
        totales_frame.grid(row=4, column=0, sticky="ew", pady=10)
        totales_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_totales = ctk.CTkLabel(totales_frame, text="Totales: Debe: 0.00 | Haber: 0.00", font=ctk.CTkFont(weight="bold"))
        self.lbl_totales.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.lbl_estado = ctk.CTkLabel(totales_frame, text="[ DESCUADRADO ]", text_color="red", font=ctk.CTkFont(weight="bold"))
        self.lbl_estado.grid(row=0, column=1, padx=20, pady=10)
        
        self.btn_guardar = ctk.CTkButton(totales_frame, text="GUARDAR ASIENTO", command=self.guardar_asiento, state="disabled")
        self.btn_guardar.grid(row=0, column=2, padx=20, pady=10)
        
        self.actualizar_datos()
        
    def actualizar_datos(self):
        datos_cuentas = database.get_cuentas()
        self.cuentas = [f"{c[1]} - {c[2]}" for c in datos_cuentas]
        self.cuentas_dict = {f"{c[1]} - {c[2]}": c[0] for c in datos_cuentas}
        
        if not self.lineas:
            self.agregar_linea()
            self.agregar_linea()
            
    def agregar_linea(self):
        row_idx = len(self.lineas) + 1
        
        combo_cuenta = ctk.CTkComboBox(self.transacciones_frame, values=self.cuentas, width=300)
        combo_cuenta.grid(row=row_idx, column=1, sticky="we", padx=5, pady=5)
        
        entry_debe = ctk.CTkEntry(self.transacciones_frame, width=100)
        entry_debe.insert(0, "0.00")
        entry_debe.grid(row=row_idx, column=2, padx=5, pady=5)
        entry_debe.bind("<KeyRelease>", self.validar_totales)
        
        entry_haber = ctk.CTkEntry(self.transacciones_frame, width=100)
        entry_haber.insert(0, "0.00")
        entry_haber.grid(row=row_idx, column=3, padx=5, pady=5)
        entry_haber.bind("<KeyRelease>", self.validar_totales)
        
        btn_eliminar = ctk.CTkButton(self.transacciones_frame, text="X", width=30, fg_color="#8B0000", hover_color="#5C0000",
                                     command=lambda r=row_idx: self.eliminar_linea(r))
        btn_eliminar.grid(row=row_idx, column=4, padx=5, pady=5)
        
        self.lineas.append({
            "row_idx": row_idx,
            "combo": combo_cuenta,
            "debe": entry_debe,
            "haber": entry_haber,
            "btn": btn_eliminar
        })
        self.validar_totales(None)
        
    def eliminar_linea(self, row_idx):
        if len(self.lineas) <= 2: return
            
        for linea in self.lineas:
            if linea["row_idx"] == row_idx:
                linea["combo"].destroy()
                linea["debe"].destroy()
                linea["haber"].destroy()
                linea["btn"].destroy()
                self.lineas.remove(linea)
                break
        self.validar_totales(None)
        
    def obtener_detalles_actuales(self):
        detalles = []
        try:
            for l in self.lineas:
                cuenta_str = l["combo"].get()
                if not cuenta_str: continue
                cuenta_id = self.cuentas_dict.get(cuenta_str)
                if not cuenta_id: continue
                
                d_val = float(l["debe"].get() or 0)
                h_val = float(l["haber"].get() or 0)
                
                if d_val < 0 or h_val < 0: raise ValueError("Negativos")
                if d_val == 0 and h_val == 0: continue
                    
                detalles.append((cuenta_id, d_val, h_val))
        except ValueError:
            return None
        return detalles
        
    def validar_totales(self, event):
        detalles = self.obtener_detalles_actuales()
        if detalles is None:
            self.lbl_estado.configure(text="[ ERROR DE FORMATO ]", text_color="red")
            self.lbl_totales.configure(text="Totales: Debe: ERR | Haber: ERR")
            self.btn_guardar.configure(state="disabled")
            return
            
        suma_debe = sum(d[1] for d in detalles)
        suma_haber = sum(d[2] for d in detalles)
        
        self.lbl_totales.configure(text=f"Totales: Debe: {suma_debe:.2f} | Haber: {suma_haber:.2f}")
        
        if sum(d[1] for d in detalles) == 0 and sum(d[2] for d in detalles) == 0:
            self.lbl_estado.configure(text="[ VACÍO ]", text_color="gray")
            self.btn_guardar.configure(state="disabled")
            return
            
        if logic.validar_equilibrio(detalles):
            self.lbl_estado.configure(text="[ CUADRADO ]", text_color="#2ecc71")
            self.btn_guardar.configure(state="normal", fg_color="#27ae60")
        else:
            self.lbl_estado.configure(text="[ DESCUADRADO ]", text_color="#e74c3c")
            self.btn_guardar.configure(state="disabled", fg_color="gray")
            
    def guardar_asiento(self):
        fecha = self.entry_fecha.get()
        concepto = self.entry_concepto.get()
        
        if not fecha or not concepto:
            messagebox.showwarning("Faltan Datos", "Debe ingresar fecha y concepto.")
            return
            
        valido, msg_f = logic.validar_fecha_asiento(fecha)
        if not valido:
            messagebox.showerror("Bloqueo de Período", msg_f)
            return
            
        detalles = self.obtener_detalles_actuales()
        if not detalles or len(detalles) < 2:
            messagebox.showwarning("Asiento Inválido", "Debe ingresar al menos dos líneas de transacción válidas.")
            return
            
        exito, msg = database.insertar_asiento(fecha, concepto, detalles)
        if exito:
            messagebox.showinfo("Éxito", "Asiento registrado correctamente.")
            self.entry_concepto.delete(0, 'end')
            for l in self.lineas:
                l["debe"].delete(0, 'end')
                l["debe"].insert(0, "0.00")
                l["haber"].delete(0, 'end')
                l["haber"].insert(0, "0.00")
            self.validar_totales(None)
        else:
            messagebox.showerror("Error", msg)

class MayorView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="LIBRO MAYOR (Saldos)", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
    def actualizar_datos(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
            
        headers = ["Código", "Cuenta", "Tipo", "Saldo Neto ($)"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.scroll_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, pady=10, sticky="w", padx=10)
            
        saldos = logic.calcular_saldos_mayor()
        row = 1
        for s in saldos:
            if s["debe"] == 0 and s["haber"] == 0: continue
            ctk.CTkLabel(self.scroll_frame, text=s["codigo"]).grid(row=row, column=0, sticky="w", padx=10)
            ctk.CTkLabel(self.scroll_frame, text=s["nombre"]).grid(row=row, column=1, sticky="w", padx=10)
            ctk.CTkLabel(self.scroll_frame, text=s["tipo"]).grid(row=row, column=2, sticky="w", padx=10)
            ctk.CTkLabel(self.scroll_frame, text=f"{s['saldo']:,.2f}").grid(row=row, column=3, sticky="w", padx=10)
            row += 1

class BalanceComprobacionView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="BALANCE DE COMPROBACIÓN", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.totales_lbl = ctk.CTkLabel(self, text="Sumas Iguales: 0.00", font=ctk.CTkFont(size=18, weight="bold"))
        self.totales_lbl.grid(row=2, column=0, pady=20, sticky="e")
        
    def actualizar_datos(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
            
        headers = ["Código", "Cuenta", "Deudor ($)", "Acreedor ($)"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.scroll_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, pady=10, sticky="w", padx=10)
            
        saldos = logic.calcular_saldos_mayor()
        row = 1
        suma_deudor = 0
        suma_acreedor = 0
        
        for s in saldos:
            if s["debe"] == 0 and s["haber"] == 0: continue
            
            ctk.CTkLabel(self.scroll_frame, text=s["codigo"]).grid(row=row, column=0, sticky="w", padx=10)
            ctk.CTkLabel(self.scroll_frame, text=s["nombre"]).grid(row=row, column=1, sticky="w", padx=10)
            
            if s["tipo"] in ["Activo", "Egreso"]:
                ctk.CTkLabel(self.scroll_frame, text=f"{s['saldo']:,.2f}").grid(row=row, column=2, sticky="w", padx=10)
                ctk.CTkLabel(self.scroll_frame, text="-").grid(row=row, column=3, sticky="w", padx=10)
                suma_deudor += s['saldo']
            else:
                ctk.CTkLabel(self.scroll_frame, text="-").grid(row=row, column=2, sticky="w", padx=10)
                ctk.CTkLabel(self.scroll_frame, text=f"{s['saldo']:,.2f}").grid(row=row, column=3, sticky="w", padx=10)
                suma_acreedor += s['saldo']
            row += 1
            
        self.totales_lbl.configure(text=f"Sumas Iguales: Deudor {suma_deudor:,.2f} | Acreedor {suma_acreedor:,.2f}")

class EstadosFinancierosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="ESTADOS FINANCIEROS", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        self.frame_resultados = ctk.CTkScrollableFrame(self)
        self.frame_resultados.grid(row=1, column=0, sticky="nsew", padx=10)
        
        self.frame_situacion = ctk.CTkScrollableFrame(self)
        self.frame_situacion.grid(row=1, column=1, sticky="nsew", padx=10)
        
    def actualizar_datos(self):
        for w in self.frame_resultados.winfo_children(): w.destroy()
        for w in self.frame_situacion.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.frame_resultados, text="ESTADO DE RESULTADOS", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.frame_situacion, text="ESTADO DE SITUACIÓN FINANCIERA", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        saldos = logic.calcular_saldos_mayor()
        
        ingresos = sum(s["saldo"] for s in saldos if s["tipo"] == "Ingreso")
        egresos = sum(s["saldo"] for s in saldos if s["tipo"] == "Egreso")
        
        ctk.CTkLabel(self.frame_resultados, text="INGRESOS:").pack(anchor="w", padx=10)
        for s in saldos:
            if s["tipo"] == "Ingreso" and s["saldo"] != 0:
                ctk.CTkLabel(self.frame_resultados, text=f"  {s['nombre']}: {s['saldo']:,.2f}").pack(anchor="w", padx=10)
                
        ctk.CTkLabel(self.frame_resultados, text="EGRESOS:").pack(anchor="w", padx=10, pady=(10,0))
        for s in saldos:
            if s["tipo"] == "Egreso" and s["saldo"] != 0:
                ctk.CTkLabel(self.frame_resultados, text=f"  {s['nombre']}: {s['saldo']:,.2f}").pack(anchor="w", padx=10)
                
        utilidad = ingresos - egresos
        color = "#2ecc71" if utilidad >= 0 else "#e74c3c"
        ctk.CTkLabel(self.frame_resultados, text=f"UTILIDAD/PÉRDIDA: {utilidad:,.2f}", text_color=color, font=ctk.CTkFont(weight="bold")).pack(pady=20)
        
        activos = sum(s["saldo"] for s in saldos if s["tipo"] == "Activo")
        pasivos = sum(s["saldo"] for s in saldos if s["tipo"] == "Pasivo")
        capital = sum(s["saldo"] for s in saldos if s["tipo"] == "Capital")
        
        ctk.CTkLabel(self.frame_situacion, text="ACTIVOS:").pack(anchor="w", padx=10)
        for s in saldos:
            if s["tipo"] == "Activo" and s["saldo"] != 0:
                ctk.CTkLabel(self.frame_situacion, text=f"  {s['nombre']}: {s['saldo']:,.2f}").pack(anchor="w", padx=10)
                
        ctk.CTkLabel(self.frame_situacion, text="PASIVOS:").pack(anchor="w", padx=10, pady=(10,0))
        for s in saldos:
            if s["tipo"] == "Pasivo" and s["saldo"] != 0:
                ctk.CTkLabel(self.frame_situacion, text=f"  {s['nombre']}: {s['saldo']:,.2f}").pack(anchor="w", padx=10)
                
        ctk.CTkLabel(self.frame_situacion, text="CAPITAL:").pack(anchor="w", padx=10, pady=(10,0))
        for s in saldos:
            if s["tipo"] == "Capital" and s["saldo"] != 0:
                ctk.CTkLabel(self.frame_situacion, text=f"  {s['nombre']}: {s['saldo']:,.2f}").pack(anchor="w", padx=10)
                
        if utilidad != 0:
            lbl_util = "Utilidad del Ejercicio (En curso)" if utilidad > 0 else "Pérdida del Ejercicio (En curso)"
            ctk.CTkLabel(self.frame_situacion, text=f"  {lbl_util}: {utilidad:,.2f}").pack(anchor="w", padx=10)
                
        ctk.CTkLabel(self.frame_situacion, text=f"TOTAL ACTIVO: {activos:,.2f}", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self.frame_situacion, text=f"TOTAL PASIVO + CAPITAL: {(pasivos + capital + utilidad):,.2f}", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
class CierreView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        ctk.CTkLabel(self, text="CIERRE CONTABLE", font=ctk.CTkFont(size=24, weight="bold"), text_color="#e74c3c").pack(pady=20)
        
        info = "⚠️ ADVERTENCIA ⚠️\n\nEl cierre contable consolidará las cuentas nominales (Ingresos y Egresos)\ny transferirá el resultado a la cuenta de Capital Social.\n\nAl realizar el cierre, se BLOQUEARÁ EL PERÍODO. No podrá ingresar\nningún asiento nuevo con fecha igual o anterior a la fecha de cierre.\n\nEsta acción es irreversible."
        ctk.CTkLabel(self, text=info, font=ctk.CTkFont(size=14)).pack(pady=20)
        
        ctk.CTkLabel(self, text="Fecha de Cierre (YYYY-MM-DD):").pack(pady=5)
        self.entry_fecha = ctk.CTkEntry(self, width=150)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(pady=5)
        
        self.btn_cierre = ctk.CTkButton(self, text="EJECUTAR CIERRE DEL EJERCICIO", fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(weight="bold"), command=self.ejecutar_cierre)
        self.btn_cierre.pack(pady=30)
        
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
