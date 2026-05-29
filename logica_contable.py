import sqlite3 #Librería para base de datos
from pathlib import Path #Librería para trabajar con rutas de archivos y directorios y que sea compatible con windows y linux

def registrar_asiento(fecha, descripcion_general, detalles): #Primera funcion: registrar_asiento
    """
    Registra un asiento contable completo en el Libro Diario aplicando partida doble.
    
    'detalles' debe ser una lista de diccionarios con este formato: #Aqui se define como debe ser el formato de los detalles del asiento
    [
        {"cuenta_id": 1, "descripcion": "Aporte inicial", "debe": 1000.0, "haber": 0.0}, 
        {"cuenta_id": 5, "descripcion": "Aporte inicial", "debe": 0.0, "haber": 1000.0}
    ]#Nota:Debemos diseñar una interfaz que cumpla con esta estructura de datos para garantizar que los asientos se registren correctamente.
    """
    # Para la logica del programa es necesario validar la Partida Doble antes de tocar la Base de Datos
    total_debe = sum(item.get("debe", 0.0) for item in detalles)
    total_haber = sum(item.get("haber", 0.0) for item in detalles)
    
    # Usamos round() a 2 decimales para evitar errores
    if round(total_debe, 2) != round(total_haber, 2): #si el debe es diferente al haber, entonces no se puede registrar
        return False, f"Error: El asiento no está cuadrado. Debe: {total_debe} | Haber: {total_haber}"
    
    if len(detalles) < 2: #Si solo afecctamos el debe o solo el haber, entonces no se puede registrar
        return False, "Error: Un asiento contable requiere al menos dos cuentas (debe y haber)."

    ruta_db = Path(__file__).parent / "contabilidad.db" #Crea una ruta absoluta y compatible 
    conexion = sqlite3.connect(ruta_db) #Se conecta a la base de datos
    cursor = conexion.cursor() #Crea un cursor
    
    try:
        # Habilitar claves foráneas
        cursor.execute("PRAGMA foreign_keys = ON;") #Habilita las claves foráneas
        
        # Iniciar una transacción explícita. Si algo falla, nada se guarda para conservar la integridad de los datos
        cursor.execute("BEGIN TRANSACTION;")
        
        # Insertar la cabecera del asiento
        cursor.execute("""
            INSERT INTO asientos (fecha, descripcion) 
            VALUES (?, ?);
        """, (fecha, descripcion_general))
        
        # Obtener el ID asignado automáticamente al asiento recién creado
        asiento_id = cursor.lastrowid #Obtiene el id autoincremento del ultimo registro en la tabla asientos
        
        # Insertar cada renglón del detalle
        for item in detalles: #Recorre cada renglón del detalle
            cursor.execute("""
                INSERT INTO detalle_asientos (asiento_id, cuenta_id, descripcion, debe, haber)
                VALUES (?, ?, ?, ?, ?);
            """, (
                asiento_id,
                item["cuenta_id"],
                item.get("descripcion", ""), #Si no se proporciona una descripcion, se inserta una cadena vacia
                item.get("debe", 0.0), #Si no se proporciona un debe, se inserta 0.0
                item.get("haber", 0.0) #Si no se proporciona un haber, se inserta 0.0
            ))
        
        # Si todo se ejecutó bien, guardamos permanentemente en el archivo local
        conexion.commit() #Guarda permanentemente en el archivo local
        return True, f"¡Asiento #{asiento_id} registrado con éxito y cuadrado correctamente!"
        
    except sqlite3.Error as e: #Si ocurre un error de base de datos, cancelamos toda la operación (Rollback)
        conexion.rollback() #Cancela toda la operación
        return False, f"Error en la base de datos al registrar: {e}"
    finally:
        conexion.close() #Cierra la conexión a la base de datos

