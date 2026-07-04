# -*- coding: utf-8 -*-
# Este archivo se encarga de gestionar la Base de Datos. Guarda y recupera toda la información
# del sistema (usuarios, cuentas contables y asientos) en un archivo local llamado 'contabilidad.db'.

import sqlite3
import os
import sys

def get_db_path():
    # Si la aplicación se ejecuta compilada como un ejecutable (.exe),
    # guardamos la base de datos en la carpeta Local AppData del usuario
    # para evitar problemas de permisos de escritura (ej. al estar en Archivos de Programa)
    if getattr(sys, 'frozen', False):
        app_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'AuraBooks')
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
        return os.path.join(app_data_dir, 'contabilidad.db')
    else:
        # En desarrollo local, guardamos directamente en la carpeta raíz del proyecto
        return 'contabilidad.db'

DB_PATH = get_db_path()

def get_connection():
    # Conecta el programa con el archivo físico de la base de datos para poder guardar o leer información.
    return sqlite3.connect(DB_PATH)

def init_db():
    # Prepara el archivo de base de datos la primera vez que se abre el programa.
    # Crea las "tablas" (como hojas de Excel) para almacenar Usuarios, Cuentas, Asientos Contables y sus detalles.
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')
    
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
            ("1.1.05", "Mobiliario y Equipo", "Activo"),
            ("1.1.06", "Equipos de Computación", "Activo"),
            ("1.1.07", "Edificios", "Activo"),
            ("2.1.01", "Cuentas por Pagar", "Pasivo"),
            ("2.1.02", "Préstamos Bancarios", "Pasivo"),
            ("2.1.03", "Documentos por Pagar", "Pasivo"),
            ("2.1.04", "Impuestos por Pagar", "Pasivo"),
            ("3.1.01", "Capital Social", "Capital"),
            ("3.1.02", "Utilidad del Ejercicio", "Capital"),
            ("3.1.03", "Pérdida del Ejercicio", "Capital"),
            ("3.1.04", "Reservas Legales", "Capital"),
            ("4.1.01", "Ingresos por Ventas", "Ingreso"),
            ("4.1.02", "Ingresos por Servicios", "Ingreso"),
            ("4.1.03", "Ingresos Financieros", "Ingreso"),
            ("5.1.01", "Gastos de Alquiler", "Egreso"),
            ("5.1.02", "Gastos de Salarios", "Egreso"),
            ("5.1.03", "Gastos de Servicios Básicos", "Egreso"),
            ("5.1.04", "Gastos de Seguros", "Egreso"),
            ("5.1.05", "Gastos de Publicidad", "Egreso")
        ]
        cursor.executemany("INSERT INTO cuentas (codigo, nombre, tipo) VALUES (?, ?, ?)", cuentas_base)

    # Población Inicial Usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios_base = [
            ("admin", "Ab123456", "Administrador"),
            ("operador", "OP123456", "Operador")
        ]
        cursor.executemany("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", usuarios_base)
    
    conn.commit()
    conn.close()

def get_cuentas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, codigo, nombre, tipo FROM cuentas ORDER BY codigo")
    cuentas = cursor.fetchall()
    conn.close()
    return cuentas

def insertar_cuenta(codigo, nombre, tipo):
    # Agrega una nueva cuenta contable al catálogo (por ejemplo: "1.1.08 Caja Chica" de tipo "Activo").
    # Verifica primero que no exista ya otra cuenta registrada con el mismo código.
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM cuentas WHERE codigo = ?", (codigo,))
        if cursor.fetchone():
            return False, "El código de cuenta ya existe."
        
        cursor.execute("INSERT INTO cuentas (codigo, nombre, tipo) VALUES (?, ?, ?)", (codigo, nombre, tipo))
        conn.commit()
        return True, "Cuenta creada exitosamente."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_fecha_ultimo_cierre():
    # Asumimos que los asientos de cierre tienen una descripción específica "ASIENTO DE CIERRE EJERCICIO"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(fecha) FROM asientos WHERE descripcion = 'ASIENTO DE CIERRE EJERCICIO'")
    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado

def insertar_asiento(fecha, descripcion, detalles):
    # Guarda un nuevo registro de transacción (asiento contable) en el libro diario.
    # Guarda la cabecera (fecha y explicación) y cada una de las líneas con sus montos en el Debe o en el Haber.
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
    # Suma todos los montos registrados en el Debe y el Haber de cada cuenta en toda la historia
    # para saber cuánto dinero se ha movido en total en cada una de ellas.
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
    # Recupera todos los asientos contables registrados con sus cuentas y montos,
    # ordenados cronológicamente, para mostrarlos en el reporte del Libro Diario.
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

def autenticar_usuario(username, password):
    # Compara el nombre de usuario y contraseña escritos en la pantalla de login con los guardados
    # en la base de datos para dar acceso al programa si son correctos.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, rol FROM usuarios WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "rol": user[2]}
    return None

