# -*- coding: utf-8 -*-
# Este archivo contiene la "Lógica de Negocio". Aquí se realizan los cálculos matemáticos,
# validaciones contables y los cierres de ejercicio para asegurar que se respeten las reglas de la contabilidad.

from datetime import datetime
import database

def validar_equilibrio(detalles):
    # Regla de Oro Contable: Valida que la suma de todos los montos en el Debe sea
    # exactamente igual a la suma de todos los montos en el Haber en un asiento (Partida Doble).
    suma_debe = round(sum(float(d[1]) for d in detalles), 2)
    suma_haber = round(sum(float(d[2]) for d in detalles), 2)
    return suma_debe == suma_haber

def validar_fecha_asiento(fecha_str):
    # Valida que la fecha del asiento no corresponda a un periodo que ya ha sido cerrado.
    # Si el periodo contable ya se cerró, impide registrar nuevos movimientos en esa fecha.
    ultimo_cierre_str = database.get_fecha_ultimo_cierre()
    if not ultimo_cierre_str:
        return True, ""
    
    fecha_ingresada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    fecha_ultimo_cierre = datetime.strptime(ultimo_cierre_str, "%Y-%m-%d").date()
    
    if fecha_ingresada <= fecha_ultimo_cierre:
        return False, f"Período cerrado. No se permiten asientos en o antes del {ultimo_cierre_str}."
    return True, ""

def calcular_saldos_mayor():
    # Indica el saldo neto total de cada cuenta y si aumenta por el Debe o por el Haber.
    # Resta Debe menos Haber para cuentas de Activo/Egreso, y Haber menos Debe para Pasivo/Capital/Ingreso.
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
    # Proceso de Cierre de Ejercicio: Toma todas las cuentas de Ingresos y Egresos (cuentas nominales)
    # y traslada la utilidad o pérdida calculada a la cuenta patrimonial de Capital Social, saldando y bloqueando el periodo.
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

def reversar_asiento(asiento_id, fecha_reverso, descripcion_reverso):
    # Reverso Contable (Anulación): Crea una transacción que invierte los montos (el Debe pasa al Haber
    # y el Haber al Debe) del asiento original seleccionado para anular su efecto financiero sin borrar la auditoría.
    valido, msg = validar_fecha_asiento(fecha_reverso)
    if not valido:
        return False, msg
        
    asiento = database.get_asiento(asiento_id)
    if not asiento:
        return False, "Asiento original no encontrado."
        
    detalles_reverso = []
    for detalle in asiento["detalles"]:
        cuenta_id, debe, haber = detalle
        # Invertimos: el nuevo debe es el antiguo haber, el nuevo haber es el antiguo debe
        detalles_reverso.append((cuenta_id, haber, debe))
        
    if not validar_equilibrio(detalles_reverso):
        return False, "Error de cuadre en el asiento de reverso."
        
    exito, msg = database.insertar_asiento(fecha_reverso, descripcion_reverso, detalles_reverso)
    return exito, msg

def calcular_movimientos_mayor(cuenta_id):
    # Calcula la columna de "Saldo Acumulado" línea por línea para los movimientos de una cuenta específica,
    # sumando o restando según el tipo de cuenta (si aumenta por el debe o por el haber).
    cuentas = database.get_cuentas()
    cuenta_obj = next((c for c in cuentas if c[0] == cuenta_id), None)
    if not cuenta_obj: return []
    
    tipo = cuenta_obj[3]
    es_deudora = tipo in ["Activo", "Egreso"]
    
    movimientos = database.get_movimientos_cuenta(cuenta_id)
    resultado = []
    saldo_acumulado = 0.0
    
    for mov in movimientos:
        fecha, desc, debe, haber = mov
        if es_deudora:
            saldo_acumulado += (debe - haber)
        else:
            saldo_acumulado += (haber - debe)
            
        resultado.append({
            "fecha": fecha,
            "concepto": desc,
            "debe": debe,
            "haber": haber,
            "saldo": saldo_acumulado
        })
    return resultado

def calcular_hoja_trabajo():
    # Genera la Hoja de Trabajo de 12 columnas: una matriz analítica que clasifica y suma
    # los movimientos en Sumas, Saldos, Ajustes, Saldos Ajustados, Resultados y Balance General.
    saldos = database.get_saldos_cuentas()
    filas = []
    totales = {
        "sum_d": 0, "sum_h": 0,
        "sal_d": 0, "sal_h": 0,
        "aju_d": 0, "aju_h": 0,
        "aju_sal_d": 0, "aju_sal_h": 0,
        "res_d": 0, "res_h": 0,
        "bg_d": 0, "bg_h": 0
    }
    
    for c in saldos:
        _, codigo, nombre, tipo, debe_sum, haber_sum = c
        debe_sum = debe_sum or 0
        haber_sum = haber_sum or 0
        
        if debe_sum == 0 and haber_sum == 0:
            continue
            
        sal_d, sal_h = 0, 0
        if tipo in ["Activo", "Egreso"]:
            sal_d = max(0, debe_sum - haber_sum)
            sal_h = max(0, haber_sum - debe_sum)
        else:
            sal_h = max(0, haber_sum - debe_sum)
            sal_d = max(0, debe_sum - haber_sum)
            
        # Sin ajustes por ahora
        aju_d, aju_h = 0, 0
        aju_sal_d, aju_sal_h = sal_d, sal_h
        
        res_d, res_h = 0, 0
        bg_d, bg_h = 0, 0
        
        if tipo == "Egreso":
            res_d = aju_sal_d
        elif tipo == "Ingreso":
            res_h = aju_sal_h
        elif tipo == "Activo":
            bg_d = aju_sal_d
        elif tipo in ["Pasivo", "Capital"]:
            bg_h = aju_sal_h
            
        filas.append({
            "cuenta": f"{codigo} - {nombre}",
            "sum_d": debe_sum, "sum_h": haber_sum,
            "sal_d": sal_d, "sal_h": sal_h,
            "aju_d": aju_d, "aju_h": aju_h,
            "aju_sal_d": aju_sal_d, "aju_sal_h": aju_sal_h,
            "res_d": res_d, "res_h": res_h,
            "bg_d": bg_d, "bg_h": bg_h
        })
        
        totales["sum_d"] += debe_sum
        totales["sum_h"] += haber_sum
        totales["sal_d"] += sal_d
        totales["sal_h"] += sal_h
        totales["aju_sal_d"] += aju_sal_d
        totales["aju_sal_h"] += aju_sal_h
        totales["res_d"] += res_d
        totales["res_h"] += res_h
        totales["bg_d"] += bg_d
        totales["bg_h"] += bg_h

    utilidad = totales["res_h"] - totales["res_d"]
    totales["utilidad"] = utilidad
    
    return filas, totales
