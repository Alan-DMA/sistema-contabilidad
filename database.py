# -*- coding: utf-8 -*-
import sqlite3
import os

DB_PATH = 'contabilidad.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla Cuentas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    
    # Tabla Asientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE NOT NULL,
            descripcion TEXT NOT NULL
        )
    ''')
    
    # Tabla Detalle Asientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detalle_asientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asiento_id INTEGER,
            cuenta_id INTEGER,
            debe DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            haber DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            FOREIGN KEY(asiento_id) REFERENCES asientos(id),
            FOREIGN KEY(cuenta_id) REFERENCES cuentas(id)
        )
    ''')
    
    # Población Inicial del Catálogo de Cuentas si está vacío
    cursor.execute("SELECT COUNT(*) FROM cuentas")
    if cursor.fetchone()[0] == 0:
        cuentas_base = [
            ("1.1.01", "Caja", "Activo"),
            ("1.1.02", "Bancos", "Activo"),
            ("1.1.03", "Cuentas por Cobrar", "Activo"),
            ("1.1.04", "Inventario", "Activo"),
            ("2.1.01", "Cuentas por Pagar", "Pasivo"),
            ("2.1.02", "Préstamos Bancarios", "Pasivo"),
            ("3.1.01", "Capital Social", "Capital"),
            ("3.1.02", "Utilidad del Ejercicio", "Capital"),
            ("3.1.03", "Pérdida del Ejercicio", "Capital"),
            ("4.1.01", "Ingresos por Ventas", "Ingreso"),
            ("4.1.02", "Ingresos por Servicios", "Ingreso"),
            ("5.1.01", "Gastos de Alquiler", "Egreso"),
            ("5.1.02", "Gastos de Salarios", "Egreso"),
            ("5.1.03", "Gastos de Servicios Básicos", "Egreso")
        ]
        cursor.executemany("INSERT INTO cuentas (codigo, nombre, tipo) VALUES (?, ?, ?)", cuentas_base)
    
    conn.commit()
    conn.close()

def get_cuentas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo, nombre, tipo FROM cuentas ORDER BY codigo")
    cuentas = cursor.fetchall()
    conn.close()
    return cuentas

def get_fecha_ultimo_cierre():
    # Asumimos que los asientos de cierre tienen una descripción específica "ASIENTO DE CIERRE EJERCICIO"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(fecha) FROM asientos WHERE descripcion = 'ASIENTO DE CIERRE EJERCICIO'")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado

def insertar_asiento(fecha, descripcion, detalles):
    # detalles es una lista de tuplas: (cuenta_id, debe, haber)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO asientos (fecha, descripcion) VALUES (?, ?)", (fecha, descripcion))
        asiento_id = cursor.lastrowid
        
        for cuenta_id, debe, haber in detalles:
            cursor.execute('''
                INSERT INTO detalle_asientos (asiento_id, cuenta_id, debe, haber)
                VALUES (?, ?, ?, ?)
            ''', (asiento_id, cuenta_id, debe, haber))
            
        conn.commit()
        return True, "Asiento guardado exitosamente."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_saldos_cuentas():
    # Retorna los saldos consolidados por cuenta basándose en todo el historial
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            c.id, c.codigo, c.nombre, c.tipo,
            SUM(d.debe) as total_debe,
            SUM(d.haber) as total_haber
        FROM cuentas c
        LEFT JOIN detalle_asientos d ON c.id = d.cuenta_id
        GROUP BY c.id
        ORDER BY c.codigo
    ''')
    saldos = cursor.fetchall()
    conn.close()
    return saldos

def get_libro_diario():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.fecha, a.descripcion, c.codigo, c.nombre, d.debe, d.haber
        FROM asientos a
        JOIN detalle_asientos d ON a.id = d.asiento_id
        JOIN cuentas c ON c.id = d.cuenta_id
        ORDER BY a.fecha, a.id, d.id
    ''')
    registros = cursor.fetchall()
    conn.close()
    return registros