def get_asiento(asiento_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, descripcion FROM asientos WHERE id = ?", (asiento_id,))
    asiento = cursor.fetchone()
    if not asiento:
        conn.close()
        return None
        
    cursor.execute("SELECT cuenta_id, debe, haber FROM detalle_asientos WHERE asiento_id = ?", (asiento_id,))
    detalles = cursor.fetchall()
    conn.close()
    
    return {
        "id": asiento_id,
        "fecha": asiento[0],
        "descripcion": asiento[1],
        "detalles": detalles
    }

def get_movimientos_cuenta(cuenta_id):
    # Obtiene todos los movimientos (entradas y salidas) de una cuenta específica ordenados por fecha,
    # necesario para armar el reporte del Libro Mayor de esa cuenta.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.fecha, a.descripcion, d.debe, d.haber
        FROM detalle_asientos d
        JOIN asientos a ON d.asiento_id = a.id
        WHERE d.cuenta_id = ?
        ORDER BY a.fecha, a.id
    ''', (cuenta_id,))
    movimientos = cursor.fetchall()
    conn.close()
    return movimientos

def get_dashboard_data():
    # Obtiene los datos generales que se muestran en el panel de control inicial (Dashboard):
    # Activos totales, ingresos, egresos, cuentas por cobrar y los 4 asientos más recientes.
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.tipo, SUM(d.debe), SUM(d.haber), c.nombre
        FROM cuentas c
        LEFT JOIN detalle_asientos d ON c.id = d.cuenta_id
        GROUP BY c.id
    ''')
    cuentas_data = cursor.fetchall()
    
    total_activos = 0.0
    total_ingresos = 0.0
    total_egresos = 0.0
    cuentas_cobrar = 0.0
    
    for row in cuentas_data:
        tipo = row[0]
        debe = row[1] or 0.0
        haber = row[2] or 0.0
        nombre = row[3]
        
        if tipo == "Activo":
            saldo = debe - haber
            total_activos += saldo
            if "cobrar" in nombre.lower():
                cuentas_cobrar += saldo
        elif tipo == "Ingreso":
            saldo = haber - debe
            total_ingresos += saldo
        elif tipo == "Egreso":
            saldo = debe - haber
            total_egresos += saldo
            
    cursor.execute('''
        SELECT a.id, a.fecha, a.descripcion
        FROM asientos a
        ORDER BY a.fecha DESC, a.id DESC
        LIMIT 4
    ''')
    recent_asientos = cursor.fetchall()
    
    actividades = []
    for a in recent_asientos:
        a_id, fecha, desc = a
        cursor.execute('SELECT SUM(debe) FROM detalle_asientos WHERE asiento_id = ?', (a_id,))
        monto = cursor.fetchone()[0] or 0.0
        
        sign = "+"
        if "pago" in desc.lower() or "gasto" in desc.lower() or "compra" in desc.lower():
            sign = "-"
            
        actividades.append({
            "fecha": fecha,
            "descripcion": desc,
            "categoria": "OPERACIÓN",
            "monto_str": f"{sign}Bs. {monto:,.2f}"
        })
        
    # Check for alerts
    cursor.execute('SELECT COUNT(*) FROM asientos')
    num_asientos = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "balance_total": f"Bs. {total_activos:,.2f}",
        "ingresos": f"Bs. {total_ingresos:,.2f}",
        "egresos": f"Bs. {total_egresos:,.2f}",
        "cuentas_cobrar": f"Bs. {cuentas_cobrar:,.2f}",
        "actividades": actividades,
        "num_asientos": num_asientos
    }

def get_ultimo_anio_asiento():
    # Obtiene el año más reciente registrado en los asientos contables para mostrar ese año por defecto en el Dashboard.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(strftime('%Y', fecha)) FROM asientos")
    res = cursor.fetchone()[0]
    conn.close()
    return int(res) if res else datetime.now().year

def get_flujo_caja(anio):
    # Obtiene la suma mensual de todos los Ingresos (Haber) y Egresos (Debe) para el año especificado,
    # estructurando la información mes a mes (de enero a diciembre) para pintar el gráfico de flujo de caja.
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT strftime('%m', a.fecha) as mes,
               SUM(CASE WHEN c.tipo = 'Ingreso' THEN d.haber - d.debe ELSE 0 END) as ingresos,
               SUM(CASE WHEN c.tipo = 'Egreso' THEN d.debe - d.haber ELSE 0 END) as egresos
        FROM detalle_asientos d
        JOIN asientos a ON d.asiento_id = a.id
        JOIN cuentas c ON d.cuenta_id = c.id
        WHERE strftime('%Y', a.fecha) = ?
        GROUP BY mes
        ORDER BY mes
    ''', (str(anio),))
    
    resultados = cursor.fetchall()
    conn.close()
    
    # Crear estructura vacía para los 12 meses del año
    flujo = {f"{i:02d}": {"ingresos": 0.0, "egresos": 0.0} for i in range(1, 13)}
    for r in resultados:
        mes, ing, egr = r
        flujo[mes] = {
            "ingresos": max(0.0, float(ing or 0.0)),
            "egresos": max(0.0, float(egr or 0.0))
        }
    return flujo

