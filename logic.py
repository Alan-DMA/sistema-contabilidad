# -*- coding: utf-8 -*-
from datetime import datetime
import database

def validar_equilibrio(detalles):
    """
    Valida la regla de oro de la partida doble.
    detalles: lista de tuplas (cuenta_id, debe, haber)
    """
    suma_debe = round(sum(float(d[1]) for d in detalles), 2) #esta linea compara la suma del debe con la suma del haber
    suma_haber = round(sum(float(d[2]) for d in detalles), 2)
    return suma_debe == suma_haber

def validar_fecha_asiento(fecha_str):
    """
    Valida que la fecha del asiento no sea menor o igual al último cierre (Bloqueo de período).
    Retorna (es_valida, mensaje)
    """
    ultimo_cierre_str = database.get_fecha_ultimo_cierre()
    if not ultimo_cierre_str:
        return True, ""
    
    fecha_ingresada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    fecha_ultimo_cierre = datetime.strptime(ultimo_cierre_str, "%Y-%m-%d").date()
    
    if fecha_ingresada <= fecha_ultimo_cierre:
        return False, f"Período cerrado. No se permiten asientos en o antes del {ultimo_cierre_str}."
    return True, ""

def calcular_saldos_mayor():
    """
    Devuelve una lista de cuentas con su saldo neto y si es Deudor o Acreedor.
    """
    datos = database.get_saldos_cuentas()
    resultados = []
    for row in datos:
        cuenta_id, codigo, nombre, tipo, total_debe, total_haber = row
        total_debe = float(total_debe or 0.0)
        total_haber = float(total_haber or 0.0)
        
        # Cuentas Deudoras: Activos, Egresos
        if tipo in ["Activo", "Egreso"]:
            saldo = total_debe - total_haber
        # Cuentas Acreedoras: Pasivos, Capital, Ingresos
        else:
            saldo = total_haber - total_debe
            
        resultados.append({
            "id": cuenta_id,
            "codigo": codigo,
            "nombre": nombre,
            "tipo": tipo,
            "debe": total_debe,
            "haber": total_haber,
            "saldo": saldo
        })
    return resultados

def ejecutar_cierre_contable(fecha_cierre):
    """
    Consolida cuentas de Ingreso y Egreso, y calcula la utilidad.
    Genera el asiento de cierre contra Capital Social.
    """
    valido, msg = validar_fecha_asiento(fecha_cierre)
    if not valido:
        return False, msg
        
    saldos = calcular_saldos_mayor()
    
    ingresos = [c for c in saldos if c["tipo"] == "Ingreso" and c["saldo"] != 0]
    egresos = [c for c in saldos if c["tipo"] == "Egreso" and c["saldo"] != 0]
    
    if not ingresos and not egresos:
        return False, "No hay saldos en cuentas nominales para cerrar."
        
    detalles_asiento = []
    
    total_ingresos = 0.0
    for ing in ingresos:
        # Ingreso tiene saldo acreedor. Para cerrarlo lo cargamos (Debe)
        detalles_asiento.append((ing["id"], ing["saldo"], 0.0))
        total_ingresos += ing["saldo"]
        
    total_egresos = 0.0
    for egr in egresos:
        # Egreso tiene saldo deudor. Para cerrarlo lo abonamos (Haber)
        detalles_asiento.append((egr["id"], 0.0, egr["saldo"]))
        total_egresos += egr["saldo"]
        
    utilidad = total_ingresos - total_egresos
    
    # Buscar cuenta destino según el resultado
    cuentas = database.get_cuentas()
    cuenta_id_destino = None
    
    nombre_cuenta_destino = "Utilidad del Ejercicio" if utilidad >= 0 else "Pérdida del Ejercicio"
    
    for c in cuentas:
        if c[2] == nombre_cuenta_destino:
            cuenta_id_destino = c[0]
            break
            
    if not cuenta_id_destino:
        return False, f"No se encontró la cuenta '{nombre_cuenta_destino}' para el cierre."
        
    # Asentar la utilidad/pérdida
    if utilidad >= 0:
        detalles_asiento.append((cuenta_id_destino, 0.0, utilidad))
    else:
        detalles_asiento.append((cuenta_id_destino, abs(utilidad), 0.0))
        
    if not validar_equilibrio(detalles_asiento):
        return False, "Error interno matemático en el cuadre del cierre."
        
    exito, msg = database.insertar_asiento(fecha_cierre, "ASIENTO DE CIERRE EJERCICIO", detalles_asiento)
    return exito, msg