def obtener_saldos_mayor():
    """
    Actúa como el controlador que procesa todo el Libro Diario, 
    agrupa los movimientos por cuenta y calcula el saldo neto actual
    según la naturaleza de la cuenta (Activo, Pasivo, etc.).
    """
    ruta_db = Path(__file__).parent / "contabilidad.db" #Crea una ruta absoluta y compatible con windows y linux
    conexion = sqlite3.connect(ruta_db) #Se conecta a la base de datos local (archivo contabilidad.db) que se encuentra en el mismo directorio que este script
    # Cambiamos el row_factory para poder acceder a las columnas por su nombre como un diccionario
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # Consulta SQL que hace el "mapeo" es como una estructura de datos que agrupa toda la información relevante de las cuentas y sus movimientos en el Libro Diario
    consulta = """
        SELECT 
            c.id,
            c.codigo,
            c.nombre,
            c.tipo,
            COALESCE(SUM(da.debe), 0.0) as total_debe, #esto es para evitar que si no hay movimientos en el debe o haber, se muestre como 0.0 en lugar de NULL
            COALESCE(SUM(da.haber), 0.0) as total_haber
        FROM cuentas c
        LEFT JOIN detalle_asientos da ON c.id = da.cuenta_id
        GROUP BY c.id;
    """
    
    try:
        cursor.execute(consulta) #esto se usa para realizar la consulta SQL y obtener los datos necesarios para calcular los saldos de cada cuenta en el Libro Mayor
        filas = cursor.fetchall()
        
        cronica_mayor = []
        
        for fila in filas: #Usamos un ciclo para recorrer cada fila del resultado de la consulta y calcular el saldo neto de cada cuenta según su tipo (Activo, Pasivo, etc.) y la lógica contable de partida doble
            t_debe = fila["total_debe"]
            t_haber = fila["total_haber"]
            tipo_cuenta = fila["tipo"]
            
            # Lógica matemática según la naturaleza de la cuenta (Arquitectura del saldo)
            # Activos y Egresos aumentan por el Debe (Saldo Deudor)
            # Pasivos, Capital e Ingresos aumentan por el Haber (Saldo Acreedor)
            if tipo_cuenta in ['Activo', 'Egreso']:
                saldo = t_debe - t_haber
            else:
                saldo = t_haber - t_debe
                
            cronica_mayor.append({
                "codigo": fila["codigo"],
                "nombre": fila["nombre"],
                "tipo": tipo_cuenta,
                "debe": t_debe,
                "haber": t_haber,
                "saldo": round(saldo, 2)
            })
            
        return cronica_mayor
        
    except sqlite3.Error as e:
        print(f"Error de lectura en el bus de datos (DB): {e}")
        return []
    finally:
        conexion.close()
# BLOQUE DE PRUEBA LOCAL: sirve para probar la función directamente desde la terminal
if __name__ == "__main__":
    print("=== CONTROL DE LOGICA CONTABLE ===")
    
    # 1. Ejecutamos una lectura limpia del Libro Mayor antes de operar
    print("\n[INFO] Consultando estado inicial de las cuentas:")
    saldos = obtener_saldos_mayor()
    for s in saldos:
        print(f"Cuenta: {s['nombre']} ({s['tipo']}) | Saldo Actual: {s['saldo']}$")
        
    # 2. Insertamos un movimiento de prueba (Compra de mercancía en efectivo)
    print("\n[INFO] Registrando nueva transacción (Compra de mercancía por 200$)...")
    asiento_mercancia = [
        {"cuenta_id": 3, "descripcion": "Entrada de inventario", "debe": 200.0, "haber": 0.0}, # Inventario (id 3)
        {"cuenta_id": 1, "descripcion": "Pago en efectivo", "debe": 0.0, "haber": 200.0}      # Caja Chica (id 1)
    ]
    exito, mensaje = registrar_asiento("2026-05-28", "Compra de inventario al contado", asiento_mercancia)
    print(mensaje)
    
    # 3. Volvemos a leer el Libro Mayor para verificar el impacto de los datos en tiempo real
    print("\n[INFO] Consultando estado posterior de las cuentas recalculadas:")
    saldos_actualizados = obtener_saldos_mayor()
    for s in saldos_actualizados:
        # Solo mostraremos las cuentas que sufrieron cambios para no saturar la pantalla
        if s['debe'] > 0 or s['haber'] > 0:
            print(f"Cuenta: {s['nombre']} | Total Debe: {s['debe']}$ | Total Haber: {s['haber']}$ | Saldo Neto: {s['saldo']}$")